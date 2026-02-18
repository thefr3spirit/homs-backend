"""
Room model for hotel room inventory.
"""
from sqlalchemy import Column, String, Integer, Float, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
from database import Base
import uuid
import enum


class RoomType(str, enum.Enum):
    """Room type classification."""
    STANDARD = "standard"
    DELUXE = "deluxe"
    SUITE = "suite"
    EXECUTIVE = "executive"


class RoomStatus(str, enum.Enum):
    """Room availability status."""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    RESERVED = "reserved"
    CLEANING = "cleaning"


class Room(Base):
    """
    Room model for inventory management.
    """
    __tablename__ = "rooms"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Room details
    room_number = Column(String, unique=True, nullable=False, index=True)
    room_type = Column(SQLEnum(RoomType), nullable=False)
    floor = Column(Integer, nullable=False)
    capacity = Column(Integer, default=2, nullable=False)  # Max guests
    
    # Pricing
    daily_rate = Column(Float, nullable=False)
    
    # Status
    status = Column(SQLEnum(RoomStatus), default=RoomStatus.AVAILABLE, nullable=False, index=True)
    
    # Description
    description = Column(String, nullable=True)
    amenities = Column(JSON, nullable=True)  # ["WiFi", "TV", "AC", "Mini Bar"]
    
    def __repr__(self):
        return f"<Room(number={self.room_number}, type={self.room_type}, status={self.status})>"
