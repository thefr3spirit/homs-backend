"""
Customer management routes with balance tracking.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional
from datetime import datetime

from database import get_db
from models.user import User, UserRole
from models.customer import Customer
from models.booking import Booking
from schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    CustomerBalanceResponse, CustomerSearchResponse
)
from middleware.auth import get_current_user, require_role

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer_data: CustomerCreate,
    current_user: User = Depends(require_role(UserRole.OWNER, UserRole.RECEPTIONIST)),
    db: Session = Depends(get_db)
):
    """
    Create a new customer.
    Only accessible by OWNER and RECEPTIONIST.
    """
    # Check if customer with same phone already exists
    existing = db.query(Customer).filter(Customer.phone == customer_data.phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer with phone {customer_data.phone} already exists"
        )
    
    # Check email if provided
    if customer_data.email:
        existing_email = db.query(Customer).filter(Customer.email == customer_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer with email {customer_data.email} already exists"
            )
    
    customer = Customer(**customer_data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    return customer


@router.get("/", response_model=CustomerSearchResponse)
def list_customers(
    search: Optional[str] = Query(None, description="Search by name, phone, or email"),
    customer_type: Optional[str] = Query(None, description="Filter by customer type"),
    has_pending_balance: Optional[bool] = Query(None, description="Filter customers with pending balance"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List customers with search and filtering.
    All authenticated users can view customers.
    """
    query = db.query(Customer)
    
    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Customer.full_name.ilike(search_pattern),
                Customer.phone.ilike(search_pattern),
                Customer.email.ilike(search_pattern)
            )
        )
    
    # Filter by customer type
    if customer_type:
        query = query.filter(Customer.customer_type == customer_type)
    
    # Filter by pending balance
    if has_pending_balance is not None:
        if has_pending_balance:
            query = query.filter(Customer.pending_balance > 0)
        else:
            query = query.filter(Customer.pending_balance == 0)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    customers = query.order_by(Customer.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "customers": customers,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/pending-balances", response_model=list[CustomerBalanceResponse])
def list_pending_balances(
    min_balance: float = Query(0.01, description="Minimum balance to show"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all customers with pending balances.
    Useful for financial oversight and follow-up.
    """
    customers = db.query(Customer).filter(
        Customer.pending_balance >= min_balance
    ).order_by(Customer.pending_balance.desc()).all()
    
    results = []
    for customer in customers:
        # Get last booking date
        last_booking = db.query(Booking).filter(
            Booking.customer_id == customer.id
        ).order_by(Booking.created_at.desc()).first()
        
        results.append({
            "customer_id": customer.id,
            "full_name": customer.full_name,
            "pending_balance": customer.pending_balance,
            "total_spent": customer.total_spent,
            "last_booking_date": last_booking.created_at if last_booking else None
        })
    
    return results


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get customer details by ID.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return customer


@router.get("/{customer_id}/balance", response_model=CustomerBalanceResponse)
def get_customer_balance(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed balance information for a customer.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Get last booking
    last_booking = db.query(Booking).filter(
        Booking.customer_id == customer_id
    ).order_by(Booking.created_at.desc()).first()
    
    return {
        "customer_id": customer.id,
        "full_name": customer.full_name,
        "pending_balance": customer.pending_balance,
        "total_spent": customer.total_spent,
        "last_booking_date": last_booking.created_at if last_booking else None
    }


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: str,
    customer_data: CustomerUpdate,
    current_user: User = Depends(require_role(UserRole.OWNER, UserRole.RECEPTIONIST)),
    db: Session = Depends(get_db)
):
    """
    Update customer information.
    Only accessible by OWNER and RECEPTIONIST.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Check if updating phone to an existing one
    if customer_data.phone and customer_data.phone != customer.phone:
        existing = db.query(Customer).filter(
            Customer.phone == customer_data.phone,
            Customer.id != customer_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Another customer with phone {customer_data.phone} already exists"
            )
    
    # Check if updating email to an existing one
    if customer_data.email and customer_data.email != customer.email:
        existing_email = db.query(Customer).filter(
            Customer.email == customer_data.email,
            Customer.id != customer_id
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Another customer with email {customer_data.email} already exists"
            )
    
    # Update fields
    update_data = customer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    customer.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(customer)
    
    return customer


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: str,
    current_user: User = Depends(require_role(UserRole.OWNER)),
    db: Session = Depends(get_db)
):
    """
    Delete a customer (soft delete by archiving).
    Only accessible by OWNER.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Check if customer has pending balance
    if customer.pending_balance > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete customer with pending balance of {customer.pending_balance}"
        )
    
    # Check if customer has active bookings
    active_bookings = db.query(Booking).filter(
        Booking.customer_id == customer_id,
        Booking.booking_status.in_(["PENDING", "CONFIRMED", "CHECKED_IN"])
    ).count()
    
    if active_bookings > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete customer with {active_bookings} active booking(s)"
        )
    
    db.delete(customer)
    db.commit()
    
    return {"message": "Customer deleted successfully"}


@router.get("/{customer_id}/bookings")
def get_customer_bookings(
    customer_id: str,
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get customer's booking history.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    bookings = db.query(Booking).filter(
        Booking.customer_id == customer_id
    ).order_by(Booking.created_at.desc()).limit(limit).all()
    
    return bookings
