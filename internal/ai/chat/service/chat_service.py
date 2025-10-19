import httpx
import logging
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from internal.ai.chat.model.chat_dto import CourseChatRequest, CourseChatResponse, GuideChatRequest, GuideChatResponse
from internal.ai.chat.repository.session_repository import SessionRepository
from internal.ai.chat.repository.message_repository import MessageRepository
from internal.course.service.course_service import CourseService
from internal.course.repository.course_repository_db import DatabaseCourseRepository
from internal.guide.service.guide_service import GuideService
from internal.guide.repository.guide_repository_db import DatabaseGuideRepository
from internal.oauth.service.oauth_service import OAuthService
from internal.oauth.repository.oauth_repository_db import DatabaseOAuthRepository
from internal.user.service.user_service import UserService
from internal.user.repository.user_repository_db import DatabaseUserRepository
from app.config import settings
from datetime import datetime, timezone, timedelta

# GMT+7 timezone
GMT_PLUS_7 = timezone(timedelta(hours=7))

logger = logging.getLogger(__name__)

class ChatService:
    """Service for AI chat operations with permanent sessions"""
    
    def __init__(self, db: Session):
        self.db = db
        self.session_repository = SessionRepository(db)
        self.message_repository = MessageRepository(db)
        
        # Initialize course and guide services
        course_repository = DatabaseCourseRepository(db)
        self.course_service = CourseService(course_repository)
        
        # Initialize guide service with all required dependencies
        guide_repository = DatabaseGuideRepository(db)
        oauth_repository = DatabaseOAuthRepository(db)
        oauth_service = OAuthService(oauth_repository)
        user_repository = DatabaseUserRepository(db)
        user_service = UserService(user_repository)
        self.guide_service = GuideService(oauth_service, guide_repository, user_service)
        
        self.ai_base_url = "https://agent.taraai.tech"

    async def chat_about_course(self, course_id: str, chat_request: CourseChatRequest, user_id: UUID) -> CourseChatResponse:
        """Chat with AI about a specific course using permanent session"""
        try:
            # Get course details
            course = await self.course_service.get_course_by_id(UUID(course_id), user_id)
            if not course:
                raise ValueError(f"Course not found: {course_id}")

            # Get or create permanent session
            session = await self.session_repository.get_course_session(user_id, UUID(course_id))
            
            if not session:
                # Create new AI session
                ai_session_id = await self._create_new_ai_session(str(user_id))
                session = await self.session_repository.get_or_create_course_session(
                    user_id, UUID(course_id), ai_session_id
                )
                logger.info(f"Created new permanent course chat session: {session.id}")
            else:
                # Update session timestamp
                await self.session_repository.update_session_timestamp(session.id, is_course=True)
                logger.info(f"Using existing permanent course chat session: {session.id}")

            # Save user message
            user_message_order = await self.message_repository.get_next_message_order(session.id, is_course=True)
            await self.message_repository.save_course_message(
                session.id, chat_request.message, True, user_message_order
            )

            # Prepare course context
            course_context = self._prepare_course_context(course)
            
            # Send message to AI service
            ai_response = await self._send_message_to_ai(
                session.ai_session_id, 
                chat_request.message, 
                course_context,
                str(user_id)
            )
            
            # Save AI response
            ai_message_order = await self.message_repository.get_next_message_order(session.id, is_course=True)
            await self.message_repository.save_course_message(
                session.id, ai_response, False, ai_message_order
            )
            
            return CourseChatResponse(
                response=ai_response,
                session_id=str(session.id),
                timestamp=datetime.now(GMT_PLUS_7)
            )
            
        except Exception as e:
            logger.error(f"Error in course chat for course {course_id}: {str(e)}")
            raise e

    async def chat_about_guide(self, guide_id: str, chat_request: GuideChatRequest, user_id: UUID) -> GuideChatResponse:
        """Chat with AI about a specific guide using permanent session"""
        try:
            # Convert guide_id to UUID
            try:
                guide_uuid = UUID(guide_id)
            except (ValueError, AttributeError) as e:
                raise ValueError(f"Invalid guide ID format: {guide_id}")
            
            # Get guide details
            guide = await self.guide_service.get_guide_by_id(guide_uuid, user_id)
            if not guide:
                raise ValueError(f"Guide not found: {guide_id}")

            # Get or create permanent session
            session = await self.session_repository.get_guide_session(user_id, guide_uuid)
            
            if not session:
                # Create new AI session
                ai_session_id = await self._create_new_ai_session(str(user_id))
                session = await self.session_repository.get_or_create_guide_session(
                    user_id, guide_uuid, ai_session_id
                )
                logger.info(f"Created new permanent guide chat session: {session.id}")
            else:
                # Update session timestamp
                await self.session_repository.update_session_timestamp(session.id, is_course=False)
                logger.info(f"Using existing permanent guide chat session: {session.id}")

            # Save user message
            user_message_order = await self.message_repository.get_next_message_order(session.id, is_course=False)
            await self.message_repository.save_guide_message(
                session.id, chat_request.message, True, user_message_order
            )

            # Prepare guide context
            guide_context = self._prepare_guide_context(guide)
            
            # Send message to AI service
            ai_response = await self._send_message_to_ai(
                session.ai_session_id, 
                chat_request.message, 
                guide_context,
                str(user_id)
            )
            
            # Save AI response
            ai_message_order = await self.message_repository.get_next_message_order(session.id, is_course=False)
            await self.message_repository.save_guide_message(
                session.id, ai_response, False, ai_message_order
            )
            
            return GuideChatResponse(
                response=ai_response,
                session_id=str(session.id),
                timestamp=datetime.now(GMT_PLUS_7)
            )
            
        except Exception as e:
            logger.error(f"Error in guide chat for guide {guide_id}: {str(e)}")
            raise e

    async def _create_new_ai_session(self, user_id: str) -> str:
        """Create a new AI session"""
        url = f"{self.ai_base_url}/apps/follow_up_agent/users/{user_id}/sessions"
        
        payload = {
            "parts": []
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                session_id = data.get("session_id")
                
                if not session_id:
                    raise ValueError("No session ID returned from AI service")
                
                logger.info(f"Created new AI session: {session_id}")
                return session_id
                
        except httpx.TimeoutException:
            logger.error("AI session creation timed out")
            raise RuntimeError("Failed to create AI session: timeout")
        except httpx.HTTPStatusError as e:
            logger.error(f"AI session creation failed: {e.response.status_code}: {e.response.text}")
            raise RuntimeError(f"Failed to create AI session: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Unexpected error creating AI session: {str(e)}")
            raise RuntimeError(f"Failed to create AI session: {str(e)}")

    async def _send_message_to_ai(self, session_id: str, user_message: str, context: str, user_id: str) -> str:
        """Send message to AI service"""
        url = f"{self.ai_base_url}/run"
        
        # Build contextual message
        contextual_message = f"Context: {context}. Question: {user_message}"
        
        payload = {
            "app_name": "follow_up_agent",
            "user_id": user_id,
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [
                    {
                        "text": contextual_message
                    }
                ]
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Log the request
        logger.info(f"Sending request to {url}")
        logger.info(f"Request payload: {payload}")
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                
                # Log the response
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response data: {data}")
                # Extract AI response from the response format
                # Response format: [{"content": {"role": "model", "parts": [{"text": "..."}]}}]
                ai_response = None
                
                if isinstance(data, list) and len(data) > 0:
                    content = data[0].get("content", {})
                    if content.get("role") == "model":
                        parts = content.get("parts", [])
                        if len(parts) > 0:
                            ai_response = parts[0].get("text")
                
                if not ai_response:
                    return "I'm sorry, I couldn't process your request."
                
                return ai_response
                
        except httpx.TimeoutException:
            logger.error("AI message request timed out")
            return "I'm sorry, the request timed out. Please try again."
        except httpx.HTTPStatusError as e:
            logger.error(f"AI message request failed: {e.response.status_code}: {e.response.text}")
            return "I'm sorry, there was an error processing your request. Please try again."
        except Exception as e:
            logger.error(f"Unexpected error sending message to AI: {str(e)}")
            return "I'm sorry, I encountered an unexpected error. Please try again."

    def _prepare_course_context(self, course) -> str:
        """Prepare course context for AI"""
        context = f"Course Title: {course.title}\n"
        
        if course.description:
            context += f"Description: {course.description}\n"
        
        if course.learning_objectives:
            context += f"Learning Objectives: {', '.join(course.learning_objectives)}\n"
        
        if course.difficulty:
            context += f"Difficulty: {course.difficulty}\n"
        
        # Add modules and lessons
        if hasattr(course, 'modules') and course.modules:
            context += "\nCourse Content:\n"
            for module in course.modules:
                context += f"\nModule: {module.title}\n"
                if hasattr(module, 'lessons') and module.lessons:
                    for lesson in module.lessons:
                        context += f"  - Lesson: {lesson.title}\n"
                        if hasattr(lesson, 'content') and lesson.content:
                            context += f"    Content: {lesson.content[:500]}...\n"
        
        return context

    def _prepare_guide_context(self, guide) -> str:
        """Prepare guide context for AI"""
        context = f"Guide Title: {guide.title}\n"
        
        if guide.description:
            context += f"Description: {guide.description}\n"
        
        if hasattr(guide, 'content') and guide.content:
            context += f"Content: {guide.content}\n"
        
        if hasattr(guide, 'source_from') and guide.source_from:
            context += f"Sources: {', '.join(guide.source_from)}\n"
        
        return context
