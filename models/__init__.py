"""
SQLAlchemy models for Lemi Hotel Management System.
"""
from sqlalchemy import Column, String, Integer, Float, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base
import uuid

# Import all models
from models.user import User, UserRole
from models.customer import Customer, CustomerType
from models.customer_balance import CustomerBalance
from models.room import Room, RoomType, RoomStatus
from models.booking import Booking, BookingStatus
from models.payment import Payment, PaymentMethod, PaymentType, PaymentStatus
from models.expense import Expense, ExpenseCategory, ExpenseStatus
from models.audit_log import AuditLog


class DailySummary(Base):
    """
    Model representing daily hotel summary data.
    Stores operational metrics submitted by the desktop counter app.
    KEPT FOR BACKWARD COMPATIBILITY with existing Gift's counter app.
    """
    __tablename__ = "daily_summaries"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Date of the summary
    date = Column(Date, nullable=False, unique=True, index=True)
    
    # Room statistics
    rooms_total = Column(Integer, nullable=False)
    rooms_occupied = Column(Integer, nullable=False)
    rooms_available = Column(Integer, nullable=False)
    
    # Financial data (in local currency)
    cash_collected = Column(Float, nullable=False, default=0.0)
    momo_collected = Column(Float, nullable=False, default=0.0)
    cheque_collected = Column(Float, nullable=False, default=0.0)
    total_collected = Column(Float, nullable=False, default=0.0)
    expected_balance = Column(Float, nullable=False, default=0.0)
    expenses_logged = Column(Float, nullable=False, default=0.0)
    
    # User tracking (who submitted/updated summary)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    updated_by = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Timestamp tracking
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<DailySummary(date={self.date}, total_collected={self.total_collected})>"


# Export all models
__all__ = [
    "User",
    "UserRole",
    "Customer",
    "CustomerType",
    "Room",
    "RoomType",
    "RoomStatus",
    "Booking",
    "BookingStatus",
    "Payment",
    "PaymentMethod",
    "PaymentType",
    "PaymentStatus",
    "Expense",
    "ExpenseCategory",
    "ExpenseStatus",
    "AuditLog",
    "DailySummary",
]
