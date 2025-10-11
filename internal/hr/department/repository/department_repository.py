from abc import ABC, abstractmethod
from typing import List
from internal.hr.department.model.department_dto import DepartmentOverviewItem


class DepartmentRepository(ABC):
    """Abstract repository for department data"""
    
    @abstractmethod
    async def get_department_overview(self) -> List[DepartmentOverviewItem]:
        """Get department overview statistics"""
        pass
