from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from internal.hr.department.service.department_service import DepartmentService
from internal.hr.department.repository.department_repository_db import DatabaseDepartmentRepository
from internal.hr.department.model.department_dto import DepartmentOverviewResponse

router = APIRouter(prefix="/hr/department", tags=["hr-department"])


def get_department_service(db: Session = Depends(get_db)) -> DepartmentService:
    """Dependency to get department service"""
    repository = DatabaseDepartmentRepository(db)
    return DepartmentService(repository)


@router.get("/overview", response_model=DepartmentOverviewResponse)
async def get_department_overview(
    department_service: DepartmentService = Depends(get_department_service)
):
    """Get department overview statistics"""
    
    try:
        return await department_service.get_department_overview()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get department overview: {str(e)}"
        )
