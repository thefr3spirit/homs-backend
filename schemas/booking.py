"""
Pydantic schemas for Booking operations.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from models.booking import BookingStatus


class BookingBase(BaseModel):
    """Base booking schema with common fields."""
    customer_id: str
    room_id: str
    check_in_date: date
    check_out_date: date
    num_guests: int
    special_requests: Optional[str] = None
    notes: Optional[str] = None


class BookingCreate(BookingBase):
    """Schema for creating a new booking."""
    total_amount: float
    amount_paid: float = 0.0


class BookingUpdate(BaseModel):
    """Schema for updating booking information."""
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    num_guests: Optional[int] = None
    total_amount: Optional[float] = None
    special_requests: Optional[str] = None
    notes: Optional[str] = None


class BookingResponse(BookingBase):
    """Schema for booking response."""
    id: str
    created_by: str
    checked_in_by: Optional[str]
    checked_out_by: Optional[str]
    actual_checkin: Optional[datetime]
    actual_checkout: Optional[datetime]
    total_amount: float
    amount_paid: float
    booking_status: BookingStatus
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Computed field
    balance_due: float

    class Config:
        from_attributes = True


class CheckInRequest(BaseModel):
    """Schema for check-in operation."""
    notes: Optional[str] = None


class CheckOutRequest(BaseModel):
    """Schema for check-out operation."""
    notes: Optional[str] = None
    additional_charges: float = 0.0


class BookingSearchResponse(BaseModel):
    """Schema for booking search results."""
    bookings: list[BookingResponse]
    total: int
    page: int
    page_size: int
