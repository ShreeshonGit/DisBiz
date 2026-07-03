-- Migration: 001_init_brands.sql
-- Description: Create the base brands table and updated_at trigger function

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create brands table
CREATE TABLE IF NOT EXISTS brands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    official_website TEXT NOT NULL,
    dealer_locator_url TEXT UNIQUE NOT NULL,
    logo_url TEXT NULL,
    industry TEXT NOT NULL,
    category TEXT NOT NULL,
    notes TEXT NULL,
    scraper_type TEXT DEFAULT 'STATIC_HTML',
    scrape_frequency INTEGER DEFAULT 7,
    scraper_enabled BOOLEAN DEFAULT TRUE,
    active BOOLEAN DEFAULT TRUE,
    last_scraped TIMESTAMP WITH TIME ZONE NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trigger for brands updated_at
CREATE TRIGGER update_brands_updated_at
    BEFORE UPDATE ON brands
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
