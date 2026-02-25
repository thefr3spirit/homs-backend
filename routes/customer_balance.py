"""
Customer balance tracking routes for mobile app.
Updated to query directly from customers table instead of customer_balance table.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from database import get_db
from models.user import User
from models.customer import Customer
from schemas.customer import CustomerResponse
from middleware.auth import get_current_user

router = APIRouter(prefix="/customer-balances", tags=["customer-balances"])


@router.get("/", response_model=List[CustomerResponse])
def get_customer_balances(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all customers with outstanding balances.
    Returns customers ordered by balance amount (highest first).
    Used by mobile app to display pending balances list.
    
    NOW QUERIES FROM CUSTOMERS TABLE (pending_balance > 0)
    """
    customers = db.query(Customer).filter(
        Customer.pending_balance > 0
    ).order_by(Customer.pending_balance.desc()).all()
    
    return customers


@router.get("/total")
def get_balance_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get summary of pending balances: count and total amount.
    Used by mobile app dashboard for quick overview.
    Returns {customer_count: 0, total_pending: 0} if no balances exist.
    
    NOW QUERIES FROM CUSTOMERS TABLE (pending_balance > 0)
    """
    result = db.query(
        func.count(Customer.id).label('count'),
        func.coalesce(func.sum(Customer.pending_balance), 0).label('total')
    ).filter(
        Customer.pending_balance > 0
    ).first()
    
    return {
        "customer_count": result.count if result else 0,
        "total_pending": float(result.total) if result and result.total else 0.0
    }


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer_balance(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific customer's balance information by customer ID.
    
    NOW QUERIES FROM CUSTOMERS TABLE
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    return customer
