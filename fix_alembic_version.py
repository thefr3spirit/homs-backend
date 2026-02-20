"""
Fix Alembic version table - should only have one version at a time.
Keeping 004_daily_summary_tracking and removing 003_user_tracking.
"""
from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Start a transaction
    trans = conn.begin()
    try:
        # Check current versions
        result = conn.execute(text('SELECT version_num FROM alembic_version'))
        versions = [v[0] for v in result.fetchall()]
        print(f'Current versions in DB: {versions}')
        
        # Delete 003_user_tracking (older version)
        if '003_user_tracking' in versions:
            conn.execute(text("DELETE FROM alembic_version WHERE version_num = '003_user_tracking'"))
            print('❌ Deleted 003_user_tracking')
        
        # Ensure 004_daily_summary_tracking is present
        if '004_daily_summary_tracking' not in versions:
            conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('004_daily_summary_tracking')"))
            print('✅ Added 004_daily_summary_tracking')
        
        # Commit the transaction
        trans.commit()
        print('\n✅ Database version table fixed')
        
        # Verify
        result = conn.execute(text('SELECT version_num FROM alembic_version'))
        final_version = result.fetchone()[0]
        print(f'Current DB version: {final_version}')
        
    except Exception as e:
        trans.rollback()
        print(f'❌ Error: {e}')
        raise
