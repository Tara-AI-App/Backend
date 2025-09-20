from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from jose import jwt
from internal.user.model.user_entity import User
from internal.user.model.user_dto import UserCreateRequest, UserLoginRequest, UserLoginResponse, UserResponse, UserCreateResponse
from internal.user.repository.user_repository import UserRepository
from app.config import settings


class UserService:
    """Service for user operations"""
    
    def __init__(self, user_repository: UserRepository, secret_key: str = None):
        self.user_repository = user_repository
        self.secret_key = secret_key or settings.SECRET_KEY
    
    async def create_user(self, user_data: UserCreateRequest) -> UserCreateResponse:
        """Create a new user"""
        user = User(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password,
            country=user_data.country,
            created_at=datetime.now(timezone.utc)
        )
        
        created_user = await self.user_repository.create_user(user)
        
        return UserCreateResponse(
            id=created_user.id,
            name=created_user.name,
            email=created_user.email,
            country=created_user.country,
            created_at=created_user.created_at
        )
    
    async def login_user(self, login_data: UserLoginRequest) -> UserLoginResponse:
        """Authenticate user and return JWT token"""
        user = await self.user_repository.get_user_by_email(login_data.email)
        
        if not user:
            raise ValueError("Invalid email or password")
        
        if not user.verify_password(login_data.password):
            raise ValueError("Invalid email or password")
        
        # Generate JWT token
        token_payload = {
            "user_id": str(user.id),
            "email": user.email,
            "exp": datetime.now(timezone.utc).timestamp() + settings.JWT_EXPIRATION_SECONDS  # Configurable expiration
        }
        
        access_token = jwt.encode(token_payload, self.secret_key, algorithm="HS256")
        
        user_response = UserResponse(
            id=user.id,
            department_id=user.department_id,
            position_id=user.position_id,
            manager_id=user.manager_id,
            location_id=user.location_id,
            name=user.name,
            image=user.image,
            email=user.email,
            country=user.country,
            created_at=user.created_at
        )
        
        return UserLoginResponse(
            user=user_response,
            access_token=access_token
        )
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[UserResponse]:
        """Get user by ID"""
        user = await self.user_repository.get_user_by_id(user_id)
        
        if not user:
            return None
        
        return UserResponse(
            id=user.id,
            department_id=user.department_id,
            position_id=user.position_id,
            manager_id=user.manager_id,
            location_id=user.location_id,
            name=user.name,
            image=user.image,
            email=user.email,
            country=user.country,
            created_at=user.created_at
        )
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
