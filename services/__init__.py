"""
Business logic services for daily summary operations.
Handles CRUD operations and business rules.
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date, timedelta
from typing import List, Optional
from models import DailySummary
from schemas import DailySummaryCreate, DailySummaryUpdate
from fastapi import HTTPException, status


class SummaryService:
    """Service class for daily summary operations."""

    @staticmethod
    def create_summary(db: Session, summary_data: DailySummaryCreate) -> DailySummary:
        """
        Create a new daily summary.
        If a summary for the date already exists, update it instead.
        """
        # Check if summary for this date already exists
        existing = db.query(DailySummary).filter(DailySummary.date == summary_data.date).first()
        
        if existing:
            # Update existing summary
            for key, value in summary_data.model_dump().items():
                setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return existing
        
        # Create new summary
        db_summary = DailySummary(**summary_data.model_dump())
        db.add(db_summary)
        db.commit()
        db.refresh(db_summary)
        return db_summary

    @staticmethod
    def get_summary_by_date(db: Session, summary_date: date) -> Optional[DailySummary]:
        """Get a summary for a specific date."""
        return db.query(DailySummary).filter(DailySummary.date == summary_date).first()

    @staticmethod
    def get_today_summary(db: Session) -> Optional[DailySummary]:
        """Get today's summary."""
        today = date.today()
        return SummaryService.get_summary_by_date(db, today)

    @staticmethod
    def get_latest_summary(db: Session) -> Optional[DailySummary]:
        """Get the most recent summary (may not be today)."""
        return db.query(DailySummary).order_by(desc(DailySummary.date)).first()

    @staticmethod
    def get_summary_history(
        db: Session,
        limit: int = 30,
        offset: int = 0
    ) -> List[DailySummary]:
        """
        Get historical summaries, ordered by date descending.
        
        Args:
            limit: Maximum number of records to return (default 30)
            offset: Number of records to skip (for pagination)
        """
        return (
            db.query(DailySummary)
            .order_by(desc(DailySummary.date))
            .limit(limit)
            .offset(offset)
            .all()
        )

    @staticmethod
    def get_date_range_summaries(
        db: Session,
        start_date: date,
        end_date: date
    ) -> List[DailySummary]:
        """Get summaries within a date range."""
        return (
            db.query(DailySummary)
            .filter(DailySummary.date >= start_date, DailySummary.date <= end_date)
            .order_by(desc(DailySummary.date))
            .all()
        )

    @staticmethod
    def update_summary(
        db: Session,
        summary_date: date,
        update_data: DailySummaryUpdate
    ) -> Optional[DailySummary]:
        """Update an existing summary."""
        summary = SummaryService.get_summary_by_date(db, summary_date)
        
        if not summary:
            return None
        
        # Update only provided fields
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(summary, key, value)
        
        db.commit()
        db.refresh(summary)
        return summary

    @staticmethod
    def delete_summary(db: Session, summary_date: date) -> bool:
        """Delete a summary for a specific date."""
        summary = SummaryService.get_summary_by_date(db, summary_date)
        
        if not summary:
            return False
        
        db.delete(summary)
        db.commit()
        return True

    @staticmethod
    def get_summary_count(db: Session) -> int:
        """Get total count of summaries in database."""
        return db.query(DailySummary).count()
