from typing import List, Dict, Any, Optional
from uuid import UUID
from app.database.supabase import supabase
import logging

logger = logging.getLogger(__name__)

class DealerRepository:
    """
    Repository layer for managing persistence of parsed dealer records in Supabase.
    """

    def _get_client(self) -> Any:
        if supabase is None:
            raise RuntimeError("Database connection not initialized.")
        return supabase

    def create_batch(self, brand_id: UUID, dealers: List[Dict[str, Any]]) -> int:
        """
        Bulk inserts multiple dealer records into the database.
        Splits data into chunks for memory-safe API execution.
        """
        if not dealers:
            return 0
        try:
            client = self._get_client()
            
            insert_rows = []
            for d in dealers:
                insert_rows.append({
                    "brand_id": str(brand_id),
                    "dealer_name": d.get("dealer_name"),
                    "address": d.get("address"),
                    "city": d.get("city") or "",
                    "state": d.get("state") or "",
                    "pincode": d.get("pincode") or "",
                    "latitude": d.get("latitude"),
                    "longitude": d.get("longitude"),
                    "phone": d.get("phone"),
                    "email": d.get("email"),
                    "website": d.get("website")
                })

            chunk_size = 100
            inserted_count = 0
            for i in range(0, len(insert_rows), chunk_size):
                chunk = insert_rows[i:i + chunk_size]
                res = client.table("dealers").insert(chunk).execute()
                if res.data:
                    inserted_count += len(res.data)
            logger.info(f"Successfully inserted {inserted_count} / {len(dealers)} dealers in database.")
            return inserted_count
        except Exception as e:
            logger.error(f"Error bulk inserting dealers for brand {brand_id}: {e}")
            raise e

    def get_by_brand_id(self, brand_id: UUID) -> List[Dict[str, Any]]:
        """
        Fetches all stored dealers matching a specific brand.
        """
        try:
            client = self._get_client()
            res = client.table("dealers").select("*").eq("brand_id", str(brand_id)).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Error fetching dealers for brand {brand_id}: {e}")
            raise e
