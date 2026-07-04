import asyncio
from datetime import datetime
from uuid import UUID
from typing import Dict, Any, List, Optional

class JobQueue:
    """
    Priority job queue for scraper tasks.
    Supports HIGH, NORMAL, and LOW priorities.
    """
    def __init__(self) -> None:
        self._queue: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()
        
        # Priority weight map (lower value = higher priority)
        self.priority_weights = {
            "HIGH": 0,
            "NORMAL": 1,
            "LOW": 2
        }

    async def enqueue(self, brand_id: UUID, schedule_id: Optional[UUID] = None, priority: str = "NORMAL", max_retries: int = 3, retry_delay_minutes: int = 5, retry_policy: str = "EXPONENTIAL") -> None:
        """
        Enqueues a scraper job with given priority.
        """
        async with self._lock:
            # Check if this schedule is already in queue
            for job in self._queue:
                if job["brand_id"] == brand_id and job.get("schedule_id") == schedule_id:
                    # Already queued, skip to prevent double queuing
                    return

            priority_upper = priority.upper() if priority else "NORMAL"
            weight = self.priority_weights.get(priority_upper, 1)
            
            job = {
                "brand_id": brand_id,
                "schedule_id": schedule_id,
                "priority": priority_upper,
                "priority_weight": weight,
                "queued_at": datetime.now(),
                "retries": 0,
                "max_retries": max_retries,
                "retry_delay_minutes": retry_delay_minutes,
                "retry_policy": retry_policy
            }
            self._queue.append(job)
            # Sort O(n log n) by priority_weight and queued_at time
            self._queue.sort(key=lambda x: (x["priority_weight"], x["queued_at"]))

    async def dequeue(self, active_brands: List[UUID]) -> Optional[Dict[str, Any]]:
        """
        Pops the highest priority job whose brand is NOT in active_brands.
        """
        async with self._lock:
            for idx, job in enumerate(self._queue):
                if job["brand_id"] not in active_brands:
                    return self._queue.pop(idx)
            return None

    async def remove_by_schedule_id(self, schedule_id: UUID) -> bool:
        """
        Removes a job from the queue if matched by schedule_id.
        """
        async with self._lock:
            for idx, job in enumerate(self._queue):
                if job.get("schedule_id") == schedule_id:
                    self._queue.pop(idx)
                    return True
            return False

    async def get_items(self) -> List[Dict[str, Any]]:
        """Returns copy of queue elements."""
        async with self._lock:
            return list(self._queue)

    async def clear(self) -> None:
        async with self._lock:
            self._queue.clear()

    async def size(self) -> int:
        async with self._lock:
            return len(self._queue)
