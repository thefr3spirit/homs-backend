"""
Booking management routes with receptionist tracking.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
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


def recalculate_customer_pending_balance(customer_id: str, db: Session) -> None:
    """
    Recalculate customer's pending balance as the sum of all balance_due
    from their bookings.
    
    This should be called after:
    - Creating a booking
    - Recording a payment
    - Checking out a booking
    - Canceling a booking
    """
    # Calculate total pending balance from all bookings
    # balance_due = total_amount - amount_paid for each booking
    total_pending = db.query(
        func.coalesce(
            func.sum(Booking.total_amount - Booking.amount_paid),
            0.0
        )
    ).filter(
        Booking.customer_id == customer_id,
        Booking.booking_status.in_([
            BookingStatus.PENDING,
            BookingStatus.CONFIRMED,
            BookingStatus.CHECKED_IN,
            BookingStatus.CHECKED_OUT
        ]),
        (Booking.total_amount - Booking.amount_paid) > 0.01  # Only include bookings with balance > 0
    ).scalar() or 0.0
    
    # Update customer's pending balance
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer:
        customer.pending_balance = float(total_pending)


def add_user_names_to_booking(booking: Booking, db: Session) -> Booking:
    """Helper function to add user names to a booking object."""
    if booking.created_by:
        creator = db.query(User).filter(User.id == booking.created_by).first()
        booking.created_by_name = creator.full_name if creator else None
    
    if booking.checked_in_by:
        checker_in = db.query(User).filter(User.id == booking.checked_in_by).first()
        booking.checked_in_by_name = checker_in.full_name if checker_in else None
    
    if booking.checked_out_by:
        checker_out = db.query(User).filter(User.id == booking.checked_out_by).first()
        booking.checked_out_by_name = checker_out.full_name if checker_out else None
    
    return booking


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
    
    # Recalculate customer's pending balance
    recalculate_customer_pending_balance(customer.id, db)
    db.commit()
    
    # Add user names
    booking = add_user_names_to_booking(booking, db)
    
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
    
    # Add user names to each booking
    for booking in bookings:
        add_user_names_to_booking(booking, db)
    
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
    
    # Add user names
    booking = add_user_names_to_booking(booking, db)
    
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
    
    # Recalculate customer's pending balance
    recalculate_customer_pending_balance(booking.customer_id, db)
    
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
    
    # Recalculate customer's pending balance (cancelled bookings won't count)
    recalculate_customer_pending_balance(booking.customer_id, db)
    
    db.commit()
    
    return {"message": "Booking cancelled successfully", "booking_id": booking_id}
