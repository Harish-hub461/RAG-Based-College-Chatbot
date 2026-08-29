import os
import shutil
import datetime
from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from app.core.config import settings
from app.core.database import get_db
from app.api.auth import get_current_user, get_current_admin
from app.schemas.schemas import DocumentResponse, DocumentUpdate
from app.rag.pipeline import RAGPipeline
from app.rag.vector_db import VectorDatabaseManager

router = APIRouter(prefix="/documents", tags=["Document Management"])
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}


def _doc_to_response(doc: dict) -> DocumentResponse:
    return DocumentResponse(
        id=str(doc["_id"]),
        title=doc["title"],
        file_name=doc["file_name"],
        file_path=doc["file_path"],
        file_type=doc["file_type"],
        category=doc.get("category", "General"),
        version=doc.get("version", "1.0"),
        uploaded_by=str(doc["uploaded_by"]),
        processing_status=doc.get("processing_status", "pending"),
        page_count=doc.get("page_count", 0),
        chunk_count=doc.get("chunk_count", 0),
        error_message=doc.get("error_message"),
        created_at=doc.get("created_at", datetime.datetime.utcnow()),
        updated_at=doc.get("updated_at", doc.get("created_at", datetime.datetime.utcnow())),
    )


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    title: str = Form(...),
    category: str = Form("General"),
    version: str = Form("1.0"),
    file: UploadFile = File(...),
    db=Depends(get_db),
    admin_user: dict = Depends(get_current_admin)
):
    filename = file.filename
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '.{ext}'. Supported formats: PDF, DOCX, TXT."
        )

    safe_filename = f"{str(admin_user['_id'])}_{int(os.urandom(4).hex(), 16)}_{filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    now = datetime.datetime.utcnow()
    doc_dict = {
        "title": title,
        "file_name": filename,
        "file_path": file_path,
        "file_type": ext,
        "category": category,
        "version": version,
        "uploaded_by": admin_user["_id"],
        "processing_status": "pending",
        "page_count": 0,
        "chunk_count": 0,
        "error_message": None,
        "created_at": now,
        "updated_at": now,
    }
    result = await db["documents"].insert_one(doc_dict)
    doc_dict["_id"] = result.inserted_id

    # Process via RAG pipeline
    RAGPipeline.process_document_mongo(db, str(result.inserted_id))

    # Refresh from DB
    doc_dict = await db["documents"].find_one({"_id": result.inserted_id})
    return _doc_to_response(doc_dict)


@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    category: Optional[str] = None,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = {}
    if category and category.lower() != "all":
        query["category"] = category

    cursor = db["documents"].find(query).sort("created_at", -1)
    docs = await cursor.to_list(length=200)
    return [_doc_to_response(d) for d in docs]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        doc = await db["documents"].find_one({"_id": ObjectId(document_id)})
    except Exception:
        raise HTTPException(status_code=404, detail="Document not found")
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return _doc_to_response(doc)


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    doc_in: DocumentUpdate,
    db=Depends(get_db),
    admin_user: dict = Depends(get_current_admin)
):
    try:
        oid = ObjectId(document_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = await db["documents"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    update_fields = {"updated_at": datetime.datetime.utcnow()}
    if doc_in.title is not None:
        update_fields["title"] = doc_in.title
    if doc_in.category is not None:
        update_fields["category"] = doc_in.category
    if doc_in.version is not None:
        update_fields["version"] = doc_in.version

    await db["documents"].update_one({"_id": oid}, {"$set": update_fields})
    doc = await db["documents"].find_one({"_id": oid})
    return _doc_to_response(doc)


@router.post("/{document_id}/reprocess", response_model=DocumentResponse)
async def reprocess_document(
    document_id: str,
    db=Depends(get_db),
    admin_user: dict = Depends(get_current_admin)
):
    try:
        oid = ObjectId(document_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = await db["documents"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    RAGPipeline.process_document_mongo(db, document_id)
    doc = await db["documents"].find_one({"_id": oid})
    return _doc_to_response(doc)


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db=Depends(get_db),
    admin_user: dict = Depends(get_current_admin)
):
    try:
        oid = ObjectId(document_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = await db["documents"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if os.path.exists(doc.get("file_path", "")):
        try:
            os.remove(doc["file_path"])
        except Exception:
            pass

    vec_mgr = VectorDatabaseManager.get_instance()
    vec_mgr.delete_document_chunks(document_id)

    await db["document_chunks"].delete_many({"document_id": oid})
    await db["documents"].delete_one({"_id": oid})
    return {"message": f"Document {document_id} deleted successfully"}
