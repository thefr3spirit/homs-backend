"""
Room management routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime

from database import get_db
from models.user import User, UserRole
from models.room import Room, RoomStatus, RoomType
from models.booking import Booking, BookingStatus
from schemas.room import (
    RoomCreate, RoomUpdate, RoomStatusUpdate,
    RoomResponse, RoomAvailabilityResponse
)
from middleware.auth import get_current_user, require_role

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
    room_data: RoomCreate,
    current_user: User = Depends(require_role(UserRole.OWNER)),
    db: Session = Depends(get_db)
):
    """
    Create a new room.
    Only accessible by OWNER.
    """
    # Check if room number already exists
    existing = db.query(Room).filter(Room.room_number == room_data.room_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Room {room_data.room_number} already exists"
        )
    
    room = Room(**room_data.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    
    return room


@router.get("/", response_model=list[RoomResponse])
def list_rooms(
    status: Optional[RoomStatus] = Query(None, description="Filter by room status"),
    room_type: Optional[RoomType] = Query(None, description="Filter by room type"),
    floor: Optional[int] = Query(None, description="Filter by floor"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all rooms with optional filters.
    All authenticated users can view rooms.
    """
    query = db.query(Room)
    
    if status:
        query = query.filter(Room.status == status)
    
    if room_type:
        query = query.filter(Room.room_type == room_type)
    
    if floor is not None:
        query = query.filter(Room.floor == floor)
    
    rooms = query.order_by(Room.room_number).all()
    
    return rooms


@router.get("/available", response_model=list[RoomAvailabilityResponse])
def get_available_rooms(
    check_in: Optional[date] = Query(None, description="Check-in date"),
    check_out: Optional[date] = Query(None, description="Check-out date"),
    room_type: Optional[RoomType] = Query(None, description="Filter by room type"),
    min_capacity: Optional[int] = Query(None, description="Minimum guest capacity"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get available rooms for booking.
    If dates provided, checks booking conflicts. Otherwise, returns rooms with AVAILABLE status.
    """
    query = db.query(Room)
    
    # Apply filters
    if room_type:
        query = query.filter(Room.room_type == room_type)
    
    if min_capacity:
        query = query.filter(Room.capacity >= min_capacity)
    
    rooms = query.all()
    
    available_rooms = []
    for room in rooms:
        is_available = True
        
        # If dates provided, check for booking conflicts
        if check_in and check_out:
            # Check if room has any bookings that overlap with requested dates
            conflicting_bookings = db.query(Booking).filter(
                Booking.room_id == room.id,
                Booking.booking_status.in_([
                    BookingStatus.CONFIRMED,
                    BookingStatus.CHECKED_IN,
                    BookingStatus.PENDING
                ]),
                Booking.check_in_date < check_out,
                Booking.check_out_date > check_in
            ).count()
            
            is_available = conflicting_bookings == 0 and room.status in [RoomStatus.AVAILABLE, RoomStatus.RESERVED]
        else:
            # Just check current status
            is_available = room.status == RoomStatus.AVAILABLE
        
        available_rooms.append({
            "room_id": room.id,
            "room_number": room.room_number,
            "room_type": room.room_type,
            "daily_rate": room.daily_rate,
            "capacity": room.capacity,
            "is_available": is_available,
            "current_status": room.status
        })
    
    # Filter to only available if requested
    return [r for r in available_rooms if r["is_available"]]


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(
    room_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get room details by ID.
    """
    room = db.query(Room).filter(Room.id == room_id).first()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    return room


@router.put("/{room_id}", response_model=RoomResponse)
def update_room(
    room_id: str,
    room_data: RoomUpdate,
    current_user: User = Depends(require_role(UserRole.OWNER)),
    db: Session = Depends(get_db)
):
    """
    Update room information.
    Only accessible by OWNER.
    """
    room = db.query(Room).filter(Room.id == room_id).first()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Check if updating room number to an existing one
    if room_data.room_number and room_data.room_number != room.room_number:
        existing = db.query(Room).filter(
            Room.room_number == room_data.room_number,
            Room.id != room_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Room {room_data.room_number} already exists"
            )
    
    # Update fields
    update_data = room_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(room, field, value)
    
    db.commit()
    db.refresh(room)
    
    return room


@router.patch("/{room_id}/status", response_model=RoomResponse)
def update_room_status(
    room_id: str,
    status_data: RoomStatusUpdate,
    current_user: User = Depends(require_role(UserRole.OWNER, UserRole.RECEPTIONIST)),
    db: Session = Depends(get_db)
):
    """
    Update room status only (for maintenance, cleaning, etc.).
    Accessible by OWNER and RECEPTIONIST.
    """
    room = db.query(Room).filter(Room.id == room_id).first()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Check if room has active bookings before changing to maintenance/cleaning
    if status_data.status in [RoomStatus.MAINTENANCE, RoomStatus.CLEANING]:
        active_bookings = db.query(Booking).filter(
            Booking.room_id == room_id,
            Booking.booking_status == BookingStatus.CHECKED_IN
        ).count()
        
        if active_bookings > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot change status: room has {active_bookings} active guest(s)"
            )
    
    room.status = status_data.status
    db.commit()
    db.refresh(room)
    
    return room


@router.delete("/{room_id}")
def delete_room(
    room_id: str,
    current_user: User = Depends(require_role(UserRole.OWNER)),
    db: Session = Depends(get_db)
):
    """
    Delete a room.
    Only accessible by OWNER.
    """
    room = db.query(Room).filter(Room.id == room_id).first()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Check if room has any bookings
    bookings_count = db.query(Booking).filter(Booking.room_id == room_id).count()
    
    if bookings_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete room with {bookings_count} booking(s) in history"
        )
    
    db.delete(room)
    db.commit()
    
    return {"message": f"Room {room.room_number} deleted successfully"}
