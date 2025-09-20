from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class OAuthTokenResponse(BaseModel):
    """Response model for OAuth token"""
    id: UUID
    access_token: str
    user_id: UUID
    provider: str
    token_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class GitHubOAuthRequest(BaseModel):
    """Request model for GitHub OAuth callback"""
    code: str
    state: Optional[str] = None


class GitHubOAuthResponse(BaseModel):
    """Response model for GitHub OAuth"""
    access_token: str
    token_type: str
    scope: str


class OAuthTokenCreate(BaseModel):
    """Model for creating OAuth token"""
    user_id: UUID
    provider: str
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_at: Optional[datetime] = None


class OAuthTokenUpdate(BaseModel):
    """Model for updating OAuth token"""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
