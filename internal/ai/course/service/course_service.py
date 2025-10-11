import httpx
import logging
from typing import Optional
from uuid import UUID, uuid4
from internal.ai.course.model.course_dto import (
    AiCourseGenerateRequest, 
    AiCourseGenerateResponse, 
    ExternalAiCourseGenerateResponse,
    Module,
    Lesson,
    QuizQuestion,
    CourseListResponse
)
from internal.oauth.service.oauth_service import OAuthService
from internal.ai.course.repository.ai_course_repository import AiCourseRepository
from app.config import settings

logger = logging.getLogger(__name__)

class AiCourseService:
    """Service for AI course operations"""

    def __init__(self, oauth_service: OAuthService, course_repository: AiCourseRepository):
        self.oauth_service = oauth_service
        self.course_repository = course_repository

    async def generate_course(self, course_data: AiCourseGenerateRequest, user_id: UUID) -> AiCourseGenerateResponse:
        """Generate a course using AI"""
        try:
            # Validate and refresh Google Drive token if needed
            valid_drive_token = await self._validate_and_refresh_drive_token(user_id)
            if not valid_drive_token:
                logger.warning(f"No valid Google Drive token available for user {user_id}, continuing without token validation")
            else:
                logger.info(f"Google Drive token validated for user {user_id}")
            
            # Update course_data with the valid token
            course_data.token_drive = valid_drive_token
            
            # Call external API
            external_response = await self._call_external_api(course_data, user_id)
            logger.info(f"External API course created: {external_response.title}")
            
            # Save course to database
            response = await self.course_repository.save_course(user_id, external_response)
            logger.info(f"Course saved successfully with ID: {response.course_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating course: {str(e)}")
            # Re-raise the exception to propagate the error
            raise e

    async def _call_external_api(self, course_data: AiCourseGenerateRequest, user_id: UUID) -> ExternalAiCourseGenerateResponse:
        """Call external AI API to generate course content"""
        url = f"{settings.AI_API_BASE_URL}/course/generate"
        
        payload = {
            "token_github": course_data.token_github,
            "token_drive": course_data.token_drive,
            "prompt": course_data.prompt,
            "files_url": course_data.files_url or "",
            "user_id": str(user_id),
            "cv": course_data.cv or ""
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        logger.info(f"Calling external AI API at {url} with timeout {settings.AI_API_TIMEOUT}s")
        logger.info(f"Request payload: {payload}")
        
        try:
            async with httpx.AsyncClient(timeout=settings.AI_API_TIMEOUT) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"External AI API responded successfully with {len(data.get('modules', []))} modules")
        except httpx.TimeoutException:
            logger.error(f"External AI API request timed out after {settings.AI_API_TIMEOUT}s")
            raise TimeoutError(f"AI service request timed out after {settings.AI_API_TIMEOUT} seconds. Please try again.")
        except httpx.HTTPStatusError as e:
            logger.error(f"External AI API returned HTTP {e.response.status_code}: {e.response.text}")
            raise ConnectionError(f"AI service returned error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error calling external AI API: {str(e)}")
            raise RuntimeError(f"Failed to connect to AI service: {str(e)}")
        
        # Parse modules and lessons
        modules = []
        for module_data in data.get("modules", []):
            lessons = []
            for lesson_data in module_data.get("lessons", []):
                lesson = Lesson(
                    title=lesson_data["title"],
                    content=lesson_data["content"],
                    index=lesson_data["index"]
                )
                lessons.append(lesson)
            
            # Parse quiz data if present
            quiz_questions = []
            if "quiz" in module_data and module_data["quiz"]:
                for quiz_data in module_data["quiz"]:
                    quiz_question = QuizQuestion(
                        question=quiz_data["question"],
                        choices=quiz_data["choices"],
                        answer=quiz_data["answer"]
                    )
                    quiz_questions.append(quiz_question)
            
            module = Module(
                title=module_data["title"],
                lessons=lessons,
                index=module_data["index"],
                quiz=quiz_questions if quiz_questions else None
            )
            modules.append(module)
        
        return ExternalAiCourseGenerateResponse(
            learning_objectives=data["learning_objectives"],
            description=data["description"],
            estimated_duration=data["estimated_duration"],
            modules=modules,
            title=data["title"],
            source_from=data["source_from"],
            difficulty=data["difficulty"],
            skills=data.get("skills")
        )

    async def _validate_and_refresh_drive_token(self, user_id: UUID) -> Optional[str]:
        """Validate and refresh Google Drive token if needed"""
        try:
            # Use the OAuth service to get a valid token (it will refresh if needed)
            valid_token = await self.oauth_service.get_valid_google_drive_token(user_id)
            
            if not valid_token:
                logger.warning(f"No valid Google Drive token found for user {user_id}")
                return None
            
            logger.info(f"Valid Google Drive token obtained for user {user_id}")
            return valid_token
            
        except Exception as e:
            logger.error(f"Error validating/refreshing Google Drive token for user {user_id}: {str(e)}")
            return None

    async def get_courses(self, user_id: UUID) -> CourseListResponse:
        """Get all courses for a user"""
        try:
            logger.info(f"Getting courses for user {user_id}")
            return await self.course_repository.get_courses_by_user(user_id)
        except Exception as e:
            logger.error(f"Error getting courses for user {user_id}: {str(e)}")
            raise e
