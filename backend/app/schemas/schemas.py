from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, EmailStr

# Auth Schemas
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[str] = "student"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str          # MongoDB ObjectId as string
    name: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Document Schemas
class DocumentResponse(BaseModel):
    id: str          # MongoDB ObjectId as string
    title: str
    file_name: str
    file_path: str
    file_type: str
    category: str
    version: str
    uploaded_by: str  # MongoDB ObjectId as string
    processing_status: str
    page_count: int
    chunk_count: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    version: Optional[str] = None

# Chat & RAG Schemas
class SourceReference(BaseModel):
    document_id: Any     # can be int or str
    document_title: str
    file_name: str
    category: str
    page_number: int
    similarity_score: float
    snippet: str

class AskQuestionRequest(BaseModel):
    conversation_id: Optional[str] = None   # MongoDB ObjectId string
    question: str
    category_filter: Optional[str] = None

class MessageResponse(BaseModel):
    id: str              # MongoDB ObjectId as string
    conversation_id: str
    sender: str
    message_text: str
    sources: Optional[List[SourceReference]] = None
    is_unanswered: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: str              # MongoDB ObjectId as string
    user_id: str
    title: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: Optional[List[MessageResponse]] = []

    class Config:
        from_attributes = True

class FeedbackCreate(BaseModel):
    message_id: str      # MongoDB ObjectId string
    rating: int          # 1 or -1
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: str
    message_id: str
    user_id: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Dashboard & Analytics Schemas
class AdminDashboardStats(BaseModel):
    total_documents: int
    total_chunks: int
    total_conversations: int
    total_questions: int
    unanswered_questions_count: int
    categories_breakdown: dict
    recent_documents: List[Any]
    frequently_asked_topics: List[dict]
