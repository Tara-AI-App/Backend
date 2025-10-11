from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from internal.hr.company.service.company_service import CompanyService
from internal.hr.company.repository.company_repository_db import DatabaseCompanyRepository
from internal.hr.company.model.company_dto import CompanyStatisticResponse

router = APIRouter(prefix="/hr/company", tags=["hr-company"])


def get_company_service(db: Session = Depends(get_db)) -> CompanyService:
    """Dependency to get company service"""
    repository = DatabaseCompanyRepository(db)
    return CompanyService(repository)


@router.get("/statistic", response_model=CompanyStatisticResponse)
async def get_company_statistics(
    company_service: CompanyService = Depends(get_company_service)
):
    """Get company statistics for HR dashboard"""
    try:
        return await company_service.get_company_statistics()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get company statistics: {str(e)}"
        )
