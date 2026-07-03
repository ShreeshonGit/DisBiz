from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
import httpx
from app.repositories.scrape_job_repository import ScrapeJobRepository
import logging

logger = logging.getLogger(__name__)

class ScraperRecoveryManager:
    """
    Manages failure classification, error retries, checkpoint updates,
    and recovery tracking in the database for scraper jobs.
    """

    def __init__(self) -> None:
        self.job_repo = ScrapeJobRepository()

    def classify_exception(self, exc: Exception) -> str:
        """
        Classifies exceptions into standard error categories:
        NETWORK_ERROR, TIMEOUT_ERROR, SELECTOR_ERROR, or PARSE_ERROR.
        """
        exc_name = type(exc).__name__.lower()
        exc_str = str(exc).lower()

        if isinstance(exc, (httpx.ConnectError, httpx.ConnectTimeout, httpx.NetworkError)):
            return "NETWORK_ERROR"
        elif isinstance(exc, (httpx.TimeoutException, httpx.ReadTimeout, httpx.WriteTimeout)):
            return "TIMEOUT_ERROR"
        elif "selector" in exc_str or "soup" in exc_str or "attributeerror" in exc_name:
            return "SELECTOR_ERROR"
        else:
            return "PARSE_ERROR"

    def update_checkpoint(self, job_id: UUID, page_number: int) -> None:
        """
        Saves the last successful page index to the database as a recovery checkpoint.
        """
        try:
            self.job_repo.update(job_id, {
                "last_successful_page": page_number
            })
            logger.info(f"Job {job_id} checkpoint updated: last_successful_page = {page_number}")
        except Exception as e:
            logger.error(f"Failed to update checkpoint for job {job_id}: {e}")

    def record_failure(self, job_id: UUID, exception: Exception, retry_count: int, last_page: int) -> str:
        """
        Classifies the error, formats the details, and records the failure parameters in the database.
        """
        failure_type = self.classify_exception(exception)
        error_msg = f"{failure_type}: {str(exception)}"

        try:
            self.job_repo.update(job_id, {
                "failure_reason": failure_type,
                "error_message": error_msg,
                "error_log": error_msg,
                "retry_count": retry_count,
                "last_successful_page": last_page
            })
            logger.info(f"Job {job_id} failure recorded: {failure_type} (Page {last_page}, Retry {retry_count})")
        except Exception as e:
            logger.error(f"Failed to save failure details for job {job_id}: {e}")

        return failure_type
