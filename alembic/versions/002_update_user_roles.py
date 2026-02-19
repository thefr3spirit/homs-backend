"""update_user_roles_enum

Revision ID: 002_update_roles
Revises: ebf9359b2ba9
Create Date: 2026-02-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_update_roles'
down_revision = 'ebf9359b2ba9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Update UserRole enum:
    - Remove ACCOUNTANT
    - Add ADMIN
    - Migrate any existing ACCOUNTANT users to RECEPTIONIST
    """
    # Step 1: Update any existing accountant users to receptionist
    # This prevents foreign key issues when we modify the enum
    op.execute("""
        UPDATE users 
        SET role = 'RECEPTIONIST' 
        WHERE role = 'ACCOUNTANT';
    """)
    
    # Step 2: For PostgreSQL, we need to alter the enum type
    # First, create a new enum type with the updated values
    op.execute("ALTER TYPE userrole RENAME TO userrole_old;")
    
    # Create the new enum type
    op.execute("CREATE TYPE userrole AS ENUM ('OWNER', 'RECEPTIONIST', 'ADMIN');")
    
    # Update the column to use the new enum type
    op.execute("""
        ALTER TABLE users 
        ALTER COLUMN role TYPE userrole 
        USING role::text::userrole;
    """)
    
    # Drop the old enum type
    op.execute("DROP TYPE userrole_old;")
    
    print("✅ Successfully migrated UserRole enum:")
    print("   - Removed ACCOUNTANT")
    print("   - Added ADMIN")
    print("   - Migrated existing ACCOUNTANT users to RECEPTIONIST")


def downgrade() -> None:
    """
    Revert UserRole enum changes:
    - Remove ADMIN
    - Add back ACCOUNTANT
    - Migrate any ADMIN users to RECEPTIONIST
    """
    # Update any admin users to receptionist before changing enum
    op.execute("""
        UPDATE users 
        SET role = 'RECEPTIONIST' 
        WHERE role = 'ADMIN';
    """)
    
    # Rename current enum
    op.execute("ALTER TYPE userrole RENAME TO userrole_old;")
    
    # Create the old enum type
    op.execute("CREATE TYPE userrole AS ENUM ('OWNER', 'RECEPTIONIST', 'ACCOUNTANT');")
    
    # Update the column to use the old enum type
    op.execute("""
        ALTER TABLE users 
        ALTER COLUMN role TYPE userrole 
        USING role::text::userrole;
    """)
    
    # Drop the temporary enum type
    op.execute("DROP TYPE userrole_old;")
