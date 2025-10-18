from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.connection import get_db
from internal.ai.guide.model.guide_dto import AiGuideGenerateRequest, AiGuideGenerateResponse, GuideListResponse
from internal.ai.guide.service.guide_service import AiGuideService
from internal.ai.guide.repository.ai_guide_repository_db import DatabaseAiGuideRepository
from internal.oauth.service.oauth_service import OAuthService
from internal.oauth.repository.oauth_repository_db import DatabaseOAuthRepository
from internal.auth.middleware import get_current_user_id
from internal.user.service.user_service import UserService
from internal.user.repository.user_repository_db import DatabaseUserRepository

router = APIRouter(prefix="/ai/guide", tags=["ai-guide"])
security = HTTPBearer()

def get_oauth_service(db: Session = Depends(get_db)) -> OAuthService:
    """Dependency to get OAuth service"""
    oauth_repository = DatabaseOAuthRepository(db)
    return OAuthService(oauth_repository)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency to get user service"""
    user_repository = DatabaseUserRepository(db)
    return UserService(user_repository)

def get_ai_guide_service(
    oauth_service: OAuthService = Depends(get_oauth_service),
    user_service: UserService = Depends(get_user_service),
    db: Session = Depends(get_db)
) -> AiGuideService:
    """Dependency to get AI guide service"""
    guide_repository = DatabaseAiGuideRepository(db)
    return AiGuideService(oauth_service, guide_repository, user_service)

@router.post("/generate", response_model=AiGuideGenerateResponse)
async def generate_guide(
    guide_data: AiGuideGenerateRequest,
    ai_guide_service: AiGuideService = Depends(get_ai_guide_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Generate a guide using AI"""
    try:
        user_id = UUID(current_user_id)
        return await ai_guide_service.generate_guide(guide_data, user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate guide: {str(e)}"
        )

@router.get("/", response_model=GuideListResponse)
async def get_guides(
    ai_guide_service: AiGuideService = Depends(get_ai_guide_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get all guides for the current user"""
    try:
        user_id = UUID(current_user_id)
        return await ai_guide_service.get_guides(user_id)
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
