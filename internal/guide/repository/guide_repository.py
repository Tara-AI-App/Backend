from abc import ABC, abstractmethod
from uuid import UUID
from internal.guide.model.guide_dto import AiGuideGenerateRequest, AiGuideGenerateResponse, ExternalAiGuideGenerateResponse, GuideListResponse, GuideDetailResponse

class GuideRepository(ABC):
    """Abstract repository for guide operations"""

    @abstractmethod
    async def save_guide(self, user_id: UUID, external_response: ExternalAiGuideGenerateResponse) -> AiGuideGenerateResponse:
        """Save a generated guide to the database"""
        pass

    @abstractmethod
    async def get_guides_by_user(self, user_id: UUID) -> GuideListResponse:
        """Get all guides for a user"""
        pass

    @abstractmethod
    async def get_guide_by_id(self, guide_id: UUID, user_id: UUID) -> GuideDetailResponse:
        """Get a specific guide by ID for a user"""
        pass
