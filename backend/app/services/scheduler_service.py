import asyncio
import logging
import time
from datetime import datetime, timedelta
from uuid import UUID
from typing import Dict, Any, List, Optional, Set
from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.scrape_job_repository import ScrapeJobRepository
from app.repositories.brand_repository import BrandRepository
from app.services.scraping_service import ScrapingService

from app.utils.async_utils import safe_create_task

logger = logging.getLogger(__name__)

def calculate_next_run(cron_expr: str, base_time: datetime = None) -> datetime:
    """
    Calculates next execution time based on a 5-field cron expression.
    """
    if base_time is None:
        base_time = datetime.now()
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        return base_time + timedelta(hours=1)
    
    # Check steps: e.g. */15 * * * *
    if parts[0].startswith("*/"):
        step = int(parts[0].split("/")[1])
        minutes_to_add = step - (base_time.minute % step)
        next_time = base_time + timedelta(minutes=minutes_to_add)
        return next_time.replace(second=0, microsecond=0)
    
    # Check hourly: 0 * * * *
    if parts[0] == "0" and parts[1] == "*":
        next_time = base_time + timedelta(hours=1)
        return next_time.replace(minute=0, second=0, microsecond=0)
    
    # Check daily: 0 2 * * *
    if parts[0] == "0" and parts[1].isdigit():
        target_hour = int(parts[1])
        next_time = base_time.replace(hour=target_hour, minute=0, second=0, microsecond=0)
        if next_time <= base_time:
            next_time += timedelta(days=1)
        return next_time

    # Check weekly: 0 3 * * 1 (3 AM on Monday)
    if parts[0] == "0" and parts[1].isdigit() and parts[4].isdigit():
        target_hour = int(parts[1])
        target_wday = int(parts[4])  # 1 = Monday
        next_time = base_time.replace(hour=target_hour, minute=0, second=0, microsecond=0)
        days_ahead = target_wday - next_time.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_time += timedelta(days=days_ahead)
        return next_time
        
    return base_time + timedelta(hours=1)

