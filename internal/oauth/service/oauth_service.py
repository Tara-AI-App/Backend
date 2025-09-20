import httpx
import asyncio
import uuid
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from internal.oauth.model.oauth_dto import (
    OAuthTokenCreate, 
    OAuthTokenUpdate, 
    GitHubOAuthResponse
)
from internal.oauth.model.oauth_entity import OAuthTokenEntity
from internal.oauth.repository.oauth_repository import OAuthRepository
from app.config import settings


class OAuthService:
    """OAuth service for handling GitHub and Google Drive integration"""

    def __init__(self, oauth_repository: OAuthRepository):
        self.oauth_repository = oauth_repository

    def get_github_auth_url(self, state: Optional[str] = None) -> str:
        """Generate GitHub OAuth authorization URL"""
        if not state:
            state = "default_state"
            
        auth_url = f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&redirect_uri={settings.GITHUB_REDIRECT_URI}&scope=repo&state={state}"
        return auth_url

    async def exchange_github_code_for_token(
        self, 
        code: str
    ) -> GitHubOAuthResponse:
        """Exchange GitHub authorization code for access token"""
        async with httpx.AsyncClient() as client:
            # Exchange code for token
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": settings.GITHUB_REDIRECT_URI,
                },
                headers={"Accept": "application/json"}
            )
            
            if token_response.status_code != 200:
                raise ValueError("Failed to exchange code for token")
            
            token_data = token_response.json()
            
            if "error" in token_data:
                raise ValueError(f"GitHub OAuth error: {token_data['error']}")
            
            # Get user information
            user_response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {token_data['access_token']}"}
            )
            
            if user_response.status_code != 200:
                raise ValueError("Failed to get user information from GitHub")
            
            user_data = user_response.json()
            
            return GitHubOAuthResponse(
                access_token=token_data["access_token"],
                token_type=token_data.get("token_type", "bearer"),
                scope=token_data.get("scope", ""),
                user_info=user_data
            )

    async def save_github_token(
        self, 
        user_id: UUID, 
        github_response: GitHubOAuthResponse
    ) -> OAuthTokenEntity:
        """Save GitHub OAuth token to database"""
        # Calculate expiration (GitHub tokens don't expire by default, but we'll set a long expiration)
        expires_at = datetime.now() + timedelta(days=365)
        
        # Create new token
        token_entity = OAuthTokenEntity(
            id=uuid.uuid4(),
            user_id=user_id,
            provider="github",
            access_token=github_response.access_token,
            refresh_token=None,
            token_type=github_response.token_type or "Bearer",
            expires_at=expires_at,
            created_at=datetime.now()
        )
        return await self.oauth_repository.create_token(token_entity)

    async def get_user_github_token(self, user_id: UUID) -> Optional[OAuthTokenEntity]:
        """Get user's GitHub token"""
        return await self.oauth_repository.get_token_by_user_and_provider(
            user_id, "github"
        )

