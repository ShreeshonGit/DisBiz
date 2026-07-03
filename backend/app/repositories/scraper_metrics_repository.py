from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from app.database.supabase import supabase
import logging

logger = logging.getLogger(__name__)

class ScraperMetricsRepository:
    """
    Repository layer for managing scraper performance metrics.
    """

    def _get_client(self) -> Any:
        if supabase is None:
            raise RuntimeError("Database connection not initialized.")
        return supabase

    def get_by_brand_id(self, brand_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieves performance metrics for a specific brand.
        """
        try:
            client = self._get_client()
            res = client.table("scraper_metrics").select("*").eq("brand_id", str(brand_id)).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            return None
        except Exception as e:
            logger.error(f"Error fetching scraper metrics for brand {brand_id}: {e}")
            raise e

    def upsert_metrics(self, brand_id: UUID, is_success: bool, runtime: float, records_scraped: int) -> Dict[str, Any]:
        """
        Updates (or creates) metrics for a brand, recalculating moving averages.
        """
        try:
            client = self._get_client()
            existing = self.get_by_brand_id(brand_id)
            now_str = datetime.now().isoformat()

            if not existing:
                insert_data = {
                    "brand_id": str(brand_id),
                    "total_jobs": 1,
                    "success_jobs": 1 if is_success else 0,
                    "failed_jobs": 0 if is_success else 1,
                    "avg_runtime": float(runtime),
                    "avg_records_scraped": float(records_scraped),
                    "last_run_at": now_str
                }
                res = client.table("scraper_metrics").insert(insert_data).execute()
                if res.data and len(res.data) > 0:
                    return res.data[0]
                raise ValueError("Failed to create new scraper metrics.")
            
            else:
                total = existing["total_jobs"]
                new_total = total + 1
                success_count = existing["success_jobs"] + (1 if is_success else 0)
                failed_count = existing["failed_jobs"] + (0 if is_success else 1)
                
                # Recalculate rolling moving averages
                new_avg_runtime = (existing["avg_runtime"] * total + runtime) / new_total
                new_avg_records = (existing["avg_records_scraped"] * total + records_scraped) / new_total

                update_data = {
                    "total_jobs": new_total,
                    "success_jobs": success_count,
                    "failed_jobs": failed_count,
                    "avg_runtime": float(new_avg_runtime),
                    "avg_records_scraped": float(new_avg_records),
                    "last_run_at": now_str
                }
                
                res = client.table("scraper_metrics").update(update_data).eq("id", existing["id"]).execute()
                if res.data and len(res.data) > 0:
                    return res.data[0]
                raise ValueError("Failed to update existing scraper metrics.")
                
        except Exception as e:
            logger.error(f"Error updating metrics for brand {brand_id}: {e}")
            raise e
