from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Project info
    PROJECT_NAME: str = "Tara API"
    PROJECT_DESCRIPTION: str = "A FastAPI application with Domain Driven Design"
    VERSION: str = "1.0.0"
    
    # API settings
    API_V1_STR: str = "/api/v1"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 9000
    DEBUG: bool = True
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database settings - only what's actually used
    DATABASE_URL: str = Field(description="Full database URL")
    
    # Security settings
    SECRET_KEY: str = Field(description="Secret key for JWT token signing")
    JWT_EXPIRATION_SECONDS: int = Field(default=2592000, description="JWT token expiration time in seconds (default: 1 month)")
    
    # GitHub OAuth settings
    GH_CLIENT_ID: str = Field(description="GitHub OAuth client ID")
    GH_CLIENT_SECRET: str = Field(description="GitHub OAuth client secret")
    GH_REDIRECT_URI: str = Field(description="GitHub OAuth redirect URI")
    
    # Google Drive OAuth settings
    GOOGLE_CLIENT_ID: str = Field(description="Google OAuth client ID")
    GOOGLE_CLIENT_SECRET: str = Field(description="Google OAuth client secret")
    GOOGLE_REDIRECT_URI: str = Field(description="Google OAuth redirect URI")
    
    # External AI API settings
    AI_API_BASE_URL: str = Field(default="https://agent.taraai.tech", description="Base URL for external AI API")
    AI_API_TIMEOUT: int = Field(default=30, description="Timeout for AI API requests in seconds")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
