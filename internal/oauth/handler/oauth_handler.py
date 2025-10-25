from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.database.connection import get_db
from internal.oauth.model.oauth_dto import (
    OAuthTokenResponse, 
    GitHubOAuthResponse,
    GoogleDriveOAuthResponse,
    OAuthTokenListResponse
)
from internal.oauth.service.oauth_service import OAuthService
from internal.oauth.repository.oauth_repository_db import DatabaseOAuthRepository
from internal.user.service.user_service import UserService
from internal.user.repository.user_repository_db import DatabaseUserRepository
from internal.auth.middleware import get_current_user_id, get_current_user_payload

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
    user_id: str = Depends(get_current_user_id),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """Save GitHub OAuth token for a user"""
    try:
        # Get user ID from JWT token
        user_id = UUID(user_id)
        
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
    user_id: str = Depends(get_current_user_id),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """Get current user's GitHub token"""
    try:
        user_id = UUID(user_id)
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


@router.get("/tokens", response_model=OAuthTokenListResponse)
async def get_user_oauth_tokens(
    providers: Optional[List[str]] = Query(None, description="Filter by OAuth provider(s) (e.g., 'github', 'google'). Can specify multiple providers."),
    user_id: str = Depends(get_current_user_id),
    oauth_service: OAuthService = Depends(get_oauth_service),
    response: Response = None
):
    """Get current user's OAuth tokens, optionally filtered by provider(s)"""
    try:
        # Add explicit CORS headers
        if response:
            response.headers["Access-Control-Allow-Origin"] = "https://taraai.tech"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "accept, authorization, content-type, origin, x-requested-with"
        
        user_id = UUID(user_id)
        token_entities = await oauth_service.get_user_tokens_by_provider(user_id, providers)
        
        # Convert entities to response DTOs
        token_responses = [
            OAuthTokenResponse(
                id=token.id,
                access_token=token.access_token,
                user_id=token.user_id,
                provider=token.provider,
                token_type=token.token_type,
                created_at=token.created_at
            )
            for token in token_entities
        ]
        
        return OAuthTokenListResponse(
            tokens=token_responses,
            total=len(token_responses),
            providers=providers
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get OAuth tokens: {str(e)}"
        )


@router.options("/tokens")
async def options_tokens(response: Response):
    """Handle CORS preflight requests for tokens endpoint"""
    response.headers["Access-Control-Allow-Origin"] = "https://taraai.tech"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "accept, authorization, content-type, origin, x-requested-with"
    return {"message": "CORS preflight handled"}


@router.get("/drive/auth-url")
async def get_google_drive_auth_url(
    state: Optional[str] = Query(None, description="Optional state parameter for security"),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """Get Google Drive OAuth authorization URL"""
    try:
        auth_url = oauth_service.get_google_drive_auth_url(state)
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Google Drive auth URL: {str(e)}"
        )


@router.get("/drive/callback", response_model=GoogleDriveOAuthResponse)
async def google_drive_oauth_callback_get(
    code: str = Query(..., description="Google authorization code"),
    state: Optional[str] = Query(None, description="State parameter"),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """Handle Google Drive OAuth callback (GET) and exchange code for token"""
    try:
        # Exchange code for token
        google_response = await oauth_service.exchange_google_drive_code_for_token(code)
        
        return google_response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google Drive OAuth callback failed: {str(e)}"
        )


@router.post("/drive/save-token", response_model=OAuthTokenResponse)
async def save_google_drive_token(
    request: dict,
    user_id: str = Depends(get_current_user_id),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """Save Google Drive OAuth token for a user"""
    try:
        # Get user ID from JWT token
        user_id = UUID(user_id)
        
        # Log the incoming request
        print(f"📥 Frontend save-token request:")
        print(f"   User ID: {user_id}")
        print(f"   Request body: {request}")
        
        # Extract access token from request
        access_token = request.get("access_token")
        refresh_token = request.get("refresh_token")
        
        print(f"🔑 Extracted tokens:")
        print(f"   Access token: {access_token[:20]}..." if access_token else "   Access token: None")
        print(f"   Refresh token: {refresh_token[:20]}..." if refresh_token else "   Refresh token: None")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="access_token is required"
            )
        
        # Create Google Drive response object
        google_response = GoogleDriveOAuthResponse(
            access_token=access_token,
            refresh_token=refresh_token or "",
            token_type="bearer",
            expires_in=3600,
            scope="https://www.googleapis.com/auth/drive"
        )
        
        token_entity = await oauth_service.save_google_drive_token(user_id, google_response)
        return OAuthTokenResponse(
            id=token_entity.id,
            access_token=token_entity.access_token,
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
            detail=f"Failed to save Google Drive token: {str(e)}"
        )


@router.post("/drive/refresh-token")
async def refresh_google_drive_token(
    user_id: str = Depends(get_current_user_id),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """Refresh Google Drive access token for current user"""
    try:
        user_id = UUID(user_id)
        
        # Get valid token (will refresh if needed)
        valid_token = await oauth_service.get_valid_google_drive_token(user_id)
        
        if not valid_token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No valid Google Drive token found or refresh failed"
            )
        
        return {
            "message": "Token refreshed successfully",
            "access_token": valid_token[:20] + "...",  # Only show first 20 chars for security
            "expires_at": "Updated in database"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh Google Drive token: {str(e)}"
        )