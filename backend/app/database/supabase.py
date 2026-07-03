import logging
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)

supabase: Client = None

if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        logger.info("Supabase client initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing Supabase client: {e}")
else:
    logger.warning("Supabase environment variables are missing. Client not initialized.")
