from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from internal.hr.employee.model.employee_dto import EmployeeDetailResponse


class EmployeeRepository(ABC):
    """Abstract repository for employee operations"""
    
    @abstractmethod
    async def get_employee_detail(self, user_id: UUID) -> Optional[EmployeeDetailResponse]:
        """Get detailed employee information by user ID"""
        pass
