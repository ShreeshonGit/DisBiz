from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from app.database.supabase import supabase
import logging

logger = logging.getLogger(__name__)

class ScraperMetricsRepository:
    """
    Repository layer for managing scraper performance metrics.
    Includes advanced telemetry statistics like fuzzy duplicate ratios, response times,
    invalid counts, selector fallback occurrences, and API discovery rates.
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

    def upsert_metrics(
        self,
        brand_id: UUID,
        is_success: bool,
        runtime: float,
        records_scraped: int,
        response_time: float = 0.0,
        pages_crawled: int = 1,
        duplicate_percentage: float = 0.0,
        invalid_records: int = 0,
        fallback_usage: int = 0,
        retry_frequency: float = 0.0,
        api_detection_rate: float = 0.0
    ) -> Dict[str, Any]:
        """
        Updates (or creates) metrics for a brand, recalculating rolling moving averages.
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
                    "last_run_at": now_str,
                    "avg_response_time": float(response_time),
                    "avg_pages_crawled": float(pages_crawled),
                    "duplicate_percentage": float(duplicate_percentage),
                    "invalid_records": int(invalid_records),
                    "fallback_usage_count": int(fallback_usage),
                    "retry_frequency": float(retry_frequency),
                    "api_detection_rate": float(api_detection_rate)
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
                new_avg_resp_time = (existing.get("avg_response_time", 0.0) * total + response_time) / new_total
                new_avg_pages = (existing.get("avg_pages_crawled", 0.0) * total + pages_crawled) / new_total
                new_dup_pct = (existing.get("duplicate_percentage", 0.0) * total + duplicate_percentage) / new_total
                new_retry_freq = (existing.get("retry_frequency", 0.0) * total + retry_frequency) / new_total
                new_api_rate = (existing.get("api_detection_rate", 0.0) * total + api_detection_rate) / new_total

                update_data = {
                    "total_jobs": new_total,
                    "success_jobs": success_count,
                    "failed_jobs": failed_count,
                    "avg_runtime": float(new_avg_runtime),
                    "avg_records_scraped": float(new_avg_records),
                    "last_run_at": now_str,
                    "avg_response_time": float(new_avg_resp_time),
                    "avg_pages_crawled": float(new_avg_pages),
                    "duplicate_percentage": float(new_dup_pct),
                    "invalid_records": existing.get("invalid_records", 0) + invalid_records,
                    "fallback_usage_count": existing.get("fallback_usage_count", 0) + fallback_usage,
                    "retry_frequency": float(new_retry_freq),
                    "api_detection_rate": float(new_api_rate)
                }
                
                res = client.table("scraper_metrics").update(update_data).eq("id", existing["id"]).execute()
                if res.data and len(res.data) > 0:
                    return res.data[0]
                raise ValueError("Failed to update existing scraper metrics.")
                
        except Exception as e:
            logger.error(f"Error updating metrics for brand {brand_id}: {e}")
            raise e
