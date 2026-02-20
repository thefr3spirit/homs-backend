"""
Customer balance tracking routes for mobile app.
This handles the separate customer_balance table that the desktop PWA writes to.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from database import get_db
from models.user import User
from models.customer_balance import CustomerBalance
from schemas.customer_balance import (
    CustomerBalanceResponse,
    CustomerBalanceSummary
)
from middleware.auth import get_current_user

router = APIRouter(prefix="/customer-balances", tags=["customer-balances"])


@router.get("/", response_model=List[CustomerBalanceResponse])
def get_customer_balances(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all customers with outstanding balances.
    Returns customers ordered by balance amount (highest first).
    Used by mobile app to display pending balances list.
    """
    balances = db.query(CustomerBalance).filter(
        CustomerBalance.balance_amount > 0
    ).order_by(CustomerBalance.balance_amount.desc()).all()
    
    return balances


@router.get("/total", response_model=CustomerBalanceSummary)
def get_balance_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get summary of pending balances: count and total amount.
    Used by mobile app dashboard for quick overview.
    Returns {customer_count: 0, total_pending: 0} if no balances exist.
    """
    result = db.query(
        func.count(CustomerBalance.id).label('count'),
        func.coalesce(func.sum(CustomerBalance.balance_amount), 0).label('total')
    ).filter(
        CustomerBalance.balance_amount > 0
    ).first()
    
    return {
        "customer_count": result.count if result else 0,
        "total_pending": float(result.total) if result and result.total else 0.0
    }


@router.get("/{balance_id}", response_model=CustomerBalanceResponse)
def get_customer_balance(
    balance_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific customer balance record by ID.
    """
    balance = db.query(CustomerBalance).filter(CustomerBalance.id == balance_id).first()
    
    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer balance record with ID {balance_id} not found"
        )
    
    return balance
