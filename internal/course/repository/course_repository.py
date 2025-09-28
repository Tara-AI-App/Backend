from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Optional
from internal.course.model.course_dto import CourseListResponse, CourseDetail

class CourseRepository(ABC):
    """Abstract repository for course operations"""

    @abstractmethod
    async def get_courses_by_user(self, user_id: UUID) -> CourseListResponse:
        """Get all courses for a user"""
        pass

    @abstractmethod
    async def get_course_by_id(self, course_id: UUID, user_id: UUID) -> Optional[CourseDetail]:
        """Get a course by ID for a specific user"""
        pass
