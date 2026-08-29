import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from app.core.config import settings

class VectorDatabaseManager:
    _instance = None

    def __init__(self):
        self.chroma_client = None
        self.collection = None
        self.use_fallback = False
        self.fallback_file = os.path.join(settings.CHROMA_DIR, "vector_store.json")
        self.vector_store: List[Dict[str, Any]] = []

        self._init_vector_db()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = VectorDatabaseManager()
        return cls._instance

    def _init_vector_db(self):
        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
            self.collection = self.chroma_client.get_or_create_collection(
                name="college_documents",
                metadata={"hnsw:space": "cosine"}
            )
            print("[VectorDatabaseManager] Initialized ChromaDB persistent vector collection.")
        except Exception as e:
            print(f"[VectorDatabaseManager] ChromaDB not available ({e}). Using persistent vector engine.")
            self.use_fallback = True
            self._load_fallback_store()

    def _load_fallback_store(self):
        if os.path.exists(self.fallback_file):
            try:
                with open(self.fallback_file, "r", encoding="utf-8") as f:
                    self.vector_store = json.load(f)
            except Exception as e:
                print(f"[VectorDatabaseManager] Error loading vector_store.json: {e}")
                self.vector_store = []
        else:
            self.vector_store = []

    def _save_fallback_store(self):
        try:
            with open(self.fallback_file, "w", encoding="utf-8") as f:
                json.dump(self.vector_store, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[VectorDatabaseManager] Error saving vector_store.json: {e}")

    def add_chunks(
        self,
        document_id: int,
        document_title: str,
        file_name: str,
        category: str,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ):
        """
        Stores document chunks and their vectors in the vector database.
        """
        if not chunks or not embeddings:
            return

        ids = [f"doc_{document_id}_chunk_{c['chunk_index']}" for c in chunks]
        metadatas = [
            {
                "document_id": document_id,
                "document_title": document_title,
                "file_name": file_name,
                "category": category,
                "chunk_index": c["chunk_index"],
                "page_number": c["page_number"],
                "char_count": c.get("char_count", len(c["chunk_text"]))
            }
            for c in chunks
        ]
        documents = [c["chunk_text"] for c in chunks]

        if not self.use_fallback and self.collection:
            try:
                # Remove existing chunks for this document if re-uploading
                try:
                    self.collection.delete(where={"document_id": document_id})
                except Exception:
                    pass

                self.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas
                )
                print(f"[VectorDatabaseManager] Added {len(chunks)} chunks to ChromaDB.")
                return
            except Exception as e:
                print(f"[VectorDatabaseManager] ChromaDB add error: {e}. Falling back.")
                self.use_fallback = True

        # Fallback persistence
        # First remove existing document chunks
        self.vector_store = [item for item in self.vector_store if item.get("metadata", {}).get("document_id") != document_id]
        
        for i, c in enumerate(chunks):
            item = {
                "id": ids[i],
                "embedding": embeddings[i],
                "document": documents[i],
                "metadata": metadatas[i]
            }
            self.vector_store.append(item)
        
        self._save_fallback_store()
        print(f"[VectorDatabaseManager] Added {len(chunks)} chunks to vector store.")

    def delete_document_chunks(self, document_id: int):
        """Deletes all chunks belonging to a specific document."""
        if not self.use_fallback and self.collection:
            try:
                self.collection.delete(where={"document_id": document_id})
            except Exception as e:
                print(f"[VectorDatabaseManager] Error deleting from ChromaDB: {e}")

        # Update fallback store as well
        self.vector_store = [item for item in self.vector_store if item.get("metadata", {}).get("document_id") != document_id]
        self._save_fallback_store()

    def search_similar(
        self,
        query_embedding: List[float],
        top_k: int = 4,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes semantic similarity search against indexed vector chunks.
        Returns list of dicts:
        [{
            "document": text,
            "metadata": {...},
            "similarity_score": float
        }]
        """
        if not query_embedding:
            return []

        if not self.use_fallback and self.collection:
            try:
                where_filter = {}
                if category_filter and category_filter.lower() != "all":
                    where_filter = {"category": category_filter}

                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=where_filter if where_filter else None
                )

                retrieved = []
                if results and results.get("documents") and results["documents"][0]:
                    docs = results["documents"][0]
                    metas = results["metadatas"][0]
                    distances = results.get("distances", [[]])[0]

                    for idx in range(len(docs)):
                        dist = distances[idx] if idx < len(distances) else 0.5
                        # Chroma cosine distance range: [0, 2], similarity = 1 - dist
                        similarity = max(0.0, 1.0 - (dist / 2.0))
                        retrieved.append({
                            "document": docs[idx],
                            "metadata": metas[idx],
                            "similarity_score": round(similarity, 4)
                        })
                return retrieved
            except Exception as e:
                print(f"[VectorDatabaseManager] ChromaDB search failed: {e}. Falling back.")
                self.use_fallback = True
                self._load_fallback_store()

        # Vector search using cosine similarity
        if not self.vector_store:
            return []

        q_vec = np.array(query_embedding, dtype=float)
        q_norm = np.linalg.norm(q_vec) or 1.0

        scores = []
        for item in self.vector_store:
            meta = item.get("metadata", {})
            if category_filter and category_filter.lower() != "all":
                if meta.get("category", "").lower() != category_filter.lower():
                    continue

            doc_vec = np.array(item["embedding"], dtype=float)
            doc_norm = np.linalg.norm(doc_vec) or 1.0
            
            dot_prod = np.dot(q_vec, doc_vec)
            cosine_sim = dot_prod / (q_norm * doc_norm)

            scores.append({
                "document": item["document"],
                "metadata": meta,
                "similarity_score": round(float(cosine_sim), 4)
            })

        # Sort by similarity descending
        scores.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scores[:top_k]