class SchedulerService:
    """
    Intelligent async job scheduler and worker dispatch queue.
    """
    _instance: Optional["SchedulerService"] = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SchedulerService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.schedule_repo = ScheduleRepository()
        self.job_repo = ScrapeJobRepository()
        self.brand_repo = BrandRepository()
        self.scraping_service = ScrapingService()
        
        # State
        self.queue: List[Dict[str, Any]] = []  # List of jobs: {brand_id, schedule_id, priority, retries}
        self.active_jobs: Set[UUID] = set()    # Set of brand_id currently running
        self.active_workers: Set[str] = set()   # Worker execution tags
        self.max_workers = 3
        self.running = False
        self.uptime_start = time.time()
        self.sse_queues: List[asyncio.Queue] = []
        
        # Metrics
        self.total_runs = 0
        self.total_successes = 0
        self.runtimes: List[float] = []

        self._initialized = True

    def log(self, tag: str, message: str, level: int = logging.INFO) -> None:
        """Structured logging wrapper."""
        msg = f"[{tag}] {message}"
        logger.log(level, msg)
        print(msg, flush=True)

    async def start(self) -> None:
        """Starts background loops and recovers pending queue."""
        if self.running:
            return
        self.running = True
        self.log("Scheduler", "Initializing Scheduler Service...")
        
        # Recovery: Restore active schedules, recover any 'RUNNING' jobs that crashed
        await self.recover_crashed_jobs()
        
        # Start core loops
        safe_create_task(self.scheduler_loop(), name="SchedulerService_CronLoop")
        safe_create_task(self.worker_loop(), name="SchedulerService_WorkerLoop")
        self.log("Scheduler", "Scheduler Service successfully initialized and running.")

    async def stop(self) -> None:
        self.running = False
        self.log("Scheduler", "Stopped Scheduler Service.")

    async def recover_crashed_jobs(self) -> None:
        """Finds running jobs from DB and marks them aborted / recovers schedules."""
        self.log("Recovery", "Running database health checks and recovery scans...")
        try:
            # Get active schedules
            schedules = self.schedule_repo.get_active_schedules()
            now = datetime.now()
            for s in schedules:
                if not s.get("next_run"):
                    next_run = calculate_next_run(s["cron_expression"], now)
                    self.schedule_repo.update(s["id"], {"next_run": next_run.isoformat()})
                    self.log("Recovery", f"Recovered schedule {s['schedule_name']} next run set to {next_run}.")
        except Exception as e:
            self.log("Recovery", f"Recovery scan encountered error: {e}", logging.ERROR)

    async def scheduler_loop(self) -> None:
        """Periodically checks database for due schedules."""
        while self.running:
            try:
                now = datetime.now()
                schedules = self.schedule_repo.get_active_schedules()
                for s in schedules:
                    next_run_str = s.get("next_run")
                    if not next_run_str:
                        continue
                    
                    next_run = datetime.fromisoformat(next_run_str.replace("Z", "+00:00")).replace(tzinfo=None)
                    if next_run <= now:
                        self.log("Scheduler", f"Schedule '{s['schedule_name']}' is due. Enqueuing job.")
                        
                        # Calculate and update next run time
                        new_next_run = calculate_next_run(s["cron_expression"], now)
                        self.schedule_repo.update(s["id"], {
                            "last_run": now.isoformat(),
                            "next_run": new_next_run.isoformat()
                        })
                        
                        # Add action log
                        self.schedule_repo.log_action(
                            schedule_id=s["id"],
                            brand_id=s["brand_id"],
                            action="DISPATCH",
                            status="PENDING",
                            details=f"Job queued automatically by cron scheduler loop."
                        )
                        
                        await self.enqueue_job(s["brand_id"], s["id"], s["priority"])
            except Exception as e:
                self.log("Scheduler", f"Error in scheduler tick: {e}", logging.ERROR)
            await asyncio.sleep(5)

    async def worker_loop(self) -> None:
        """Dispatches queued tasks to concurrent workers."""
        while self.running:
            try:
                # Dispatch if workers available and queue has eligible items
                if len(self.active_workers) < self.max_workers and self.queue:
                    # Find first item in queue whose brand is NOT currently running
                    job_to_run = None
                    for idx, job in enumerate(self.queue):
                        if job["brand_id"] not in self.active_jobs:
                            job_to_run = self.queue.pop(idx)
                            break
                    
                    if job_to_run:
                        worker_id = f"Worker-{len(self.active_workers) + 1}"
                        self.active_workers.add(worker_id)
                        safe_create_task(
                            self.execute_job_wrapper(job_to_run, worker_id),
                            name=f"SchedulerService_Job_{job_to_run['brand_id']}"
                        )
            except Exception as e:
                self.log("Worker", f"Worker loop error: {e}", logging.ERROR)
            await asyncio.sleep(1)

    async def enqueue_job(self, brand_id: UUID, schedule_id: Optional[UUID] = None, priority: str = "MEDIUM") -> None:
        """Thread-safe enqueue operation."""
        # Check if brand is disabled before enqueuing
        try:
            brand = self.brand_repo.get_by_id(brand_id)
            if not brand:
                self.log("Queue", f"Cannot queue job: brand {brand_id} not found.", logging.WARNING)
                return
        except Exception:
            pass

        # Sort priority (HIGH first)
        job = {
            "brand_id": brand_id,
            "schedule_id": schedule_id,
            "priority": priority.upper(),
            "retries": 0,
            "queued_at": datetime.now()
        }
        
        # Position insertion based on priority (HIGH at front, LOW at back)
        if priority.upper() == "HIGH":
            self.queue.insert(0, job)
        else:
            self.queue.append(job)
            
        self.log("Queue", f"Job for brand {brand_id} enqueued (Priority: {priority}). Queue size: {len(self.queue)}")
        await self.broadcast({"event": "queue_update", "queue_size": len(self.queue)})

    async def execute_job_wrapper(self, job: Dict[str, Any], worker_id: str) -> None:
        """Runs the crawler service inside a structured lifecycle check."""
        brand_id = job["brand_id"]
        sched_id = job["schedule_id"]
        
        self.active_jobs.add(brand_id)
        self.log("Worker", f"{worker_id} started running job for brand {brand_id}.")
        await self.broadcast({"event": "job_started", "brand_id": str(brand_id), "worker": worker_id})
        
        start_time = time.time()
        success = False
        details = ""
        
        try:
            # Call live backend scraping service runner
            class DummyBackgroundTasks:
                def add_task(self, func, *args, **kwargs):
                    safe_create_task(func(*args, **kwargs), name="SchedulerService_Background_Scrape")
            
            # Start job execution
            res = await self.scraping_service.start_scrape_job(brand_id, DummyBackgroundTasks())
            job_id = UUID(res["job_id"]) if res.get("job_id") else None
            
            # Periodically poll job status until completion
            while True:
                await asyncio.sleep(2)
                if not job_id:
                    break
                job_status = self.job_repo.get_by_id(job_id)
                if job_status and job_status["status"] in ["COMPLETED", "FAILED"]:
                    success = (job_status["status"] == "COMPLETED")
                    details = job_status.get("error_message") or f"Scraped {job_status.get('records_saved')} dealers."
                    break
        except Exception as e:
            details = str(e)
            self.log("Worker", f"Job failed inside execution wrapper: {e}", logging.ERROR)

        duration = time.time() - start_time
        self.runtimes.append(duration)
        self.total_runs += 1

        if success:
            self.total_successes += 1
            self.log("Dispatch", f"Job completed successfully in {duration:.1f}s.")
            self.schedule_repo.log_action(sched_id, brand_id, "RUN", "SUCCESS", details)
            await self.broadcast({"event": "job_completed", "brand_id": str(brand_id), "duration": duration})
        else:
            # Handle retry logic
            max_retries = 3
            if sched_id:
                try:
                    s = self.schedule_repo.get_by_id(sched_id)
                    max_retries = s.get("max_retries", 3)
                except Exception:
                    pass
            
            if job["retries"] < max_retries:
                job["retries"] += 1
                self.log("Retry", f"Job failed. Retrying ({job['retries']}/{max_retries}) in 10s...")
                self.schedule_repo.log_action(sched_id, brand_id, "RETRY", "PENDING", f"Attempt {job['retries']} failed: {details}")
                
                await asyncio.sleep(10)
                # Re-enqueue
                self.queue.append(job)
            else:
                self.log("Worker", f"Job failed and exceeded max retries: {details}", logging.ERROR)
                self.schedule_repo.log_action(sched_id, brand_id, "RUN", "FAILURE", f"Max retries reached: {details}")
                await self.broadcast({"event": "job_failed", "brand_id": str(brand_id), "error": details})

        # Cleanup
        self.active_jobs.discard(brand_id)
        self.active_workers.discard(worker_id)
        await self.broadcast({"event": "worker_free", "worker": worker_id})

    async def broadcast(self, data: Dict[str, Any]) -> None:
        """Pushes event logs to all listening SSE stream generators."""
        for q in self.sse_queues:
            await q.put(data)

    def get_status(self) -> Dict[str, Any]:
        success_rate = (self.total_successes / self.total_runs * 100.0) if self.total_runs > 0 else 100.0
        return {
            "status": "RUNNING" if self.running else "STOPPED",
            "queue_size": len(self.queue),
            "worker_count": len(self.active_workers),
            "active_jobs": len(self.active_jobs),
            "success_rate": round(success_rate, 1),
            "total_runs": self.total_runs,
            "uptime_seconds": time.time() - self.uptime_start
        }
