"""
Pydantic schemas for Customer operations.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from models.customer import CustomerType


class CustomerBase(BaseModel):
    """Base customer schema with common fields."""
    full_name: str
    email: Optional[EmailStr] = None
    phone: str
    id_number: Optional[str] = None
    address: Optional[str] = None
    customer_type: CustomerType = CustomerType.REGULAR
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    """Schema for creating a new customer."""
    pass


class CustomerUpdate(BaseModel):
    """Schema for updating customer information."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    id_number: Optional[str] = None
    address: Optional[str] = None
    customer_type: Optional[CustomerType] = None
    notes: Optional[str] = None


class CustomerResponse(CustomerBase):
    """Schema for customer response."""
    id: str
    pending_balance: float
    total_spent: float
    total_visits: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CustomerBalanceResponse(BaseModel):
    """Schema for customer balance information."""
    customer_id: str
    full_name: str
    pending_balance: float
    total_spent: float
    last_booking_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerSearchResponse(BaseModel):
    """Schema for customer search results."""
    customers: list[CustomerResponse]
    total: int
    page: int
    page_size: int
