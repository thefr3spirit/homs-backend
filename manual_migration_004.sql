-- Manual Migration 004: Add user tracking to daily_summaries
-- Run this directly in Supabase SQL Editor

-- Add tracking columns to daily_summaries table
ALTER TABLE daily_summaries 
ADD COLUMN IF NOT EXISTS created_by VARCHAR,
ADD COLUMN IF NOT EXISTS updated_by VARCHAR;

-- Add foreign key constraints
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_daily_summaries_created_by'
    ) THEN
        ALTER TABLE daily_summaries
        ADD CONSTRAINT fk_daily_summaries_created_by
        FOREIGN KEY (created_by) REFERENCES users(id);
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_daily_summaries_updated_by'
    ) THEN
        ALTER TABLE daily_summaries
        ADD CONSTRAINT fk_daily_summaries_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(id);
    END IF;
END $$;

-- Update alembic version to 004
UPDATE alembic_version 
SET version_num = '004_daily_summary_tracking'
WHERE version_num = '003_add_user_tracking';

-- If alembic_version doesn't have the row, insert it
INSERT INTO alembic_version (version_num)
SELECT '004_daily_summary_tracking'
WHERE NOT EXISTS (SELECT 1 FROM alembic_version WHERE version_num = '004_daily_summary_tracking');

-- Verify the changes
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns
WHERE table_name = 'daily_summaries' 
AND column_name IN ('created_by', 'updated_by')
ORDER BY column_name;
