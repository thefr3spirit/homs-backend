"""
Payment model for tracking all financial transactions.
"""
from sqlalchemy import Column, String, Float, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from database import Base
import uuid
import enum


class PaymentMethod(str, enum.Enum):
    """Payment method options."""
    CASH = "cash"
    MOMO = "momo"
    CHEQUE = "cheque"
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"


class PaymentType(str, enum.Enum):
    """Payment type classification."""
    DEPOSIT = "deposit"
    PARTIAL = "partial"
    FULL = "full"
    REFUND = "refund"


class PaymentStatus(str, enum.Enum):
    """Payment status."""
    PENDING = "pending"
    COMPLETED = "completed"
    REFUNDED = "refunded"
    FAILED = "failed"


class Payment(Base):
    """
    Payment model with full receptionist tracking.
    Critical for audit trail and accountability.
    """
    __tablename__ = "payments"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    booking_id = Column(String, ForeignKey("bookings.id"), nullable=False, index=True)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False, index=True)
    received_by = Column(String, ForeignKey("users.id"), nullable=False)  # Which receptionist received payment
    
    # Payment details
    amount = Column(Float, nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    payment_type = Column(SQLEnum(PaymentType), nullable=False)
    
    # Transaction tracking
    transaction_ref = Column(String, nullable=True)  # Reference number for momo/card/cheque
    payment_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Status
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.COMPLETED, nullable=False)
    
    # Notes
    notes = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Payment(amount={self.amount}, method={self.payment_method}, received_by={self.received_by[:8]})>"
