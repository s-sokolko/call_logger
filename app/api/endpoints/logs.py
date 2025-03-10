# app/api/endpoints/logs.py
"""Endpoints for logging phone events."""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.models import LogEntry
from app.config import logger
from app.services.call_processor import process_event

router = APIRouter()


@router.get("/log")
async def log_event(request: Request, session: AsyncSession = Depends(get_session)):
    """
    Endpoint to receive phone action URL callbacks.
    
    Args:
        request: FastAPI request object
        session: Database session
        
    Returns:
        JSON response with status
    """
    # Get full URL including query parameters
    full_url = str(request.url)
    
    # Log the request
    query_params = dict(request.query_params)
    logger.info(f"Received action URL: {full_url}")
    logger.info(f"Query parameters: {query_params}")
    
    # Store the raw request in logs table
    log_entry = LogEntry(url=full_url)
    session.add(log_entry)
    await session.commit()
    
    # Process the event to update calls table
    await process_event(query_params, session)
    
    return {"status": "success", "message": "Event logged"}

