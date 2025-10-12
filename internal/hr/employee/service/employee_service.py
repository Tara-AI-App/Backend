from internal.hr.employee.repository.employee_repository import EmployeeRepository
from internal.hr.employee.model.employee_dto import EmployeeDetailResponse
from typing import Optional
from uuid import UUID


class EmployeeService:
    """Service for employee operations"""
    
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository
    
    async def get_employee_detail(self, user_id: UUID) -> Optional[EmployeeDetailResponse]:
        """Get detailed employee information by user ID"""
        return await self.repository.get_employee_detail(user_id)
