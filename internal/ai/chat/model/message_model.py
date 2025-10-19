from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base
import uuid

class ChatMessage(Base):
    """Model for storing all chat messages"""
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    course_session_id = Column(UUID(as_uuid=True), ForeignKey("course_chat_sessions.id"), nullable=True)
    guide_session_id = Column(UUID(as_uuid=True), ForeignKey("guide_chat_sessions.id"), nullable=True)
    content = Column(Text, nullable=False)
    is_user = Column(Boolean, nullable=False)  # True for user message, False for AI response
    message_order = Column(Integer, nullable=False)  # Order within the session
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    course_session = relationship("CourseChatSession", back_populates="messages", foreign_keys=[course_session_id])
    guide_session = relationship("GuideChatSession", back_populates="messages", foreign_keys=[guide_session_id])

