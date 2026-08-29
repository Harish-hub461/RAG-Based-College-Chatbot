import os
import sys
import asyncio
import datetime

# Ensure backend folder is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.security import get_password_hash
from app.rag.pipeline import RAGPipeline

import certifi

async def run_test():
    print("=" * 60)
    print("  AUTOMATED END-TO-END RAG PIPELINE TEST (MongoDB Atlas)  ")
    print("=" * 60)

    client = AsyncIOMotorClient(settings.DATABASE_URL, tlsAllowInvalidCertificates=True)
    db = client.get_default_database()
    print(f"[MongoDB] Connected to database: {db.name}")

    try:
        # 1. Admin Verification
        admin = await db["users"].find_one({"role": "admin"})
        if not admin:
            new_admin = {
                "name": "Test Admin",
                "email": settings.ADMIN_EMAIL.lower(),
                "password_hash": get_password_hash(settings.ADMIN_PASSWORD),
                "role": "admin",
                "created_at": datetime.datetime.utcnow(),
            }
            res = await db["users"].insert_one(new_admin)
            new_admin["_id"] = res.inserted_id
            admin = new_admin
        print(f"[TEST 1] Admin User Ready: {admin['email']} (ID: {admin['_id']})")

        # 2. Upload and Index Sample Document
        sample_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample_docs", "CSE_Admissions_and_Fees_2026.txt"))
        if not os.path.exists(sample_path):
            print(f"Error: Sample file missing at {sample_path}")
            return

        doc = await db["documents"].find_one({"file_name": "CSE_Admissions_and_Fees_2026.txt"})
        if not doc:
            now = datetime.datetime.utcnow()
            doc_dict = {
                "title": "CSE Admissions Bulletin 2026",
                "file_name": "CSE_Admissions_and_Fees_2026.txt",
                "file_path": sample_path,
                "file_type": "txt",
                "category": "Admissions",
                "version": "1.0",
                "uploaded_by": admin["_id"],
                "processing_status": "pending",
                "page_count": 0,
                "chunk_count": 0,
                "error_message": None,
                "created_at": now,
                "updated_at": now,
            }
            res = await db["documents"].insert_one(doc_dict)
            doc_dict["_id"] = res.inserted_id
            doc = doc_dict
        
        doc_id_str = str(doc["_id"])
        print(f"[TEST 2] Processing Document ID {doc_id_str}...")
        success = RAGPipeline.process_document_mongo(db, doc_id_str)
        
        doc = await db["documents"].find_one({"_id": doc["_id"]})
        print(f"         Processing Status: {doc.get('processing_status')}")
        print(f"         Chunks Created: {doc.get('chunk_count')}")

        assert success, "Document processing failed"
        assert doc.get("chunk_count", 0) > 0, "No chunks were created"

        # 3. Query RAG with Supported Question
        question_1 = "What is the tuition fee for CSE?"
        print(f"\n[TEST 3] Querying Supported Question: '{question_1}'")
        res_1 = RAGPipeline.query(question_1)
        print("         Answer Response:")
        print("         " + res_1["answer"].replace("\n", "\n         "))
        print(f"         Sources Count: {len(res_1['sources'])}")
        for s in res_1["sources"]:
            print(f"         - Document: {s['document_title']} | Page: {s['page_number']} | Score: {s['similarity_score']}")

        assert len(res_1["sources"]) > 0, "Expected sources for supported question"
        assert not res_1["is_unanswered"], "Question should be answered"

        # 4. Query RAG with Unsupported Question (Non-Hallucination Check)
        question_2 = "What is the secret recipe for chocolate cake?"
        print(f"\n[TEST 4] Querying Unsupported Question: '{question_2}'")
        res_2 = RAGPipeline.query(question_2)
        print("         Answer Response:")
        print("         " + res_2["answer"].replace("\n", "\n         "))
        print(f"         Is Unanswered Flag: {res_2['is_unanswered']}")

        assert res_2["is_unanswered"], "Off-topic question should be flagged unanswered"
        assert "couldn't find reliable information" in res_2["answer"].lower(), "Response must be safe unknown fallback"

        print("\n" + "=" * 60)
        print("  ALL RAG PIPELINE TESTS (MongoDB Atlas) PASSED SUCCESSFULLY!  ")
        print("=" * 60)

    except Exception as e:
        print(f"\n[TEST FAILED]: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(run_test())

