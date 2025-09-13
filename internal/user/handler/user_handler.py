from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.database.connection import get_db
from internal.user.model.user_dto import UserCreateRequest, UserLoginRequest, UserLoginResponse, UserResponse
from internal.user.service.user_service import UserService
from internal.user.repository.user_repository_db import DatabaseUserRepository

router = APIRouter(prefix="/users", tags=["users"])
security = HTTPBearer()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency to get user service"""
    user_repository = DatabaseUserRepository(db)
    return UserService(user_repository)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service)
) -> dict:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = user_service.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreateRequest,
    user_service: UserService = Depends(get_user_service)
):
    """Register a new user"""
    try:
        return await user_service.create_user(user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=UserLoginResponse)
async def login_user(
    login_data: UserLoginRequest,
    user_service: UserService = Depends(get_user_service)
):
    """Login user and get access token"""
    try:
        return await user_service.login_user(login_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get current user information"""
    user_id = UUID(current_user["user_id"])
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service)
):
    """Get user by ID"""
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
