# app/api/endpoints/reports.py
"""Endpoints for retrieving call reports and statistics."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.api.deps import get_session
from app.models import Call

router = APIRouter()


@router.get("/calls")
async def get_call_reports(session: AsyncSession = Depends(get_session)):
    """
    Endpoint to get call reports.
    
    Args:
        session: Database session
        
    Returns:
        List of recent calls
    """
    result = await session.execute(
        select(Call).order_by(Call.started.desc()).limit(100)
    )
    calls = result.scalars().all()
    
    # Convert SQLAlchemy objects to dictionaries
    calls_list = [call.to_dict() for call in calls]
    
    return {"calls": calls_list}


@router.get("/stats")
async def get_call_statistics(session: AsyncSession = Depends(get_session)):
    """
    Endpoint to get call statistics.
    
    Args:
        session: Database session
        
    Returns:
        Dictionary with various call statistics
    """
    # Get total calls by direction
    direction_result = await session.execute(
        select(
            Call.direction,
            func.count().label('count'),
            func.avg(Call.total_duration).label('avg_duration'),
            func.sum(Call.total_duration).label('total_duration')
        ).group_by(Call.direction)
    )
    direction_stats = []
    for row in direction_result:
        direction_stats.append({
            "direction": row[0],
            "count": row[1],
            "avg_duration": float(row[2]) if row[2] is not None else 0,
            "total_duration": row[3] if row[3] is not None else 0
        })
    
    # Get calls by status
    status_result = await session.execute(
        select(
            Call.status,
            func.count().label('count')
        ).group_by(Call.status)
    )
    status_stats = [{"status": row[0], "count": row[1]} for row in status_result]
    
    # Get calls by phone
    phone_result = await session.execute(
        select(
            Call.phone_mac,
            func.count().label('count')
        ).group_by(Call.phone_mac)
    )
    phone_stats = [{"phone_mac": row[0], "count": row[1]} for row in phone_result]
    
    return {
        "by_direction": direction_stats,
        "by_status": status_stats,
        "by_phone": phone_stats
    }

