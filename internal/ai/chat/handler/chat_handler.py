from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.connection import get_db
from internal.ai.chat.model.chat_dto import CourseChatRequest, CourseChatResponse, GuideChatRequest, GuideChatResponse
from internal.ai.chat.service.chat_service import ChatService
from internal.auth.middleware import get_current_user_id

router = APIRouter(prefix="/ai/chat", tags=["ai-chat"])

def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    """Dependency to get chat service"""
    return ChatService(db)

@router.post("/course/{course_id}", response_model=CourseChatResponse)
async def chat_with_course(
    course_id: UUID,
    chat_request: CourseChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Chat with AI about a specific course"""
    try:
        user_id = UUID(current_user_id)
        return await chat_service.chat_about_course(str(course_id), chat_request, user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process course chat: {str(e)}"
        )

@router.post("/guide/{guide_id}", response_model=GuideChatResponse)
async def chat_with_guide(
    guide_id: UUID,
    chat_request: GuideChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Chat with AI about a specific guide"""
    try:
        user_id = UUID(current_user_id)
        return await chat_service.chat_about_guide(str(guide_id), chat_request, user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process guide chat: {str(e)}"
        )
