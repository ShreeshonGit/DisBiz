import asyncio
import logging
from datetime import datetime
from uuid import UUID
from typing import Dict, Any, List, Optional

from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.scrape_job_repository import ScrapeJobRepository
from app.repositories.brand_repository import BrandRepository
from app.scheduler.cron_parser import calculate_next_run
from app.scheduler.job_queue import JobQueue
from app.scheduler.concurrency_manager import ConcurrencyManager
from app.scheduler.worker import Worker
from app.scheduler.scheduler_monitor import SchedulerMonitor
from app.scheduler.job_dispatcher import JobDispatcher

logger = logging.getLogger(__name__)

class SchedulerEngine:
    """
    Intelligent Scheduler Engine. Coordinates job queues, cron triggers, 
    recovery sequences, and active worker pools.
    """
    _instance: Optional["SchedulerEngine"] = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SchedulerEngine, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized") and self._initialized:
            return
            
        self.schedule_repo = ScheduleRepository()
        self.job_repo = ScrapeJobRepository()
        self.brand_repo = BrandRepository()
        
        # Subsystems
        self.queue = JobQueue()
        self.concurrency = ConcurrencyManager()
        self.worker = Worker(self.schedule_repo, self.job_repo)
        self.monitor = SchedulerMonitor()
        self.dispatcher = JobDispatcher(self.queue, self.concurrency, self.worker, self.monitor)
        
        # Hook up dispatcher callback
        self.dispatcher.set_event_callback(self.handle_dispatcher_event)
        
        self.running = False
        self._cron_task: Optional[asyncio.Task] = None
        self.sse_queues: List[asyncio.Queue] = []
        self._initialized = True

    def _log(self, tag: str, message: str, level: int = logging.INFO) -> None:
        msg = f"[{tag}] {message}"
        logger.log(level, msg)
        print(msg, flush=True)

    async def start(self) -> None:
        """Starts loops and recovers pending queue."""
        if self.running:
            return
        self.running = True
        self._log("Scheduler", "Starting Intelligent Scheduler Engine...")
        
        # 1. Recovery: Restore active schedules
        await self.recover_scheduler_state()
        
        # 2. Start dispatcher loops
        await self.dispatcher.start()
        
        # 3. Start cron loop
        from app.utils.async_utils import safe_create_task
        self._cron_task = safe_create_task(self._cron_loop(), name="CronLoop")
        self._log("Scheduler", "Scheduler Engine successfully initialized.")

    async def stop(self) -> None:
        self.running = False
        await self.dispatcher.stop()
        if self._cron_task:
            self._cron_task.cancel()
            try:
                await self._cron_task
            except asyncio.CancelledError:
                pass
        self._log("Scheduler", "Stopped Scheduler Engine.")

    async def recover_scheduler_state(self) -> None:
        """
        Scans DB on restart to fix status and calculate missing next runs.
        """
        self._log("Recovery", "Running engine database diagnostics...")
        try:
            now = datetime.now()
            schedules = self.schedule_repo.get_active_schedules()
            for s in schedules:
                if not s.get("next_run") or s.get("status") == "Running":
                    next_run = calculate_next_run(s["cron_expression"], now)
                    self.schedule_repo.update(s["id"], {
                        "next_run": next_run.isoformat(),
                        "status": "ACTIVE"
                    })
                    self._log("Recovery", f"Recovered schedule {s['schedule_name']}: next run set to {next_run}.")
        except Exception as e:
            self._log("Recovery", f"Recovery routine failed: {e}", logging.ERROR)

    async def _cron_loop(self) -> None:
        """
        Check schedules next_run every 10 seconds.
        """
        while self.running:
            try:
                now = datetime.now()
                schedules = self.schedule_repo.get_active_schedules()
                for s in schedules:
                    if not s.get("enabled"):
                        continue
                        
                    next_run_str = s.get("next_run")
                    if not next_run_str:
                        continue
                        
                    next_run = datetime.fromisoformat(next_run_str.replace("Z", "+00:00")).replace(tzinfo=None)
                    if next_run <= now:
                        self._log("Scheduler", f"Schedule '{s['schedule_name']}' is due. Adding to queue.")
                        
                        new_next_run = calculate_next_run(s["cron_expression"], now)
                        self.schedule_repo.update(s["id"], {
                            "last_run": now.isoformat(),
                            "next_run": new_next_run.isoformat()
                        })
                        
                        await self.queue.enqueue(
                            brand_id=UUID(s["brand_id"]),
                            schedule_id=UUID(s["id"]),
                            priority=s.get("priority", "NORMAL"),
                            max_retries=s.get("max_retries", 3),
                            retry_delay_minutes=s.get("retry_delay_minutes", 5),
                            retry_policy=s.get("retry_policy", "EXPONENTIAL")
                        )
            except Exception as e:
                logger.error(f"[Scheduler] Error in cron loop: {e}")
                
            await asyncio.sleep(10)

    async def handle_dispatcher_event(self, event_data: Dict[str, Any]) -> None:
        """Pushes events to all listening Server-Sent Events (SSE) connections."""
        for q in list(self.sse_queues):
            try:
                await q.put(event_data)
            except Exception:
                self.sse_queues.remove(q)

    async def register_listener(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self.sse_queues.append(q)
        return q

    def unregister_listener(self, q: asyncio.Queue) -> None:
        if q in self.sse_queues:
            self.sse_queues.remove(q)
