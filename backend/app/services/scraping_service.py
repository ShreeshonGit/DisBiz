from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
import time

from app.repositories.brand_repository import BrandRepository
from app.repositories.scraper_config_repository import ScraperConfigRepository
from app.repositories.scrape_job_repository import ScrapeJobRepository
from app.scrapers.scraper_factory import ScraperFactory
from app.schemas.scrape_schema import AutoDetectResponse, PreviewResponse, PreviewDealer
import logging

logger = logging.getLogger(__name__)

class ScrapingService:
    """
    Service layer coordinating all web scraping tasks, auto-detection,
    preview runs, and job management logs.
    """

    def __init__(self) -> None:
        self.brand_repository = BrandRepository()
        self.config_repository = ScraperConfigRepository()
        self.job_repository = ScrapeJobRepository()

    async def auto_detect_brand(self, brand_id: UUID) -> AutoDetectResponse:
        """
        Fetches the brand locator URL, connects to the site, classifies its rendering type,
        and saves/updates the configuration table.
        """
        # Fetch brand
        brand = self.brand_repository.get_by_id(brand_id)
        if not brand:
            raise ValueError(f"Brand with ID {brand_id} not found.")

        url = brand["dealer_locator_url"]
        logger.info(f"Auto-detecting locator configuration for brand '{brand['name']}' at {url}")

        # Instantiate generic scraper to run detection
        scraper = ScraperFactory.get_scraper(brand_id, brand["name"], url)
        locator_type = await scraper.detect_locator_type()
        
        # Suggest corresponding scraper engine
        suggested_scraper = "STATIC_HTML"
        if locator_type == "JAVASCRIPT":
            suggested_scraper = "PLAYWRIGHT"
        elif locator_type == "API":
            suggested_scraper = "API"

        # Update scraper_configs table
        config_data = {
            "scraper_type": suggested_scraper,
            "locator_type": locator_type,
            "parser_strategy": "JSON_PATH" if locator_type == "API" else "CSS_SELECTOR"
        }
        
        self.config_repository.upsert(brand_id, config_data)

        # Hit the site once more to check headers for response stats
        import httpx
        status_code = 200
        content_length = 0
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url, timeout=10)
                status_code = res.status_code
                content_length = len(res.content)
        except Exception:
            pass

        return AutoDetectResponse(
            brand_id=brand_id,
            locator_url=url,
            detected_locator_type=locator_type,
            suggested_scraper_type=suggested_scraper,
            status_code=status_code,
            content_length=content_length
        )

    async def preview_scrape(self, brand_id: UUID, override_config: Optional[Dict[str, Any]] = None) -> PreviewResponse:
        """
        Runs an in-memory preview scrape. Fetches the page and returns the first 10
        normalized and validated records. Logs all steps for diagnosis.
        """
        brand = self.brand_repository.get_by_id(brand_id)
        if not brand:
            raise ValueError(f"Brand with ID {brand_id} not found.")

        url = brand["dealer_locator_url"]
        
        # Load configuration
        db_config = self.config_repository.get_by_brand_id(brand_id) or {}
        config = dict(db_config)
        
        # Apply temporary overrides if passed (e.g. from UI testing modal)
        if override_config:
            config.update(override_config)

        logger.info(f"Running preview scrape for brand '{brand['name']}' using config: {config}")

        # Instantiate scraper via Factory
        scraper = ScraperFactory.get_scraper(brand_id, brand["name"], url, config)
        scraper.log(f"Initialized preview job for brand '{brand['name']}'")

        try:
            # Perform preview
            records = await scraper.preview(limit=10)
            scraper.log(f"Extraction successful. Retrieved {len(records)} preview records.")
            
            preview_dealers = []
            for item in records:
                preview_dealers.append(PreviewDealer(
                    name=item["dealer_name"],
                    address=item["address"],
                    city=item.get("city"),
                    state=item.get("state"),
                    pincode=item.get("pincode"),
                    phone=item.get("phone"),
                    email=item.get("email"),
                    latitude=item.get("latitude"),
                    longitude=item.get("longitude"),
                    validation_status=item["validation_status"],
                    validation_errors=item["validation_errors"]
                ))
            
            return PreviewResponse(
                brand_id=brand_id,
                brand_name=brand["name"],
                locator_url=url,
                total_extracted=len(preview_dealers),
                preview_records=preview_dealers,
                logs=scraper.logs
            )
        except Exception as e:
            scraper.log(f"CRITICAL ERROR during preview: {e}")
            raise ValueError(f"Preview scrape failed: {e}. Check execution logs:\n" + "\n".join(scraper.logs))

    def get_jobs(self) -> List[Dict[str, Any]]:
        """Retrieves history of all scraping runs."""
        return self.job_repository.get_all()

    def get_job_by_id(self, job_id: UUID) -> Dict[str, Any]:
        """Retrieves detail logs for a specific scrape job."""
        job = self.job_repository.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job with ID {job_id} not found.")
        return job

    def cancel_job(self, job_id: UUID) -> Dict[str, Any]:
        """Cancels a queued or currently executing scraping job."""
        job = self.job_repository.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job with ID {job_id} not found.")

        # Update status
        updated = self.job_repository.update(job_id, {"status": "Cancelled"})
        return updated
