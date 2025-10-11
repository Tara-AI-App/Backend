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
