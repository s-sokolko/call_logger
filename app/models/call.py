# app/models/call.py
"""Call model for storing call statistics."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.mutable import MutableList

from app.models.base import Base


class Call(Base):
    """Model for storing call information."""
    
    __tablename__ = 'calls'
    
    call_id = Column(String, primary_key=True)
    from_number = Column(String)
    to_number = Column(String)
    phone_mac = Column(String)
    started = Column(DateTime, default=datetime.now)
    finished = Column(DateTime, nullable=True)
    direction = Column(String)
    status = Column(String, default='in_progress')
    total_duration = Column(Integer, nullable=True)
    transfers = Column(MutableList.as_mutable(JSON), default=list)
    
    def __repr__(self):
        return f"<Call(call_id={self.call_id}, direction={self.direction}, status={self.status})>"
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "call_id": self.call_id,
            "from_number": self.from_number,
            "to_number": self.to_number,
            "phone_mac": self.phone_mac,
            "started": self.started.isoformat() if self.started else None,
            "finished": self.finished.isoformat() if self.finished else None,
            "direction": self.direction,
            "status": self.status,
            "total_duration": self.total_duration,
            "transfers": self.transfers
        }