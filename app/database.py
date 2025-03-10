# app/database.py
"""Database connection and session management."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings, logger
from app.models.base import Base


# Global variables to store engine and session factory
engine = None
async_session = None


async def init_db():
    """Initialize database connection and create tables if they don't exist."""
    global engine, async_session
    
    logger.info(f"Initializing database connection to {settings.db_url}")
    engine = create_async_engine(settings.db_url, echo=settings.debug)
    
    # Create tables
    async with engine.begin() as conn:
        logger.info("Creating database tables if they don't exist")
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    
    logger.info("Database initialization complete")
    return engine, async_session


async def close_db():
    """Close database connections."""
    if engine:
        logger.info("Closing database connections")
        await engine.dispose()


async def get_session() -> AsyncSession:
    """Dependency for getting a database session."""
    async with async_session() as session:
        yield session

