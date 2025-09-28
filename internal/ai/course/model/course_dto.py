from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

@dataclass
class AiCourseGenerateRequest:
    """Request model for AI course generation"""

    token_github: str
    token_drive: str
    prompt: str
    files_url: Optional[str] = None

@dataclass
class Lesson:
    """Lesson model"""
    title: str
    content: str
    index: int

@dataclass
class Module:
    """Module model"""
    title: str
    lessons: List[Lesson]
    index: int

@dataclass
class ExternalAiCourseGenerateResponse:
    """Response model from external API"""
    learning_objectives: List[str]
    description: str
    estimated_duration: int
    modules: List[Module]
    title: str
    source_from: List[str]
    difficulty: str

@dataclass
class AiCourseGenerateResponse:
    """Response model for AI course generation"""

    course_id: UUID
    external_response: Optional[ExternalAiCourseGenerateResponse] = None

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
class CourseListResponse:
    """Response model for course list"""
    courses: List[CourseListItem]
    total: int
    