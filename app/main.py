from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
# from internal.domain.handler.item_handler import router as item_router
from internal.ai.handler.ai_handler import router as ai_router
from internal.user.handler.user_handler import router as user_router
# from internal.domain.handler.lms_handler import (
#     department_router, position_router, location_router,
#     user_router, course_router, module_router
# )
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

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    # app.include_router(item_router, prefix=settings.API_V1_STR)
    app.include_router(ai_router, prefix=settings.API_V1_STR)
    app.include_router(user_router, prefix=settings.API_V1_STR)
    
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
