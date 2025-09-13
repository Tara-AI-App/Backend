from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class UserCreateRequest:
    """DTO for creating a new user"""
    
    department_id: Optional[UUID] = None
    position_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    location_id: Optional[UUID] = None
    name: str = ""
    image: Optional[str] = None
    email: str = ""
    password: str = ""
    country: Optional[str] = None


@dataclass
class UserLoginRequest:
    """DTO for user login"""
    
    email: str
    password: str


@dataclass
class UserUpdateRequest:
    """DTO for updating an existing user"""
    
    department_id: Optional[UUID] = None
    position_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    location_id: Optional[UUID] = None
    name: Optional[str] = None
    image: Optional[str] = None
    email: Optional[str] = None
    country: Optional[str] = None


@dataclass
class UserResponse:
    """DTO for user response"""
    
    id: UUID
    department_id: Optional[UUID]
    position_id: Optional[UUID]
    manager_id: Optional[UUID]
    location_id: Optional[UUID]
    name: str
    image: Optional[str]
    email: str
    country: Optional[str]
    created_at: datetime


@dataclass
class UserLoginResponse:
    """DTO for user login response"""
    
    user: UserResponse
    access_token: str
    token_type: str = "bearer"