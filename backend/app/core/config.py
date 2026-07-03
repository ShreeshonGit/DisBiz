from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Dealer Discovery Platform API"
    API_V1_STR: str = "/api/v1"
    
    # CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Supabase Config
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    
    @field_validator("SUPABASE_URL", mode="before")
    @classmethod
    def clean_supabase_url(cls, v: str) -> str:
        if not v:
            return v
        v = v.strip()
        
        # Validation checks
        if "postgresql://" in v:
            raise ValueError("SUPABASE_URL must NOT contain 'postgresql://'. Use the HTTP API URL instead.")
        if "db." in v:
            raise ValueError("SUPABASE_URL must NOT contain 'db.'. Use the HTTP API URL instead.")
        
        # Automatically clean trailing /rest/v1 or trailing slashes
        v = v.rstrip("/")
        if v.endswith("/rest/v1"):
            v = v[:-8]
        v = v.rstrip("/")
        
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
