-- Migration: 005_update_scrape_jobs.sql
-- Description: Enhance scrape_jobs table with background engine tracking columns and indexes

-- Add new columns if not present
ALTER TABLE scrape_jobs 
ADD COLUMN IF NOT EXISTS start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS end_time TIMESTAMP WITH TIME ZONE NULL,
ADD COLUMN IF NOT EXISTS records_scraped INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS error_log TEXT NULL,
ADD COLUMN IF NOT EXISTS execution_logs JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Add indexes on (brand_id, status) for performance optimization
CREATE INDEX IF NOT EXISTS idx_scrape_jobs_brand_status ON scrape_jobs(brand_id, status);
