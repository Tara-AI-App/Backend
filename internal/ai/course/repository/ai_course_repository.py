from abc import ABC, abstractmethod
from uuid import UUID
from internal.ai.course.model.course_dto import AiCourseGenerateRequest, AiCourseGenerateResponse, ExternalAiCourseGenerateResponse

class AiCourseRepository(ABC):
    """Abstract repository for AI course operations"""

    @abstractmethod
    async def save_course(self, user_id: UUID, external_response: ExternalAiCourseGenerateResponse) -> AiCourseGenerateResponse:
        """Save a generated course to the database"""
        pass
