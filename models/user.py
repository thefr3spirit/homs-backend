"""
User model for authentication and authorization.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from database import Base
import uuid
import enum


class UserRole(str, enum.Enum):
    """User role enumeration."""
    OWNER = "owner"
    RECEPTIONIST = "receptionist"
    ADMIN = "admin"


class User(Base):
    """
    User model for system authentication.
    Tracks who performs actions for audit purposes.
    """
    __tablename__ = "users"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Authentication
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    
    # Profile
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    
    # Authorization
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.RECEPTIONIST)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<User(email={self.email}, role={self.role}, active={self.is_active})>"
