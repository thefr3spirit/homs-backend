"""
Script to backfill cheque_collected for existing records.
Run this after deploying the migration to ensure old data has default values.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env")
    exit(1)

# Create engine
engine = create_engine(DATABASE_URL)

# Update existing records to set cheque_collected to 0.0 where it's null
with engine.connect() as conn:
    result = conn.execute(
        text("UPDATE daily_summaries SET cheque_collected = 0.0 WHERE cheque_collected IS NULL")
    )
    conn.commit()
    print(f"✅ Updated {result.rowcount} records with default cheque_collected value")

print("✅ Backfill completed successfully!")
