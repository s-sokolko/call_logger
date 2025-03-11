# app/api/deps.py
"""Dependency injection for API endpoints."""
from app.database import get_session

# Re-export dependencies
__all__ = ['get_session']
