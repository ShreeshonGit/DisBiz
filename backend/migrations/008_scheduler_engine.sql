-- Migration: 008_scheduler_engine.sql
-- Description: Create scrape_schedules and scheduler_logs tables for Intelligent Scheduler

-- Drop tables if they exist to prevent conflict
DROP TABLE IF EXISTS scheduler_logs;
DROP TABLE IF EXISTS scrape_schedules;

-- Create scrape_schedules table
CREATE TABLE scrape_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE,
    schedule_name TEXT NOT NULL,
    cron_expression TEXT NOT NULL,
    frequency TEXT NULL,
    timezone TEXT NOT NULL DEFAULT 'UTC',
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    last_run TIMESTAMP WITH TIME ZONE NULL,
    next_run TIMESTAMP WITH TIME ZONE NULL,
    last_success TIMESTAMP WITH TIME ZONE NULL,
    last_failure TIMESTAMP WITH TIME ZONE NULL,
    retry_policy TEXT NOT NULL DEFAULT 'EXPONENTIAL', -- IMMEDIATE, LINEAR, EXPONENTIAL
    max_retries INTEGER NOT NULL DEFAULT 3,
    retry_delay_minutes INTEGER NOT NULL DEFAULT 5,
    priority TEXT NOT NULL DEFAULT 'NORMAL', -- HIGH, NORMAL, LOW
    concurrency_group TEXT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, PAUSED, COMPLETED, FAILED
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_brand_schedule_name UNIQUE(brand_id, schedule_name)
);

-- Trigger for scrape_schedules updated_at
CREATE TRIGGER update_scrape_schedules_updated_at
    BEFORE UPDATE ON scrape_schedules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create scheduler_logs table
CREATE TABLE scheduler_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_id UUID REFERENCES scrape_schedules(id) ON DELETE SET NULL,
    job_id UUID REFERENCES scrape_jobs(id) ON DELETE SET NULL,
    event TEXT NOT NULL, -- e.g., DISPATCH, RETRY, RECOVERY, RUN_NOW, PAUSE, RESUME
    status TEXT NOT NULL, -- e.g., SUCCESS, FAILURE, PENDING
    message TEXT NULL,
    execution_time DOUBLE PRECISION NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance queries
CREATE INDEX idx_scrape_schedules_next_run ON scrape_schedules(next_run) WHERE status = 'ACTIVE' AND enabled = TRUE;
CREATE INDEX idx_scrape_schedules_brand_id ON scrape_schedules(brand_id);
CREATE INDEX idx_scheduler_logs_created_at ON scheduler_logs(created_at DESC);
