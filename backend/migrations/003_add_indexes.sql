-- Migration: 003_add_indexes.sql
-- Description: Create indexes for database search and query optimization

-- Indexes on brands table
CREATE INDEX IF NOT EXISTS idx_brands_slug ON brands(slug);

-- Indexes on brand_keywords table
CREATE INDEX IF NOT EXISTS idx_brand_keywords_brand_id ON brand_keywords(brand_id);

-- Indexes on dealers table
CREATE INDEX IF NOT EXISTS idx_dealers_brand_id ON dealers(brand_id);
CREATE INDEX IF NOT EXISTS idx_dealers_city_state ON dealers(city, state);

-- Indexes on scrape_jobs table
CREATE INDEX IF NOT EXISTS idx_scrape_jobs_brand_id ON scrape_jobs(brand_id);
