-- Migration: 007_production_scraper.sql
-- Description: Upgrade dealers, scraper_configs, and scraper_metrics tables with production columns

-- Enhance dealers table
ALTER TABLE dealers
ADD COLUMN IF NOT EXISTS formatted_address TEXT NULL,
ADD COLUMN IF NOT EXISTS country TEXT DEFAULT 'India',
ADD COLUMN IF NOT EXISTS quality_score INTEGER DEFAULT 0;

-- Enhance scraper_configs table
ALTER TABLE scraper_configs
ADD COLUMN IF NOT EXISTS suggested_selectors JSONB NULL,
ADD COLUMN IF NOT EXISTS detected_api_metadata JSONB NULL;

-- Enhance scraper_metrics table
ALTER TABLE scraper_metrics
ADD COLUMN IF NOT EXISTS avg_response_time DOUBLE PRECISION DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS avg_pages_crawled DOUBLE PRECISION DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS duplicate_percentage DOUBLE PRECISION DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS invalid_records INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS fallback_usage_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS retry_frequency DOUBLE PRECISION DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS api_detection_rate DOUBLE PRECISION DEFAULT 0.0;
