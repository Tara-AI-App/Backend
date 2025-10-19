from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class ChatRequest(BaseModel):
    """Request model for chat messages"""
    message: str

class ChatResponse(BaseModel):
    """Response model for chat messages"""
    response: str
    session_id: str
    timestamp: datetime

class CourseChatRequest(ChatRequest):
    """Request model for course chat messages"""
    pass

class CourseChatResponse(ChatResponse):
    """Response model for course chat messages"""
    pass

class GuideChatRequest(ChatRequest):
    """Request model for guide chat messages"""
    pass

class GuideChatResponse(ChatResponse):
    """Response model for guide chat messages"""
    pass

class ChatMessageResponse(BaseModel):
    """Response model for individual chat messages"""
    id: str
    content: str
    is_user: bool
    timestamp: datetime
    message_order: int

class ChatSessionResponse(BaseModel):
    """Response model for chat session info"""
    id: str
    ai_session_id: str
    created_at: datetime
    updated_at: datetime
