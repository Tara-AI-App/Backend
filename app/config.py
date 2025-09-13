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
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database settings - only what's actually used
    DATABASE_URL: str = Field(default="sqlite:///./test.db", description="Full database URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
