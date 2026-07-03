from typing import List, Optional, Dict, Any
from uuid import UUID
from app.database.supabase import supabase
from postgrest.exceptions import APIError
import logging

logger = logging.getLogger(__name__)

class BrandRepository:
    """
    Repository layer for interacting with the Supabase 'brands' table.
    Enforces data layer constraints and handles connection logic.
    """

    def _get_client(self) -> Any:
        """Helper to ensure Supabase client is initialized."""
        if supabase is None:
            raise RuntimeError(
                "Database connection not initialized. Please verify SUPABASE_URL "
                "and SUPABASE_ANON_KEY in backend/.env"
            )
        return supabase

    def get_all(self) -> List[Dict[str, Any]]:
        """
        Retrieves all brands, sorted alphabetically by name.
        """
        try:
            client = self._get_client()
            response = client.table("brands").select("*").order("name").execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching all brands: {e}")
            raise e

    def get_by_id(self, brand_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single brand by its unique UUID.
        """
        try:
            client = self._get_client()
            response = client.table("brands").select("*").eq("id", str(brand_id)).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error fetching brand by ID {brand_id}: {e}")
            raise e

    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a brand by its unique name (case-insensitive check handled at Python/DB level).
        """
        try:
            client = self._get_client()
            response = client.table("brands").select("*").eq("name", name).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error fetching brand by name {name}: {e}")
            raise e

    def get_by_dealer_locator_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a brand by its unique dealer locator url.
        """
        try:
            client = self._get_client()
            response = client.table("brands").select("*").eq("dealer_locator_url", url).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error fetching brand by dealer locator URL {url}: {e}")
            raise e

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new brand record.
        """
        try:
            client = self._get_client()
            response = client.table("brands").insert(data).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            raise ValueError("Failed to create brand, empty response returned.")
        except APIError as ae:
            logger.error(f"Supabase APIError creating brand: {ae.message}")
            raise ae
        except Exception as e:
            logger.error(f"Unexpected error creating brand: {e}")
            raise e

    def update(self, brand_id: UUID, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Updates an existing brand by ID with partial details.
        """
        try:
            client = self._get_client()
            response = client.table("brands").update(data).eq("id", str(brand_id)).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except APIError as ae:
            logger.error(f"Supabase APIError updating brand {brand_id}: {ae.message}")
            raise ae
        except Exception as e:
            logger.error(f"Unexpected error updating brand {brand_id}: {e}")
            raise e

    def delete(self, brand_id: UUID) -> bool:
        """
        Deletes a brand by ID. Returns True if deleted, False otherwise.
        """
        try:
            client = self._get_client()
            response = client.table("brands").delete().eq("id", str(brand_id)).execute()
            return response.data is not None and len(response.data) > 0
        except Exception as e:
            logger.error(f"Error deleting brand {brand_id}: {e}")
            raise e
