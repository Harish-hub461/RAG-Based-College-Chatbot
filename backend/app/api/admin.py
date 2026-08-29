import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.api.auth import get_current_admin, _format_user
from app.schemas.schemas import AdminDashboardStats, UserResponse

router = APIRouter(prefix="/admin", tags=["Admin Portal"])


@router.get("/dashboard", response_model=AdminDashboardStats)
async def get_admin_dashboard(
    db=Depends(get_db),
    admin_user: dict = Depends(get_current_admin)
):
    total_docs = await db["documents"].count_documents({})
    total_chunks = await db["document_chunks"].count_documents({})
    total_conversations = await db["conversations"].count_documents({})
    total_questions = await db["messages"].count_documents({"sender": "user"})
    unanswered_count = await db["messages"].count_documents({"is_unanswered": True})

    # Category breakdown
    pipeline = [{"$group": {"_id": "$category", "count": {"$sum": 1}}}]
    cat_cursor = db["documents"].aggregate(pipeline)
    categories_breakdown = {}
    async for doc in cat_cursor:
        categories_breakdown[doc["_id"] or "General"] = doc["count"]

    # Recent documents
    recent_cursor = db["documents"].find({}).sort("created_at", -1).limit(5)
    recent_docs_raw = await recent_cursor.to_list(length=5)
    recent_docs = []
    for d in recent_docs_raw:
        recent_docs.append({
            "id": str(d["_id"]),
            "title": d["title"],
            "file_name": d["file_name"],
            "file_type": d["file_type"],
            "category": d.get("category", "General"),
            "version": d.get("version", "1.0"),
            "uploaded_by": str(d["uploaded_by"]),
            "processing_status": d.get("processing_status", "pending"),
            "page_count": d.get("page_count", 0),
            "chunk_count": d.get("chunk_count", 0),
            "error_message": d.get("error_message"),
            "file_path": d.get("file_path", ""),
            "created_at": d.get("created_at", datetime.datetime.utcnow()),
            "updated_at": d.get("updated_at", d.get("created_at", datetime.datetime.utcnow())),
        })

    # Top user questions
    msg_pipeline = [
        {"$match": {"sender": "user"}},
        {"$group": {"_id": "$message_text", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    top_cursor = db["messages"].aggregate(msg_pipeline)
    top_topics = []
    async for item in top_cursor:
        top_topics.append({"question": item["_id"], "count": item["count"]})

    return AdminDashboardStats(
        total_documents=total_docs,
        total_chunks=total_chunks,
        total_conversations=total_conversations,
        total_questions=total_questions,
        unanswered_questions_count=unanswered_count,
        categories_breakdown=categories_breakdown,
        recent_documents=recent_docs,
        frequently_asked_topics=top_topics
    )


@router.get("/analytics")
async def get_analytics(
    db=Depends(get_db),
    admin_user: dict = Depends(get_current_admin)
):
    cursor = db["messages"].find(
        {"sender": "user", "is_unanswered": True}
    ).sort("created_at", -1).limit(20)
    unanswered_msgs = await cursor.to_list(length=20)
    unanswered_list = [
        {"question": m["message_text"], "timestamp": str(m.get("created_at", ""))}
        for m in unanswered_msgs
    ]

    pipeline = [
        {"$lookup": {"from": "documents", "localField": "document_id", "foreignField": "_id", "as": "doc"}},
        {"$unwind": "$doc"},
        {"$group": {"_id": "$doc.category", "chunks": {"$sum": 1}}},
    ]
    chunk_cursor = db["document_chunks"].aggregate(pipeline)
    chunk_distribution = {}
    async for item in chunk_cursor:
        chunk_distribution[item["_id"] or "General"] = item["chunks"]

    return {
        "unanswered_questions": unanswered_list,
        "chunk_distribution": chunk_distribution
    }


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    db=Depends(get_db),
    admin_user: dict = Depends(get_current_admin)
):
    cursor = db["users"].find({}).sort("created_at", -1)
    users = await cursor.to_list(length=500)
    return [UserResponse(**_format_user(u)) for u in users]
