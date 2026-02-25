"""add_emergency_contact_to_customers

Revision ID: 006_emergency_contact
Revises: 005_customer_balance
Create Date: 2026-02-25 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006_emergency_contact'
down_revision = '005_customer_balance'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add emergency_contact column to customers table.
    This field stores emergency contact information (phone/name).
    """
    op.add_column('customers', sa.Column('emergency_contact', sa.String(), nullable=True))
    print("✅ Added emergency_contact column to customers table")


def downgrade() -> None:
    """
    Remove emergency_contact column from customers table.
    """
    op.drop_column('customers', 'emergency_contact')
    print("✅ Removed emergency_contact column from customers table")
