import os
import asyncio
from uuid import UUID
from typing import Set

class ConcurrencyManager:
    """
    Manages job limits and prevents multiple concurrent scraper runs for the same brand.
    """
    def __init__(self) -> None:
        # Load max concurrent limits from environment
        try:
            self.max_concurrent_jobs = int(os.getenv("MAX_CONCURRENT_JOBS", "3"))
        except ValueError:
            self.max_concurrent_jobs = 3
            
        self.active_brands: Set[UUID] = set()
        self._lock = asyncio.Lock()

    async def acquire_brand(self, brand_id: UUID) -> bool:
        """
        Attempts to acquire an execution slot for the brand.
        Returns True if successful, False otherwise.
        """
        async with self._lock:
            # 1. Respect overall concurrency limits
            if len(self.active_brands) >= self.max_concurrent_jobs:
                return False
                
            # 2. Prevent duplicate execution of the same brand
            if brand_id in self.active_brands:
                return False
                
            self.active_brands.add(brand_id)
            return True

    async def release_brand(self, brand_id: UUID) -> None:
        """
        Releases the execution slot for the brand.
        """
        async with self._lock:
            self.active_brands.discard(brand_id)

    async def is_brand_running(self, brand_id: UUID) -> bool:
        async with self._lock:
            return brand_id in self.active_brands

    async def can_dispatch(self) -> bool:
        async with self._lock:
            return len(self.active_brands) < self.max_concurrent_jobs

    async def get_active_count(self) -> int:
        async with self._lock:
            return len(self.active_brands)
            
    async def get_active_brands(self) -> Set[UUID]:
        async with self._lock:
            return set(self.active_brands)
