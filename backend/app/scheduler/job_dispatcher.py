import asyncio
import logging
from typing import Dict, Any, Optional

from app.scheduler.job_queue import JobQueue
from app.scheduler.concurrency_manager import ConcurrencyManager
from app.scheduler.worker import Worker
from app.scheduler.scheduler_monitor import SchedulerMonitor
from app.utils.async_utils import safe_create_task

logger = logging.getLogger(__name__)

class JobDispatcher:
    """
    Scheduler Job Dispatcher. Polls the JobQueue and dispatches tasks to Worker instances.
    """
    def __init__(self, queue: JobQueue, concurrency: ConcurrencyManager, worker: Worker, monitor: SchedulerMonitor) -> None:
        self.queue = queue
        self.concurrency = concurrency
        self.worker = worker
        self.monitor = monitor
        self.running = False
        self._dispatch_task: Optional[asyncio.Task] = None
        self._on_event_cb = None

    def set_event_callback(self, cb) -> None:
        self._on_event_cb = cb

    async def start(self) -> None:
        if self.running:
            return
        self.running = True
        self._dispatch_task = safe_create_task(self._dispatch_loop(), name="JobDispatcher_Loop")
        logger.info("[Dispatch] JobDispatcher loop started.")

    async def stop(self) -> None:
        self.running = False
        if self._dispatch_task:
            self._dispatch_task.cancel()
            try:
                await self._dispatch_task
            except asyncio.CancelledError:
                pass
        logger.info("[Dispatch] JobDispatcher loop stopped.")

    async def _dispatch_loop(self) -> None:
        while self.running:
            try:
                # Check concurrency constraints and queue depth
                if await self.concurrency.can_dispatch() and await self.queue.size() > 0:
                    active_brands = list(await self.concurrency.get_active_brands())
                    
                    # Dequeue next job that is NOT already running
                    job = await self.queue.dequeue(active_brands)
                    if job:
                        brand_id = job["brand_id"]
                        
                        acquired = await self.concurrency.acquire_brand(brand_id)
                        if acquired:
                            # Start execution in background task
                            worker_id = f"Worker-{await self.concurrency.get_active_count()}"
                            safe_create_task(self._run_job_task(job, worker_id), name=f"Scraper_{brand_id}")
                        else:
                            # Re-enqueue if slot was not acquired
                            await self.queue.enqueue(
                                brand_id=brand_id,
                                schedule_id=job.get("schedule_id"),
                                priority=job.get("priority"),
                                max_retries=job.get("max_retries", 3),
                                retry_delay_minutes=job.get("retry_delay_minutes", 5),
                                retry_policy=job.get("retry_policy", "EXPONENTIAL")
                            )
            except Exception as e:
                logger.error(f"[Dispatch] Exception in loop: {e}")
                
            await asyncio.sleep(1)

    async def _run_job_task(self, job: Dict[str, Any], worker_id: str) -> None:
        brand_id = job["brand_id"]
        start_time = asyncio.get_event_loop().time()
        success = False
        
        try:
            async def worker_event_handler(event_data: Dict[str, Any]):
                if event_data["event"] == "enqueue_retry":
                    retry_job = event_data["job"]
                    await self.queue.enqueue(
                        brand_id=retry_job["brand_id"],
                        schedule_id=retry_job.get("schedule_id"),
                        priority=retry_job.get("priority"),
                        max_retries=retry_job.get("max_retries", 3),
                        retry_delay_minutes=retry_job.get("retry_delay_minutes", 5),
                        retry_policy=retry_job.get("retry_policy", "EXPONENTIAL")
                    )
                if self._on_event_cb:
                    await self._on_event_cb(event_data)

            success = await self.worker.execute_job(job, worker_id, worker_event_handler)
        except Exception as e:
            logger.error(f"[Dispatch] Worker crashed for brand {brand_id}: {e}")
        finally:
            duration = asyncio.get_event_loop().time() - start_time
            self.monitor.record_run(duration, success, job.get("retries", 0))
            await self.concurrency.release_brand(brand_id)
            if self._on_event_cb:
                await self._on_event_cb({"event": "worker_released", "worker_id": worker_id})
