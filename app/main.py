from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import logging
from internal.user.handler.user_handler import router as user_router
from internal.oauth.handler.oauth_handler import router as oauth_router
from internal.ai.course.handler.course_handler import router as ai_course_router
from internal.course.handler.course_handler import router as course_router
from internal.hr.company.handler.company_handler import router as hr_company_router
from internal.auth.middleware import JWTMiddleware
from app.config import settings
from app.database.connection import SessionLocal

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create logger for this module
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
    )

    # Add CORS middleware - must be added before other middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # Next.js dev server
            "http://127.0.0.1:3000",  # Alternative localhost
            "http://localhost:3001",  # Alternative port
            "http://127.0.0.1:3001",  # Alternative localhost and port
            "https://taraai.tech",  
        ],
        allow_credentials=True,  # Allow credentials (cookies, authorization headers)
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],  # Specific methods
        allow_headers=[
            "accept",
            "accept-encoding", 
            "authorization",
            "content-type",
            "dnt",
            "origin",
            "user-agent",
            "x-csrftoken",
            "x-requested-with",
        ],  # Specific headers that are commonly needed
        expose_headers=["*"],  # Headers that the frontend can access
    )
    
    # Add JWT authentication middleware
    app.middleware("http")(JWTMiddleware())

    # Include routers
    app.include_router(user_router, prefix=settings.API_V1_STR)
    app.include_router(oauth_router, prefix=settings.API_V1_STR)
    app.include_router(ai_course_router, prefix=settings.API_V1_STR)
    app.include_router(course_router, prefix=settings.API_V1_STR)
    app.include_router(hr_company_router, prefix=settings.API_V1_STR)

    @app.get("/")
    async def read_root():
        return {"message": "Welcome to Tara API"}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    @app.get("/cors-test")
    async def cors_test():
        return {"message": "CORS is working!", "timestamp": "2025-01-27"}
    
    @app.options("/{path:path}")
    async def cors_preflight(path: str):
        """Handle CORS preflight requests"""
        return {"message": "CORS preflight handled"}

    @app.on_event("startup")
    async def startup_event():
        """Test database connection on startup"""
        logger.info("🚀 Starting Tara API application...")
        try:
            # Test database connection
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            logger.info("✅ Database connection successful")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise e

    return app

# Create app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
