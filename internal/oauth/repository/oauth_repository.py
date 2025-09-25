from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from internal.oauth.model.oauth_entity import OAuthTokenEntity


class OAuthRepository(ABC):
    """Abstract OAuth repository interface"""

    @abstractmethod
    async def create_token(self, token: OAuthTokenEntity) -> OAuthTokenEntity:
        """Create a new OAuth token"""
        pass

    @abstractmethod
    async def get_token_by_user_and_provider(
        self, 
        user_id: UUID, 
        provider: str
    ) -> Optional[OAuthTokenEntity]:
        """Get OAuth token by user ID and provider"""
        pass

    @abstractmethod
    async def get_tokens_by_user_and_provider(
        self, 
        user_id: UUID, 
        providers: Optional[List[str]] = None
    ) -> List[OAuthTokenEntity]:
        """Get OAuth tokens by user ID and optional provider filter(s)"""
        pass

    @abstractmethod
    async def update_token(self, token: OAuthTokenEntity) -> OAuthTokenEntity:
        """Update an existing OAuth token"""
        pass
