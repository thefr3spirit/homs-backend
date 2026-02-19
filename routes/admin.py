"""
Manual migration endpoint for running database migrations.
Useful for free tier deployments without shell access.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from alembic.config import Config
from alembic import command
import os

from database import get_db
from models.user import User, UserRole
from middleware.auth import get_current_user, require_role

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/run-migrations")
def run_migrations(
    current_user: User = Depends(require_role(UserRole.OWNER)),
    db: Session = Depends(get_db)
):
    """
    Manually run database migrations.
    Only accessible by OWNER role.
    
    Use this when you need to run migrations without shell access.
    """
    try:
        # Run alembic migrations
        alembic_cfg = Config("alembic.ini")
        
        # Get current revision
        from alembic.script import ScriptDirectory
        from alembic.runtime.migration import MigrationContext
        
        script = ScriptDirectory.from_config(alembic_cfg)
        
        # Get database connection from session
        connection = db.connection()
        context = MigrationContext.configure(connection)
        current_rev = context.get_current_revision()
        
        # Get head revision
        head_rev = script.get_current_head()
        
        if current_rev == head_rev:
            return {
                "status": "success",
                "message": "Database is already up to date",
                "current_revision": current_rev,
                "head_revision": head_rev
            }
        
        # Run upgrade
        command.upgrade(alembic_cfg, "head")
        
        return {
            "status": "success",
            "message": "Migrations completed successfully",
            "previous_revision": current_rev,
            "current_revision": head_rev
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )


@router.get("/migration-status")
def get_migration_status(
    current_user: User = Depends(require_role(UserRole.OWNER)),
    db: Session = Depends(get_db)
):
    """
    Check current migration status.
    Shows current database revision vs latest available revision.
    """
    try:
        from alembic.config import Config
        from alembic.script import ScriptDirectory
        from alembic.runtime.migration import MigrationContext
        
        alembic_cfg = Config("alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)
        
        # Get database connection
        connection = db.connection()
        context = MigrationContext.configure(connection)
        current_rev = context.get_current_revision()
        
        # Get head revision
        head_rev = script.get_current_head()
        
        # Check if up to date
        is_up_to_date = current_rev == head_rev
        
        return {
            "current_revision": current_rev,
            "head_revision": head_rev,
            "is_up_to_date": is_up_to_date,
            "status": "up_to_date" if is_up_to_date else "migrations_pending"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check migration status: {str(e)}"
        )
