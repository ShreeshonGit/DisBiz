import asyncio
import time
import logging
from datetime import datetime
from uuid import UUID
from typing import Dict, Any, Optional, Callable, Awaitable

from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.scrape_job_repository import ScrapeJobRepository
from app.services.scraper_job_runner import ScraperJobRunner
from app.scheduler.retry_manager import RetryManager
from app.scheduler.cron_parser import calculate_next_run
from app.utils.async_utils import safe_create_task

logger = logging.getLogger(__name__)

class Worker:
    """
    Worker task processor. Executes enqueued scraper jobs, records metrics, 
    and triggers scheduled retries.
    """
    def __init__(self, schedule_repo: ScheduleRepository, job_repo: ScrapeJobRepository) -> None:
        self.schedule_repo = schedule_repo
        self.job_repo = job_repo
        self.runner = ScraperJobRunner()

    def _log(self, tag: str, message: str, level: int = logging.INFO) -> None:
        msg = f"[{tag}] {message}"
        logger.log(level, msg)
        print(msg, flush=True)

    async def execute_job(self, job: Dict[str, Any], worker_id: str, on_event_cb: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None) -> bool:
        """
        Executes a scraper job with proper retry policy and logging.
        """
        brand_id = job["brand_id"]
        sched_id = job["schedule_id"]
        
        self._log("Worker", f"{worker_id} executing brand {brand_id}...")
        if on_event_cb:
            await on_event_cb({"event": "job_started", "brand_id": str(brand_id), "worker_id": worker_id})
            
        start_time = time.time()
        success = False
        error_msg = ""
        records_saved = 0
        job_id = None
        
        try:
            # Create scrape job record in database
            now_iso = datetime.now().isoformat()
            job_data = {
                "brand_id": str(brand_id),
                "status": "Running",
                "started_at": now_iso,
                "records_found": 0,
                "records_saved": 0,
                "retry_count": job.get("retries", 0)
            }
            created_job = self.job_repo.create(job_data)
            job_id = UUID(created_job["id"])
            
            # Log action
            self.schedule_repo.log_action(
                schedule_id=sched_id,
                brand_id=brand_id,
                job_id=job_id,
                event="DISPATCH",
                status="PENDING",
                message=f"Scraper job dispatched on {worker_id}."
            )
            
            # Execute scraper synchronously in worker task
            await self.runner.run_job(job_id, brand_id)
            
            # Poll status or check record
            job_status = self.job_repo.get_by_id(job_id)
            if job_status:
                if job_status["status"].upper() == "COMPLETED":
                    success = True
                    records_saved = job_status.get("records_saved", 0)
                else:
                    error_msg = job_status.get("error_message") or "Unknown scraper execution failure."
            else:
                error_msg = "Scraper job record not found post-execution."
                
        except Exception as e:
            error_msg = str(e)
            self._log("Worker", f"Scraper execution wrapper exception: {e}", logging.ERROR)

        duration = time.time() - start_time
        
        if success:
            self._log("Worker", f"Job completed successfully on {worker_id} in {duration:.1f}s.")
            if sched_id:
                now = datetime.now()
                # Calculate next run
                try:
                    s = self.schedule_repo.get_by_id(sched_id)
                    next_run = calculate_next_run(s["cron_expression"], now)
                    self.schedule_repo.update(sched_id, {
                        "last_run": now.isoformat(),
                        "next_run": next_run.isoformat(),
                        "last_success": now.isoformat(),
                        "status": "ACTIVE"
                    })
                except Exception as e:
                    self._log("Worker", f"Failed to update schedule runtimes: {e}", logging.ERROR)
                    
            self.schedule_repo.log_action(
                schedule_id=sched_id,
                brand_id=brand_id,
                job_id=job_id,
                event="RUN",
                status="SUCCESS",
                message=f"Job completed successfully. Extracted {records_saved} dealers.",
                execution_time=duration
            )
            if on_event_cb:
                await on_event_cb({"event": "job_completed", "brand_id": str(brand_id), "duration": duration})
            return True
        else:
            # Check if retry is allowed
            should_retry = RetryManager.should_retry(error_msg)
            max_retries = job.get("max_retries", 3)
            
            if should_retry and job["retries"] < max_retries:
                job["retries"] += 1
                delay_sec = RetryManager.calculate_retry_delay(
                    attempt=job["retries"],
                    base_delay_minutes=job.get("retry_delay_minutes", 5),
                    policy=job.get("retry_policy", "EXPONENTIAL")
                )
                self._log("Retry", f"Job failed: {error_msg}. Retrying in {delay_sec}s (Attempt {job['retries']}/{max_retries}).")
                
                self.schedule_repo.log_action(
                    schedule_id=sched_id,
                    brand_id=brand_id,
                    job_id=job_id,
                    event="RETRY",
                    status="PENDING",
                    message=f"Job failed: {error_msg}. Scheduled retry {job['retries']}/{max_retries} in {delay_sec}s."
                )
                if on_event_cb:
                    await on_event_cb({"event": "job_retrying", "brand_id": str(brand_id), "attempt": job["retries"], "delay": delay_sec})
                    
                # Schedule retry enqueuing
                async def delayed_enqueue():
                    await asyncio.sleep(delay_sec)
                    if on_event_cb:
                        await on_event_cb({"event": "enqueue_retry", "job": job})
                safe_create_task(delayed_enqueue(), name=f"RetryDelayedEnqueue_{brand_id}")
            else:
                self._log("Worker", f"Job failed permanently: {error_msg}")
                
                # Fire permanent failure & retry exhausted alerts
                try:
                    from app.services.notification_service import NotificationService
                    NotificationService.create_notification(
                        "schedule_failed",
                        f"Schedule run failed permanently: {error_msg}",
                        brand_id
                    )
                    if job.get("retries", 0) >= max_retries:
                        NotificationService.create_notification(
                            "retry_exhausted",
                            f"Scraper retries exhausted ({job.get('retries')}/{max_retries}) for brand ID {brand_id}.",
                            brand_id
                        )
                except Exception as n_err:
                    self._log("Worker", f"Failed to fire worker alerts: {n_err}", logging.ERROR)

                if sched_id:
                    now = datetime.now()
                    try:
                        s = self.schedule_repo.get_by_id(sched_id)
                        next_run = calculate_next_run(s["cron_expression"], now)
                        self.schedule_repo.update(sched_id, {
                            "last_run": now.isoformat(),
                            "next_run": next_run.isoformat(),
                            "last_failure": now.isoformat(),
                            "status": "FAILED"
                        })
                    except Exception as e:
                        self._log("Worker", f"Failed to update schedule runtimes: {e}", logging.ERROR)
                        
                self.schedule_repo.log_action(
                    schedule_id=sched_id,
                    brand_id=brand_id,
                    job_id=job_id,
                    event="RUN",
                    status="FAILURE",
                    message=f"Job failed permanently. Error: {error_msg}",
                    execution_time=duration
                )
                if on_event_cb:
                    await on_event_cb({"event": "job_failed", "brand_id": str(brand_id), "error": error_msg})
            return False
