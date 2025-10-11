from internal.hr.company.repository.company_repository import CompanyRepository
from internal.hr.company.model.company_dto import CompanyStatisticResponse


class CompanyService:
    """Service for company statistics operations"""
    
    def __init__(self, repository: CompanyRepository):
        self.repository = repository
    
    async def get_company_statistics(self) -> CompanyStatisticResponse:
        """Get company statistics"""
        return await self.repository.get_company_statistics()
