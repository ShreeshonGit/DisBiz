from typing import List, Dict, Any, Optional
from uuid import UUID
import json
import re
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import httpx

from app.scrapers.base_scraper import BaseScraper
from app.scrapers.utils import fetch_url_with_retry, detect_content_type
from app.scrapers.normalizer import normalize_dealer
from app.scrapers.validator import validate_dealer
from app.scrapers.selector_fallback_engine import SelectorFallbackEngine
import logging

logger = logging.getLogger(__name__)

class GenericScraper(BaseScraper):
    """
    Highly configurable, metadata-driven scraper implementation.
    Parses dealer pages using fallback CSS selector maps or JSON key paths.
    Supports asynchronous parallel page fetching.
    """

    def __init__(self, brand_id: UUID, brand_name: str, locator_url: str, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(brand_id, brand_name, locator_url, config)
        self.fallback_engine = SelectorFallbackEngine()

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
            from app.scrapers.utils import detect_content_type
            loc_type = detect_content_type(res)
            return loc_type
        except Exception as e:
            self.log(f"Auto-detection failed: {e}")
            return "UNKNOWN"

    async def fetch_page(self) -> str:
        # Read parameters
        scraper_type = self.config.get("scraper_type", "STATIC_HTML")
        locator_type = self.config.get("locator_type", "UNKNOWN")

        # Playwright browser engine fallback for JS rendering
        if scraper_type == "PLAYWRIGHT" or locator_type == "JAVASCRIPT":
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context(
                        viewport={"width": 1280, "height": 800},
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    )
                    page = await context.new_page()
                    await page.goto(self.locator_url, wait_until="networkidle", timeout=30000)
                    await page.wait_for_timeout(1000)
                    html_content = await page.content()
                    await browser.close()
                    return html_content
            except Exception as e:
                self.log(f"Playwright rendering failed: {e}")
                raise e
        
        # Standard HTTPX client fetch
        else:
            try:
                res = await fetch_url_with_retry(self.locator_url)
                return res.text
            except Exception as e:
                self.log(f"HTTPX fetch failed: {e}")
                raise e

    def parse(self, content: str) -> List[Dict[str, Any]]:
        # 1. Handle JSON/API response type
        if content.strip().startswith(("{", "[")):
            try:
                data = json.loads(content)
                json_keys = self.config.get("json_keys") or {}
                
                records_list = data
                list_key = json_keys.get("list_path")
                if list_key and isinstance(data, dict):
                    records_list = data.get(list_key, [])
                
                if not isinstance(records_list, list):
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
                return raw_dealers
            except Exception as e:
                self.log(f"JSON parsing error: {e}")
                return []

        # 2. Handle HTML document parsing using fallback engine
        selectors = self.config.get("css_selector_config") or {}
        container_sel = selectors.get("container")

        if not container_sel:
            self.log("No CSS container selector configured. Aborting parse.")
            return []

        try:
            soup = BeautifulSoup(content, "lxml")
            containers = soup.select(container_sel)

            raw_dealers = []
            for node in containers:
                name_txt = self.fallback_engine.extract_field(node, selectors.get("name"), "name")
                addr_txt = self.fallback_engine.extract_field(node, selectors.get("address"), "address")
                city_txt = self.fallback_engine.extract_field(node, selectors.get("city"), "city")
                state_txt = self.fallback_engine.extract_field(node, selectors.get("state"), "state")
                pin_txt = self.fallback_engine.extract_field(node, selectors.get("pincode"), "pincode")
                phone_txt = self.fallback_engine.extract_field(node, selectors.get("phone"), "phone")
                email_txt = self.fallback_engine.extract_field(node, selectors.get("email"), "email")
                web_txt = self.fallback_engine.extract_field(node, selectors.get("website"), "website")

                # If primary selector failed but fallback succeeded, log a warning
                name_sels = selectors.get("name")
                if isinstance(name_sels, list) and len(name_sels) > 1:
                    if name_txt and not node.select_one(name_sels[0]):
                        self.log("[WARN] Selector fallback used for field 'name'")

                addr_sels = selectors.get("address")
                if isinstance(addr_sels, list) and len(addr_sels) > 1:
                    if addr_txt and not node.select_one(addr_sels[0]):
                        self.log("[WARN] Selector fallback used for field 'address'")

                phone_sels = selectors.get("phone")
                if isinstance(phone_sels, list) and len(phone_sels) > 1:
                    if phone_txt and not node.select_one(phone_sels[0]):
                        self.log("[WARN] Selector fallback used for field 'phone'")

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
            return raw_dealers
        except Exception as e:
            self.log(f"HTML parsing error: {e}")
            return []

    async def fetch_pages_parallel(self, urls: List[str]) -> List[str]:
        """
        Fetches multiple URLs concurrently using an async Semaphore to cap
        simultaneous requests at max 3 tasks.
        """
        semaphore = asyncio.Semaphore(3)
        html_contents = [None] * len(urls)

        async def fetch_worker(index: int, url: str):
            async with semaphore:
                self.log(f"[STEP] Fetching page {index + 1}")
                try:
                    res = await fetch_url_with_retry(url)
                    html_contents[index] = res.text
                    self.log(f"[OK] Fetched page {index + 1} successfully.")
                except Exception as e:
                    self.log(f"[ERROR] Failed to fetch page {index + 1}: {e}")
                    raise e

        tasks = [fetch_worker(i, url) for i, url in enumerate(urls)]
        await asyncio.gather(*tasks, return_exceptions=False)
        return [c for c in html_contents if c is not None]

    async def preview(self, limit: int = 10) -> List[Dict[str, Any]]:
        self.log(f"Generating preview list (max {limit} records)...")
        try:
            self.log("[STEP] Fetching page 1")
            content = await self.fetch_page()
            self.log("[OK] Fetched page 1 successfully.")
            
            raw_records = self.parse(content)
            self.log(f"[OK] Parsed {len(raw_records)} records")
            
            preview_list = []
            for raw_item in raw_records[:limit]:
                normalized = normalize_dealer(raw_item)
                is_valid, errors = validate_dealer(normalized)
                normalized["validation_status"] = "VALID" if is_valid else "INVALID"
                normalized["validation_errors"] = errors
                preview_list.append(normalized)
                
            return preview_list
        except Exception as e:
            self.log(f"[ERROR] Preview execution failed: {e}")
            raise e

    async def extract_dealers(self) -> List[Dict[str, Any]]:
        max_pages = self.config.get("max_pages", 1)
        
        # Check if we should scrape multiple pages in parallel
        if max_pages > 1:
            max_pages = min(max_pages, 5)
            urls = []
            for p in range(1, max_pages + 1):
                if p == 1:
                    urls.append(self.locator_url)
                else:
                    separator = "&" if "?" in self.locator_url else "?"
                    urls.append(f"{self.locator_url}{separator}page={p}")

            self.log(f"Running parallel page scraping for {len(urls)} pages (max 3 concurrent)...")
            try:
                contents = await self.fetch_pages_parallel(urls)
                
                all_records = []
                for idx, content in enumerate(contents):
                    records = self.parse(content)
                    self.log(f"[OK] Parsed {len(records)} records from page {idx + 1}")
                    all_records.extend(records)
                    
                processed = []
                for item in all_records:
                    normalized = normalize_dealer(item)
                    is_valid, errors = validate_dealer(normalized)
                    normalized["validation_status"] = "VALID" if is_valid else "INVALID"
                    normalized["validation_errors"] = errors
                    processed.append(normalized)
                    
                return processed
            except Exception as e:
                self.log(f"[ERROR] Parallel scraping failed: {e}")
                raise e
        else:
            # Single page scrape
            self.log("[STEP] Fetching page 1")
            try:
                content = await self.fetch_page()
                self.log("[OK] Fetched page 1 successfully.")
                
                raw_records = self.parse(content)
                self.log(f"[OK] Parsed {len(raw_records)} records")
                
                processed = []
                for item in raw_records:
                    normalized = normalize_dealer(item)
                    is_valid, errors = validate_dealer(normalized)
                    normalized["validation_status"] = "VALID" if is_valid else "INVALID"
                    normalized["validation_errors"] = errors
                    processed.append(normalized)
                    
                return processed
            except Exception as e:
                self.log(f"[ERROR] Single page scrape failed: {e}")
                raise e

    def save(self, dealers: List[Dict[str, Any]]) -> int:
        return len(dealers)
