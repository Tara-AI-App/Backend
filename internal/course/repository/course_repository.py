from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Optional
from internal.course.model.course_dto import CourseListResponse, CourseDetail, LessonCompletionResponse, QuizCompletionResponse

class CourseRepository(ABC):
    """Abstract repository for course operations"""

    @abstractmethod
    async def get_courses_by_user(self, user_id: UUID, limit: int = 10, offset: int = 0) -> CourseListResponse:
        """Get courses for a user with pagination"""
        pass

    @abstractmethod
    async def get_course_by_id(self, course_id: UUID, user_id: UUID) -> Optional[CourseDetail]:
        """Get a course by ID for a specific user"""
        pass

    @abstractmethod
    async def update_lesson_completion(self, lesson_id: UUID, user_id: UUID, is_completed: bool) -> LessonCompletionResponse:
        """Update lesson completion status"""
        pass

    @abstractmethod
    async def update_quiz_completion(self, quiz_id: UUID, user_id: UUID, is_completed: bool) -> QuizCompletionResponse:
        """Update quiz completion status"""
        pass

    @abstractmethod
    async def calculate_course_progress(self, course_id: UUID, user_id: UUID) -> float:
        """Calculate course progress based on completed lessons, modules, and quizzes"""
        pass

    @abstractmethod
    async def update_course_progress(self, course_id: UUID, user_id: UUID, progress: float) -> bool:
        """Update course progress and completion status"""
        pass

    @abstractmethod
    async def check_and_update_module_completion(self, course_id: UUID, user_id: UUID) -> None:
        """Check all modules and auto-complete them if all lessons and quizzes are completed"""
        pass
