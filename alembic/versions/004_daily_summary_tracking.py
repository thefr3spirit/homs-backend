"""add tracking to daily_summaries

Revision ID: 004_add_tracking_to_daily_summaries
Revises: 003_add_user_tracking
Create Date: 2026-02-19

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_daily_summary_tracking'
down_revision = '003_add_user_tracking'
branch_labels = None
depends_on = None


def upgrade():
    # Add tracking columns to daily_summaries table
    op.add_column('daily_summaries', sa.Column('created_by', sa.String(), nullable=True))
    op.add_column('daily_summaries', sa.Column('updated_by', sa.String(), nullable=True))
    
    # Add foreign key constraints
    op.create_foreign_key(
        'fk_daily_summaries_created_by',
        'daily_summaries', 'users',
        ['created_by'], ['id']
    )
    op.create_foreign_key(
        'fk_daily_summaries_updated_by',
        'daily_summaries', 'users',
        ['updated_by'], ['id']
    )


def downgrade():
    # Drop foreign key constraints
    op.drop_constraint('fk_daily_summaries_updated_by', 'daily_summaries', type_='foreignkey')
    op.drop_constraint('fk_daily_summaries_created_by', 'daily_summaries', type_='foreignkey')
    
    # Drop columns
    op.drop_column('daily_summaries', 'updated_by')
    op.drop_column('daily_summaries', 'created_by')
