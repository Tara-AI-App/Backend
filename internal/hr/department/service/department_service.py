from internal.hr.department.repository.department_repository import DepartmentRepository
from internal.hr.department.model.department_dto import DepartmentOverviewItem, DepartmentOverviewResponse
from typing import List


class DepartmentService:
    """Service for department statistics operations"""
    
    def __init__(self, repository: DepartmentRepository):
        self.repository = repository
    
    async def get_department_overview(self) -> DepartmentOverviewResponse:
        """Get department overview statistics"""
        departments = await self.repository.get_department_overview()
        return DepartmentOverviewResponse(departments=departments)
