from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base
import uuid

# Learning Management System Models Only

class DepartmentModel(Base):
    """Department model"""
    __tablename__ = "departments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    users = relationship("UserModel", back_populates="department")

class PositionModel(Base):
    """Position model"""
    __tablename__ = "positions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    users = relationship("UserModel", back_populates="position")

class LocationModel(Base):
    """Location model"""
    __tablename__ = "locations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    city = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    users = relationship("UserModel", back_populates="location")

class UserModel(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    position_id = Column(UUID(as_uuid=True), ForeignKey("positions.id"), nullable=True)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True)
    name = Column(String(255), nullable=False)
    image = Column(String(500), nullable=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=True)  # Added password column
    status = Column(Boolean, default=True, nullable=False)  # Added status column
    cv = Column(Text, nullable=True)  # Added cv column
    country = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    department = relationship("DepartmentModel", back_populates="users")
    position = relationship("PositionModel", back_populates="users")
    location = relationship("LocationModel", back_populates="users")
    manager = relationship("UserModel", remote_side=[id], back_populates="subordinates")
    subordinates = relationship("UserModel", back_populates="manager")
    courses = relationship("CourseModel", back_populates="user")
    oauth_tokens = relationship("OAuthTokenModel", back_populates="user")

class CourseModel(Base):
    """Course model for AI-generated courses"""
    __tablename__ = "courses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    skill = Column(ARRAY(String), nullable=True)  # Array of skills associated with the course
    estimated_duration = Column(Integer, nullable=True)  # in hours
    difficulty = Column(String(50), nullable=True)  # Beginner, Intermediate, Advanced
    learning_objectives = Column(ARRAY(String), nullable=True)  # Array of learning objectives
    source_from = Column(ARRAY(String), nullable=True)  # Array of source URLs
    progress = Column(Float, default=0.0, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("UserModel", back_populates="courses")
    modules = relationship("ModuleModel", back_populates="course")

class ModuleModel(Base):
    """Module model for course modules"""
    __tablename__ = "modules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    title = Column(String(500), nullable=False)
    order_index = Column(Integer, nullable=False, default=0)  # Order of modules in course
    is_completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    course = relationship("CourseModel", back_populates="modules")
    lessons = relationship("LessonModel", back_populates="module", cascade="all, delete-orphan")
    quizzes = relationship("QuizModel", back_populates="module", cascade="all, delete-orphan")

class LessonModel(Base):
    """Lesson model for course lessons"""
    __tablename__ = "lessons"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id"), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    index = Column(Integer, nullable=False, default=0)  # Order of lessons in module
    is_completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    module = relationship("ModuleModel", back_populates="lessons")

class OAuthTokenModel(Base):
    """OAuth token model for storing GitHub and Google Drive tokens"""
    __tablename__ = "user_oauth_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider = Column(String(50), nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_type = Column(String(50), nullable=True, default="Bearer")
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("UserModel", back_populates="oauth_tokens")

class QuizModel(Base):
    """Quiz model for course quizzes"""
    __tablename__ = "quizzes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id"), nullable=False)
    questions = Column(JSON, nullable=False)  # JSON array of quiz questions
    is_completed = Column(Boolean, default=False, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    module = relationship("ModuleModel", back_populates="quizzes")