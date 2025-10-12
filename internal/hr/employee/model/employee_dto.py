from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel


class EmployeeDetailResponse(BaseModel):
    """DTO for employee detail response"""
    
    id: UUID
    name: str
    email: str
    image: Optional[str]
    status: bool
    country: Optional[str]
    cv: Optional[str]
    created_at: datetime
    
    # Department information
    department_id: Optional[UUID]
    department_name: Optional[str]
    
    # Position information
    position_id: Optional[UUID]
    position_name: Optional[str]
    
    # Manager information
    manager_id: Optional[UUID]
    manager_name: Optional[str]
    
    # Location information
    location_id: Optional[UUID]
    location_city: Optional[str]
    location_country: Optional[str]
    
    # Learning statistics
    total_courses: int
    completed_courses: int
    in_progress_courses: int
    completion_rate: float
    total_learning_hours: float
    skills: List[str]
