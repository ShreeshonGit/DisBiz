import logging
from supabase import create_client, Client
from postgrest.exceptions import APIError
from app.core.config import settings

logger = logging.getLogger(__name__)

supabase: Client = None

# Print obfuscated SUPABASE_URL on startup
if settings.SUPABASE_URL:
    try:
        url_parts = settings.SUPABASE_URL.split("://")
        if len(url_parts) == 2:
            protocol, domain = url_parts
            domain_parts = domain.split(".")
            if len(domain_parts) > 0:
                subdomain = domain_parts[0]
                # Obfuscate the middle of the subdomain
                if len(subdomain) > 6:
                    masked_subdomain = subdomain[:5] + "*" * (len(subdomain) - 5)
                else:
                    masked_subdomain = subdomain[:2] + "***"
                masked_domain = ".".join([masked_subdomain] + domain_parts[1:])
                print(f"Loaded SUPABASE_URL: {protocol}://{masked_domain}")
    except Exception as e:
        logger.error(f"Error obfuscating SUPABASE_URL: {e}")
else:
    print("Loaded SUPABASE_URL: None")

# Initialize client using service role key
if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        print("Supabase client initialized successfully with SERVICE_ROLE_KEY.")
        
        # Startup test query
        print("Executing startup database connection test query...")
        try:
            supabase.table("brands").select("*").limit(1).execute()
            print("Database connection test: SUCCESS (table connection established)")
        except Exception as query_exc:
            print("\n---------------------------------------------------------")
            print("\033[91m\033[1m[CRITICAL DATABASE ERROR] Startup connection test failed!\033[0m")
            print("---------------------------------------------------------")
            
            # Construct final REST URL being requested
            rest_url = f"{settings.SUPABASE_URL}/rest/v1/brands?select=*&limit=1"
            print(f"Requested REST URL: {rest_url}")
            
            status_code = "Unknown"
            error_details = str(query_exc)
            
            if isinstance(query_exc, APIError):
                status_code = getattr(query_exc, "code", "Unknown PostgREST code")
                error_details = f"Code: {status_code}\nMessage: {query_exc.message}"
            
            print(f"HTTP/PostgREST Status Code: {status_code}")
            print(f"Error Details:\n{error_details}")
            print("---------------------------------------------------------\n")
            
    except Exception as init_exc:
        logger.error(f"Error initializing Supabase client: {init_exc}")
else:
    logger.warning("Supabase environment variables are missing. Client not initialized.")
