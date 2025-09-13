from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import text
from sqlalchemy.orm import Session
from internal.user.model.user_entity import User
from internal.user.repository.user_repository import UserRepository


class DatabaseUserRepository(UserRepository):
    """Database implementation of User repository using raw SQL"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID using raw SQL"""
        query = text("""
            SELECT id, department_id, position_id, manager_id, location_id, 
                   name, image, email, password, country, created_at
            FROM users 
            WHERE id = :user_id
        """)
        
        result = self.db.execute(query, {"user_id": user_id}).fetchone()
        
        if not result:
            return None
        
        return User(
            id=result.id,
            department_id=result.department_id,
            position_id=result.position_id,
            manager_id=result.manager_id,
            location_id=result.location_id,
            name=result.name,
            image=result.image,
            email=result.email,
            password=result.password,
            country=result.country,
            created_at=result.created_at
        )
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email using raw SQL"""
        query = text("""
            SELECT id, department_id, position_id, manager_id, location_id, 
                   name, image, email, password, country, created_at
            FROM users 
            WHERE email = :email
        """)
        
        result = self.db.execute(query, {"email": email}).fetchone()
        
        if not result:
            return None
        
        return User(
            id=result.id,
            department_id=result.department_id,
            position_id=result.position_id,
            manager_id=result.manager_id,
            location_id=result.location_id,
            name=result.name,
            image=result.image,
            email=result.email,
            password=result.password,
            country=result.country,
            created_at=result.created_at
        )
    
    async def create_user(self, user: User) -> User:
        """Create a new user using raw SQL"""
        user.id = uuid4()
        user.hash_password()
        
        query = text("""
            INSERT INTO users (id, department_id, position_id, manager_id, location_id, 
                             name, image, email, password, country, created_at)
            VALUES (:id, :department_id, :position_id, :manager_id, :location_id, 
                    :name, :image, :email, :password, :country, :created_at)
        """)
        
        self.db.execute(query, {
            "id": user.id,
            "department_id": user.department_id,
            "position_id": user.position_id,
            "manager_id": user.manager_id,
            "location_id": user.location_id,
            "name": user.name,
            "image": user.image,
            "email": user.email,
            "password": user.password,
            "country": user.country,
            "created_at": user.created_at
        })
        
        self.db.commit()
        return user