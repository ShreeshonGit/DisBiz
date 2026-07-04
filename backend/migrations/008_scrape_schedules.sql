-- Migration: 008_scrape_schedules.sql
-- Description: Create scrape_schedules and scheduler_logs tables for Intelligent Scheduler

-- Create scrape_schedules table
CREATE TABLE IF NOT EXISTS scrape_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE,
    schedule_name TEXT NOT NULL,
    cron_expression TEXT NOT NULL,
    next_run TIMESTAMP WITH TIME ZONE NULL,
    last_run TIMESTAMP WITH TIME ZONE NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, PAUSED
    priority TEXT NOT NULL DEFAULT 'MEDIUM', -- LOW, MEDIUM, HIGH
    max_retries INTEGER NOT NULL DEFAULT 3,
    timezone TEXT NOT NULL DEFAULT 'UTC',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_brand_schedule UNIQUE(brand_id, schedule_name)
);

-- Trigger for update_schedules_updated_at
CREATE TRIGGER update_scrape_schedules_updated_at
    BEFORE UPDATE ON scrape_schedules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create scheduler_logs table
CREATE TABLE IF NOT EXISTS scheduler_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_id UUID REFERENCES scrape_schedules(id) ON DELETE SET NULL,
    job_id UUID REFERENCES scrape_jobs(id) ON DELETE SET NULL,
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE,
    action TEXT NOT NULL, -- DISPATCH, RETRY, RECOVERY, RUN_NOW, PAUSE, RESUME
    status TEXT NOT NULL, -- SUCCESS, FAILURE, PENDING
    details TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance queries
CREATE INDEX IF NOT EXISTS idx_scrape_schedules_next_run ON scrape_schedules(next_run) WHERE status = 'ACTIVE';
CREATE INDEX IF NOT EXISTS idx_scrape_schedules_brand_id ON scrape_schedules(brand_id);
CREATE INDEX IF NOT EXISTS idx_scheduler_logs_created_at ON scheduler_logs(created_at DESC);
