"""
Pydantic schemas for Payment operations.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.payment import PaymentMethod, PaymentType, PaymentStatus


class PaymentBase(BaseModel):
    """Base payment schema with common fields."""
    booking_id: str
    customer_id: str
    amount: float
    payment_method: PaymentMethod
    payment_type: PaymentType
    transaction_ref: Optional[str] = None
    notes: Optional[str] = None


class PaymentCreate(PaymentBase):
    """Schema for creating a new payment."""
    pass


class PaymentResponse(PaymentBase):
    """Schema for payment response."""
    id: str
    received_by: str
    payment_date: datetime
    status: PaymentStatus
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentSummary(BaseModel):
    """Schema for payment summary statistics."""
    total_payments: int
    total_amount: float
    by_method: dict[str, float]
    by_status: dict[str, int]


class PaymentSearchResponse(BaseModel):
    """Schema for payment search results."""
    payments: list[PaymentResponse]
    total: int
    page: int
    page_size: int
    total_amount: float
