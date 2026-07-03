from typing import List, Optional, Dict, Any
from uuid import UUID
from app.database.supabase import supabase
import logging

logger = logging.getLogger(__name__)

class ScrapeJobRepository:
    """
    Repository layer for managing scrape jobs tracking in the database.
    """

    def _get_client(self) -> Any:
        if supabase is None:
            raise RuntimeError("Database connection not initialized.")
        return supabase

    def get_all(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieves recent scrape jobs sorted by started_at descending, joining brand name.
        """
        try:
            client = self._get_client()
            res = client.table("scrape_jobs").select(
                "*, brands(name)"
            ).order("started_at", desc=True).limit(limit).execute()
            
            jobs = []
            if res.data:
                for row in res.data:
                    # Flatten the joined brand name
                    job_data = dict(row)
                    brand_info = job_data.pop("brands", None)
                    job_data["brand_name"] = brand_info.get("name") if brand_info else "Unknown Brand"
                    jobs.append(job_data)
            return jobs
        except Exception as e:
            logger.error(f"Error fetching scrape jobs: {e}")
            raise e

    def get_by_id(self, job_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieves a specific scrape job by its ID.
        """
        try:
            client = self._get_client()
            res = client.table("scrape_jobs").select("*, brands(name)").eq("id", str(job_id)).execute()
            if res.data and len(res.data) > 0:
                job_data = dict(res.data[0])
                brand_info = job_data.pop("brands", None)
                job_data["brand_name"] = brand_info.get("name") if brand_info else "Unknown Brand"
                return job_data
            return None
        except Exception as e:
            logger.error(f"Error fetching scrape job by ID {job_id}: {e}")
            raise e

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new scrape job log entry.
        """
        try:
            client = self._get_client()
            res = client.table("scrape_jobs").insert(data).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            raise ValueError("Failed to create scrape job record.")
        except Exception as e:
            logger.error(f"Error creating scrape job record: {e}")
            raise e

    def update(self, job_id: UUID, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing scrape job's fields (e.g. status, completed_at, records_found).
        """
        try:
            client = self._get_client()
            res = client.table("scrape_jobs").update(data).eq("id", str(job_id)).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            raise ValueError(f"Failed to update scrape job {job_id}.")
        except Exception as e:
            logger.error(f"Error updating scrape job {job_id}: {e}")
            raise e
