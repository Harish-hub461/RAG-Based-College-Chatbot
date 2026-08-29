import json
import datetime
from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_db
from app.api.auth import get_current_user
from app.schemas.schemas import (
    AskQuestionRequest, MessageResponse, ConversationResponse,
    FeedbackCreate, FeedbackResponse
)
from app.rag.pipeline import RAGPipeline

router = APIRouter(prefix="/chat", tags=["Chat & RAG"])


def _msg_to_response(msg: dict) -> MessageResponse:
    sources_data = json.loads(msg["sources_json"]) if msg.get("sources_json") else None
    return MessageResponse(
        id=str(msg["_id"]),
        conversation_id=str(msg["conversation_id"]),
        sender=msg["sender"],
        message_text=msg["message_text"],
        sources=sources_data,
        is_unanswered=msg.get("is_unanswered", False),
        created_at=msg.get("created_at", datetime.datetime.utcnow()),
    )


@router.post("/ask", response_model=MessageResponse)
async def ask_question(
    payload: AskQuestionRequest,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    user_id = current_user["_id"]

    # Fetch or create conversation
    conversation = None
    if payload.conversation_id:
        try:
            conversation = await db["conversations"].find_one({
                "_id": ObjectId(payload.conversation_id),
                "user_id": user_id
            })
        except Exception:
            pass

    if not conversation:
        title = question[:40] + "..." if len(question) > 40 else question
        conv_doc = {
            "user_id": user_id,
            "title": title,
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow(),
        }
        result = await db["conversations"].insert_one(conv_doc)
        conv_doc["_id"] = result.inserted_id
        conversation = conv_doc

    conv_id = conversation["_id"]

    # Save user message
    user_msg = {
        "conversation_id": conv_id,
        "sender": "user",
        "message_text": question,
        "sources_json": None,
        "is_unanswered": False,
        "created_at": datetime.datetime.utcnow(),
    }
    await db["messages"].insert_one(user_msg)

    # Execute RAG pipeline
    rag_result = RAGPipeline.query(question=question, category_filter=payload.category_filter)
    sources_json = json.dumps(rag_result["sources"]) if rag_result["sources"] else None

    # Save AI response
    ai_msg = {
        "conversation_id": conv_id,
        "sender": "ai",
        "message_text": rag_result["answer"],
        "sources_json": sources_json,
        "is_unanswered": rag_result["is_unanswered"],
        "created_at": datetime.datetime.utcnow(),
    }
    result = await db["messages"].insert_one(ai_msg)
    ai_msg["_id"] = result.inserted_id

    # Update conversation timestamp
    await db["conversations"].update_one(
        {"_id": conv_id},
        {"$set": {"updated_at": datetime.datetime.utcnow()}}
    )

    return _msg_to_response(ai_msg)


@router.get("/history", response_model=List[ConversationResponse])
async def get_chat_history(
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["_id"]
    cursor = db["conversations"].find({"user_id": user_id}).sort("updated_at", -1)
    conversations = await cursor.to_list(length=100)

    result = []
    for conv in conversations:
        result.append(ConversationResponse(
            id=str(conv["_id"]),
            user_id=str(conv["user_id"]),
            title=conv.get("title", "Conversation"),
            created_at=conv.get("created_at", datetime.datetime.utcnow()),
            updated_at=conv.get("updated_at", conv.get("created_at", datetime.datetime.utcnow())),
            messages=[]
        ))
    return result


@router.get("/conversation/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        conv = await db["conversations"].find_one({
            "_id": ObjectId(conversation_id),
            "user_id": current_user["_id"]
        })
    except Exception:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msgs_cursor = db["messages"].find({"conversation_id": conv["_id"]}).sort("created_at", 1)
    msgs = await msgs_cursor.to_list(length=500)
    messages_resp = [_msg_to_response(m) for m in msgs]

    return ConversationResponse(
        id=str(conv["_id"]),
        user_id=str(conv["user_id"]),
        title=conv.get("title", "Conversation"),
        created_at=conv.get("created_at", datetime.datetime.utcnow()),
        updated_at=conv.get("updated_at", conv.get("created_at", datetime.datetime.utcnow())),
        messages=messages_resp
    )


@router.delete("/conversation/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        oid = ObjectId(conversation_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv = await db["conversations"].find_one({"_id": oid, "user_id": current_user["_id"]})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await db["messages"].delete_many({"conversation_id": oid})
    await db["conversations"].delete_one({"_id": oid})
    return {"message": f"Conversation {conversation_id} deleted"}


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    fb_in: FeedbackCreate,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        msg_oid = ObjectId(str(fb_in.message_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Message not found")

    msg = await db["messages"].find_one({"_id": msg_oid})
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    feedback_doc = {
        "message_id": msg_oid,
        "user_id": current_user["_id"],
        "rating": fb_in.rating,
        "comment": fb_in.comment,
        "created_at": datetime.datetime.utcnow(),
    }
    result = await db["feedback"].insert_one(feedback_doc)
    feedback_doc["_id"] = result.inserted_id

    return FeedbackResponse(
        id=str(feedback_doc["_id"]),
        message_id=str(msg_oid),
        user_id=str(current_user["_id"]),
        rating=fb_in.rating,
        comment=fb_in.comment,
        created_at=feedback_doc["created_at"],
    )
