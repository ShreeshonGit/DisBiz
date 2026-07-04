from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from fastapi import BackgroundTasks

from app.repositories.brand_repository import BrandRepository
from app.repositories.scraper_config_repository import ScraperConfigRepository
from app.repositories.scrape_job_repository import ScrapeJobRepository
from app.scrapers.scraper_factory import ScraperFactory
from app.schemas.scrape_schema import AutoDetectResponse, PreviewResponse, PreviewDealer
from app.services.scraper_job_runner import ScraperJobRunner
import logging

logger = logging.getLogger(__name__)

class ScrapingService:
    """
    Service layer coordinating all web scraping tasks, auto-detection,
    preview runs, background job queue trigger, and job management logs.
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
        brand = self.brand_repository.get_by_id(brand_id)
        if not brand:
            raise ValueError(f"Brand with ID {brand_id} not found.")

        url = brand["dealer_locator_url"]
        logger.info(f"Auto-detecting locator configuration for brand '{brand['name']}' at {url}")

        scraper = ScraperFactory.get_scraper(brand_id, brand["name"], url)
        locator_type = await scraper.detect_locator_type()
        
        suggested_scraper = "STATIC_HTML"
        if locator_type == "JAVASCRIPT":
            suggested_scraper = "PLAYWRIGHT"
        elif locator_type == "API":
            suggested_scraper = "API"

        config_data = {
            "scraper_type": suggested_scraper,
            "locator_type": locator_type,
            "parser_strategy": "JSON_PATH" if locator_type == "API" else "CSS_SELECTOR"
        }
        
        self.config_repository.upsert(brand_id, config_data)

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
        
        db_config = self.config_repository.get_by_brand_id(brand_id) or {}
        config = dict(db_config)
        
        if override_config:
            config.update(override_config)

        scraper = ScraperFactory.get_scraper(brand_id, brand["name"], url, config)
        scraper.log(f"Initialized preview job for brand '{brand['name']}'")

        try:
            from app.scrapers.normalizer import normalize_dealer
            from app.scrapers.validator import validate_dealer

            records = await scraper.preview(limit=10)
            scraper.log(f"Extraction successful. Retrieved {len(records)} preview records.")
            
            preview_dealers = []
            for item in records:
                normalized = normalize_dealer(item)
                is_valid, errors = validate_dealer(normalized)
                
                preview_dealers.append(PreviewDealer(
                    name=normalized.get("dealer_name") or "Unnamed Dealer",
                    address=normalized.get("address") or "No Address Provided",
                    city=normalized.get("city"),
                    state=normalized.get("state"),
                    pincode=normalized.get("pincode"),
                    phone=normalized.get("phone"),
                    email=normalized.get("email"),
                    latitude=normalized.get("latitude"),
                    longitude=normalized.get("longitude"),
                    validation_status="VALID" if is_valid else "INVALID",
                    validation_errors=errors
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

    async def start_scrape_job(self, brand_id: UUID, background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """
        Creates a new scrape job log in database as Queued, and triggers the background
        execution runner asynchronously.
        """
        brand = self.brand_repository.get_by_id(brand_id)
        if not brand:
            raise ValueError(f"Brand with ID {brand_id} not found.")

        # Prepare scrape job parameters
        now = datetime.now().isoformat()
        job_data = {
            "brand_id": str(brand_id),
            "status": "Queued",
            "started_at": now,
            "start_time": now,
            "records_found": 0,
            "records_saved": 0,
            "retry_count": 0
        }

        # Create record in DB
        created_job = self.job_repository.create(job_data)
        job_id = UUID(created_job["id"])

        logger.info(f"Queued scrape job {job_id} in database. Triggering background runner...")

        # Add runner to FastAPI BackgroundTasks queue
        runner = ScraperJobRunner()
        background_tasks.add_task(runner.run_job, job_id, brand_id)

        # Retrieve and return job details flattening brand name
        job_details = self.job_repository.get_by_id(job_id)
        return job_details if job_details else created_job

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

        # Update status to Cancelled in DB. The background thread will check
        # this state to halt execution.
        updated = self.job_repository.update(job_id, {"status": "Cancelled"})
        return updated
