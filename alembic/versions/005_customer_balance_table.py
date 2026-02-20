"""create_customer_balance_table

Revision ID: 005_customer_balance
Revises: 004_daily_summary_tracking
Create Date: 2026-02-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005_customer_balance'
down_revision = '004_daily_summary_tracking'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create customer_balance table for tracking outstanding payments.
    This is a separate table optimized for quick mobile app queries.
    """
    op.create_table(
        'customer_balance',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.Column('customer_name', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('balance_amount', sa.Float(), nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('created_by_name', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('updated_by_name', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id']),
        sa.UniqueConstraint('customer_id', name='uq_customer_balance_customer_id')
    )
    
    # Create indexes for faster queries
    op.create_index('ix_customer_balance_customer_id', 'customer_balance', ['customer_id'])
    op.create_index('ix_customer_balance_amount', 'customer_balance', ['balance_amount'])
    
    print("✅ Created customer_balance table with indexes")
    
    # Optional: Populate from existing customers with pending_balance > 0
    # Uncomment if you want to migrate existing data
    # op.execute("""
    #     INSERT INTO customer_balance (customer_id, customer_name, phone, balance_amount, created_at)
    #     SELECT id, full_name, phone, pending_balance, created_at
    #     FROM customers
    #     WHERE pending_balance > 0
    #     ON CONFLICT (customer_id) DO NOTHING
    # """)


def downgrade() -> None:
    """
    Drop customer_balance table.
    """
    op.drop_index('ix_customer_balance_amount', 'customer_balance')
    op.drop_index('ix_customer_balance_customer_id', 'customer_balance')
    op.drop_table('customer_balance')
    
    print("⏪ Dropped customer_balance table")
