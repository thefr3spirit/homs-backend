"""add_user_tracking_to_customers_and_rooms

Revision ID: 003_user_tracking
Revises: 002_update_roles
Create Date: 2026-02-19 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_user_tracking'
down_revision = '002_update_roles'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add user tracking columns to customers and rooms tables:
    - created_by (who created the record)
    - updated_by (who last updated the record)
    Also add timestamps to rooms table.
    """
    # Add user tracking to customers table
    op.add_column('customers', sa.Column('created_by', sa.String(), nullable=True))
    op.add_column('customers', sa.Column('updated_by', sa.String(), nullable=True))
    op.create_foreign_key('fk_customers_created_by', 'customers', 'users', ['created_by'], ['id'])
    op.create_foreign_key('fk_customers_updated_by', 'customers', 'users', ['updated_by'], ['id'])
    
    # Add user tracking and timestamps to rooms table
    op.add_column('rooms', sa.Column('created_by', sa.String(), nullable=True))
    op.add_column('rooms', sa.Column('updated_by', sa.String(), nullable=True))
    op.add_column('rooms', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('rooms', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key('fk_rooms_created_by', 'rooms', 'users', ['created_by'], ['id'])
    op.create_foreign_key('fk_rooms_updated_by', 'rooms', 'users', ['updated_by'], ['id'])
    
    print("✅ Added user tracking to customers and rooms tables")


def downgrade() -> None:
    """
    Remove user tracking columns.
    """
    # Remove from rooms
    op.drop_constraint('fk_rooms_updated_by', 'rooms', type_='foreignkey')
    op.drop_constraint('fk_rooms_created_by', 'rooms', type_='foreignkey')
    op.drop_column('rooms', 'updated_at')
    op.drop_column('rooms', 'created_at')
    op.drop_column('rooms', 'updated_by')
    op.drop_column('rooms', 'created_by')
    
    # Remove from customers
    op.drop_constraint('fk_customers_updated_by', 'customers', type_='foreignkey')
    op.drop_constraint('fk_customers_created_by', 'customers', type_='foreignkey')
    op.drop_column('customers', 'updated_by')
    op.drop_column('customers', 'created_by')
