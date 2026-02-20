from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text('SELECT version_num FROM alembic_version'))
    versions = result.fetchall()
    if versions:
        print(f'Database has {len(versions)} version(s):')
        for v in versions:
            print(f'  - {v[0]}')
    else:
        print('No version recorded in database')
