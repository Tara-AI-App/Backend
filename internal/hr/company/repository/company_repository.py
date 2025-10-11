from abc import ABC, abstractmethod
from typing import Dict, Any
from internal.hr.company.model.company_dto import CompanyStatisticResponse


class CompanyRepository(ABC):
    """Abstract repository for company data"""
    
    @abstractmethod
    async def get_company_statistics(self) -> CompanyStatisticResponse:
        """Get company statistics"""
        pass
