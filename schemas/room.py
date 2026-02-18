"""
Pydantic schemas for Room operations.
"""
from pydantic import BaseModel
from typing import Optional
from models.room import RoomType, RoomStatus


class RoomBase(BaseModel):
    """Base room schema with common fields."""
    room_number: str
    room_type: RoomType
    floor: int
    capacity: int
    daily_rate: float
    description: Optional[str] = None
    amenities: Optional[dict] = None


class RoomCreate(RoomBase):
    """Schema for creating a new room."""
    pass


class RoomUpdate(BaseModel):
    """Schema for updating room information."""
    room_number: Optional[str] = None
    room_type: Optional[RoomType] = None
    floor: Optional[int] = None
    capacity: Optional[int] = None
    daily_rate: Optional[float] = None
    status: Optional[RoomStatus] = None
    description: Optional[str] = None
    amenities: Optional[dict] = None


class RoomStatusUpdate(BaseModel):
    """Schema for updating room status only."""
    status: RoomStatus


class RoomResponse(RoomBase):
    """Schema for room response."""
    id: str
    status: RoomStatus

    class Config:
        from_attributes = True


class RoomAvailabilityResponse(BaseModel):
    """Schema for room availability check."""
    room_id: str
    room_number: str
    room_type: RoomType
    daily_rate: float
    capacity: int
    is_available: bool
    current_status: RoomStatus

    class Config:
        from_attributes = True
