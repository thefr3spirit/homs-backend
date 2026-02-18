"""
Booking model for reservations and check-ins.
"""
from sqlalchemy import Column, String, Integer, Float, Date, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid
import enum


class BookingStatus(str, enum.Enum):
    """Booking status lifecycle."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class Booking(Base):
    """
    Booking/Reservation model.
    Tracks which receptionist handled the booking.
    """
    __tablename__ = "bookings"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False, index=True)
    room_id = Column(String, ForeignKey("rooms.id"), nullable=False, index=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)  # Receptionist who created booking
    checked_in_by = Column(String, ForeignKey("users.id"), nullable=True)  # Receptionist who checked in
    checked_out_by = Column(String, ForeignKey("users.id"), nullable=True)  # Receptionist who checked out
    
    # Dates
    check_in_date = Column(Date, nullable=False, index=True)
    check_out_date = Column(Date, nullable=False)
    actual_checkin = Column(DateTime(timezone=True), nullable=True)
    actual_checkout = Column(DateTime(timezone=True), nullable=True)
    
    # Booking details
    num_guests = Column(Integer, default=1, nullable=False)
    total_amount = Column(Float, nullable=False)  # Total expected amount
    amount_paid = Column(Float, default=0.0, nullable=False)  # Total paid so far
    
    # Status
    booking_status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False, index=True)
    
    # Notes
    special_requests = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Booking(id={self.id[:8]}, customer={self.customer_id[:8]}, room={self.room_id[:8]}, status={self.booking_status})>"
    
    @property
    def balance_due(self):
        """Calculate remaining balance."""
        return self.total_amount - self.amount_paid
