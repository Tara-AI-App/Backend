from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
# from internal.domain.handler.item_handler import router as item_router
from internal.ai.handler.ai_handler import router as ai_router
from internal.user.handler.user_handler import router as user_router
from internal.oauth.handler.oauth_handler import router as oauth_router
# from internal.domain.handler.lms_handler import (
#     department_router, position_router, location_router,
#     user_router, course_router, module_router
# )
from internal.auth.middleware import JWTMiddleware
from app.config import settings
from app.database.connection import SessionLocal

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
    # app.include_router(item_router, prefix=settings.API_V1_STR)
    app.include_router(ai_router, prefix=settings.API_V1_STR)
    app.include_router(user_router, prefix=settings.API_V1_STR)
    app.include_router(oauth_router, prefix=settings.API_V1_STR)
    
    # Include LMS routers (commented out until handlers are implemented)
    # app.include_router(department_router, prefix=settings.API_V1_STR)
    # app.include_router(position_router, prefix=settings.API_V1_STR)
    # app.include_router(location_router, prefix=settings.API_V1_STR)
    # app.include_router(user_router, prefix=settings.API_V1_STR)
    # app.include_router(course_router, prefix=settings.API_V1_STR)
    # app.include_router(module_router, prefix=settings.API_V1_STR)

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
        try:
            # Test database connection
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
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
