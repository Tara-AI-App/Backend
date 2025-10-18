import logging
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from sqlalchemy import text
from internal.ai.guide.repository.ai_guide_repository import AiGuideRepository
from internal.ai.guide.model.guide_dto import AiGuideGenerateResponse, ExternalAiGuideGenerateResponse, GuideListResponse, GuideListItem

logger = logging.getLogger(__name__)

class DatabaseAiGuideRepository(AiGuideRepository):
    """Database repository for AI guide operations using raw SQL queries"""

    def __init__(self, db: Session):
        self.db = db

    async def save_guide(self, user_id: UUID, external_response: ExternalAiGuideGenerateResponse) -> AiGuideGenerateResponse:
        """Save a generated guide to the database using raw SQL queries with explicit transaction"""
        try:
            # Generate guide ID
            guide_id = uuid4()
            
            # Insert guide
            self._insert_guide(guide_id, user_id, external_response)
            
            # Commit the transaction
            self.db.commit()
            
            return AiGuideGenerateResponse(
                guide_id=guide_id,
                external_response=external_response
            )
                
        except Exception as e:
            # Rollback the transaction
            self.db.rollback()
            raise e

    def _insert_guide(self, guide_id: UUID, user_id: UUID, external_response: ExternalAiGuideGenerateResponse) -> None:
        """Insert guide record"""
        guide_query = text("""
            INSERT INTO guides (id, user_id, title, description, content, source_from, created_at, updated_at)
            VALUES (:id, :user_id, :title, :description, :content, :source_from, NOW(), NOW())
        """)
        
        self.db.execute(guide_query, {
            "id": guide_id,
            "user_id": user_id,
            "title": external_response.title,
            "description": external_response.description,
            "content": external_response.content,
            "source_from": external_response.source_from
        })

    async def get_guides_by_user(self, user_id: UUID) -> GuideListResponse:
        """Get all guides for a user"""
        try:
            query = text("""
                SELECT id, title, description, content, source_from, created_at, updated_at
                FROM guides
                WHERE user_id = :user_id
                ORDER BY created_at DESC
            """)
            
            result = self.db.execute(query, {"user_id": user_id})
            rows = result.fetchall()
            
            guides = []
            for row in rows:
                guide = GuideListItem(
                    id=row.id,
                    title=row.title,
                    description=row.description,
                    content=row.content,
                    source_from=row.source_from,
                    created_at=row.created_at.isoformat() if row.created_at else "",
                    updated_at=row.updated_at.isoformat() if row.updated_at else ""
                )
                guides.append(guide)
            
            return GuideListResponse(
                guides=guides,
                total=len(guides)
            )
            
        except Exception as e:
            logger.error(f"Error getting guides for user {user_id}: {str(e)}")
            raise e
