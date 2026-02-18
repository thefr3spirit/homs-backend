"""
Customer model for guest information and balance tracking.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from database import Base
import uuid
import enum


class CustomerType(str, enum.Enum):
    """Customer type classification."""
    REGULAR = "regular"
    VIP = "vip"
    CORPORATE = "corporate"


class Customer(Base):
    """
    Customer/Guest model.
    Tracks customer information and pending balances.
    """
    __tablename__ = "customers"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Personal information
    full_name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=False, index=True)
    id_number = Column(String, nullable=True)  # National ID or passport
    address = Column(String, nullable=True)
    
    # Classification
    customer_type = Column(SQLEnum(CustomerType), default=CustomerType.REGULAR, nullable=False)
    
   # Financial tracking
    total_spent = Column(Float, default=0.0, nullable=False)  # Lifetime spending
    pending_balance = Column(Float, default=0.0, nullable=False)  # Amount owed
    total_visits = Column(Integer, default=0, nullable=False)
    
    # Notes
    notes = Column(String, nullable=True)  # Special requests, preferences, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Customer(name={self.full_name}, phone={self.phone}, pending={self.pending_balance})>"
