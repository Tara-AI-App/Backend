from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.connection import get_db
from internal.guide.model.guide_dto import GuideListResponse, GuideDetailResponse
from internal.guide.service.guide_service import GuideService
from internal.guide.repository.guide_repository_db import DatabaseGuideRepository
from internal.oauth.service.oauth_service import OAuthService
from internal.oauth.repository.oauth_repository_db import DatabaseOAuthRepository
from internal.auth.middleware import get_current_user_id
from internal.user.service.user_service import UserService
from internal.user.repository.user_repository_db import DatabaseUserRepository

router = APIRouter(prefix="/guide", tags=["guide"])
security = HTTPBearer()

def get_oauth_service(db: Session = Depends(get_db)) -> OAuthService:
    """Dependency to get OAuth service"""
    oauth_repository = DatabaseOAuthRepository(db)
    return OAuthService(oauth_repository)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency to get user service"""
    user_repository = DatabaseUserRepository(db)
    return UserService(user_repository)

def get_guide_service(
    oauth_service: OAuthService = Depends(get_oauth_service),
    user_service: UserService = Depends(get_user_service),
    db: Session = Depends(get_db)
) -> GuideService:
    """Dependency to get guide service"""
    guide_repository = DatabaseGuideRepository(db)
    return GuideService(oauth_service, guide_repository, user_service)

@router.get("/", response_model=GuideListResponse)
async def get_guides(
    guide_service: GuideService = Depends(get_guide_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get all guides for the current user"""
    try:
        user_id = UUID(current_user_id)
        return await guide_service.get_guides(user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get guides: {str(e)}"
        )

@router.get("/{guide_id}", response_model=GuideDetailResponse)
async def get_guide_detail(
    guide_id: str,
    guide_service: GuideService = Depends(get_guide_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get a specific guide by ID for the current user"""
    try:
        guide_uuid = UUID(guide_id)
        user_id = UUID(current_user_id)
        return await guide_service.get_guide_by_id(guide_uuid, user_id)
    except ValueError as e:
        if "Guide not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get guide: {str(e)}"
        )
