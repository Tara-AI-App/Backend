import httpx
import asyncio
import uuid
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, timedelta, timezone
from internal.oauth.model.oauth_dto import (
    OAuthTokenCreate, 
    OAuthTokenUpdate, 
    GitHubOAuthResponse,
    GoogleDriveOAuthResponse
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
            
        auth_url = f"https://github.com/login/oauth/authorize?client_id={settings.GH_CLIENT_ID}&redirect_uri={settings.GH_REDIRECT_URI}&scope=repo,read:org&state={state}"
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
                    "client_id": settings.GH_CLIENT_ID,
                    "client_secret": settings.GH_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": settings.GH_REDIRECT_URI,
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
        expires_at = datetime.now(timezone.utc) + timedelta(days=365)
        
        # Create new token
        token_entity = OAuthTokenEntity(
            id=uuid.uuid4(),
            user_id=user_id,
            provider="github",
            access_token=github_response.access_token,
            refresh_token=None,
            token_type=github_response.token_type or "Bearer",
            expires_at=expires_at,
            created_at=datetime.now(timezone.utc)
        )
        return await self.oauth_repository.create_token(token_entity)

    async def get_user_github_token(self, user_id: UUID) -> Optional[OAuthTokenEntity]:
        """Get user's GitHub token"""
        return await self.oauth_repository.get_token_by_user_and_provider(
            user_id, "github"
        )

    async def get_user_tokens_by_provider(
        self, 
        user_id: UUID, 
        providers: Optional[List[str]] = None
    ) -> List[OAuthTokenEntity]:
        """Get user's OAuth tokens, optionally filtered by provider(s)"""
        return await self.oauth_repository.get_tokens_by_user_and_provider(
            user_id, providers
        )

    def get_google_drive_auth_url(self, state: Optional[str] = None) -> str:
        """Generate Google Drive OAuth authorization URL"""
        if not state:
            state = "default_state"
            
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.GOOGLE_REDIRECT_URI}&scope=https://www.googleapis.com/auth/drive&response_type=code&access_type=offline&prompt=consent&state={state}"
        return auth_url

    async def exchange_google_drive_code_for_token(
        self, 
        code: str
    ) -> GoogleDriveOAuthResponse:
        """Exchange Google Drive authorization code for access token"""
        async with httpx.AsyncClient() as client:
            # Exchange code for token
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if token_response.status_code != 200:
                raise ValueError("Failed to exchange code for token")
            
            token_data = token_response.json()
            
            # Log the raw token response from Google
            print(f"🔍 Google OAuth Token Response: {token_data}")
            
            if "error" in token_data:
                raise ValueError(f"Google OAuth error: {token_data['error']}")
            
            # Extract and log expiration details
            expires_in = token_data.get("expires_in", 3600)
            print(f"⏰ Google Token expires_in: {expires_in} seconds")
            print(f"📅 Calculated expiration: {datetime.now(timezone.utc) + timedelta(seconds=expires_in)}")
            
            return GoogleDriveOAuthResponse(
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token", ""),
                token_type=token_data.get("token_type", "Bearer"),
                expires_in=expires_in,
                scope=token_data.get("scope", "")
            )

    async def save_google_drive_token(
        self, 
        user_id: UUID, 
        google_response: GoogleDriveOAuthResponse
    ) -> OAuthTokenEntity:
        """Save Google Drive OAuth token to database"""
        # Calculate expiration
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=google_response.expires_in)
        
        # Log token details before saving
        print(f"💾 Saving Google Drive Token:")
        print(f"   User ID: {user_id}")
        print(f"   Provider: drive")
        print(f"   Expires in: {google_response.expires_in} seconds")
        print(f"   Expires at: {expires_at}")
        print(f"   Has refresh token: {bool(google_response.refresh_token)}")
        print(f"   Token type: {google_response.token_type}")
        print(f"   Scope: {google_response.scope}")
        
        # Create new token
        token_entity = OAuthTokenEntity(
            id=uuid.uuid4(),
            user_id=user_id,
            provider="drive",
            access_token=google_response.access_token,
            refresh_token=google_response.refresh_token,
            token_type=google_response.token_type,
            expires_at=expires_at,
            created_at=datetime.now(timezone.utc)
        )
        
        saved_token = await self.oauth_repository.create_token(token_entity)
        print(f"✅ Token saved successfully with ID: {saved_token.id}")
        
        return saved_token

    async def get_user_google_drive_token(self, user_id: UUID) -> Optional[OAuthTokenEntity]:
        """Get user's Google Drive token"""
        return await self.oauth_repository.get_token_by_user_and_provider(
            user_id, "drive"
        )

    async def refresh_google_drive_token(self, refresh_token: str) -> GoogleDriveOAuthResponse:
        """Refresh Google Drive access token using refresh token"""
        async with httpx.AsyncClient() as client:
            # Use refresh token to get new access token
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if token_response.status_code != 200:
                raise ValueError("Failed to refresh token")
            
            token_data = token_response.json()
            
            # Log the refresh response
            print(f"🔄 Google Token Refresh Response: {token_data}")
            
            if "error" in token_data:
                raise ValueError(f"Google refresh error: {token_data['error']}")
            
            # Extract and log expiration details
            expires_in = token_data.get("expires_in", 3600)
            print(f"⏰ New Token expires_in: {expires_in} seconds ({expires_in/3600:.1f} hours)")
            
            return GoogleDriveOAuthResponse(
                access_token=token_data["access_token"],
                refresh_token=refresh_token,  # Keep the same refresh token
                token_type=token_data.get("token_type", "Bearer"),
                expires_in=expires_in,
                scope=token_data.get("scope", "https://www.googleapis.com/auth/drive")
            )

    async def get_valid_google_drive_token(self, user_id: UUID) -> Optional[str]:
        """Get a valid Google Drive access token, refreshing if needed"""
        token_entity = await self.get_user_google_drive_token(user_id)
        
        if not token_entity:
            print(f"❌ No Google Drive token found for user {user_id}")
            return None
        
        # Check if token is expired or expires soon (within 5 minutes)
        now = datetime.now(timezone.utc)
        expires_at = token_entity.expires_at
        
        if expires_at and expires_at > now + timedelta(minutes=5):
            print(f"✅ Token is still valid until {expires_at}")
            return token_entity.access_token
        
        # Token is expired or expires soon, refresh it
        if not token_entity.refresh_token:
            print(f"❌ No refresh token available for user {user_id}")
            return None
        
        print(f"🔄 Token expired or expires soon, refreshing...")
        
        try:
            # Refresh the token
            refreshed_response = await self.refresh_google_drive_token(token_entity.refresh_token)
            
            # Update the token in database
            new_expires_at = datetime.now(timezone.utc) + timedelta(seconds=refreshed_response.expires_in)
            
            token_entity.access_token = refreshed_response.access_token
            token_entity.expires_at = new_expires_at
            token_entity.token_type = refreshed_response.token_type
            
            # Save updated token
            updated_token = await self.oauth_repository.update_token(token_entity)
            
            print(f"✅ Token refreshed successfully, new expiration: {new_expires_at}")
            return updated_token.access_token
            
        except Exception as e:
            print(f"❌ Failed to refresh token: {str(e)}")
            return None

