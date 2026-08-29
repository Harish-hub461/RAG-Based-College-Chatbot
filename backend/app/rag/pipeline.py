import json
import re
import asyncio
import datetime
import requests
from typing import Dict, Any, List, Optional
from bson import ObjectId

from app.core.config import settings
from app.rag.extractor import DocumentExtractor
from app.rag.chunker import TextChunker
from app.rag.embedder import VectorEmbedder
from app.rag.vector_db import VectorDatabaseManager


class RAGPipeline:
    UNANSWERED_RESPONSE = (
        "I couldn't find reliable information about this in the available college documents. "
        "Please contact the relevant department or try asking in a different way."
    )

    GREETINGS = {
        "hi", "hii", "hiii", "hello", "hey", "heyy", "greetings", "good morning", 
        "good afternoon", "good evening", "i have a doubt", "i have a question",
        "who are you", "what can you do", "help", "can you help me"
    }

    GREETING_RESPONSE = (
        "Hello! I am your official College Information Assistant. "
        "I can help you with questions regarding admissions, course fee structures, hostel policies, exam schedules, scholarships, and placement details. "
        "What specific information would you like to know?"
    )

    @classmethod
    def process_document(cls, db, document_id: int) -> bool:
        """
        Executes full document indexing pipeline:
        Extraction -> Cleaning -> Chunking -> Database Chunks -> Embeddings -> Vector DB
        """
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return False

        try:
            doc.processing_status = "processing"
            db.commit()

            # 1. Text Extraction
            pages = DocumentExtractor.extract_text(doc.file_path, doc.file_type)
            doc.page_count = len(pages)

            # 2. Chunking
            chunks = TextChunker.chunk_pages(
                extracted_pages=pages,
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP
            )

            if not chunks:
                doc.processing_status = "error"
                doc.error_message = "No readable text content found in document."
                db.commit()
                return False

            # Delete old relational chunks if any
            db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()
            db.commit()

            # 3. Create Relational DB Chunks
            for c in chunks:
                chunk_obj = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=c["chunk_index"],
                    chunk_text=c["chunk_text"],
                    page_number=c["page_number"],
                    metadata_json=json.dumps({
                        "category": doc.category,
                        "title": doc.title,
                        "file_name": doc.file_name
                    })
                )
                db.add(chunk_obj)
            db.commit()

            # 4. Generate Embeddings
            chunk_texts = [c["chunk_text"] for c in chunks]
            embeddings = VectorEmbedder.embed_texts(chunk_texts)

            # 5. Store in Vector DB
            vec_mgr = VectorDatabaseManager.get_instance()
            vec_mgr.add_chunks(
                document_id=doc.id,
                document_title=doc.title,
                file_name=doc.file_name,
                category=doc.category,
                chunks=chunks,
                embeddings=embeddings
            )

            # Update Document state
            doc.chunk_count = len(chunks)
            doc.processing_status = "completed"
            doc.error_message = None
            db.commit()
            print(f"[RAGPipeline] Successfully processed Document ID {doc.id} ({len(chunks)} chunks).")
            return True

        except Exception as e:
            db.rollback()
            doc.processing_status = "error"
            doc.error_message = str(e)
            db.commit()
            print(f"[RAGPipeline] Error processing document {document_id}: {e}")
            return False

    @classmethod
    def process_document_mongo(cls, db, document_id: str) -> bool:
        """
        Executes full document indexing pipeline for MongoDB:
        Extraction -> Cleaning -> Chunking -> MongoDB Chunks -> Embeddings -> Vector DB
        """
        async def _run():
            try:
                oid = ObjectId(document_id)
                doc = await db["documents"].find_one({"_id": oid})
                if not doc:
                    return False

                await db["documents"].update_one({"_id": oid}, {"$set": {"processing_status": "processing"}})

                pages = DocumentExtractor.extract_text(doc["file_path"], doc["file_type"])
                await db["documents"].update_one({"_id": oid}, {"$set": {"page_count": len(pages)}})

                chunks = TextChunker.chunk_pages(
                    extracted_pages=pages,
                    chunk_size=settings.CHUNK_SIZE,
                    chunk_overlap=settings.CHUNK_OVERLAP
                )

                if not chunks:
                    await db["documents"].update_one({"_id": oid}, {"$set": {
                        "processing_status": "error",
                        "error_message": "No readable text content found in document."
                    }})
                    return False

                # Delete old chunks
                await db["document_chunks"].delete_many({"document_id": oid})

                # Store new chunks in MongoDB
                now = datetime.datetime.utcnow()
                chunk_docs = []
                for c in chunks:
                    chunk_docs.append({
                        "document_id": oid,
                        "chunk_index": c["chunk_index"],
                        "chunk_text": c["chunk_text"],
                        "page_number": c["page_number"],
                        "metadata_json": json.dumps({
                            "category": doc["category"],
                            "title": doc["title"],
                            "file_name": doc["file_name"]
                        }),
                        "created_at": now,
                    })
                if chunk_docs:
                    await db["document_chunks"].insert_many(chunk_docs)

                # Generate Embeddings
                chunk_texts = [c["chunk_text"] for c in chunks]
                embeddings = VectorEmbedder.embed_texts(chunk_texts)

                # Store in Vector DB
                vec_mgr = VectorDatabaseManager.get_instance()
                vec_mgr.add_chunks(
                    document_id=document_id,
                    document_title=doc["title"],
                    file_name=doc["file_name"],
                    category=doc["category"],
                    chunks=chunks,
                    embeddings=embeddings
                )

                await db["documents"].update_one({"_id": oid}, {"$set": {
                    "chunk_count": len(chunks),
                    "processing_status": "completed",
                    "error_message": None,
                    "updated_at": datetime.datetime.utcnow(),
                }})

                print(f"[RAGPipeline] Successfully processed MongoDB Document ID {document_id} ({len(chunks)} chunks).")
                return True

            except Exception as e:
                try:
                    await db["documents"].update_one(
                        {"_id": ObjectId(document_id)},
                        {"$set": {"processing_status": "error", "error_message": str(e)}}
                    )
                except Exception:
                    pass
                print(f"[RAGPipeline] Error processing MongoDB document {document_id}: {e}")
                return False

        # Run async function in event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, _run())
                    return future.result(timeout=60)
            else:
                return loop.run_until_complete(_run())
        except Exception as e:
            print(f"[RAGPipeline] process_document_mongo scheduling error: {e}")
            return False

    @classmethod
    def query(cls, question: str, category_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes complete question answering RAG workflow:
        Query embedding -> Vector similarity search -> Grounding verification -> LLM answer generation -> Source mapping
        """
        clean_q = question.strip().lower()
        if not clean_q:
            return {
                "answer": "Please ask a specific college-related question.",
                "sources": [],
                "is_unanswered": True
            }

        # 0. Check for conversational greetings
        clean_no_punct = re.sub(r'[^\w\s]', '', clean_q)
        if clean_no_punct in cls.GREETINGS or clean_q in cls.GREETINGS:
            return {
                "answer": cls.GREETING_RESPONSE,
                "sources": [],
                "is_unanswered": False
            }

        # 1. Query Embedding
        query_vector = VectorEmbedder.embed_query(question)

        # 2. Vector Similarity Search
        vec_mgr = VectorDatabaseManager.get_instance()
        retrieved_results = vec_mgr.search_similar(
            query_embedding=query_vector,
            top_k=settings.TOP_K_CHUNKS,
            category_filter=category_filter
        )

        # 3. Filter by similarity threshold
        threshold = settings.SIMILARITY_THRESHOLD
        relevant_chunks = [r for r in retrieved_results if r["similarity_score"] >= threshold]

        # Category Fallback: If no hit with active category filter, retry across all categories
        if not relevant_chunks and category_filter and category_filter.lower() != "all":
            all_retrieved = vec_mgr.search_similar(
                query_embedding=query_vector,
                top_k=settings.TOP_K_CHUNKS,
                category_filter=None
            )
            relevant_chunks = [r for r in all_retrieved if r["similarity_score"] >= threshold]

        # 4. Handle Unknown / Unanswered questions
        if not relevant_chunks:
            return {
                "answer": cls.UNANSWERED_RESPONSE,
                "sources": [],
                "is_unanswered": True
            }

        # 5. Format Context and Source References
        context_str_list = []
        sources = []

        for idx, item in enumerate(relevant_chunks, 1):
            meta = item["metadata"]
            doc_title = meta.get("document_title", meta.get("file_name", "College Document"))
            page_num = meta.get("page_number", 1)
            category = meta.get("category", "General")
            score = item["similarity_score"]
            text_snippet = item["document"]

            context_str_list.append(
                f"[Source {idx} - Document: '{doc_title}' (Category: {category}, Page {page_num})]:\n{text_snippet}"
            )

            sources.append({
                "document_id": meta.get("document_id", 0),
                "document_title": doc_title,
                "file_name": meta.get("file_name", "document.pdf"),
                "category": category,
                "page_number": page_num,
                "similarity_score": score,
                "snippet": text_snippet[:200] + "..." if len(text_snippet) > 200 else text_snippet
            })

        combined_context = "\n\n".join(context_str_list)

        # 6. Generate LLM Response
        answer = cls._generate_llm_answer(question, combined_context)

        return {
            "answer": answer,
            "sources": sources,
            "is_unanswered": False
        }

    @classmethod
    def _generate_llm_answer(cls, question: str, context: str) -> str:
        """
        Sends grounded RAG prompt to Gemini API, OpenAI API, or uses local grounded synthesizer.
        """
        prompt = (
            "You are an authoritative, helpful College Information Assistant.\n"
            "Your job is to answer student questions accurately based ONLY on the provided official college document context.\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. Base your answer STRICTLY on the retrieved context below.\n"
            "2. Do NOT invent information or assume facts not stated in the context.\n"
            "3. If the context does not contain enough information to answer the question, state: "
            f"'{cls.UNANSWERED_RESPONSE}'\n"
            "4. Provide a clear, professional, and well-structured answer.\n\n"
            f"=== RETRIEVED COLLEGE DOCUMENTS CONTEXT ===\n{context}\n\n"
            f"=== STUDENT QUESTION ===\n{question}\n\n"
            "=== ANSWER ==="
        )

        # Attempt Gemini API via REST if API Key is set
        if settings.GEMINI_API_KEY:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.LLM_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
                headers = {"Content-Type": "application/json"}
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.2, "maxOutputTokens": 800}
                }
                res = requests.post(url, headers=headers, json=payload, timeout=15)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                        if text:
                            return text
            except Exception as e:
                print(f"[RAGPipeline] Gemini REST call failed: {e}")

        # Attempt OpenAI API via REST if API Key is set
        if settings.OPENAI_API_KEY:
            try:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are a helpful college information assistant. Answer strictly based on context."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2
                }
                res = requests.post(url, headers=headers, json=payload, timeout=15)
                if res.status_code == 200:
                    data = res.json()
                    text = data["choices"][0]["message"]["content"].strip()
                    if text:
                        return text
            except Exception as e:
                print(f"[RAGPipeline] OpenAI REST call failed: {e}")

        # Local Grounded Context Synthesizer (Fallback when no external API key is active)
        return cls._local_grounded_synthesis(question, context)

    @staticmethod
    def _local_grounded_synthesis(question: str, context: str) -> str:
        """
        Synthesizes an answer directly from the top retrieved text chunks when no API key is provided.
        """
        lines = [line.strip() for line in context.split("\n") if line.strip() and not line.startswith("[Source")]
        summary_paragraphs = lines[:6]
        
        body = "\n\n".join(summary_paragraphs)
        return (
            f"Based on the official college documents:\n\n"
            f"{body}\n\n"
            f"*(Note: Information retrieved directly from official college documentation)*"
        )
