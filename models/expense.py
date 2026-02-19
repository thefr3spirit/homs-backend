"""
Expense model for tracking hotel expenses.
"""
from sqlalchemy import Column, String, Float, Date, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from database import Base
import uuid
import enum


class ExpenseCategory(str, enum.Enum):
    """Expense categorization."""
    UTILITIES = "utilities"
    SALARY = "salary"
    SUPPLIES = "supplies"
    MAINTENANCE = "maintenance"
    MARKETING = "marketing"
    FOOD = "food"
    CLEANING = "cleaning"
    OTHER = "other"


class ExpenseStatus(str, enum.Enum):
    """Expense approval status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Expense(Base):
    """
    Expense model for daily operational costs.
    Tracks who recorded and who approved expenses.
    """
    __tablename__ = "expenses"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    recorded_by = Column(String, ForeignKey("users.id"), nullable=False)  # Who recorded the expense
    approved_by = Column(String, ForeignKey("users.id"), nullable=True)  # Who approved (owner/admin)
    
    # Expense details
    category = Column(SQLEnum(ExpenseCategory), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    vendor_name = Column(String, nullable=True)
    
    # Date
    expense_date = Column(Date, nullable=False, index=True)
    
    # Receipt
    receipt_url = Column(String, nullable=True)  # URL to receipt image/PDF
    
    # Status
    status = Column(SQLEnum(ExpenseStatus), default=ExpenseStatus.PENDING, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Expense(category={self.category}, amount={self.amount}, recorded_by={self.recorded_by[:8]})>"
