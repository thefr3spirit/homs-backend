"""
Booking management routes with receptionist tracking.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime

from database import get_db
from models.user import User, UserRole
from models.booking import Booking, BookingStatus
from models.room import Room, RoomStatus
from models.customer import Customer
from schemas.booking import (
    BookingCreate, BookingUpdate, BookingResponse,
    CheckInRequest, CheckOutRequest, BookingSearchResponse
)
from middleware.auth import get_current_user, require_role

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(require_role(UserRole.OWNER, UserRole.RECEPTIONIST)),
    db: Session = Depends(get_db)
):
    """
    Create a new booking.
    Automatically tracks which receptionist created it.
    Only accessible by OWNER and RECEPTIONIST.
    """
    # Validate customer exists
    customer = db.query(Customer).filter(Customer.id == booking_data.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Validate room exists
    room = db.query(Room).filter(Room.id == booking_data.room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Check date validity
    if booking_data.check_out_date <= booking_data.check_in_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out date must be after check-in date"
        )
    
    # Check room availability for the dates
    conflicting_bookings = db.query(Booking).filter(
        Booking.room_id == booking_data.room_id,
        Booking.booking_status.in_([
            BookingStatus.CONFIRMED,
            BookingStatus.CHECKED_IN,
            BookingStatus.PENDING
        ]),
        Booking.check_in_date < booking_data.check_out_date,
        Booking.check_out_date > booking_data.check_in_date
    ).count()
    
    if conflicting_bookings > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Room {room.room_number} is not available for the selected dates"
        )
    
    # Create booking
    booking = Booking(
        **booking_data.model_dump(),
        created_by=current_user.id,  # ← Track who created it
        booking_status=BookingStatus.CONFIRMED
    )
    
    # Update room status if check-in is today or in the past
    if booking_data.check_in_date <= date.today():
        room.status = RoomStatus.RESERVED
    
    # Update customer stats
    customer.total_visits += 1
    
    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    return booking


@router.get("/", response_model=BookingSearchResponse)
def list_bookings(
    status: Optional[BookingStatus] = Query(None, description="Filter by booking status"),
    customer_id: Optional[str] = Query(None, description="Filter by customer"),
    room_id: Optional[str] = Query(None, description="Filter by room"),
    check_in_date: Optional[date] = Query(None, description="Filter by check-in date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List bookings with filtering and pagination.
    All authenticated users can view bookings.
    """
    query = db.query(Booking)
    
    if status:
        query = query.filter(Booking.booking_status == status)
    
    if customer_id:
        query = query.filter(Booking.customer_id == customer_id)
    
    if room_id:
        query = query.filter(Booking.room_id == room_id)
    
    if check_in_date:
        query = query.filter(Booking.check_in_date == check_in_date)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    bookings = query.order_by(Booking.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "bookings": bookings,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/today")
def get_today_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get today's check-ins and check-outs.
    """
    today = date.today()
    
    check_ins = db.query(Booking).filter(
        Booking.check_in_date == today,
        Booking.booking_status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING])
    ).all()
    
    check_outs = db.query(Booking).filter(
        Booking.check_out_date == today,
        Booking.booking_status == BookingStatus.CHECKED_IN
    ).all()
    
    return {
        "check_ins": check_ins,
        "check_outs": check_outs,
        "total_check_ins": len(check_ins),
        "total_check_outs": len(check_outs)
    }


@router.get("/upcoming")
def get_upcoming_bookings(
    days: int = Query(7, ge=1, le=30, description="Number of days ahead to look"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get upcoming bookings within specified days.
    """
    from datetime import timedelta
    
    today = date.today()
    end_date = today + timedelta(days=days)
    
    bookings = db.query(Booking).filter(
        Booking.check_in_date >= today,
        Booking.check_in_date <= end_date,
        Booking.booking_status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING])
    ).order_by(Booking.check_in_date).all()
    
    return bookings


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get booking details by ID.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    return booking


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: str,
    booking_data: BookingUpdate,
    current_user: User = Depends(require_role(UserRole.OWNER, UserRole.RECEPTIONIST)),
    db: Session = Depends(get_db)
):
    """
    Update booking information.
    Only accessible by OWNER and RECEPTIONIST.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Cannot update checked-out bookings
    if booking.booking_status == BookingStatus.CHECKED_OUT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update checked-out booking"
        )
    
    # Validate date changes if provided
    check_in = booking_data.check_in_date or booking.check_in_date
    check_out = booking_data.check_out_date or booking.check_out_date
    
    if check_out <= check_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out date must be after check-in date"
        )
    
    # Update fields
    update_data = booking_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(booking, field, value)
    
    booking.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(booking)
    
    return booking


@router.post("/{booking_id}/checkin", response_model=BookingResponse)
def checkin_guest(
    booking_id: str,
    checkin_data: CheckInRequest,
    current_user: User = Depends(require_role(UserRole.OWNER, UserRole.RECEPTIONIST)),
    db: Session = Depends(get_db)
):
    """
    Check in a guest.
    Automatically tracks which receptionist performed the check-in.
    Only accessible by OWNER and RECEPTIONIST.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Validate booking status
    if booking.booking_status == BookingStatus.CHECKED_IN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guest is already checked in"
        )
    
    if booking.booking_status == BookingStatus.CHECKED_OUT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot check in a checked-out booking"
        )
    
    if booking.booking_status == BookingStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot check in a cancelled booking"
        )
    
    # Update booking
    booking.booking_status = BookingStatus.CHECKED_IN
    booking.actual_checkin = datetime.utcnow()
    booking.checked_in_by = current_user.id  # ← Track who checked in the guest
    
    if checkin_data.notes:
        booking.notes = f"{booking.notes or ''}\n[Check-in by {current_user.full_name}]: {checkin_data.notes}".strip()
    
    # Update room status
    room = db.query(Room).filter(Room.id == booking.room_id).first()
    if room:
        room.status = RoomStatus.OCCUPIED
    
    db.commit()
    db.refresh(booking)
    
    return booking


