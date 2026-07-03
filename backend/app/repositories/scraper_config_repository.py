from typing import Optional, Dict, Any
from uuid import UUID
from app.database.supabase import supabase
import logging

logger = logging.getLogger(__name__)

class ScraperConfigRepository:
    """
    Repository layer for managing brand scraping configurations in the database.
    """

    def _get_client(self) -> Any:
        if supabase is None:
            raise RuntimeError("Database connection not initialized.")
        return supabase

    def get_by_brand_id(self, brand_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Fetches the scraping configuration for a specific brand.
        """
        try:
            client = self._get_client()
            res = client.table("scraper_configs").select("*").eq("brand_id", str(brand_id)).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            return None
        except Exception as e:
            logger.error(f"Error fetching scraper config for brand {brand_id}: {e}")
            raise e

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new scraper configuration.
        """
        try:
            client = self._get_client()
            res = client.table("scraper_configs").insert(data).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            raise ValueError("Failed to create scraper configuration.")
        except Exception as e:
            logger.error(f"Error creating scraper config: {e}")
            raise e

    def update(self, config_id: UUID, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing scraper configuration by its ID.
        """
        try:
            client = self._get_client()
            res = client.table("scraper_configs").update(data).eq("id", str(config_id)).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            raise ValueError(f"Failed to update scraper config with ID {config_id}.")
        except Exception as e:
            logger.error(f"Error updating scraper config {config_id}: {e}")
            raise e

    def upsert(self, brand_id: UUID, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inserts or updates the configuration for a given brand.
        """
        try:
            existing = self.get_by_brand_id(brand_id)
            if existing:
                return self.update(UUID(existing["id"]), data)
            else:
                data["brand_id"] = str(brand_id)
                return self.create(data)
        except Exception as e:
            logger.error(f"Error upserting scraper config for brand {brand_id}: {e}")
            raise e
