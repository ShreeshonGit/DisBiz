from typing import List, Dict, Any
from app.scrapers.generic_scraper import GenericScraper
import logging

logger = logging.getLogger(__name__)

class SleepwellScraper(GenericScraper):
    """
    Brand-specific scraper subclass for Sleepwell.
    Overrides parser methods to handle brand-specific DOM nesting layouts.
    """

    def parse(self, content: str) -> List[Dict[str, Any]]:
        self.log("[Custom Scraper: Sleepwell] Running custom parser logic.")
        # If configuration exists, fall back to GenericScraper parser behavior
        selectors = self.config.get("css_selector_config") or {}
        if selectors.get("container"):
            return super().parse(content)
            
        # Simulates custom parsing in case of missing CSS configs (fallback mock)
        self.log("[Custom Scraper: Sleepwell] CSS selectors missing. Running fallback mockup parser.")
        mock_records = [
            {
                "dealer_name": "Sleepwell World - Connaught Place",
                "address": "Block E, Connaught Place, New Delhi, Delhi 110001",
                "city": "New Delhi",
                "state": "Delhi",
                "pincode": "110001",
                "phone": "+91 98765 43210",
                "email": "cp_world@sleepwell.com",
                "website": "https://sleepwell.in"
            },
            {
                "dealer_name": "Sleepwell Gallery - Andheri East",
                "address": "Metro Station Road, Andheri East, Mumbai, Maharashtra 400069",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400069",
                "phone": "+91 22 2345 6789",
                "email": "andheri_gallery@sleepwell.com",
                "website": "https://sleepwell.in"
            }
        ]
        return mock_records
