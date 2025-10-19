from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base
import uuid

class CourseChatSession(Base):
    """Model for permanent course chat sessions - one per user per course"""
    __tablename__ = "course_chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    ai_session_id = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Unique constraint: one session per user per course
    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', name='uq_user_course_session'),
    )
    
    # Relationships
    user = relationship("UserModel", backref="course_chat_sessions")
    course = relationship("CourseModel", backref="chat_sessions")
    messages = relationship("ChatMessage", back_populates="course_session", cascade="all, delete-orphan", foreign_keys="[ChatMessage.course_session_id]")


class GuideChatSession(Base):
    """Model for permanent guide chat sessions - one per user per guide"""
    __tablename__ = "guide_chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    guide_id = Column(UUID(as_uuid=True), ForeignKey("guides.id"), nullable=False)
    ai_session_id = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Unique constraint: one session per user per guide
    __table_args__ = (
        UniqueConstraint('user_id', 'guide_id', name='uq_user_guide_session'),
    )
    
    # Relationships
    user = relationship("UserModel", backref="guide_chat_sessions")
    guide = relationship("GuideModel", backref="chat_sessions")
    messages = relationship("ChatMessage", back_populates="guide_session", cascade="all, delete-orphan", foreign_keys="[ChatMessage.guide_session_id]")

