-- Migration: 011_notifications.sql
-- Description: Create the notifications table for storing scraper execution alerts

CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL, -- 'job_completed', 'job_failed', 'schedule_failed', 'retry_exhausted', 'new_dealers_discovered'
    message TEXT NOT NULL,
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);
