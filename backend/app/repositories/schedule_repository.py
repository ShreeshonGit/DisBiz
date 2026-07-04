from typing import List, Optional, Dict, Any
from uuid import UUID
from app.database.supabase import supabase
import logging

logger = logging.getLogger(__name__)

class ScheduleRepository:
    """
    Repository layer for managing scrape schedules and scheduler action logs in the database.
    """

    def _get_client(self) -> Any:
        if supabase is None:
            raise RuntimeError("Database connection not initialized.")
        return supabase

    def get_all(self) -> List[Dict[str, Any]]:
        """
        Retrieves all scrape schedules, joining brand name.
        """
        try:
            client = self._get_client()
            res = client.table("scrape_schedules").select("*, brands(name)").execute()
            
            schedules = []
            if res.data:
                for row in res.data:
                    sched = dict(row)
                    brand_info = sched.pop("brands", None)
                    sched["brand_name"] = brand_info.get("name") if brand_info else "Unknown Brand"
                    schedules.append(sched)
            return schedules
        except Exception as e:
            logger.error(f"Error fetching schedules: {e}")
            raise e

    def get_by_id(self, schedule_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieves a schedule by ID, joining brand name.
        """
        try:
            client = self._get_client()
            res = client.table("scrape_schedules").select("*, brands(name)").eq("id", str(schedule_id)).execute()
            if res.data and len(res.data) > 0:
                sched = dict(res.data[0])
                brand_info = sched.pop("brands", None)
                sched["brand_name"] = brand_info.get("name") if brand_info else "Unknown Brand"
                return sched
            return None
        except Exception as e:
            logger.error(f"Error fetching schedule by ID {schedule_id}: {e}")
            raise e

    def get_by_brand_id(self, brand_id: UUID) -> List[Dict[str, Any]]:
        """
        Retrieves schedules configured for a specific brand ID.
        """
        try:
            client = self._get_client()
            res = client.table("scrape_schedules").select("*").eq("brand_id", str(brand_id)).execute()
            return res.data if res.data else []
        except Exception as e:
            logger.error(f"Error fetching schedules by brand ID {brand_id}: {e}")
            raise e

    def get_active_schedules(self) -> List[Dict[str, Any]]:
        """
        Retrieves active schedules.
        """
        try:
            client = self._get_client()
            res = client.table("scrape_schedules").select("*, brands(name)").eq("status", "ACTIVE").execute()
            schedules = []
            if res.data:
                for row in res.data:
                    sched = dict(row)
                    brand_info = sched.pop("brands", None)
                    sched["brand_name"] = brand_info.get("name") if brand_info else "Unknown Brand"
                    schedules.append(sched)
            return schedules
        except Exception as e:
            logger.error(f"Error fetching active schedules: {e}")
            raise e

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new scrape schedule entry.
        """
        try:
            client = self._get_client()
            res = client.table("scrape_schedules").insert(data).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            raise ValueError("Failed to create scrape schedule.")
        except Exception as e:
            logger.error(f"Error creating schedule: {e}")
            raise e

    def update(self, schedule_id: UUID, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing schedule.
        """
        try:
            client = self._get_client()
            res = client.table("scrape_schedules").update(data).eq("id", str(schedule_id)).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            raise ValueError(f"Failed to update schedule {schedule_id}.")
        except Exception as e:
            logger.error(f"Error updating schedule {schedule_id}: {e}")
            raise e

    def delete(self, schedule_id: UUID) -> bool:
        """
        Deletes a schedule. Returns True if successful.
        """
        try:
            client = self._get_client()
            res = client.table("scrape_schedules").delete().eq("id", str(schedule_id)).execute()
            return res.data is not None and len(res.data) > 0
        except Exception as e:
            logger.error(f"Error deleting schedule {schedule_id}: {e}")
            raise e

    def log_action(self, schedule_id: Optional[UUID], brand_id: UUID, action: str, status: str, details: Optional[str] = None, job_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Inserts a new log entry into scheduler_logs.
        """
        try:
            client = self._get_client()
            log_entry = {
                "schedule_id": str(schedule_id) if schedule_id else None,
                "brand_id": str(brand_id),
                "action": action,
                "status": status,
                "details": details,
                "job_id": str(job_id) if job_id else None
            }
            res = client.table("scheduler_logs").insert(log_entry).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            raise ValueError("Failed to create scheduler action log.")
        except Exception as e:
            logger.error(f"Error creating scheduler log: {e}")
            raise e

    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieves recent logs sorted by created_at descending.
        """
        try:
            client = self._get_client()
            res = client.table("scheduler_logs").select("*").order("created_at", desc=True).limit(limit).execute()
            
            # Fetch brands to map brand_id to brand_name in memory
            brands_res = client.table("brands").select("id, name").execute()
            brand_map = {}
            if brands_res.data:
                for b in brands_res.data:
                    brand_map[str(b["id"])] = b["name"]

            logs = []
            if res.data:
                for row in res.data:
                    log_data = dict(row)
                    b_id = str(log_data.get("brand_id", ""))
                    log_data["brand_name"] = brand_map.get(b_id, "Unknown Brand")
                    logs.append(log_data)
            return logs
        except Exception as e:
            logger.error(f"Error fetching scheduler logs: {e}")
            raise e
