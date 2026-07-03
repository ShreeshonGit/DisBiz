-- Migration: 002_add_scraper_tables.sql
-- Description: Create brand_keywords, dealers, and scrape_jobs tables linked to brands

-- Create brand_keywords table
CREATE TABLE IF NOT EXISTS brand_keywords (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID NOT NULL,
    keyword TEXT NOT NULL,
    priority INTEGER DEFAULT 100,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE CASCADE
);

-- Create dealers table
CREATE TABLE IF NOT EXISTS dealers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE,
    dealer_name TEXT NOT NULL,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    pincode TEXT NOT NULL,
    latitude DOUBLE PRECISION NULL,
    longitude DOUBLE PRECISION NULL,
    phone TEXT NULL,
    email TEXT NULL,
    website TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trigger for dealers updated_at
CREATE TRIGGER update_dealers_updated_at
    BEFORE UPDATE ON dealers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create scrape_jobs table
CREATE TABLE IF NOT EXISTS scrape_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE NULL,
    duration_seconds INTEGER NULL,
    records_found INTEGER DEFAULT 0,
    records_saved INTEGER DEFAULT 0,
    error_message TEXT NULL
);
