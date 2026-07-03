import re
from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID

class IndustryEnum(str, Enum):
    CONSUMER_GOODS = "Consumer Goods"
    ELECTRONICS = "Electronics"
    RETAIL = "Retail"
    HEALTHCARE = "Healthcare"
    INDUSTRIAL = "Industrial"
    AUTOMOBILE = "Automobile"
    SPORTS = "Sports"
    HOME_LIVING = "Home & Living"
    FMCG = "FMCG"
    OTHER = "Other"

class CategoryEnum(str, Enum):
    MOBILE_PHONES = "Mobile Phones"
    CONSUMER_ELECTRONICS = "Consumer Electronics"
    FURNITURE = "Furniture"
    HOME_APPLIANCES = "Home Appliances"
    KITCHEN = "Kitchen"
    FOOTWEAR = "Footwear"
    FASHION = "Fashion"
    HEALTHCARE = "Healthcare"
    SPORTS = "Sports"
    INDUSTRIAL = "Industrial"
    OTHER = "Other"

class ScraperTypeEnum(str, Enum):
    STATIC_HTML = "STATIC_HTML"
    PLAYWRIGHT = "PLAYWRIGHT"
    API = "API"
    CUSTOM = "CUSTOM"

def generate_slug(name: str) -> str:
    """
    Generates a slug from a brand name.
    Converts to lowercase, removes non-alphanumeric chars, and replaces spaces/hyphens.
    """
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '-', slug)
    return slug

class BrandBase(BaseModel):
    name: str = Field(..., min_length=1, description="Unique name of the brand")
    official_website: str = Field(..., description="Official website URL")
    dealer_locator_url: str = Field(..., description="Dealer locator URL")
    industry: IndustryEnum = Field(..., description="Industry of the brand")
    category: CategoryEnum = Field(..., description="Category of the brand")
    logo_url: Optional[str] = Field(None, description="Optional logo image URL")
    notes: Optional[str] = Field(None, description="Optional administrative notes")
    scraper_type: ScraperTypeEnum = Field(ScraperTypeEnum.STATIC_HTML, description="Scraper engine type")
    scrape_frequency: int = Field(7, ge=1, description="Scraping frequency in days")
    scraper_enabled: bool = Field(True, description="Whether automated scraping is enabled")
    active: bool = Field(True, description="Whether the brand is active on the public page")

    @field_validator("official_website", "dealer_locator_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        url_regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ip
            r'(?::\d+)?'  # port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not url_regex.match(v):
            raise ValueError("Must be a valid absolute HTTP or HTTPS URL")
        return v

    @field_validator("logo_url")
    @classmethod
    def validate_logo_url(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        url_regex = re.compile(
            r'^(?:http|ftp)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not url_regex.match(v):
            raise ValueError("Logo URL must be a valid absolute HTTP or HTTPS URL")
        return v

class BrandCreate(BrandBase):
    pass

class BrandUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    official_website: Optional[str] = None
    dealer_locator_url: Optional[str] = None
    industry: Optional[IndustryEnum] = None
    category: Optional[CategoryEnum] = None
    logo_url: Optional[str] = None
    notes: Optional[str] = None
    scraper_type: Optional[ScraperTypeEnum] = None
    scrape_frequency: Optional[int] = Field(None, ge=1)
    scraper_enabled: Optional[bool] = None
    active: Optional[bool] = None

    @field_validator("official_website", "dealer_locator_url", "logo_url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        url_regex = re.compile(
            r'^(?:http|ftp)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not url_regex.match(v):
            raise ValueError("Must be a valid absolute HTTP or HTTPS URL")
        return v

class BrandResponse(BrandBase):
    id: UUID
    slug: str
    last_scraped: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
