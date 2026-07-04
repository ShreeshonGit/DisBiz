from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.brand_repository import BrandRepository
from app.scheduler.scheduler_engine import SchedulerEngine
from app.scheduler.cron_parser import calculate_next_run, validate_cron_expression

class ScheduleService:
    """
    Service layer coordinating brand schedule creation, lifecycle edits, 
    ad-hoc execution runs, status metrics, and log streams.
    """
    def __init__(self) -> None:
        self.repository = ScheduleRepository()
        self.brand_repo = BrandRepository()
        self.engine = SchedulerEngine()

    def get_all_schedules(self) -> List[Dict[str, Any]]:
        return self.repository.get_all()

    def get_schedule_by_id(self, schedule_id: UUID) -> Dict[str, Any]:
        schedule = self.repository.get_by_id(schedule_id)
        if not schedule:
            raise ValueError(f"Schedule with ID {schedule_id} not found.")
        return schedule

    def create_schedule(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates the cron expression, ensures target brand is active, 
        prevents duplicates, and calculates the first next run time.
        """
        brand_id = UUID(str(data["brand_id"]))
        brand = self.brand_repo.get_by_id(brand_id)
        if not brand:
            raise ValueError(f"Brand with ID {brand_id} not found.")
            
        # Validate Cron
        cron_expr = data["cron_expression"]
        is_valid, err = validate_cron_expression(cron_expr)
        if not is_valid:
            raise ValueError(f"Invalid cron expression '{cron_expr}': {err}")

        # Check duplicate schedule names per brand
        existing = self.repository.get_by_brand_id(brand_id)
        for s in existing:
            if s["schedule_name"].lower() == data["schedule_name"].lower():
                raise ValueError(f"A schedule named '{data['schedule_name']}' already exists for this brand.")

        # Compute next run
        now = datetime.now()
        data["next_run"] = calculate_next_run(cron_expr, now).isoformat()
        data["status"] = "ACTIVE"
        data["enabled"] = True

        created = self.repository.create(data)
        
        # Log schedule creation
        self.repository.log_action(
            schedule_id=UUID(created["id"]),
            brand_id=brand_id,
            action="CREATE",
            status="SUCCESS",
            details=f"Schedule created with expression '{cron_expr}'."
        )
        return created

    def update_schedule(self, schedule_id: UUID, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modifies schedule parameters and recalculates next runs if cron changes.
        """
        current = self.get_schedule_by_id(schedule_id)
        
        if "cron_expression" in data:
            cron_expr = data["cron_expression"]
            is_valid, err = validate_cron_expression(cron_expr)
            if not is_valid:
                raise ValueError(f"Invalid cron expression '{cron_expr}': {err}")
            
            # Recalculate next run
            now = datetime.now()
            data["next_run"] = calculate_next_run(cron_expr, now).isoformat()

        updated = self.repository.update(schedule_id, data)
        self.repository.log_action(
            schedule_id=schedule_id,
            brand_id=UUID(updated["brand_id"]),
            action="EDIT",
            status="SUCCESS",
            details="Schedule configuration modified."
        )
        return updated

    def delete_schedule(self, schedule_id: UUID) -> bool:
        schedule = self.get_schedule_by_id(schedule_id)
        brand_id = UUID(schedule["brand_id"])
        
        # Remove from queue if present
        try:
            from app.utils.async_utils import safe_create_task
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                safe_create_task(
                    self.engine.queue.remove_by_schedule_id(schedule_id),
                    name=f"QueueRemove_{schedule_id}"
                )
        except Exception:
            pass

        deleted = self.repository.delete(schedule_id)
        self.repository.log_action(
            schedule_id=None,
            brand_id=brand_id,
            action="DELETE",
            status="SUCCESS",
            details=f"Schedule '{schedule['schedule_name']}' deleted."
        )
        return deleted

    def pause_schedule(self, schedule_id: UUID) -> Dict[str, Any]:
        updated = self.repository.update(schedule_id, {
            "status": "PAUSED",
            "enabled": False
        })
        
        # Remove from queue
        try:
            from app.utils.async_utils import safe_create_task
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                safe_create_task(
                    self.engine.queue.remove_by_schedule_id(schedule_id),
                    name=f"QueueRemove_{schedule_id}"
                )
        except Exception:
            pass

        self.repository.log_action(
            schedule_id=schedule_id,
            brand_id=UUID(updated["brand_id"]),
            action="PAUSE",
            status="SUCCESS",
            details="Schedule manually paused."
        )
        return updated

    def resume_schedule(self, schedule_id: UUID) -> Dict[str, Any]:
        now = datetime.now()
        schedule = self.get_schedule_by_id(schedule_id)
        next_run = calculate_next_run(schedule["cron_expression"], now)
        
        updated = self.repository.update(schedule_id, {
            "status": "ACTIVE",
            "enabled": True,
            "next_run": next_run.isoformat()
        })
        self.repository.log_action(
            schedule_id=schedule_id,
            brand_id=UUID(updated["brand_id"]),
            action="RESUME",
            status="SUCCESS",
            details="Schedule manually resumed."
        )
        return updated

    async def run_schedule_now(self, schedule_id: UUID) -> Dict[str, Any]:
        """
        Manually injects the schedule's brand scraper job into the priority queue immediately.
        """
        schedule = self.get_schedule_by_id(schedule_id)
        brand_id = UUID(schedule["brand_id"])
        
        # Log manual trigger
        self.repository.log_action(
            schedule_id=schedule_id,
            brand_id=brand_id,
            action="RUN_NOW",
            status="PENDING",
            details="Manual ad-hoc run triggered."
        )
        
        # Enqueue with high priority
        await self.engine.queue.enqueue(
            brand_id=brand_id,
            schedule_id=schedule_id,
            priority="HIGH",
            max_retries=schedule.get("max_retries", 3),
            retry_delay_minutes=schedule.get("retry_delay_minutes", 5),
            retry_policy=schedule.get("retry_policy", "EXPONENTIAL")
        )
        return schedule

    def get_scheduler_status(self) -> Dict[str, Any]:
        queue_size = len(self.engine.queue._queue)
        active_workers = len(self.engine.concurrency.active_brands)
        max_workers = self.engine.concurrency.max_concurrent_jobs
        return self.engine.monitor.get_metrics(
            current_queue_size=queue_size,
            active_worker_count=active_workers,
            max_workers=max_workers
        )

    def get_scheduler_logs(self) -> List[Dict[str, Any]]:
        return self.repository.get_logs()
