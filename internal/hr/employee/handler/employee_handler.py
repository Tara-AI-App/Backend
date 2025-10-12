from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.connection import get_db
from internal.hr.employee.service.employee_service import EmployeeService
from internal.hr.employee.repository.employee_repository_db import DatabaseEmployeeRepository
from internal.hr.employee.model.employee_dto import EmployeeDetailResponse
from internal.course.service.course_service import CourseService
from internal.course.repository.course_repository_db import DatabaseCourseRepository
from internal.course.model.course_dto import CourseListResponse

router = APIRouter(prefix="/hr/employee", tags=["hr-employee"])


def get_employee_service(db: Session = Depends(get_db)) -> EmployeeService:
    """Dependency to get employee service"""
    repository = DatabaseEmployeeRepository(db)
    return EmployeeService(repository)


def get_course_service(db: Session = Depends(get_db)) -> CourseService:
    """Dependency to get course service"""
    repository = DatabaseCourseRepository(db)
    return CourseService(repository)


@router.get("/{user_id}", response_model=EmployeeDetailResponse)
async def get_employee_detail(
    user_id: UUID,
    employee_service: EmployeeService = Depends(get_employee_service)
):  
    try:
        employee = await employee_service.get_employee_detail(user_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return employee
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get employee detail: {str(e)}"
        )


@router.get("/{user_id}/course", response_model=CourseListResponse)
async def get_employee_courses(
    user_id: UUID,
    limit: int = 5,
    offset: int = 0,
    course_service: CourseService = Depends(get_course_service)
):
    """Get courses for a specific employee with pagination"""
    try:
        courses = await course_service.get_courses(user_id, limit, offset)
        return courses
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get employee courses: {str(e)}"
        )
