from abc import ABC, abstractmethod
from typing import List, Optional
from internal.hr.department.model.department_dto import DepartmentOverviewItem, DepartmentDetailResponse, DepartmentListResponse, DepartmentEmployeeListResponse


class DepartmentRepository(ABC):
    """Abstract repository for department data"""
    
    @abstractmethod
    async def get_department_overview(self) -> List[DepartmentOverviewItem]:
        """Get department overview statistics"""
        pass
    
    @abstractmethod
    async def get_department_detail(self, department_id: str) -> Optional[DepartmentDetailResponse]:
        """Get specific department detail by ID"""
        pass
    
    @abstractmethod
    async def get_department_list(self) -> DepartmentListResponse:
        """Get list of all departments"""
        pass
    
    @abstractmethod
    async def get_department_employees(self, department_id: str) -> Optional[DepartmentEmployeeListResponse]:
        """Get list of employees for a specific department"""
        pass
