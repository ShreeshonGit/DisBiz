from typing import Dict, Any, Optional
from uuid import UUID
from app.scrapers.base_scraper import BaseScraper
from app.scrapers.generic_scraper import GenericScraper
from app.scrapers.sleepwell_scraper import SleepwellScraper
from app.scrapers.lava_scraper import LavaScraper
import logging

logger = logging.getLogger(__name__)

class ScraperFactory:
    """
    Factory class for instantiating the appropriate scraper type.
    Decides between custom brand specific scraper implementations
    or the fallback GenericScraper based on metadata.
    """

    @staticmethod
    def get_scraper(
        brand_id: UUID, 
        brand_name: str, 
        locator_url: str, 
        config: Optional[Dict[str, Any]] = None
    ) -> BaseScraper:
        """
        Builds and returns the proper scraper instance.
        """
        cfg = config or {}
        name_clean = brand_name.strip().lower()
        
        # Check custom scraper type config first or fall back to brand name matching
        scraper_type = cfg.get("scraper_type", "STATIC_HTML")
        
        if name_clean == "sleepwell":
            logger.info(f"Factory: Instantiating SleepwellScraper for brand {brand_name}")
            return SleepwellScraper(brand_id, brand_name, locator_url, cfg)
            
        elif name_clean == "lava":
            logger.info(f"Factory: Instantiating LavaScraper for brand {brand_name}")
            return LavaScraper(brand_id, brand_name, locator_url, cfg)
            
        # Extensible check: if scraper config requests a CUSTOM class, we fall back to generic
        # or load custom classes dynamically. In Sprint 3.1, generic is the master fallback.
        logger.info(f"Factory: Instantiating GenericScraper for brand {brand_name}")
        return GenericScraper(brand_id, brand_name, locator_url, cfg)
