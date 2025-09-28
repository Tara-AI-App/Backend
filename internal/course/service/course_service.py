import logging
from uuid import UUID
from typing import Optional
from internal.course.model.course_dto import CourseListResponse, CourseDetail
from internal.course.repository.course_repository import CourseRepository

logger = logging.getLogger(__name__)

class CourseService:
    """Service for course operations"""

    def __init__(self, course_repository: CourseRepository):
        self.course_repository = course_repository

    async def get_courses(self, user_id: UUID) -> CourseListResponse:
        """Get all courses for a user"""
        try:
            logger.info(f"Getting courses for user {user_id}")
            return await self.course_repository.get_courses_by_user(user_id)
        except Exception as e:
            logger.error(f"Error getting courses for user {user_id}: {str(e)}")
            raise e

    async def get_course_by_id(self, course_id: UUID, user_id: UUID) -> Optional[CourseDetail]:
        """Get a course by ID for a user"""
        try:
            logger.info(f"Getting course {course_id} for user {user_id}")
            return await self.course_repository.get_course_by_id(course_id, user_id)
        except Exception as e:
            logger.error(f"Error getting course {course_id} for user {user_id}: {str(e)}")
            raise e
