import logging
from uuid import UUID
from typing import Optional
from internal.course.model.course_dto import CourseListResponse, CourseDetail, LessonCompletionResponse, QuizCompletionResponse
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

    async def update_lesson_completion(self, lesson_id: UUID, user_id: UUID, is_completed: bool) -> LessonCompletionResponse:
        """Update lesson completion status"""
        try:
            logger.info(f"Updating lesson {lesson_id} completion status to {is_completed} for user {user_id}")
            return await self.course_repository.update_lesson_completion(lesson_id, user_id, is_completed)
        except Exception as e:
            logger.error(f"Error updating lesson {lesson_id} completion for user {user_id}: {str(e)}")
            raise e

    async def update_quiz_completion(self, quiz_id: UUID, user_id: UUID, is_completed: bool) -> QuizCompletionResponse:
        """Update quiz completion status"""
        try:
            logger.info(f"Updating quiz {quiz_id} completion status to {is_completed} for user {user_id}")
            return await self.course_repository.update_quiz_completion(quiz_id, user_id, is_completed)
        except Exception as e:
            logger.error(f"Error updating quiz {quiz_id} completion for user {user_id}: {str(e)}")
            raise e

    async def calculate_course_progress(self, course_id: UUID, user_id: UUID) -> float:
        """Calculate course progress for a user"""
        try:
            logger.info(f"Calculating course progress for course {course_id}, user {user_id}")
            return await self.course_repository.calculate_course_progress(course_id, user_id)
        except Exception as e:
            logger.error(f"Error calculating course progress for {course_id}, user {user_id}: {str(e)}")
            raise e

    async def check_and_update_module_completion(self, course_id: UUID, user_id: UUID) -> None:
        """Check all modules and auto-complete them if all lessons and quizzes are completed"""
        try:
            logger.info(f"Checking module completion for course {course_id}, user {user_id}")
            await self.course_repository.check_and_update_module_completion(course_id, user_id)
        except Exception as e:
            logger.error(f"Error checking module completion for {course_id}, user {user_id}: {str(e)}")
            raise e
