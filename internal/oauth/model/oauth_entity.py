from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from uuid import UUID


@dataclass
class OAuthTokenEntity:
    """OAuth token entity"""
    id: UUID
    user_id: UUID
    provider: str
    access_token: str
    refresh_token: Optional[str]
    token_type: str
    expires_at: Optional[datetime]
    created_at: datetime

    @classmethod
    def from_model(cls, model) -> 'OAuthTokenEntity':
        """Create entity from SQLAlchemy model"""
        return cls(
            id=model.id,
            user_id=model.user_id,
            provider=model.provider,
            access_token=model.access_token,
            refresh_token=model.refresh_token,
            token_type=model.token_type or "Bearer",
            expires_at=model.expires_at,
            created_at=model.created_at
        )

    def to_model_data(self) -> dict:
        """Convert entity to dictionary for model creation"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'provider': self.provider,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_type': self.token_type or "Bearer",
            'expires_at': self.expires_at,
            'created_at': self.created_at
        }
