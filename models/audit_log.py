"""
Audit log model for tracking all system changes.
"""
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from database import Base
import uuid


class AuditLog(Base):
    """
    Audit log for tracking all changes made by users.
    Critical for accountability and troubleshooting.
    """
    __tablename__ = "audit_logs"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Who did what
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String, nullable=False)  # create, update, delete, login, etc.
    
    # What was changed
    entity_type = Column(String, nullable=False, index=True)  # booking, payment, customer, etc.
    entity_id = Column(String, nullable=False, index=True)
    
    # Change details
    changes = Column(JSON, nullable=True)  # {"field": {"old": "value1", "new": "value2"}}
    
    # Request metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return f"<AuditLog(user={self.user_id[:8]}, action={self.action}, entity={self.entity_type})>"
