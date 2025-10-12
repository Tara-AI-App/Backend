from internal.hr.department.repository.department_repository import DepartmentRepository
from internal.hr.department.model.department_dto import DepartmentOverviewItem, DepartmentOverviewResponse, DepartmentDetailResponse, DepartmentListResponse, DepartmentEmployeeListResponse
from typing import List, Optional


class DepartmentService:
    """Service for department statistics operations"""
    
    def __init__(self, repository: DepartmentRepository):
        self.repository = repository
    
    async def get_department_overview(self) -> DepartmentOverviewResponse:
        """Get department overview statistics"""
        departments = await self.repository.get_department_overview()
        return DepartmentOverviewResponse(departments=departments)
    
    async def get_department_detail(self, department_id: str) -> Optional[DepartmentDetailResponse]:
        """Get specific department detail by ID"""
        return await self.repository.get_department_detail(department_id)
    
    async def get_department_list(self) -> DepartmentListResponse:
        """Get list of all departments"""
        return await self.repository.get_department_list()
    
    async def get_department_employees(self, department_id: str) -> Optional[DepartmentEmployeeListResponse]:
        """Get list of employees for a specific department"""
        return await self.repository.get_department_employees(department_id)
