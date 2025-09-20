from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database.models import OAuthTokenModel
from internal.oauth.model.oauth_entity import OAuthTokenEntity
from internal.oauth.repository.oauth_repository import OAuthRepository


class DatabaseOAuthRepository(OAuthRepository):
    """Database implementation of OAuth repository"""

    def __init__(self, db: Session):
        self.db = db

    async def create_token(self, token: OAuthTokenEntity) -> OAuthTokenEntity:
        """Create a new OAuth token"""
        # Create database model with explicit field assignment
        db_token = OAuthTokenModel(
            id=token.id,
            user_id=token.user_id,
            provider=token.provider,
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            token_type=token.token_type or "Bearer",
            expires_at=token.expires_at
            # Let database handle created_at with server_default
        )
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)
        return OAuthTokenEntity.from_model(db_token)

    async def get_token_by_user_and_provider(
        self, 
        user_id: UUID, 
        provider: str
    ) -> Optional[OAuthTokenEntity]:
        """Get OAuth token by user ID and provider"""
        db_token = self.db.query(OAuthTokenModel).filter(
            and_(
                OAuthTokenModel.user_id == user_id,
                OAuthTokenModel.provider == provider
            )
        ).first()
        
        if db_token:
            return OAuthTokenEntity.from_model(db_token)
        return None
