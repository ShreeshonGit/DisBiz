from typing import List, Dict, Any, Optional
from uuid import UUID
import json
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import httpx

from app.scrapers.base_scraper import BaseScraper
from app.scrapers.utils import fetch_url_with_retry, detect_content_type
from app.scrapers.normalizer import normalize_dealer
from app.scrapers.validator import validate_dealer
import logging

logger = logging.getLogger(__name__)

class GenericScraper(BaseScraper):
    """
    Highly configurable, metadata-driven scraper implementation.
    Parses dealer pages using CSS selector maps or JSON key paths.
    """

    def validate_url(self) -> bool:
        self.log("Validating locator URL format.")
        url_regex = re.compile(
            r'^(?:http|ftp)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_regex.match(self.locator_url))

    async def detect_locator_type(self) -> str:
        self.log(f"Auto-detecting locator type for: {self.locator_url}")
        try:
            res = await fetch_url_with_retry(self.locator_url)
            self.log(f"Received HTTP status code {res.status_code}.")
            from app.scrapers.utils import detect_content_type
            loc_type = detect_content_type(res)
            self.log(f"Auto-detected locator type: {loc_type}")
            return loc_type
        except Exception as e:
            self.log(f"Auto-detection failed: {e}")
            return "UNKNOWN"

    async def fetch_page(self) -> str:
        self.log("Initializing fetch_page sequence.")
        
        # Read scraper engine parameters
        scraper_type = self.config.get("scraper_type", "STATIC_HTML")
        locator_type = self.config.get("locator_type", "UNKNOWN")

        # Playwright browser engine fallback for JS rendering
        if scraper_type == "PLAYWRIGHT" or locator_type == "JAVASCRIPT":
            self.log("Launching headless browser via Playwright...")
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context(
                        viewport={"width": 1280, "height": 800},
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    )
                    page = await context.new_page()
                    self.log(f"Navigating to {self.locator_url}")
                    await page.goto(self.locator_url, wait_until="networkidle", timeout=30000)
                    # Small wait for safety
                    await page.wait_for_timeout(2000)
                    html_content = await page.content()
                    await browser.close()
                    self.log("Page rendered and fetched successfully.")
                    return html_content
            except Exception as e:
                self.log(f"Playwright rendering failed: {e}")
                raise e
        
        # Standard HTTPX client fetch
        else:
            self.log("Fetching page source asynchronously via HTTPX client...")
            try:
                res = await fetch_url_with_retry(self.locator_url)
                self.log(f"HTTPX fetch completed: {res.status_code}")
                return res.text
            except Exception as e:
                self.log(f"HTTPX fetch failed: {e}")
                raise e

    def parse(self, content: str) -> List[Dict[str, Any]]:
        self.log("Initializing document parser.")
        
        # 1. Handle JSON/API response type
        if content.strip().startswith(("{", "[")):
            self.log("Detected JSON API content. Parsing JSON structure...")
            try:
                data = json.loads(content)
                json_keys = self.config.get("json_keys") or {}
                
                records_list = data
                list_key = json_keys.get("list_path")
                if list_key and isinstance(data, dict):
                    records_list = data.get(list_key, [])
                
                if not isinstance(records_list, list):
                    self.log("JSON root is not a list. Skipping parsing.")
                    return []

                raw_dealers = []
                for item in records_list:
                    if not isinstance(item, dict):
                        continue
                    raw_dealers.append({
                        "dealer_name": item.get(json_keys.get("name", "name"), ""),
                        "address": item.get(json_keys.get("address", "address"), ""),
                        "city": item.get(json_keys.get("city", "city"), ""),
                        "state": item.get(json_keys.get("state", "state"), ""),
                        "pincode": item.get(json_keys.get("pincode", "pincode"), ""),
                        "phone": item.get(json_keys.get("phone", "phone"), ""),
                        "email": item.get(json_keys.get("email", "email"), ""),
                        "latitude": item.get(json_keys.get("latitude", "latitude"), None),
                        "longitude": item.get(json_keys.get("longitude", "longitude"), None),
                        "website": item.get(json_keys.get("website", "website"), "")
                    })
                self.log(f"Parsed {len(raw_dealers)} records from JSON API.")
                return raw_dealers
            except Exception as e:
                self.log(f"JSON parsing error: {e}")
                return []

        # 2. Handle HTML document parsing
        selectors = self.config.get("css_selector_config") or {}
        container_sel = selectors.get("container")

        if not container_sel:
            self.log("No CSS container selector configured. Aborting parse.")
            return []

        self.log(f"Parsing HTML document using CSS selector maps...")
        try:
            soup = BeautifulSoup(content, "lxml")
            containers = soup.select(container_sel)
            self.log(f"Found {len(containers)} dealer nodes matching container selector '{container_sel}'")

            raw_dealers = []
            for node in containers:
                # Extract relative selectors
                name_sel = selectors.get("name")
                addr_sel = selectors.get("address")
                city_sel = selectors.get("city")
                state_sel = selectors.get("state")
                pin_sel = selectors.get("pincode")
                phone_sel = selectors.get("phone")
                email_sel = selectors.get("email")
                web_sel = selectors.get("website")

                name_txt = node.select_one(name_sel).get_text() if (name_sel and node.select_one(name_sel)) else ""
                addr_txt = node.select_one(addr_sel).get_text() if (addr_sel and node.select_one(addr_sel)) else ""
                city_txt = node.select_one(city_sel).get_text() if (city_sel and node.select_one(city_sel)) else ""
                state_txt = node.select_one(state_sel).get_text() if (state_sel and node.select_one(state_sel)) else ""
                pin_txt = node.select_one(pin_sel).get_text() if (pin_sel and node.select_one(pin_sel)) else ""
                phone_txt = node.select_one(phone_sel).get_text() if (phone_sel and node.select_one(phone_sel)) else ""
                email_txt = node.select_one(email_sel).get_text() if (email_sel and node.select_one(email_sel)) else ""
                web_txt = node.select_one(web_sel).get_text() if (web_sel and node.select_one(web_sel)) else ""

                if not name_txt.strip() and not addr_txt.strip():
                    continue

                raw_dealers.append({
                    "dealer_name": name_txt.strip(),
                    "address": addr_txt.strip(),
                    "city": city_txt.strip(),
                    "state": state_txt.strip(),
                    "pincode": pin_txt.strip(),
                    "phone": phone_txt.strip(),
                    "email": email_txt.strip(),
                    "website": web_txt.strip()
                })
            self.log(f"Parsed {len(raw_dealers)} records from HTML containers.")
            return raw_dealers
        except Exception as e:
            self.log(f"HTML parsing error: {e}")
            return []

    async def preview(self, limit: int = 10) -> List[Dict[str, Any]]:
        self.log(f"Generating preview list (max {limit} records)...")
        try:
            content = await self.fetch_page()
            self.log("Page content successfully loaded.")
            
            raw_records = self.parse(content)
            self.log(f"Extracted {len(raw_records)} total raw records from page source.")
            
            preview_list = []
            for raw_item in raw_records[:limit]:
                # Normalize
                normalized = normalize_dealer(raw_item)
                # Validate
                is_valid, errors = validate_dealer(normalized)
                
                normalized["validation_status"] = "VALID" if is_valid else "INVALID"
                normalized["validation_errors"] = errors
                preview_list.append(normalized)
                
            self.log(f"Successfully compiled {len(preview_list)} preview records.")
            return preview_list
        except Exception as e:
            self.log(f"Preview execution failed: {e}")
            raise e

    async def extract_dealers(self) -> List[Dict[str, Any]]:
        self.log("Starting full extraction sequence...")
        try:
            content = await self.fetch_page()
            raw_records = self.parse(content)
            
            processed = []
            for item in raw_records:
                normalized = normalize_dealer(item)
                is_valid, errors = validate_dealer(normalized)
                
                normalized["validation_status"] = "VALID" if is_valid else "INVALID"
                normalized["validation_errors"] = errors
                processed.append(normalized)
                
            self.log(f"Full extraction finished. Extracted {len(processed)} records.")
            return processed
        except Exception as e:
            self.log(f"Full extraction execution failed: {e}")
            raise e

    def save(self, dealers: List[Dict[str, Any]]) -> int:
        self.log("Saving records (Skeleton execution).")
        # Sprint 3.1 is skeleton return count only
        return len(dealers)
