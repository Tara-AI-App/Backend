from pydantic import BaseModel
from typing import List


class DepartmentOverviewItem(BaseModel):
    """Individual department overview item"""
    
    department: str
    total_users: int
    active_users: int
    avg_progress: int  # Percentage as integer (72 for 72%)


class DepartmentOverviewResponse(BaseModel):
    """Response model for department overview"""
    
    departments: List[DepartmentOverviewItem]


class DepartmentDetailResponse(BaseModel):
    """Response model for specific department detail"""
    
    department_name: str
    description: str
    total_employees: int
    active_learners: int
    avg_progress: int  # Percentage as integer (72 for 72%)
    courses_completed: int


class DepartmentListItem(BaseModel):
    """Individual department list item"""
    
    id: str
    name: str
    description: str
    created_at: str


class DepartmentListResponse(BaseModel):
    """Response model for department list"""
    
    departments: List[DepartmentListItem]
