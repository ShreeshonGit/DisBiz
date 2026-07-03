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
from app.scrapers.scraper_factory import ScraperFactory
from app.scrapers.normalizer import normalize_dealer
from app.scrapers.validator import validate_dealer
import logging

logger = logging.getLogger(__name__)

class ScraperJobRunner:
    """
    Background job execution runner. Enforces non-blocking execution,
    real-time job updates, record validations, bulk storage, and logging.
    """

    def __init__(self) -> None:
        self.brand_repo = BrandRepository()
        self.config_repo = ScraperConfigRepository()
        self.job_repo = ScrapeJobRepository()
        self.dealer_repo = DealerRepository()

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

        # 1. Transition state to RUNNING
        try:
            self.job_repo.update(job_id, {
                "status": "Running",
                "start_time": start_time.isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to update job {job_id} status to Running: {e}")
            return

        # Fetch Brand
        brand = self.brand_repo.get_by_id(brand_id)
        if not brand:
            err_msg = f"Brand with ID {brand_id} not found."
            log_error(err_msg)
            self._mark_failed(job_id, err_msg, logs, start_time)
            return

        brand_name = brand["name"]
        url = brand["dealer_locator_url"]
        log_info(f"Starting scraper for brand: {brand_name}")
        log_info(f"Fetching locator URL: {url}")

        # Check cancellation before fetching
        if await self._is_cancelled(job_id):
            log_warn("Job cancellation detected before loading configuration. Aborting.")
            return

        # Load Scraper Config
        db_config = self.config_repo.get_by_brand_id(brand_id) or {}
        config = dict(db_config)
        
        # Enforce safety limits (Max pages per scrape = 5)
        config["max_pages"] = 5
        
        # Resolve Scraper
        try:
            scraper = ScraperFactory.get_scraper(brand_id, brand_name, url, config)
            log_info(f"Loaded config and resolved scraper of type: {scraper.__class__.__name__}")
        except Exception as e:
            err_msg = f"Failed to instantiate scraper for {brand_name}: {e}"
            log_error(err_msg)
            self._mark_failed(job_id, err_msg, logs, start_time)
            return

        # Check cancellation
        if await self._is_cancelled(job_id):
            log_warn("Job cancellation detected. Aborting.")
            return

        # Execute Scraping with Retry support (max 3 retries)
        raw_records = []
        success = False
        retry_count = 0
        max_retries = 3

        while retry_count < max_retries and not success:
            if retry_count > 0:
                log_warn(f"Retry attempt {retry_count}/{max_retries}...")
            
            try:
                # Perform page fetch and parse
                # Under Sprint 3.1 & 3.2, extract_dealers parses HTML/API data
                raw_records = await scraper.extract_dealers()
                success = True
            except Exception as e:
                retry_count += 1
                log_warn(f"Extraction failed on attempt {retry_count}: {e}")
                if retry_count < max_retries:
                    # Exponential backoff wait
                    backoff = 2 ** retry_count
                    log_info(f"Waiting {backoff}s before retrying...")
                    time.sleep(backoff)
                else:
                    err_msg = f"Scraping extraction failed after {max_retries} attempts."
                    log_error(err_msg)
                    self._mark_failed(job_id, err_msg, logs + scraper.logs, start_time, retry_count)
                    return

        # Append scraper internal logs
        for line in scraper.logs:
            logs.append(line)

        log_info(f"Page source fetched. Parsed {len(raw_records)} raw dealer nodes.")

        # Check cancellation
        if await self._is_cancelled(job_id):
            log_warn("Job cancellation detected post-scraping. Data will not be saved.")
            return

        # 2. Run Data Processing Pipeline (Normalizer & Validator)
        valid_dealers = []
        invalid_count = 0

        for idx, item in enumerate(raw_records):
            # Normalization
            normalized = normalize_dealer(item)
            # Validation
            is_valid, errors = validate_dealer(normalized)

            if is_valid:
                valid_dealers.append(normalized)
            else:
                invalid_count += 1
                rejection_reason = ", ".join(errors)
                log_warn(f"Row {idx+1} ({normalized.get('dealer_name') or 'Unnamed'}) rejected. Reason: {rejection_reason}")

        log_info(f"Pipeline complete. Valid: {len(valid_dealers)} records. Invalid/Skipped: {invalid_count} records.")

        # Check cancellation before database write
        if await self._is_cancelled(job_id):
            log_warn("Job cancellation detected before DB insertion. Aborting.")
            return

        # 3. Insert valid dealers in Database
        records_saved = 0
        if valid_dealers:
            log_info(f"Inserting {len(valid_dealers)} valid records into database...")
            try:
                records_saved = self.dealer_repo.create_batch(brand_id, valid_dealers)
                log_info(f"Successfully saved {records_saved} dealers into database.")
            except Exception as e:
                err_msg = f"Database write failed during bulk insertion: {e}"
                log_error(err_msg)
                self._mark_failed(job_id, err_msg, logs, start_time, retry_count)
                return
        else:
            log_warn("No valid dealer records to save.")

        # 4. Update job to COMPLETED
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

    async def _is_cancelled(self, job_id: UUID) -> bool:
        """Helper to check if job state has been flipped to Cancelled in DB."""
        try:
            job = self.job_repo.get_by_id(job_id)
            return job is not None and job.get("status") == "Cancelled"
        except Exception:
            return False

    def _mark_failed(self, job_id: UUID, error_msg: str, logs: List[str], start_time: datetime, retries: int = 0) -> None:
        """Helper to record a job execution failure."""
        end_time = datetime.now()
        duration = int((end_time - start_time).total_seconds())
        try:
            self.job_repo.update(job_id, {
                "status": "Failed",
                "completed_at": end_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "error_message": error_msg,
                "error_log": error_msg,
                "execution_logs": logs,
                "retry_count": retries
            })
        except Exception as e:
            logger.error(f"Failed to write failure logs for job {job_id}: {e}")
