from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.connection import get_db
from internal.course.model.course_dto import CourseListResponse, CourseDetail, LessonCompletionRequest, LessonCompletionResponse
from internal.course.service.course_service import CourseService
from internal.course.repository.course_repository_db import DatabaseCourseRepository
from internal.auth.middleware import get_current_user_id

router = APIRouter(prefix="/course", tags=["course"])

def get_course_service(db: Session = Depends(get_db)) -> CourseService:
    """Dependency to get course service"""
    course_repository = DatabaseCourseRepository(db)
    return CourseService(course_repository)

@router.get("", response_model=CourseListResponse)
async def get_courses(
    course_service: CourseService = Depends(get_course_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get all courses for the current user"""
    try:
        user_id = UUID(current_user_id)
        return await course_service.get_courses(user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get courses: {str(e)}"
        )

@router.get("/{course_id}", response_model=CourseDetail)
async def get_course_by_id(
    course_id: UUID,
    course_service: CourseService = Depends(get_course_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get a specific course by ID for the current user"""
    try:
        user_id = UUID(current_user_id)
        course = await course_service.get_course_by_id(course_id, user_id)
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        return course
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get course: {str(e)}"
        )

@router.patch("/lesson/{lesson_id}/complete", response_model=LessonCompletionResponse)
async def update_lesson_completion(
    lesson_id: UUID,
    request: LessonCompletionRequest,
    course_service: CourseService = Depends(get_course_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Mark a lesson as completed or incomplete"""
    try:
        user_id = UUID(current_user_id)
        return await course_service.update_lesson_completion(lesson_id, user_id, request.is_completed)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update lesson completion: {str(e)}"
        )
