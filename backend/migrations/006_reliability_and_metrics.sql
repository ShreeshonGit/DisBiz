-- Migration: 006_reliability_and_metrics.sql
-- Description: Add failure_reason and last_successful_page to scrape_jobs, and create scraper_metrics table

-- Enhance scrape_jobs table with recovery columns
ALTER TABLE scrape_jobs 
ADD COLUMN IF NOT EXISTS failure_reason TEXT NULL,
ADD COLUMN IF NOT EXISTS last_successful_page INTEGER DEFAULT 0;

-- Create scraper_metrics table
CREATE TABLE IF NOT EXISTS scraper_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID UNIQUE NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    total_jobs INTEGER DEFAULT 0,
    success_jobs INTEGER DEFAULT 0,
    failed_jobs INTEGER DEFAULT 0,
    avg_runtime DOUBLE PRECISION DEFAULT 0.0,
    avg_records_scraped DOUBLE PRECISION DEFAULT 0.0,
    last_run_at TIMESTAMP WITH TIME ZONE NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trigger for scraper_metrics updated_at
CREATE TRIGGER update_scraper_metrics_updated_at
    BEFORE UPDATE ON scraper_metrics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Index on brand_id for metrics
CREATE INDEX IF NOT EXISTS idx_scraper_metrics_brand_id ON scraper_metrics(brand_id);
