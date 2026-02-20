"""
Pydantic schemas for customer balance data validation and serialization.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CustomerBalanceBase(BaseModel):
    """Base schema for customer balance."""
    customer_id: str
    customer_name: str
    phone: str
    balance_amount: float = Field(gt=0, description="Outstanding balance amount (must be > 0)")


class CustomerBalanceCreate(CustomerBalanceBase):
    """Schema for creating a new balance record."""
    pass


class CustomerBalanceUpdate(BaseModel):
    """Schema for updating balance amount."""
    balance_amount: float = Field(ge=0, description="New balance amount (0 = paid in full)")


class CustomerBalanceResponse(CustomerBalanceBase):
    """Schema for customer balance response."""
    id: int
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerBalanceSummary(BaseModel):
    """Summary of all pending balances."""
    customer_count: int = Field(description="Number of customers with pending balance")
    total_pending: float = Field(description="Total amount outstanding across all customers")
