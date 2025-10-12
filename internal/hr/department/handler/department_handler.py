from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from internal.hr.department.service.department_service import DepartmentService
from internal.hr.department.repository.department_repository_db import DatabaseDepartmentRepository
from internal.hr.department.model.department_dto import DepartmentOverviewResponse, DepartmentDetailResponse, DepartmentListResponse, DepartmentEmployeeListResponse

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

@router.get("/list", response_model=DepartmentListResponse)
async def get_department_list(
    department_service: DepartmentService = Depends(get_department_service)
):
    """Get list of all departments"""
    
    try:
        return await department_service.get_department_list()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get department list: {str(e)}"
        )

@router.get("/{department_id}", response_model=DepartmentDetailResponse)
async def get_department_detail(
    department_id: str,
    department_service: DepartmentService = Depends(get_department_service)
):
    """Get specific department detail by ID"""
    
    try:
        detail = await department_service.get_department_detail(department_id)
        if not detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department with ID {department_id} not found"
            )
        return detail
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get department detail: {str(e)}"
        )


@router.get("/{department_id}/list", response_model=DepartmentEmployeeListResponse)
async def get_department_employees(
    department_id: str,
    department_service: DepartmentService = Depends(get_department_service)
):
    """Get list of employees for a specific department"""
    
    try:
        employees = await department_service.get_department_employees(department_id)
        if not employees:
            # Return empty list instead of error
            return DepartmentEmployeeListResponse(employees=[], total_count=0)
        return employees
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get department employees: {str(e)}"
        )
