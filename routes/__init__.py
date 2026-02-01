"""
API routes for daily summary operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from database import get_db
from schemas import (
    DailySummaryCreate,
    DailySummaryResponse,
    MessageResponse,
    ErrorResponse
)
from services import SummaryService

# Create router
router = APIRouter(
    prefix="/summary",
    tags=["summary"]
)


@router.post(
    "",
    response_model=DailySummaryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit daily summary",
    description="Submit daily hotel summary data. If a summary for the date exists, it will be updated."
)
def create_summary(
    summary: DailySummaryCreate,
    db: Session = Depends(get_db)
):
    """
    Create or update a daily summary.
    
    - **date**: Date of the summary (YYYY-MM-DD)
    - **rooms_total**: Total hotel rooms
    - **rooms_occupied**: Number of occupied rooms
    - **rooms_available**: Number of available rooms
    - **cash_collected**: Cash collected
    - **momo_collected**: Mobile money collected
    - **total_collected**: Total amount collected
    - **expected_balance**: Expected balance
    - **expenses_logged**: Logged expenses
    """
    try:
        db_summary = SummaryService.create_summary(db, summary)
        return db_summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create summary: {str(e)}"
        )


@router.get(
    "/today",
    response_model=DailySummaryResponse,
    summary="Get today's summary",
    description="Retrieve the summary for today's date."
)
def get_today_summary(db: Session = Depends(get_db)):
    """
    Get today's summary.
    Returns 404 if no summary exists for today.
    """
    summary = SummaryService.get_today_summary(db)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No summary found for today ({date.today()})"
        )
    
    return summary


@router.get(
    "/latest",
    response_model=DailySummaryResponse,
    summary="Get latest summary",
    description="Retrieve the most recent summary (may not be today)."
)
def get_latest_summary(db: Session = Depends(get_db)):
    """
    Get the most recent summary in the database.
    Returns 404 if no summaries exist.
    """
    summary = SummaryService.get_latest_summary(db)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No summaries found in database"
        )
    
    return summary


@router.get(
    "/history",
    response_model=List[DailySummaryResponse],
    summary="Get summary history",
    description="Retrieve historical summaries with pagination support."
)
def get_summary_history(
    limit: int = Query(30, ge=1, le=100, description="Maximum number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db)
):
    """
    Get historical summaries.
    
    - **limit**: Maximum records to return (1-100, default 30)
    - **offset**: Records to skip for pagination (default 0)
    
    Returns summaries ordered by date (most recent first).
    """
    summaries = SummaryService.get_summary_history(db, limit=limit, offset=offset)
    return summaries


@router.get(
    "/date/{summary_date}",
    response_model=DailySummaryResponse,
    summary="Get summary by date",
    description="Retrieve a summary for a specific date."
)
def get_summary_by_date(
    summary_date: date,
    db: Session = Depends(get_db)
):
    """
    Get summary for a specific date.
    
    - **summary_date**: Date in YYYY-MM-DD format
    """
    summary = SummaryService.get_summary_by_date(db, summary_date)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No summary found for date {summary_date}"
        )
    
    return summary


@router.get(
    "/range",
    response_model=List[DailySummaryResponse],
    summary="Get summaries by date range",
    description="Retrieve summaries within a date range."
)
def get_date_range_summaries(
    start_date: date = Query(..., description="Start date (inclusive)"),
    end_date: date = Query(..., description="End date (inclusive)"),
    db: Session = Depends(get_db)
):
    """
    Get summaries within a date range.
    
    - **start_date**: Start date (inclusive)
    - **end_date**: End date (inclusive)
    """
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before or equal to end_date"
        )
    
    summaries = SummaryService.get_date_range_summaries(db, start_date, end_date)
    return summaries


@router.delete(
    "/date/{summary_date}",
    response_model=MessageResponse,
    summary="Delete summary",
    description="Delete a summary for a specific date."
)
def delete_summary(
    summary_date: date,
    db: Session = Depends(get_db)
):
    """
    Delete a summary for a specific date.
    
    - **summary_date**: Date in YYYY-MM-DD format
    """
    success = SummaryService.delete_summary(db, summary_date)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No summary found for date {summary_date}"
        )
    
    return MessageResponse(
        message="Summary deleted successfully",
        detail=f"Summary for {summary_date} has been removed"
    )
