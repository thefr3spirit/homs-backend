"""
Pydantic schemas for request validation and response serialization.
"""
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional


class DailySummaryCreate(BaseModel):
    """Schema for creating a new daily summary."""
    date: date
    rooms_total: int
    rooms_occupied: int
    rooms_available: int
    cash_collected: float
    momo_collected: float
    total_collected: float
    expected_balance: float
    expenses_logged: float


class DailySummaryResponse(BaseModel):
    """Schema for returning daily summary data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    date: date
    rooms_total: int
    rooms_occupied: int
    rooms_available: int
    cash_collected: float
    momo_collected: float
    total_collected: float
    expected_balance: float
    expenses_logged: float
    last_updated: datetime


class DailySummaryUpdate(BaseModel):
    """Schema for updating an existing daily summary (partial update)."""
    rooms_total: Optional[int] = None
    rooms_occupied: Optional[int] = None
    rooms_available: Optional[int] = None
    cash_collected: Optional[float] = None
    momo_collected: Optional[float] = None
    total_collected: Optional[float] = None
    expected_balance: Optional[float] = None
    expenses_logged: Optional[float] = None


class MessageResponse(BaseModel):
    """Generic message response schema."""
    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: Optional[str] = None
