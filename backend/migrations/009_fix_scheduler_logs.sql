-- Migration: 009_fix_scheduler_logs.sql
-- Description: Drop and recreate scheduler_logs to align with python codebase repository schema

DROP TABLE IF EXISTS scheduler_logs;

CREATE TABLE scheduler_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_id UUID REFERENCES scrape_schedules(id) ON DELETE SET NULL,
    job_id UUID REFERENCES scrape_jobs(id) ON DELETE SET NULL,
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE,
    action TEXT NOT NULL, -- e.g., CREATE, EDIT, DELETE, PAUSE, RESUME, RUN_NOW, DISPATCH, RETRY, RECOVERY
    status TEXT NOT NULL, -- e.g., SUCCESS, FAILURE, PENDING
    details TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recreate index for performance queries
CREATE INDEX IF NOT EXISTS idx_scheduler_logs_created_at ON scheduler_logs(created_at DESC);
