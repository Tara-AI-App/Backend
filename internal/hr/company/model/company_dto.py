from pydantic import BaseModel
from typing import Optional


class CompanyStatisticResponse(BaseModel):
    """Response model for company statistics"""
    
    # Top row statistics
    total_employees: int
    active_learners: int
    avg_progress: int  # Percentage as integer (68 for 68%)
    courses_completed: int
    
    # Bottom row statistics
    top_performer: str
    most_active: str
    largest_team: str
    
    class Config:
        from_attributes = True
