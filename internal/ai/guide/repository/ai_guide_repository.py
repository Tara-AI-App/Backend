from abc import ABC, abstractmethod
from uuid import UUID
from internal.ai.guide.model.guide_dto import AiGuideGenerateRequest, AiGuideGenerateResponse, ExternalAiGuideGenerateResponse, GuideListResponse

class AiGuideRepository(ABC):
    """Abstract repository for AI guide operations"""

    @abstractmethod
    async def save_guide(self, user_id: UUID, external_response: ExternalAiGuideGenerateResponse) -> AiGuideGenerateResponse:
        """Save a generated guide to the database"""
        pass

    @abstractmethod
    async def get_guides_by_user(self, user_id: UUID) -> GuideListResponse:
        """Get all guides for a user"""
        pass