@router.post("/{booking_id}/checkout", response_model=BookingResponse)
def checkout_guest(
    booking_id: str,
    checkout_data: CheckOutRequest,
    current_user: User = Depends(require_role(UserRole.OWNER, UserRole.RECEPTIONIST)),
    db: Session = Depends(get_db)
):
    """
    Check out a guest.
    Automatically tracks which receptionist performed the check-out.
    Only accessible by OWNER and RECEPTIONIST.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Validate booking status
    if booking.booking_status != BookingStatus.CHECKED_IN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guest must be checked in before checking out"
        )
    
    # Update booking
    booking.booking_status = BookingStatus.CHECKED_OUT
    booking.actual_checkout = datetime.utcnow()
    booking.checked_out_by = current_user.id  # ← Track who checked out the guest
    
    # Add additional charges if any
    if checkout_data.additional_charges > 0:
        booking.total_amount += checkout_data.additional_charges
    
    if checkout_data.notes:
        booking.notes = f"{booking.notes or ''}\n[Check-out by {current_user.full_name}]: {checkout_data.notes}".strip()
    
    # Update room status
    room = db.query(Room).filter(Room.id == booking.room_id).first()
    if room:
        room.status = RoomStatus.CLEANING
    
    # Update customer pending balance
    balance_due = booking.total_amount - booking.amount_paid
    if balance_due > 0:
        customer = db.query(Customer).filter(Customer.id == booking.customer_id).first()
        if customer:
            customer.pending_balance += balance_due
    
    db.commit()
    db.refresh(booking)
    
    return booking


@router.post("/{booking_id}/cancel")
def cancel_booking(
    booking_id: str,
    reason: Optional[str] = Query(None, description="Cancellation reason"),
    current_user: User = Depends(require_role(UserRole.OWNER, UserRole.RECEPTIONIST)),
    db: Session = Depends(get_db)
):
    """
    Cancel a booking.
    Only accessible by OWNER and RECEPTIONIST.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Cannot cancel checked-in or checked-out bookings
    if booking.booking_status in [BookingStatus.CHECKED_IN, BookingStatus.CHECKED_OUT]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel {booking.booking_status.value} booking"
        )
    
    # Update booking
    booking.booking_status = BookingStatus.CANCELLED
    booking.updated_at = datetime.utcnow()
    
    if reason:
        booking.notes = f"{booking.notes or ''}\n[Cancelled by {current_user.full_name}]: {reason}".strip()
    
    # Free up the room
    room = db.query(Room).filter(Room.id == booking.room_id).first()
    if room and room.status == RoomStatus.RESERVED:
        room.status = RoomStatus.AVAILABLE
    
    # Refund any deposits to customer
    if booking.amount_paid > 0:
        customer = db.query(Customer).filter(Customer.id == booking.customer_id).first()
        if customer:
            customer.pending_balance -= booking.amount_paid  # Credit back
    
    db.commit()
    
    return {"message": "Booking cancelled successfully", "booking_id": booking_id}
