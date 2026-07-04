from uuid import UUID
from typing import List, Dict, Any, Optional
from app.database.supabase import supabase
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Service layer coordinating scraper notifications and alert history.
    Stores alerts for job completions, failures, exhausted retries, and new dealer discoveries.
    """
    @staticmethod
    def create_notification(event_type: str, message: str, brand_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Creates and persists a notification alert.
        """
        try:
            if not supabase:
                raise RuntimeError("Supabase client not initialized")
            data = {
                "event_type": event_type,
                "message": message,
                "read": False
            }
            if brand_id:
                data["brand_id"] = str(brand_id)
            res = supabase.table("notifications").insert(data).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.error(f"Failed to create notification for event {event_type}: {e}")
        return {}

    @staticmethod
    def get_history(limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieves recent notification history, including brand names.
        """
        try:
            if not supabase:
                return []
            res = supabase.table("notifications").select("*, brands(name)").order("created_at", desc=True).limit(limit).execute()
            return res.data if res.data else []
        except Exception as e:
            logger.error(f"Failed to fetch notification history: {e}")
            return []

    @staticmethod
    def mark_as_read(notif_id: UUID) -> Dict[str, Any]:
        """
        Marks a specific notification as read.
        """
        try:
            if not supabase:
                return {}
            res = supabase.table("notifications").update({"read": True}).eq("id", str(notif_id)).execute()
            return res.data[0] if res.data else {}
        except Exception as e:
            logger.error(f"Failed to mark notification {notif_id} as read: {e}")
            return {}

    @staticmethod
    def mark_all_read() -> List[Dict[str, Any]]:
        """
        Marks all unread notifications as read.
        """
        try:
            if not supabase:
                return []
            res = supabase.table("notifications").update({"read": True}).eq("read", False).execute()
            return res.data if res.data else []
        except Exception as e:
            logger.error(f"Failed to mark all notifications read: {e}")
            return []
