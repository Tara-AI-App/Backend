from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from uuid import UUID

@dataclass
class QuizDetail:
    """Quiz detail model"""
    id: UUID
    questions: List[Dict[str, Any]]  # JSON array of quiz questions
    is_completed: bool
    is_correct: bool
    created_at: str
    updated_at: str

@dataclass
class LessonDetail:
    """Lesson detail model"""
    id: UUID
    title: str
    content: str
    index: int
    is_completed: bool
    created_at: str
    updated_at: str

@dataclass
class ModuleDetail:
    """Module detail model"""
    id: UUID
    title: str
    order_index: int
    is_completed: bool
    created_at: str
    updated_at: str
    lessons: List[LessonDetail]
    quizzes: List[QuizDetail]

@dataclass
class CourseListItem:
    """Course list item model"""
    id: UUID
    title: str
    description: Optional[str]
    estimated_duration: Optional[int]
    difficulty: Optional[str]
    learning_objectives: Optional[List[str]]
    source_from: Optional[List[str]]
    progress: float
    is_completed: bool
    created_at: str
    updated_at: str

@dataclass
class CourseDetail:
    """Course detail model with modules and lessons"""
    id: UUID
    title: str
    description: Optional[str]
    estimated_duration: Optional[int]
    difficulty: Optional[str]
    learning_objectives: Optional[List[str]]
    source_from: Optional[List[str]]
    progress: float
    is_completed: bool
    created_at: str
    updated_at: str
    modules: List[ModuleDetail]

@dataclass
class CourseListResponse:
    """Response model for course list"""
    courses: List[CourseListItem]
    total: int
