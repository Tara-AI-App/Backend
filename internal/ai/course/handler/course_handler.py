from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.connection import get_db
from internal.ai.course.model.course_dto import AiCourseGenerateRequest, AiCourseGenerateResponse
from internal.ai.course.service.course_service import AiCourseService
from internal.ai.course.repository.ai_course_repository_db import DatabaseAiCourseRepository
from internal.oauth.service.oauth_service import OAuthService
from internal.oauth.repository.oauth_repository_db import DatabaseOAuthRepository
from internal.auth.middleware import get_current_user_id
from internal.user.service.user_service import UserService
from internal.user.repository.user_repository_db import DatabaseUserRepository

router = APIRouter(prefix="/ai/course", tags=["ai-course"])
security = HTTPBearer()

def get_oauth_service(db: Session = Depends(get_db)) -> OAuthService:
    """Dependency to get OAuth service"""
    oauth_repository = DatabaseOAuthRepository(db)
    return OAuthService(oauth_repository)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency to get user service"""
    user_repository = DatabaseUserRepository(db)
    return UserService(user_repository)

def get_ai_course_service(
    oauth_service: OAuthService = Depends(get_oauth_service),
    user_service: UserService = Depends(get_user_service),
    db: Session = Depends(get_db)
) -> AiCourseService:
    """Dependency to get AI course service"""
    course_repository = DatabaseAiCourseRepository(db)
    return AiCourseService(oauth_service, course_repository, user_service)

@router.post("/generate", response_model=AiCourseGenerateResponse)
async def generate_course(
    course_data: AiCourseGenerateRequest,
    ai_course_service: AiCourseService = Depends(get_ai_course_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Generate a course using AI"""
    try:
        user_id = UUID(current_user_id)
        return await ai_course_service.generate_course(course_data, user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate course: {str(e)}"
        )

