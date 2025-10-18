import httpx
import logging
from typing import Optional
from uuid import UUID
from internal.ai.guide.model.guide_dto import (
    AiGuideGenerateRequest, 
    AiGuideGenerateResponse, 
    ExternalAiGuideGenerateResponse,
    GuideListResponse
)
from internal.oauth.service.oauth_service import OAuthService
from internal.ai.guide.repository.ai_guide_repository import AiGuideRepository
from app.config import settings
from internal.user.service.user_service import UserService

logger = logging.getLogger(__name__)

class AiGuideService:
    """Service for AI guide operations"""

    def __init__(self, oauth_service: OAuthService, guide_repository: AiGuideRepository, user_service: UserService):
        self.oauth_service = oauth_service
        self.guide_repository = guide_repository
        self.user_service = user_service

    async def generate_guide(self, guide_data: AiGuideGenerateRequest, user_id: UUID) -> AiGuideGenerateResponse:
        """Generate a guide using AI"""
        try:
            # Validate and refresh Google Drive token if needed
            valid_drive_token = await self._validate_and_refresh_drive_token(user_id)
            if not valid_drive_token:
                logger.warning(f"No valid Google Drive token available for user {user_id}, continuing without token validation")
            else:
                logger.info(f"Google Drive token validated for user {user_id}")
            
            # Update guide_data with the valid token
            guide_data.token_drive = valid_drive_token

            # Get user CV
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"User not found for ID: {user_id}")

            # Update guide_data with the user CV
            guide_data.cv = user.cv

            # Call external API
            external_response = await self._call_external_api(guide_data, user_id)
            logger.info(f"External API guide created: {external_response.title}")
            
            # Save guide to database
            response = await self.guide_repository.save_guide(user_id, external_response)
            logger.info(f"Guide saved successfully with ID: {response.guide_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating guide: {str(e)}")
            # Re-raise the exception to propagate the error
            raise e

    async def _call_external_api(self, guide_data: AiGuideGenerateRequest, user_id: UUID) -> ExternalAiGuideGenerateResponse:
        """Call external AI API to generate guide content"""
        url = f"{settings.AI_API_BASE_URL}/guide/generate"
        
        payload = {
            "token_github": guide_data.token_github,
            "token_drive": guide_data.token_drive,
            "prompt": guide_data.prompt,
            "files_url": guide_data.files_url or "",
            "user_id": str(user_id),
            "cv": guide_data.cv or ""
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
                logger.info(f"External AI API responded successfully")
        except httpx.TimeoutException:
            logger.error(f"External AI API request timed out after {settings.AI_API_TIMEOUT}s")
            raise TimeoutError(f"AI service request timed out after {settings.AI_API_TIMEOUT} seconds. Please try again.")
        except httpx.HTTPStatusError as e:
            logger.error(f"External AI API returned HTTP {e.response.status_code}: {e.response.text}")
            raise ConnectionError(f"AI service returned error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error calling external AI API: {str(e)}")
            raise RuntimeError(f"Failed to connect to AI service: {str(e)}")
        
        return ExternalAiGuideGenerateResponse(
            title=data["title"],
            description=data["description"],
            content=data["content"],
            source_from=data["source_from"]
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

    async def get_guides(self, user_id: UUID) -> GuideListResponse:
        """Get all guides for a user"""
        try:
            logger.info(f"Getting guides for user {user_id}")
            return await self.guide_repository.get_guides_by_user(user_id)
        except Exception as e:
            logger.error(f"Error getting guides for user {user_id}: {str(e)}")
            raise e
