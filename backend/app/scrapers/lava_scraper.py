from typing import List, Dict, Any
from app.scrapers.generic_scraper import GenericScraper
from app.scrapers.utils import fetch_url_with_retry
from app.scrapers.normalizer import normalize_dealer
from app.scrapers.validator import validate_dealer
import httpx
import logging

logger = logging.getLogger(__name__)

class LavaScraper(GenericScraper):
    """
    Production-grade scraper for Lava Mobiles.
    Bypasses dynamic JS challenges by directly querying the backend API
    with correct headers and token credentials.
    """

    def parse(self, content: str) -> List[Dict[str, Any]]:
        self.log("[Custom Scraper: Lava] Parsing JSON API content.")
        try:
            import json
            data = json.loads(content)
            items = data.get("dealer_locator", [])
            
            raw_dealers = []
            for item in items:
                # Extract coordinates from map link: "lat,lng"
                lat = None
                lon = None
                map_link = item.get("google_map_link")
                if map_link and "," in map_link:
                    parts = map_link.split(",")
                    if len(parts) == 2:
                        try:
                            lat = float(parts[0].strip())
                            lon = float(parts[1].strip())
                        except ValueError:
                            pass

                raw_dealers.append({
                    "dealer_name": item.get("name") or "",
                    "address": item.get("address") or "",
                    "city": item.get("address", "").split(",")[-2].strip() if "," in item.get("address", "") else "",
                    "state": item.get("address", "").split(",")[-1].strip() if "," in item.get("address", "") else "",
                    "pincode": item.get("pincode") or "",
                    "phone": item.get("mobile") or "",
                    "email": item.get("email") or "",
                    "latitude": lat,
                    "longitude": lon,
                    "website": "https://www.lavamobiles.com"
                })
            return raw_dealers
        except Exception as e:
            self.log(f"[ERROR] Failed to parse Lava JSON payload: {e}")
            return []

    async def extract_dealers(self) -> List[Dict[str, Any]]:
        self.log("[STEP] Fetching page 1 (Lava REST API)")
        
        # Target API endpoint
        api_url = "https://webapi.lavamobiles.com/api/dealer-locator-service/dealer"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://www.lavamobiles.com",
            "Referer": "https://www.lavamobiles.com/",
            "api-key-HS256240625lava": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJsYXZhYXBpIiwibmFtZSI6ImxhdmFtb2JpbGV3ZWIiLCJhZG1pbiI6dHJ1ZSwiaWF0IjoyNDA2MjAyNX0.4v7h6QZKgI4soVGtJfK55--2gfrLQh4RIui2OukrxgI"
        }

        # Query different pincodes to build a comprehensive dataset
        pincodes = ["", "110001", "400001", "560001", "600001", "700001", "226016"]
        all_raw_records = []
        
        # Keep Alive HTTPX client with SSL verification disabled due to target cert expiry
        async with httpx.AsyncClient(verify=False) as client:
            for pin in pincodes:
                query_url = f"{api_url}?pincode={pin}" if pin else api_url
                self.log(f"[STEP] Querying Lava API endpoint for pincode: {pin or 'ALL'}")
                try:
                    res = await client.get(query_url, headers=headers, timeout=15)
                    if res.status_code == 200:
                        parsed = self.parse(res.text)
                        self.log(f"[OK] Fetched {len(parsed)} dealers for pincode: {pin or 'ALL'}")
                        all_raw_records.extend(parsed)
                    else:
                        self.log(f"[ERROR] API returned status {res.status_code} for pin {pin}")
                except Exception as e:
                    self.log(f"[ERROR] Failed to query Lava API for pin {pin}: {e}")

        # Normalize and validate all records
        processed = []
        for item in all_raw_records:
            normalized = normalize_dealer(item)
            is_valid, errors = validate_dealer(normalized)
            normalized["validation_status"] = "VALID" if is_valid else "INVALID"
            normalized["validation_errors"] = errors
            processed.append(normalized)

        return processed
