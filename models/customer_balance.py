"""
Customer Balance model for tracking outstanding payments.
Separate table for quick balance queries for mobile app.
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.sql import func
from database import Base
import uuid


class CustomerBalance(Base):
    """
    CustomerBalance model - tracks customers with outstanding balances.
    This table is automatically populated/updated by the PWA when:
    - A booking is created with partial payment
    - A payment is received
    - Balance is cleared (record deleted)
    """
    __tablename__ = "customer_balance"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Customer reference (unique - one balance record per customer)
    customer_id = Column(String, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Denormalized customer data for quick mobile app queries
    customer_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    
    # Balance information
    balance_amount = Column(Float, nullable=False, index=True)
    
    # User tracking - who created/updated this balance
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    created_by_name = Column(String, nullable=True)
    updated_by = Column(String, ForeignKey("users.id"), nullable=True)
    updated_by_name = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<CustomerBalance(customer={self.customer_name}, balance={self.balance_amount})>"
