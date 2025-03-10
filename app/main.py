# app/main.py
"""Main entry point for the FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings, logger
from app.database import init_db, close_db
from app.api.endpoints import logs, reports


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title=settings.app_name,
        description="API for logging phone call events from Yealink and Cisco phones",
        version="1.0.0"
    )
    
    # Add CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    application.include_router(logs.router, tags=["Logs"])
    application.include_router(reports.router, prefix="/reports", tags=["Reports"])
    
    # Set up startup and shutdown events
    @application.on_event("startup")
    async def startup():
        """Run on application startup."""
        await init_db()
        logger.info("Application started")
    
    @application.on_event("shutdown")
    async def shutdown():
        """Run on application shutdown."""
        await close_db()
        logger.info("Application shutdown complete")
    
    return application


app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

