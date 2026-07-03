-- Migration: 004_create_scraper_configs.sql
-- Description: Create scraper_configs table for managing brand locator parsing parameters

CREATE TABLE IF NOT EXISTS scraper_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID UNIQUE NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    scraper_type TEXT NOT NULL DEFAULT 'STATIC_HTML',
    locator_type TEXT NOT NULL DEFAULT 'UNKNOWN',
    parser_strategy TEXT NOT NULL DEFAULT 'CSS_SELECTOR',
    css_selector_config JSONB NULL,
    enabled BOOLEAN DEFAULT TRUE,
    notes TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trigger for scraper_configs updated_at
CREATE TRIGGER update_scraper_configs_updated_at
    BEFORE UPDATE ON scraper_configs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Index on brand_id
CREATE INDEX IF NOT EXISTS idx_scraper_configs_brand_id ON scraper_configs(brand_id);
