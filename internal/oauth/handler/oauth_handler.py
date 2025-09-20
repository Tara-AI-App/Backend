from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.database.connection import get_db
from internal.oauth.model.oauth_dto import (
    OAuthTokenResponse, 
    GitHubOAuthResponse
)
from internal.oauth.service.oauth_service import OAuthService
from internal.oauth.repository.oauth_repository_db import DatabaseOAuthRepository
from internal.user.service.user_service import UserService
from internal.user.repository.user_repository_db import DatabaseUserRepository

router = APIRouter(prefix="/oauth", tags=["oauth"])
security = HTTPBearer()


def get_oauth_service(db: Session = Depends(get_db)) -> OAuthService:
    """Dependency to get OAuth service"""
    oauth_repository = DatabaseOAuthRepository(db)
    return OAuthService(oauth_repository)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency to get user service"""
    user_repository = DatabaseUserRepository(db)
    return UserService(user_repository)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service)
) -> dict:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = user_service.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


@router.get("/github/auth-url")
async def get_github_auth_url(
    state: Optional[str] = Query(None, description="Optional state parameter for security"),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """Get GitHub OAuth authorization URL"""
    try:
        auth_url = oauth_service.get_github_auth_url(state)
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate GitHub auth URL: {str(e)}"
        )


@router.get("/github/callback", response_model=GitHubOAuthResponse)
async def github_oauth_callback_get(
    code: str = Query(..., description="GitHub authorization code"),
    state: Optional[str] = Query(None, description="State parameter"),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """Handle GitHub OAuth callback (GET) and exchange code for token"""
    try:
        # Exchange code for token
        github_response = await oauth_service.exchange_github_code_for_token(code)
        
        return github_response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GitHub OAuth callback failed: {str(e)}"
        )


@router.post("/github/save-token", response_model=OAuthTokenResponse)
async def save_github_token(
    request: dict,
    current_user: dict = Depends(get_current_user),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """Save GitHub OAuth token for a user"""
    try:
        # Get user ID from JWT token
        user_id = UUID(current_user["user_id"])
        
        # Extract access token from request
        access_token = request.get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="access_token is required"
            )
        
        # Create GitHub response object
        github_response = GitHubOAuthResponse(
            access_token=access_token,
            token_type="bearer",
            scope="repo",
            user_info={}
        )
        
        token_entity = await oauth_service.save_github_token(user_id, github_response)
        return OAuthTokenResponse(
            id=token_entity.id,  # Database ID
            access_token=token_entity.access_token,  # GitHub access token
            user_id=token_entity.user_id,
            provider=token_entity.provider,
            token_type=token_entity.token_type,
            created_at=token_entity.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save GitHub token: {str(e)}"
        )


@router.get("/github/token", response_model=OAuthTokenResponse)
async def get_github_token(
    current_user: dict = Depends(get_current_user),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """Get current user's GitHub token"""
    try:
        user_id = UUID(current_user["user_id"])
        token_entity = await oauth_service.get_user_github_token(user_id)
        
        if not token_entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GitHub token not found for this user"
            )
        
        return OAuthTokenResponse(
            id=token_entity.id,  # Database ID
            access_token=token_entity.access_token,  # GitHub access token
            user_id=token_entity.user_id,
            provider=token_entity.provider,
            token_type=token_entity.token_type,
            created_at=token_entity.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get GitHub token: {str(e)}"
        )


