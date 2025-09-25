from fastapi import Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
from app.config import settings
from internal.user.service.user_service import UserService
from internal.user.repository.user_repository_db import DatabaseUserRepository
from app.database.connection import SessionLocal

security = HTTPBearer(auto_error=False)

class JWTMiddleware:
    """JWT Authentication Middleware"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_user_service(self) -> UserService:
        """Get user service instance"""
        db = SessionLocal()
        user_repository = DatabaseUserRepository(db)
        return UserService(user_repository)
    
    async def __call__(self, request: Request, call_next):
        """Middleware function to handle JWT authentication"""
        
        # Skip authentication for CORS preflight requests
        if request.method == "OPTIONS":
            response = await call_next(request)
            return response
        
        # Skip authentication for specific paths
        skip_paths = [
            "/api/v1/users/login",
            "/api/v1/users/register",
            "/api/v1/oauth/github/auth-url",  # OAuth auth URL doesn't need auth
            "/api/v1/oauth/github/callback",  # OAuth callback doesn't need auth
            "/api/v1/oauth/drive/auth-url",  # Google Drive OAuth auth URL doesn't need auth
            "/api/v1/oauth/drive/callback",  # Google Drive OAuth callback doesn't need auth
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/cors-test"  # Add the CORS test endpoint
        ]
        
        # Check if current path should be skipped
        if request.url.path in skip_paths:
            response = await call_next(request)
            return response
        
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid authorization header"},
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Extract token
        token = auth_header.split(" ")[1]
        
        # Verify token
        payload = self.verify_token(token)
        
        if not payload:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Add user_id to request state for use in endpoints
        request.state.user_id = payload.get("user_id")
        request.state.user_payload = payload
        
        # Continue to the next middleware/endpoint
        response = await call_next(request)
        return response


def get_current_user_id(request: Request) -> str:
    """Dependency to get current user ID from request state"""
    if not hasattr(request.state, 'user_id') or not request.state.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )
    return request.state.user_id


def get_current_user_payload(request: Request) -> dict:
    """Dependency to get current user payload from request state"""
    if not hasattr(request.state, 'user_payload') or not request.state.user_payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )
    return request.state.user_payload


def get_user_service() -> UserService:
    """Dependency to get user service"""
    db = SessionLocal()
    user_repository = DatabaseUserRepository(db)
    return UserService(user_repository)


def get_current_user_credentials(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service)
) -> dict:
    """Legacy dependency for backward compatibility"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = user_service.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload
