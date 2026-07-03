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
                    "website": d.get("website"),
                    "formatted_address": d.get("formatted_address") or d.get("address"),
                    "country": d.get("country") or "India",
                    "quality_score": d.get("quality_score") or 0
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

    def search(
        self,
        query: Optional[str] = None,
        brand_id: Optional[UUID] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        pincode: Optional[str] = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        page: int = 1,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Searches, filters, sorts and paginates dealer listings.
        """
        try:
            client = self._get_client()
            builder = client.table("dealers").select("*, brands(name)", count="exact")
            
            if brand_id:
                builder = builder.eq("brand_id", str(brand_id))
                
            if city:
                builder = builder.ilike("city", f"%{city}%")
                
            if state:
                builder = builder.ilike("state", f"%{state}%")
                
            if pincode:
                builder = builder.eq("pincode", pincode)
                
            if query:
                or_query = f"dealer_name.ilike.%{query}%,city.ilike.%{query}%,state.ilike.%{query}%,pincode.eq.{query}"
                builder = builder.or_(or_query)

            col_map = {
                "name": "dealer_name",
                "quality_score": "quality_score",
                "created_at": "created_at"
            }
            order_col = col_map.get(sort_by, "dealer_name")
            desc_val = (sort_order == "desc")
            
            builder = builder.order(order_col, desc=desc_val)
            
            offset = (page - 1) * limit
            builder = builder.range(offset, offset + limit - 1)
            
            res = builder.execute()
            dealers = res.data or []
            total = res.count or 0
            
            for d in dealers:
                brand_info = d.get("brands")
                if brand_info and isinstance(brand_info, dict):
                    d["brand_name"] = brand_info.get("name")
                else:
                    d["brand_name"] = "Unknown Brand"
                    
            return {
                "total": total,
                "page": page,
                "limit": limit,
                "dealers": dealers
            }
        except Exception as e:
            logger.error(f"Error searching dealers: {e}")
            raise e
