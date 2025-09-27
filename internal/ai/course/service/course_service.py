import httpx
import logging
from typing import Optional
from uuid import UUID, uuid4
from internal.ai.course.model.course_dto import (
    AiCourseGenerateRequest, 
    AiCourseGenerateResponse, 
    ExternalAiCourseGenerateResponse,
    Module,
    Lesson
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
            
            # # Call external API
            # external_response = await self._call_external_api(course_data)
            
            # Create example course data for now
            external_response = self._create_example_course()
            logger.info(f"Example course created: {external_response.title}")
            
            # Save course to database
            response = await self.course_repository.save_course(user_id, external_response)
            logger.info(f"Course saved successfully with ID: {response.course_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating course: {str(e)}")
            # Return basic response even if external API fails
            return AiCourseGenerateResponse(course_id=uuid4())

    async def _call_external_api(self, course_data: AiCourseGenerateRequest) -> ExternalAiCourseGenerateResponse:
        """Call external AI API to generate course content"""
        url = f"{settings.AI_API_BASE_URL}/course/generate"
        
        payload = {
            "token_github": course_data.token_github,
            "token_drive": course_data.token_drive
        }
        
        async with httpx.AsyncClient(timeout=settings.AI_API_TIMEOUT) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse modules and lessons
            modules = []
            for module_data in data.get("modules", []):
                lessons = []
                for lesson_data in module_data.get("lessons", []):
                    lesson = Lesson(
                        title=lesson_data["title"],
                        content=lesson_data["content"]
                    )
                    lessons.append(lesson)
                
                module = Module(
                    title=module_data["title"],
                    lessons=lessons
                )
                modules.append(module)
            
            return ExternalAiCourseGenerateResponse(
                learning_objectives=data["learning_objectives"],
                description=data["description"],
                estimated_duration=data["estimated_duration"],
                modules=modules,
                title=data["title"],
                source_from=data["source_from"],
                difficulty=data["difficulty"]
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

    def _create_example_course(self) -> ExternalAiCourseGenerateResponse:
        """Create an example course for testing purposes"""
        return ExternalAiCourseGenerateResponse(
            learning_objectives=[
                "Understand the fundamentals of Google Cloud Vertex AI.",
                "Train an XGBoost model for a real-world problem.",
                "Deploy an XGBoost model to a Vertex AI endpoint for online predictions.",
                "Perform batch predictions using Vertex AI for offline use cases.",
                "Integrate XGBoost with a complete MLOps workflow on GCP."
            ],
            description="Learn how to deploy machine learning models using XGBoost on Google Cloud Vertex AI.",
            estimated_duration=10,
            modules=[
                Module(
                    title="Module 1: Introduction to Vertex AI",
                    lessons=[
                        Lesson(
                            title="Introduction to Vertex AI",
                            content="This lesson introduces Google Cloud Vertex AI, a unified platform for machine learning development. We will explore the key components of Vertex AI, including notebooks, training, and model deployment.",
                            index=1
                        ),
                        Lesson(
                            title="Setting up your GCP Environment",
                            content="Learn how to set up your Google Cloud Platform environment, create a project, enable necessary APIs, and configure authentication for Vertex AI development.",
                            index=2
                        ),
                        Lesson(
                            title="Understanding XGBoost",
                            content="Dive deep into XGBoost, a powerful gradient boosting framework. Learn about its features, advantages, and how it compares to other machine learning algorithms.",
                            index=3
                        )
                    ],
                    index=1
                ),
                Module(
                    title="Module 2: Data Preparation and Model Training",
                    lessons=[
                        Lesson(
                            title="Data Loading and Preprocessing",
                            content="Learn how to load and preprocess data for XGBoost training, including handling missing values, feature engineering, and data validation techniques.",
                            index=1
                        ),
                        Lesson(
                            title="Training XGBoost Models",
                            content="Master the art of training XGBoost models, including hyperparameter tuning, cross-validation, and model evaluation techniques.",
                            index=2
                        ),
                        Lesson(
                            title="Model Validation and Testing",
                            content="Understand how to properly validate and test your XGBoost models to ensure they perform well on unseen data.",
                            index=3
                        )
                    ],
                    index=2
                ),
                Module(
                    title="Module 3: Deployment and Production",
                    lessons=[
                        Lesson(
                            title="Deploying to Vertex AI Endpoints",
                            content="Learn how to deploy your trained XGBoost model to Vertex AI endpoints for real-time predictions and serving.",
                            index=1
                        ),
                        Lesson(
                            title="Batch Predictions",
                            content="Implement batch prediction workflows using Vertex AI for processing large datasets efficiently.",
                            index=2
                        ),
                        Lesson(
                            title="Monitoring and Maintenance",
                            content="Set up monitoring, logging, and maintenance procedures for your deployed models in production.",
                            index=3
                        )
                    ],
                    index=3
                )
            ],
            title="Machine Learning Deployment with XGBoost and Vertex AI",
            source_from=[
                "https://github.com",
                "https://google.drive.com"
            ],
            difficulty="Advanced"
        )