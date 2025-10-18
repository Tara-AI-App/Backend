from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID
import hashlib


@dataclass
class User:
    """User domain entity"""
    
    id: Optional[UUID] = None
    name: str = ""
    email: str = ""
    password: str = ""
    country: Optional[str] = None
    department_id: Optional[UUID] = None
    position_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    location_id: Optional[UUID] = None
    image: Optional[str] = None
    created_at: Optional[datetime] = None
    cv: Optional[str] = None
    
    def __post_init__(self):
        """Validate user data after initialization"""
        if not self.name:
            raise ValueError("User name is required")
        if not self.email:
            raise ValueError("User email is required")
        if self.email and "@" not in self.email:
            raise ValueError("Invalid email format")
        if not self.password:
            raise ValueError("User password is required")
    
    def is_valid(self) -> bool:
        """Check if user data is valid"""
        try:
            self.__post_init__()
            return True
        except ValueError:
            return False
    
    def update_email(self, new_email: str) -> None:
        """Update user email with validation"""
        if not new_email or "@" not in new_email:
            raise ValueError("Invalid email format")
        self.email = new_email
    
    def hash_password(self) -> None:
        """Hash the password using SHA-256"""
        if self.password:
            self.password = hashlib.sha256(self.password.encode()).hexdigest()
    
    def verify_password(self, plain_password: str) -> bool:
        """Verify password against stored hash"""
        hashed_password = hashlib.sha256(plain_password.encode()).hexdigest()
        return hashed_password == self.password
    
    def update_name(self, new_name: str) -> None:
        """Update user name with validation"""
        if not new_name:
            raise ValueError("User name cannot be empty")
        self.name = new_name
