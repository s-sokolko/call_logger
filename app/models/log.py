# app/models/log.py
"""Log entry model for storing raw request logs."""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Text

from app.models.base import Base


class LogEntry(Base):
    """Model for storing raw event logs."""
    
    __tablename__ = 'logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    received = Column(DateTime, default=datetime.now)
    url = Column(Text)
    
    def __repr__(self):
        return f"<LogEntry(id={self.id}, received={self.received})>"
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "received": self.received.isoformat() if self.received else None,
            "url": self.url
        }

