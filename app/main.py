# app/main.py
"""Main application module."""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Query, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

from app.config import settings, logger
from app.database import init_db, close_db, get_session
from app.api.endpoints import logs, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting application...")
    await init_db()
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await close_db()


# Create FastAPI application
application = FastAPI(
    title="Phone Call Logger",
    description="API for logging and tracking phone calls",
    version="1.0.0",
    lifespan=lifespan
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:application",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

