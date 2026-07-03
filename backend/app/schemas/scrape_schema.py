from pydantic import BaseModel, Field
from typing import Any, List, Optional, Dict
from uuid import UUID
from datetime import datetime

class AutoDetectRequest(BaseModel):
    brand_id: UUID = Field(..., description="ID of the brand to perform auto-detection for")

class AutoDetectResponse(BaseModel):
    brand_id: UUID
    locator_url: str
    detected_locator_type: str = Field(..., description="STATIC_HTML, JAVASCRIPT, API, or UNKNOWN")
    suggested_scraper_type: str = Field(..., description="STATIC_HTML, PLAYWRIGHT, API, or CUSTOM")
    status_code: int
    content_length: int

class ScraperConfigBase(BaseModel):
    scraper_type: str = Field("STATIC_HTML", description="STATIC_HTML, PLAYWRIGHT, API, or CUSTOM")
    locator_type: str = Field("UNKNOWN", description="STATIC_HTML, JAVASCRIPT, API, or UNKNOWN")
    parser_strategy: str = Field("CSS_SELECTOR", description="CSS_SELECTOR, JSON_PATH, or BRAND_SPECIFIC")
    css_selector_config: Optional[Dict[str, Any]] = Field(None, description="CSS selector key-values config")
    enabled: bool = True
    notes: Optional[str] = None

class ScraperConfigCreate(ScraperConfigBase):
    brand_id: UUID

class ScraperConfigUpdate(BaseModel):
    scraper_type: Optional[str] = None
    locator_type: Optional[str] = None
    parser_strategy: Optional[str] = None
    css_selector_config: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    notes: Optional[str] = None

class ScraperConfigResponse(ScraperConfigBase):
    id: UUID
    brand_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PreviewRequest(BaseModel):
    brand_id: UUID = Field(..., description="ID of the brand to execute a preview scrape for")
    override_config: Optional[Dict[str, Any]] = Field(
        None, 
        description="Optional temporary overrides for CSS selectors during testing"
    )

class PreviewDealer(BaseModel):
    name: str
    address: str
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    validation_status: str = Field(..., description="VALID or INVALID")
    validation_errors: List[str] = Field(default_factory=list)

class PreviewResponse(BaseModel):
    brand_id: UUID
    brand_name: str
    locator_url: str
    total_extracted: int
    preview_records: List[PreviewDealer]
    logs: List[str]

class ScrapeJobResponse(BaseModel):
    id: UUID
    brand_id: UUID
    brand_name: Optional[str] = None
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    records_found: int
    records_saved: int
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
