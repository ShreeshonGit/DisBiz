import os
import sys
import time
from datetime import datetime
from uuid import UUID
from typing import List, Dict, Any, Optional

from app.repositories.brand_repository import BrandRepository
from app.repositories.scraper_config_repository import ScraperConfigRepository
from app.repositories.scrape_job_repository import ScrapeJobRepository
from app.repositories.dealer_repository import DealerRepository
from app.repositories.scraper_metrics_repository import ScraperMetricsRepository
from app.scrapers.scraper_factory import ScraperFactory
from app.scrapers.normalizer import normalize_dealer
from app.scrapers.validator import validate_dealer
from app.services.scraper_recovery_manager import ScraperRecoveryManager
import logging

logger = logging.getLogger(__name__)

class ScraperJobRunner:
    """
    Background job execution runner. Coordinates asynchronous scraping executions,
    checkpoint saving, reliability failure classification, and performance metrics updates.
    """

    def __init__(self) -> None:
        self.brand_repo = BrandRepository()
        self.config_repo = ScraperConfigRepository()
        self.job_repo = ScrapeJobRepository()
        self.dealer_repo = DealerRepository()
        self.recovery_mgr = ScraperRecoveryManager()
        self.metrics_repo = ScraperMetricsRepository()

    async def run_job(self, job_id: UUID, brand_id: UUID) -> None:
        """
        Executes the scraping pipeline as a background task.
        """
        logs = []
        def log_info(msg: str):
            t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_line = f"[INFO] {msg}"
            logs.append(f"[{t}] {log_line}")
            logger.info(f"Job {job_id}: {log_line}")

        def log_warn(msg: str):
            t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_line = f"[WARN] {msg}"
            logs.append(f"[{t}] {log_line}")
            logger.warning(f"Job {job_id}: {log_line}")

        def log_error(msg: str):
            t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_line = f"[ERROR] {msg}"
            logs.append(f"[{t}] {log_line}")
            logger.error(f"Job {job_id}: {log_line}")

        start_time = datetime.now()
        log_info(f"Transitioning job {job_id} status to RUNNING.")

        # 1. Update state to Running
        try:
            self.job_repo.update(job_id, {
                "status": "Running",
                "start_time": start_time.isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to update job {job_id} status to Running: {e}")
            return

        # Fetch Brand details
        brand = self.brand_repo.get_by_id(brand_id)
        if not brand:
            err_msg = f"Brand with ID {brand_id} not found."
            log_error(err_msg)
            self._mark_failed(job_id, err_msg, logs, start_time, exception=ValueError(err_msg))
            return

        brand_name = brand["name"]
        url = brand["dealer_locator_url"]
        log_info(f"Starting scraper for brand: {brand_name}")
        log_info(f"Fetching locator URL: {url}")

        if await self._is_cancelled(job_id):
            log_warn("Job cancellation detected before loading configuration. Aborting.")
            return

        # Load Scraper config
        db_config = self.config_repo.get_by_brand_id(brand_id) or {}
        config = dict(db_config)
        
        # Enforce page limits
        max_pages = config.get("max_pages", 1)
        max_pages = min(max_pages, 5)
        config["max_pages"] = max_pages
        
        # Resolve Scraper
        try:
            scraper = ScraperFactory.get_scraper(brand_id, brand_name, url, config)
            log_info(f"Loaded config and resolved scraper of type: {scraper.__class__.__name__}")
        except Exception as e:
            err_msg = f"Failed to instantiate scraper: {e}"
            log_error(err_msg)
            self._mark_failed(job_id, err_msg, logs, start_time, exception=e)
            return

        if await self._is_cancelled(job_id):
            log_warn("Job cancellation detected. Aborting.")
            return

        # Execute Scraping with automatic Retry loops
        raw_records = []
        success = False
        retry_count = 0
        max_retries = 3

        while retry_count < max_retries and not success:
            if retry_count > 0:
                log_warn(f"Retry attempt {retry_count}/{max_retries}...")
            
            try:
                raw_records = await scraper.extract_dealers()
                success = True
            except Exception as e:
                retry_count += 1
                log_warn(f"Extraction failed on attempt {retry_count}: {e}")
                if retry_count < max_retries:
                    backoff = 2 ** retry_count
                    log_info(f"Waiting {backoff}s before retrying...")
                    time.sleep(backoff)
                else:
                    err_msg = f"Scraping extraction failed after {max_retries} attempts."
                    log_error(err_msg)
                    # Classify and record failure
                    self._mark_failed(job_id, err_msg, logs + scraper.logs, start_time, retry_count, exception=e)
                    return

        # Append scraper logs
        for line in scraper.logs:
            logs.append(line)

        # Check cancellation post-extraction
        if await self._is_cancelled(job_id):
            log_warn("Job cancellation detected. Data will not be saved.")
            return

        # Update checkpoint: count of loaded pages
        self.recovery_mgr.update_checkpoint(job_id, page_number=max_pages)

        # Run Data Normalization & Validation pipeline
        valid_dealers = []
        invalid_count = 0

        for idx, item in enumerate(raw_records):
            normalized = normalize_dealer(item)
            is_valid, errors = validate_dealer(normalized)

            if is_valid:
                valid_dealers.append(normalized)
            else:
                invalid_count += 1
                rejection_reason = ", ".join(errors)
                log_warn(f"Row {idx+1} ({normalized.get('dealer_name') or 'Unnamed'}) rejected. Reason: {rejection_reason}")

        if await self._is_cancelled(job_id):
            log_warn("Job cancellation detected. Aborting DB insert.")
            return

        # Insert records into database
        records_saved = 0
        if valid_dealers:
            log_info(f"Inserting {len(valid_dealers)} valid records into database...")
            try:
                records_saved = self.dealer_repo.create_batch(brand_id, valid_dealers)
                log_info(f"Successfully saved {records_saved} dealers into database.")
            except Exception as e:
                err_msg = f"Database bulk insert failed: {e}"
                log_error(err_msg)
                self._mark_failed(job_id, err_msg, logs, start_time, retry_count, exception=e)
                return
        else:
            log_warn("No valid dealer records to save.")

        # Update job to COMPLETED
        end_time = datetime.now()
        duration = int((end_time - start_time).total_seconds())
        log_info(f"Job completed successfully in {duration} seconds.")

        try:
            self.job_repo.update(job_id, {
                "status": "Completed",
                "completed_at": end_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "records_found": len(raw_records),
                "records_scraped": len(raw_records),
                "records_saved": records_saved,
                "execution_logs": logs,
                "retry_count": retry_count
            })
        except Exception as e:
            logger.error(f"Failed to update job {job_id} completion: {e}")

        # Update Scraper metrics: success
        try:
            self.metrics_repo.upsert_metrics(brand_id, is_success=True, runtime=duration, records_scraped=len(raw_records))
            logger.info(f"Metrics table successfully updated for brand {brand_id}.")
        except Exception as met_exc:
            logger.error(f"Failed to update metrics for success job: {met_exc}")

    async def _is_cancelled(self, job_id: UUID) -> bool:
        try:
            job = self.job_repo.get_by_id(job_id)
            return job is not None and job.get("status") == "Cancelled"
        except Exception:
            return False

    def _mark_failed(self, job_id: UUID, error_msg: str, logs: List[str], start_time: datetime, retries: int = 0, exception: Optional[Exception] = None) -> None:
        """Helper to record a job execution failure and update metrics."""
        end_time = datetime.now()
        duration = int((end_time - start_time).total_seconds())
        
        # Use recovery manager to record failure in DB
        exc = exception or RuntimeError(error_msg)
        self.recovery_mgr.record_failure(job_id, exc, retry_count=retries, last_page=0)
        
        # Update completion timestamps and logs
        try:
            self.job_repo.update(job_id, {
                "completed_at": end_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "execution_logs": logs
            })
        except Exception as e:
            logger.error(f"Failed to write final timestamps for failed job {job_id}: {e}")

        # Update Scraper metrics: failure
        try:
            # Extract brand_id
            job = self.job_repo.get_by_id(job_id)
            if job:
                brand_id = UUID(job["brand_id"])
                self.metrics_repo.upsert_metrics(brand_id, is_success=False, runtime=duration, records_scraped=0)
                logger.info(f"Metrics table successfully updated (failure) for brand {brand_id}.")
        except Exception as met_exc:
            logger.error(f"Failed to update metrics for failed job: {met_exc}")
