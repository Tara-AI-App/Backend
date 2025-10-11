from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from uuid import UUID
from internal.user.model.user_entity import User


class UserRepository(ABC):
    """Repository interface for User entities"""
    
    @abstractmethod
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass
    
    @abstractmethod
    async def create_user(self, user: User) -> User:
        """Create a new user"""
        pass
    
    @abstractmethod
    async def get_user_summary(self, user_id: UUID) -> Dict[str, Any]:
        """Get user dashboard summary statistics"""
        pass