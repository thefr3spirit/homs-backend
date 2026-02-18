"""
Payment recording routes with balance tracking and receptionist accountability.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date, datetime

from database import get_db
from models.user import User, UserRole
from models.payment import Payment, PaymentMethod, PaymentType, PaymentStatus
from models.booking import Booking
from models.customer import Customer
from schemas.payment import (
    PaymentCreate, PaymentResponse,
    PaymentSummary, PaymentSearchResponse
)
from middleware.auth import get_current_user, require_role

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def record_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(require_role(UserRole.OWNER, UserRole.RECEPTIONIST)),
    db: Session = Depends(get_db)
):
    """
    Record a payment.
    Automatically tracks which receptionist received the payment.
    Updates customer pending balance and booking amount paid.
    Only accessible by OWNER and RECEPTIONIST.
    """
    # Validate booking exists
    booking = db.query(Booking).filter(Booking.id == payment_data.booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Validate customer exists
    customer = db.query(Customer).filter(Customer.id == payment_data.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Validate customer matches booking
    if booking.customer_id != payment_data.customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer does not match booking"
        )
    
    # Validate amount
    if payment_data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount must be positive"
        )
    
    # Calculate remaining balance
    balance_due = booking.total_amount - booking.amount_paid
    
    # Check if payment exceeds balance (allow small overpayment for full payment type)
    if payment_data.payment_type != PaymentType.REFUND and payment_data.amount > balance_due + 0.01:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment amount ({payment_data.amount}) exceeds balance due ({balance_due})"
        )
    
    # Create payment record
    payment = Payment(
        **payment_data.model_dump(),
        received_by=current_user.id,  # ← Track who received the payment
        payment_date=datetime.utcnow(),
        status=PaymentStatus.COMPLETED
    )
    
    # Update booking amount paid
    booking.amount_paid += payment_data.amount
    
    # Update customer financials
    if payment_data.payment_type == PaymentType.REFUND:
        # Refund reduces total spent and pending balance
        customer.total_spent -= payment_data.amount
        customer.pending_balance += payment_data.amount
    else:
        # Regular payment increases total spent
        customer.total_spent += payment_data.amount
        
        # If customer had pending balance, reduce it
        if customer.pending_balance > 0:
            reduction = min(payment_data.amount, customer.pending_balance)
            customer.pending_balance -= reduction
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    return payment


@router.get("/", response_model=PaymentSearchResponse)
def list_payments(
    booking_id: Optional[str] = Query(None, description="Filter by booking"),
    customer_id: Optional[str] = Query(None, description="Filter by customer"),
    payment_method: Optional[PaymentMethod] = Query(None, description="Filter by payment method"),
    payment_status: Optional[PaymentStatus] = Query(None, description="Filter by status"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List payments with filtering and pagination.
    All authenticated users can view payments.
    """
    query = db.query(Payment)
    
    if booking_id:
        query = query.filter(Payment.booking_id == booking_id)
    
    if customer_id:
        query = query.filter(Payment.customer_id == customer_id)
    
    if payment_method:
        query = query.filter(Payment.payment_method == payment_method)
    
    if payment_status:
        query = query.filter(Payment.status == payment_status)
    
    if start_date:
        query = query.filter(func.date(Payment.payment_date) >= start_date)
    
    if end_date:
        query = query.filter(func.date(Payment.payment_date) <= end_date)
    
    # Get total count and sum
    total = query.count()
    total_amount = db.query(func.sum(Payment.amount)).filter(
        Payment.id.in_([p.id for p in query.all()])
    ).scalar() or 0.0
    
    # Apply pagination
    payments = query.order_by(Payment.payment_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "payments": payments,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_amount": float(total_amount)
    }


@router.get("/today")
def get_today_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get today's payments with summary.
    """
    today = date.today()
    
    payments = db.query(Payment).filter(
        func.date(Payment.payment_date) == today,
        Payment.status == PaymentStatus.COMPLETED
    ).all()
    
    total_amount = sum(p.amount for p in payments)
    
    # Group by payment method
    by_method = {}
    for payment in payments:
        method = payment.payment_method.value
        by_method[method] = by_method.get(method, 0) + payment.amount
    
    return {
        "payments": payments,
        "total_payments": len(payments),
        "total_amount": total_amount,
        "by_method": by_method
    }


@router.get("/summary", response_model=PaymentSummary)
def get_payment_summary(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get payment summary statistics for a date range.
    """
    query = db.query(Payment).filter(Payment.status == PaymentStatus.COMPLETED)
    
    if start_date:
        query = query.filter(func.date(Payment.payment_date) >= start_date)
    
    if end_date:
        query = query.filter(func.date(Payment.payment_date) <= end_date)
    
    payments = query.all()
    
    total_amount = sum(p.amount for p in payments)
    
    # Group by payment method
    by_method = {}
    for payment in payments:
        method = payment.payment_method.value
        by_method[method] = by_method.get(method, 0) + payment.amount
    
    # Group by status
    by_status = {}
    for payment in payments:
        status_val = payment.status.value
        by_status[status_val] = by_status.get(status_val, 0) + 1
    
    return {
        "total_payments": len(payments),
        "total_amount": total_amount,
        "by_method": by_method,
        "by_status": by_status
    }


@router.get("/booking/{booking_id}", response_model=list[PaymentResponse])
def get_booking_payments(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all payments for a specific booking.
    """
    # Validate booking exists
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    payments = db.query(Payment).filter(
        Payment.booking_id == booking_id
    ).order_by(Payment.payment_date).all()
    
    return payments


@router.get("/customer/{customer_id}", response_model=list[PaymentResponse])
def get_customer_payments(
    customer_id: str,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get payment history for a specific customer.
    """
    # Validate customer exists
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    payments = db.query(Payment).filter(
        Payment.customer_id == customer_id
    ).order_by(Payment.payment_date.desc()).limit(limit).all()
    
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get payment details by ID.
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return payment


@router.post("/{payment_id}/refund")
def refund_payment(
    payment_id: str,
    reason: str = Query(..., description="Refund reason"),
    current_user: User = Depends(require_role(UserRole.OWNER)),
    db: Session = Depends(get_db)
):
    """
    Process a payment refund.
    Only accessible by OWNER.
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.status == PaymentStatus.REFUNDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment already refunded"
        )
    
    if payment.status != PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only refund completed payments"
        )
    
    # Create refund payment record
    refund = Payment(
        booking_id=payment.booking_id,
        customer_id=payment.customer_id,
        amount=payment.amount,
        payment_method=payment.payment_method,
        payment_type=PaymentType.REFUND,
        transaction_ref=f"REFUND-{payment.id[:8]}",
        notes=f"Refund for payment {payment.id}. Reason: {reason}",
        received_by=current_user.id,
        payment_date=datetime.utcnow(),
        status=PaymentStatus.COMPLETED
    )
    
    # Update original payment status
    payment.status = PaymentStatus.REFUNDED
    payment.notes = f"{payment.notes or ''}\nRefunded by {current_user.full_name}: {reason}"
    
    # Update booking
    booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
    if booking:
        booking.amount_paid -= payment.amount
    
    # Update customer
    customer = db.query(Customer).filter(Customer.id == payment.customer_id).first()
    if customer:
        customer.total_spent -= payment.amount
        customer.pending_balance += payment.amount  # Increase pending balance (they owe less)
    
    db.add(refund)
    db.commit()
    
    return {
        "message": "Payment refunded successfully",
        "original_payment_id": payment_id,
        "refund_payment_id": refund.id
    }
