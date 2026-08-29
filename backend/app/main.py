import os
import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection, get_db
from app.core.security import get_password_hash
from app.api import auth, documents, chat, admin
from app.rag.pipeline import RAGPipeline

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Full-stack Retrieval-Augmented Generation (RAG) College Information Assistant API"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup():
    """Connect to MongoDB and seed default data."""
    await connect_to_mongo()
    db = get_db()

    try:
        # Seed default admin user
        admin_user = await db["users"].find_one({"email": settings.ADMIN_EMAIL.lower()})
        if not admin_user:
            new_admin = {
                "name": settings.ADMIN_NAME,
                "email": settings.ADMIN_EMAIL.lower(),
                "password_hash": get_password_hash(settings.ADMIN_PASSWORD),
                "role": "admin",
                "created_at": datetime.datetime.utcnow(),
            }
            result = await db["users"].insert_one(new_admin)
            new_admin["_id"] = result.inserted_id
            admin_user = new_admin
            print(f"[Startup] Seeded default Admin user ({settings.ADMIN_EMAIL}).")

        # Seed sample documents if none exist
        doc_count = await db["documents"].count_documents({})
        if doc_count == 0:
            sample_files = [
                {
                    "title": "CSE Admissions & Fee Structure 2026",
                    "file_name": "CSE_Admissions_and_Fees_2026.txt",
                    "category": "Admissions",
                    "path": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sample_docs", "CSE_Admissions_and_Fees_2026.txt"))
                },
                {
                    "title": "Hostel Residence & Campus Policies 2026",
                    "file_name": "Hostel_and_Campus_Rules_2026.txt",
                    "category": "Hostel",
                    "path": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sample_docs", "Hostel_and_Campus_Rules_2026.txt"))
                },
                {
                    "title": "Scholarships & Career Placement Bulletin 2026",
                    "file_name": "Scholarships_and_Placements_2026.txt",
                    "category": "Scholarships",
                    "path": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sample_docs", "Scholarships_and_Placements_2026.txt"))
                }
            ]

            for s in sample_files:
                if os.path.exists(s["path"]):
                    now = datetime.datetime.utcnow()
                    doc_dict = {
                        "title": s["title"],
                        "file_name": s["file_name"],
                        "file_path": s["path"],
                        "file_type": "txt",
                        "category": s["category"],
                        "version": "1.0",
                        "uploaded_by": admin_user["_id"],
                        "processing_status": "pending",
                        "page_count": 0,
                        "chunk_count": 0,
                        "error_message": None,
                        "created_at": now,
                        "updated_at": now,
                    }
                    result = await db["documents"].insert_one(doc_dict)
                    # Schedule async document processing in background (don't await)
                    # RAGPipeline.process_document_mongo(db, str(result.inserted_id))

            print("[Startup] Seeded initial sample college policy documents.")
    except Exception as e:
        print(f"[Startup] Error during seeding: {e}")


@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()


@app.get("/")
def root():
    return {
        "status": "online",
        "message": f"Welcome to {settings.PROJECT_NAME} API v{settings.VERSION}",
        "docs": "/docs"
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}
