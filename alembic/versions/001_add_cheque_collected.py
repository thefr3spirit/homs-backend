"""Add cheque_collected field

Revision ID: 001_cheque
Revises: 
Create Date: 2026-02-18

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_cheque'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add cheque_collected column to daily_summaries table."""
    op.add_column(
        'daily_summaries',
        sa.Column('cheque_collected', sa.Float(), nullable=False, server_default='0.0')
    )


def downgrade() -> None:
    """Remove cheque_collected column from daily_summaries table."""
    op.drop_column('daily_summaries', 'cheque_collected')
