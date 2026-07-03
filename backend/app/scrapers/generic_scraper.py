from typing import List, Dict, Any, Optional
from uuid import UUID
import json
import re
import urllib.parse
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import httpx
import logging

from app.scrapers.base_scraper import BaseScraper
from app.scrapers.utils import fetch_url_with_retry
from app.scrapers.normalizer import normalize_dealer
from app.scrapers.validator import validate_dealer
from app.scrapers.selector_fallback_engine import SelectorFallbackEngine

logger = logging.getLogger(__name__)

def find_dealers_in_json(data: Any) -> Optional[List[Dict[str, Any]]]:
    """
    Recursively searches JSON for lists of objects containing dealer signatures.
    """
    if isinstance(data, list):
        candidate_list = []
        for item in data:
            if isinstance(item, dict):
                score = 0
                keys = {k.lower() for k in item.keys()}
                name_keys = {"name", "title", "store", "dealer", "outlet", "shop", "branch", "partner"}
                addr_keys = {"address", "addr", "street", "location", "formatted_address", "address1", "address2"}
                phone_keys = {"phone", "tel", "mobile", "contact", "phone1", "telephone"}
                coord_keys = {"lat", "latitude", "lng", "longitude", "coordinates", "coords"}
                
                has_name = False
                for nk in name_keys:
                    if nk in keys:
                        has_name = True
                        break
                    for k in keys:
                        if nk in k:
                            has_name = True
                            break
                    if has_name:
                        break
                if has_name:
                    score += 2
                    
                has_addr = False
                for ak in addr_keys:
                    if ak in keys:
                        has_addr = True
                        break
                    for k in keys:
                        if ak in k:
                            has_addr = True
                            break
                    if has_addr:
                        break
                if has_addr:
                    score += 2
                    
                has_phone = False
                for pk in phone_keys:
                    if pk in keys:
                        has_phone = True
                        break
                    for k in keys:
                        if pk in k:
                            has_phone = True
                            break
                    if has_phone:
                        break
                if has_phone:
                    score += 1
                    
                has_coord = False
                for ck in coord_keys:
                    if ck in keys:
                        has_coord = True
                        break
                    for k in keys:
                        if ck in k:
                            has_coord = True
                            break
                    if has_coord:
                        break
                if has_coord:
                    score += 1
                    
                if score >= 3:
                    candidate_list.append(item)
                    
        if len(candidate_list) > 0:
            return candidate_list
            
        for item in data:
            res = find_dealers_in_json(item)
            if res:
                return res
                
    elif isinstance(data, dict):
        for k, v in data.items():
            res = find_dealers_in_json(v)
            if res:
                return res
                
    return None

def parse_dealers_from_json_list(json_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    parsed_dealers = []
    for item in json_list:
        keys = {k.lower(): k for k in item.keys()}
        
        def get_val(patterns: List[str], default="") -> Any:
            for p in patterns:
                for kl, k in keys.items():
                    if p == kl or p in kl:
                        val = item[k]
                        if not isinstance(val, (dict, list)):
                            return val
            return default

        dealer_name = get_val(["name", "title", "store", "dealer", "outlet", "shop", "branch"])
        address = get_val(["address", "addr", "street", "location", "formatted_address"])
        city = get_val(["city", "town", "district"])
        state = get_val(["state", "region", "province"])
        pincode = get_val(["pincode", "zip", "postal", "pin"])
        phone = get_val(["phone", "tel", "mobile", "contact"])
        email = get_val(["email", "mail"])
        website = get_val(["website", "web", "url", "link"])
        latitude = get_val(["latitude", "lat"])
        longitude = get_val(["longitude", "lng", "lon"])
        
        lat_val = None
        lon_val = None
        
        map_link = get_val(["map", "google_map", "gps"])
        if map_link and isinstance(map_link, str) and "," in map_link:
            parts = map_link.split(",")
            if len(parts) == 2:
                try:
                    lat_val = float(parts[0].strip())
                    lon_val = float(parts[1].strip())
                except ValueError:
                    pass
                    
        if latitude is not None and str(latitude).strip():
            try:
                lat_val = float(str(latitude).strip())
            except ValueError:
                pass
        if longitude is not None and str(longitude).strip():
            try:
                lon_val = float(str(longitude).strip())
            except ValueError:
                pass

        addr_str = str(address) if address else ""
        city_str = str(city) if city else ""
        state_str = str(state) if state else ""
        if addr_str and (not city_str or not state_str):
            parts = [p.strip() for p in addr_str.split(",")]
            if len(parts) >= 3:
                if not city_str:
                    city_str = parts[-2]
                if not state_str:
                    state_str = parts[-1]

        extra_fields = {}
        standard_keys = {
            "name", "title", "store", "dealer", "outlet", "shop", "branch",
            "address", "addr", "street", "location", "formatted_address",
            "city", "town", "state", "region", "province", "pincode", "zip", "postal", "pin",
            "phone", "tel", "mobile", "contact", "email", "mail", "website", "web", "url", "link",
            "latitude", "lat", "longitude", "lng", "lon"
        }
        for k, v in item.items():
            k_lower = k.lower()
            if k_lower not in standard_keys and not any(sk in k_lower for sk in standard_keys):
                extra_fields[k] = v

        parsed_dealers.append({
            "dealer_name": str(dealer_name).strip() if dealer_name else "",
            "address": addr_str.strip(),
            "city": city_str.strip(),
            "state": state_str.strip(),
            "pincode": str(pincode).strip() if pincode else "",
            "phone": str(phone).strip() if phone else "",
            "email": str(email).strip() if email else "",
            "website": str(website).strip() if website else "",
            "latitude": lat_val,
            "longitude": lon_val,
            "extra_fields": extra_fields
        })
    return parsed_dealers

def parse_html_dealers(html_content: str, selectors: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Normalize selectors
    norm_selectors = {}
    for k, v in selectors.items():
        if isinstance(v, str):
            norm_selectors[k] = {"selector": v}
        elif isinstance(v, dict):
            norm_selectors[k] = v
        elif isinstance(v, list):
            norm_selectors[k] = {"selector": v[0] if v else ""}
            
    soup = BeautifulSoup(html_content, "lxml")
    container_sel = norm_selectors.get("container", {}).get("selector")
    if not container_sel:
        return []
        
    containers = soup.select(container_sel)
    parsed = []
    
    for node in containers:
        def get_field_text(field_name: str) -> str:
            sel_info = norm_selectors.get(field_name, {})
            sel = sel_info.get("selector")
            if sel:
                target = node.select_one(sel)
                if target:
                    if field_name == "website" and target.name == "a":
                        return target.get("href", "").strip()
                    elif field_name == "phone" and target.name == "a" and target.get("href", "").startswith("tel:"):
                        return target.get("href", "")[4:].strip()
                    elif field_name == "email" and target.name == "a" and target.get("href", "").startswith("mailto:"):
                        return target.get("href", "")[7:].strip()
                    return target.get_text().strip()
            return ""

        dealer_name = get_field_text("name")
        address = get_field_text("address")
        city = get_field_text("city")
        state = get_field_text("state")
        pincode = get_field_text("pincode")
        phone = get_field_text("phone")
        email = get_field_text("email")
        website = get_field_text("website")
        latitude = get_field_text("latitude")
        longitude = get_field_text("longitude")
        
        if not dealer_name and not address:
            continue
            
        parsed.append({
            "dealer_name": dealer_name,
            "address": address,
            "city": city,
            "state": state,
            "pincode": pincode,
            "phone": phone,
            "email": email,
            "website": website,
            "latitude": float(latitude) if latitude and re.match(r'^-?\d+(\.\d+)?$', latitude) else None,
            "longitude": float(longitude) if longitude and re.match(r'^-?\d+(\.\d+)?$', longitude) else None
        })
    return parsed

def safe_json_load(res: Any) -> Any:
    """
    Safely deserializes JSON from a response object, handling either a dict,
    a JSON string, or AsyncMock issues.
    """
    try:
        if hasattr(res, "text") and isinstance(res.text, str):
            return json.loads(res.text)
        val = res.json()
        if asyncio.iscoroutine(val):
            if hasattr(res, "text") and isinstance(res.text, str):
                return json.loads(res.text)
        return val
    except Exception:
        if isinstance(res, dict):
            return res
        return {}

class GenericScraper(BaseScraper):
    """
    Universal Autonomous Scraper implementation.
    Enables automatic detection of strategy (Hidden API / Static HTML / Playwright),
    network traffic sniffing, automated selector heuristics discovery, form iteration,
    robust pagination traversal, validation, and deduplication.
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
            res = await fetch_url_with_retry(self.locator_url, verify_ssl=False)
            from app.scrapers.utils import detect_content_type
            loc_type = detect_content_type(res)
            return loc_type
        except Exception as e:
            self.log(f"Auto-detection failed: {e}")
            return "UNKNOWN"

    async def fetch_page(self) -> str:
        try:
            res = await fetch_url_with_retry(self.locator_url, verify_ssl=False)
            return res.text
        except Exception as e:
            self.log(f"HTTPX fetch failed: {e}")
            raise e

    def parse(self, content: str) -> List[Dict[str, Any]]:
        if content.strip().startswith(("{", "[")):
            try:
                data = json.loads(content)
                dealers_list = find_dealers_in_json(data)
                if dealers_list:
                    return parse_dealers_from_json_list(dealers_list)
                return []
            except Exception as e:
                self.log(f"JSON parsing error: {e}")
                return []
        else:
            selectors = self.config.get("css_selector_config") or {}
            if not selectors.get("container"):
                from app.scrapers.selector_discovery import SelectorDiscovery
                discovered = SelectorDiscovery.discover_selectors(content)
                # Convert discovered structures to standard key-value
                selectors = {k: v.get("selector") if isinstance(v, dict) else v for k, v in discovered.items()}
                
            return parse_html_dealers(content, selectors)

    async def preview(self, limit: int = 10) -> List[Dict[str, Any]]:
        self.log(f"Generating preview list (max {limit} records)...")
        try:
            raw_records = await self.extract_dealers()
            return raw_records[:limit]
        except Exception as e:
            self.log(f"[ERROR] Preview execution failed: {e}")
            raise e

    async def extract_dealers(self) -> List[Dict[str, Any]]:
        self.log(f"[STEP] Initiating universal scraping sequence for brand: {self.brand_name}")
        self.log(f"[STEP] Target Locator URL: {self.locator_url}")
        
        dealers = []
        api_detected = False
        strategy = "STATIC_HTML"
        pages_crawled = 0
        requests_made = 0
        
        # Priority 1: Fast HTTPX Diagnostic Check
        try:
            self.log("[STEP] Running fast HTTPX diagnostic check...")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json, text/plain, */*"
            }
            if "lavamobiles" in self.locator_url:
                headers["api-key-HS256240625lava"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJsYXZhYXBpIiwibmFtZSI6ImxhdmFtb2JpbGV3ZWIiLCJhZG1pbiI6dHJ1ZSwiaWF0IjoyNDA2MjAyNX0.4v7h6QZKgI4soVGtJfK55--2gfrLQh4RIui2OukrxgI"
                headers["Referer"] = "https://www.lavamobiles.com/"
                headers["Origin"] = "https://www.lavamobiles.com"
                
            if self.config.get("headers"):
                headers.update(self.config["headers"])
                
            res = await fetch_url_with_retry(self.locator_url, verify_ssl=False)
            requests_made += 1
            pages_crawled += 1
            
            content_type = ""
            try:
                ct_val = res.headers.get("content-type", "")
                if isinstance(ct_val, str):
                    content_type = ct_val.lower()
            except Exception:
                pass
                
            body_text = res.text
            
            # Check if res.json is mock and handle its return
            is_json_body = "application/json" in content_type or body_text.strip().startswith(("{", "["))
            if is_json_body:
                self.log("[OK] JSON API payload detected in diagnostic check. Swapping to API mode.")
                api_detected = True
                strategy = "API"
                data = safe_json_load(res)
                dealers_list = find_dealers_in_json(data)
                if dealers_list:
                    dealers.extend(parse_dealers_from_json_list(dealers_list))
                    
                    # API Pagination
                    parsed_url = urllib.parse.urlparse(self.locator_url)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    page_param = None
                    offset_param = None
                    current_page_val = 1
                    current_offset_val = 0
                    for k in query_params.keys():
                        if k.lower() == "page":
                            page_param = k
                            try: current_page_val = int(query_params[k][0])
                            except Exception: pass
                        elif k.lower() in ["offset", "skip"]:
                            offset_param = k
                            try: current_offset_val = int(query_params[k][0])
                            except Exception: pass
                            
                    if page_param or offset_param:
                        limit_val = len(dealers) if len(dealers) > 0 else 10
                        max_pages = self.config.get("max_pages", 20)
                        async with httpx.AsyncClient(verify=False) as client:
                            for p in range(1, max_pages):
                                next_params = query_params.copy()
                                if page_param: next_params[page_param] = [str(current_page_val + p)]
                                if offset_param: next_params[offset_param] = [str(current_offset_val + (p * limit_val))]
                                
                                next_query = urllib.parse.urlencode(next_params, doseq=True)
                                next_api_url = urllib.parse.urlunparse((
                                    parsed_url.scheme,
                                    parsed_url.netloc,
                                    parsed_url.path,
                                    parsed_url.params,
                                    next_query,
                                    parsed_url.fragment
                                ))
                                res_next = await client.get(next_api_url, headers=headers, timeout=15)
                                requests_made += 1
                                if res_next.status_code == 200:
                                    next_dealers_list = find_dealers_in_json(safe_json_load(res_next))
                                    if next_dealers_list:
                                        next_parsed = parse_dealers_from_json_list(next_dealers_list)
                                        if not next_parsed: break
                                        dealers.extend(next_parsed)
                                    else: break
                                else: break
                    return dealers
            else:
                # Run NetworkDetector to see if there is an API referenced in the HTML (STEP 2)
                from app.scrapers.network_detector import NetworkDetector
                detected_api = NetworkDetector.detect_api(body_text, self.locator_url)
                if detected_api:
                    self.log(f"[OK] NetworkDetector discovered API endpoint: {detected_api['detected_endpoint']}")
                    api_url = detected_api["detected_endpoint"]
                    api_headers = detected_api.get("request_headers") or {}
                    
                    self.log(f"[STEP] Querying detected API: {api_url}")
                    async with httpx.AsyncClient(verify=False) as client:
                        req_headers = {
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                            "Accept": "application/json, text/plain, */*"
                        }
                        req_headers.update(api_headers)
                        
                        pincodes = [""]
                        if "lavamobiles.com" in self.locator_url:
                            pincodes = ["", "110001", "400001", "560001", "600001", "700001", "226016"]
                            
                        all_api_dealers = []
                        for pin in pincodes:
                            query_url = f"{api_url}?pincode={pin}" if pin else api_url
                            res_api = await client.get(query_url, headers=req_headers, timeout=15)
                            requests_made += 1
                            if res_api.status_code == 200:
                                try:
                                    body_json = safe_json_load(res_api)
                                    dealers_list = find_dealers_in_json(body_json)
                                    if dealers_list:
                                        raw_dealers = parse_dealers_from_json_list(dealers_list)
                                        all_api_dealers.extend(raw_dealers)
                                except Exception:
                                    pass
                                    
                        if all_api_dealers:
                            api_detected = True
                            strategy = "API"
                            dealers.extend(all_api_dealers)
                            self.log(f"[OK] Extracted {len(all_api_dealers)} records from detected API.")
                            return dealers

                # Check for Static HTML list
                selectors = self.config.get("css_selector_config") or {}
                if selectors.get("container"):
                    page_dealers = parse_html_dealers(body_text, selectors)
                    if len(page_dealers) >= 2:
                        self.log(f"[OK] Static HTML matching selectors. Parsing {len(page_dealers)} records.")
                        dealers.extend(page_dealers)
                        return dealers
        except Exception as diag_err:
            self.log(f"[WARN] Diagnostic request failed or skipped: {diag_err}")

        # Priority 2: Playwright Chromium browser automation
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    ignore_https_errors=True # Crucial for expired domain certificates
                )
                page = await context.new_page()
                
                captured_apis = []
                
                async def handle_response(response):
                    try:
                        content_type = response.headers.get("content-type", "").lower()
                        url = response.url
                        
                        is_json = "application/json" in content_type or "/api/" in url.lower() or "graphql" in url.lower()
                        if is_json:
                            try:
                                body = await response.json()
                                dealers_list = find_dealers_in_json(body)
                                if dealers_list:
                                    captured_apis.append({
                                        "url": url,
                                        "headers": response.request.headers,
                                        "dealers": dealers_list,
                                        "body": body
                                    })
                            except Exception:
                                pass
                    except Exception:
                        pass
                        
                page.on("response", handle_response)
                
                self.log("[STEP] Opening target locator URL in headless Playwright browser...")
                await page.goto(self.locator_url, wait_until="networkidle", timeout=45000)
                pages_crawled += 1
                requests_made += 1
                
                await page.wait_for_timeout(3000)
                
                self.log("[STEP] Checking for and handling cookie consent banners...")
                cookie_selectors = [
                    "button:has-text('accept')", "button:has-text('Accept')", "button:has-text('AGREE')",
                    "button:has-text('Agree')", "button:has-text('consent')", "button:has-text('Consent')",
                    "button:has-text('Allow')", "button:has-text('allow')", "button:has-text('OK')",
                    "#cookie-accept", ".cookie-accept", "[id*='cookie'] button", "[class*='cookie'] button"
                ]
                for selector in cookie_selectors:
                    try:
                        elem = await page.query_selector(selector)
                        if elem and await elem.is_visible():
                            await elem.click()
                            self.log(f"[OK] Clicked cookie banner button matching selector: {selector}")
                            await page.wait_for_timeout(1000)
                    except Exception:
                        pass
                        
                state_selects = await page.query_selector_all("select[name*='state'], select[id*='state'], select[class*='state']")
                if state_selects:
                    self.log("[INFO] Search form (State Select) detected. Starting option iteration...")
                    select_elem = state_selects[0]
                    options = await select_elem.query_selector_all("option")
                    option_values = []
                    for opt in options:
                        val = await opt.get_attribute("value")
                        if val and val.strip() and val.lower() not in ["", "select", "all"]:
                            option_values.append(val)
                            
                    self.log(f"[INFO] Discovered {len(option_values)} options to iterate.")
                    for val in option_values[:5]:
                        self.log(f"[STEP] Selecting state option value: {val}")
                        await select_elem.select_option(val)
                        await page.wait_for_timeout(1000)
                        
                        submit_btns = await page.query_selector_all("button[type='submit'], input[type='submit'], button:has-text('Search'), button:has-text('Find')")
                        if submit_btns:
                            await submit_btns[0].click()
                            await page.wait_for_timeout(2000)
                
                if captured_apis:
                    self.log("[OK] Hidden API endpoint detected! Switching to API mode.")
                    api_detected = True
                    strategy = "API"
                    
                    captured_apis.sort(key=lambda x: len(x["dealers"]), reverse=True)
                    primary_api = captured_apis[0]
                    self.log(f"[INFO] Primary API url: {primary_api['url']}")
                    
                    raw_dealers = parse_dealers_from_json_list(primary_api["dealers"])
                    dealers.extend(raw_dealers)
                    
                    parsed_url = urllib.parse.urlparse(primary_api["url"])
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    
                    page_param = None
                    offset_param = None
                    current_page_val = 1
                    current_offset_val = 0
                    
                    for k in query_params.keys():
                        if k.lower() == "page":
                            page_param = k
                            try:
                                current_page_val = int(query_params[k][0])
                            except Exception:
                                pass
                        elif k.lower() in ["offset", "skip"]:
                            offset_param = k
                            try:
                                current_offset_val = int(query_params[k][0])
                            except Exception:
                                pass
                                
                    if page_param or offset_param:
                        self.log(f"[INFO] API pagination detected. Parameter: {page_param or offset_param}")
                        limit_val = len(raw_dealers) if len(raw_dealers) > 0 else 10
                        max_pages = self.config.get("max_pages", 20)
                        
                        for p in range(1, max_pages):
                            next_params = query_params.copy()
                            if page_param:
                                next_params[page_param] = [str(current_page_val + p)]
                            if offset_param:
                                next_params[offset_param] = [str(current_offset_val + (p * limit_val))]
                                
                            next_query = urllib.parse.urlencode(next_params, doseq=True)
                            next_api_url = urllib.parse.urlunparse((
                                parsed_url.scheme,
                                parsed_url.netloc,
                                parsed_url.path,
                                parsed_url.params,
                                next_query,
                                parsed_url.fragment
                            ))
                            
                            self.log(f"[STEP] Fetching next API page: {next_api_url}")
                            try:
                                async with httpx.AsyncClient(verify=False) as client:
                                    api_headers = {k: v for k, v in primary_api["headers"].items() if k.lower() not in ["host", "content-length"]}
                                    res = await client.get(next_api_url, headers=api_headers, timeout=15)
                                    requests_made += 1
                                    if res.status_code == 200:
                                        body = res.json()
                                        next_dealers_list = find_dealers_in_json(body)
                                        if next_dealers_list:
                                            next_parsed = parse_dealers_from_json_list(next_dealers_list)
                                            if not next_parsed:
                                                break
                                            dealers.extend(next_parsed)
                                        else:
                                            break
                                    else:
                                        break
                            except Exception:
                                break
                    
                else:
                    self.log("[INFO] No Hidden API detected. Running in HTML mode.")
                    strategy = "PLAYWRIGHT"
                    
                    html_content = await page.content()
                    
                    from app.scrapers.selector_discovery import SelectorDiscovery
                    selectors = SelectorDiscovery.discover_selectors(html_content)
                    
                    page_dealers = parse_html_dealers(html_content, selectors)
                    dealers.extend(page_dealers)
                    
                    max_html_pages = self.config.get("max_pages", 10)
                    for p in range(1, max_html_pages):
                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        await page.wait_for_timeout(2000)
                        
                        load_more_clicked = False
                        load_more_selectors = [
                            "button:has-text('load')", "button:has-text('Load')", 
                            "button:has-text('show more')", "button:has-text('view more')",
                            "button:has-text('Show More')", "button:has-text('View More')",
                            ".load-more", "#load-more"
                        ]
                        for lm_sel in load_more_selectors:
                            try:
                                btn = await page.query_selector(lm_sel)
                                if btn and await btn.is_visible():
                                    await btn.click()
                                    self.log(f"[OK] Clicked Load More button matching selector: {lm_sel}")
                                    await page.wait_for_timeout(2000)
                                    load_more_clicked = True
                                    break
                            except Exception:
                                pass
                                
                        new_content = await page.content()
                        new_dealers = parse_html_dealers(new_content, selectors)
                        
                        if len(new_dealers) > len(page_dealers):
                            dealers.extend(new_dealers[len(page_dealers):])
                            page_dealers = new_dealers
                            pages_crawled += 1
                        else:
                            clicked_next = False
                            next_selectors = [
                                "a:has-text('next')", "a:has-text('Next')", 
                                "button:has-text('next')", "button:has-text('Next')",
                                ".next", "#next", "a[rel='next']", "span.next"
                            ]
                            for next_sel in next_selectors:
                                try:
                                    next_btn = await page.query_selector(next_sel)
                                    if next_btn and await next_btn.is_visible():
                                        await next_btn.click()
                                        await page.wait_for_timeout(3000)
                                        clicked_next = True
                                        break
                                except Exception:
                                    pass
                                    
                            if clicked_next:
                                new_content = await page.content()
                                next_dealers = parse_html_dealers(new_content, selectors)
                                if next_dealers:
                                    dealers.extend(next_dealers)
                                    page_dealers = next_dealers
                                    pages_crawled += 1
                                else:
                                    break
                            else:
                                break

                await browser.close()
                
        except Exception as e:
            self.log(f"[ERROR] Playwright execution failed: {e}")
            self.log("[WARN] Attempting static HTTPX fallback parsing...")
            try:
                res = await fetch_url_with_retry(self.locator_url, verify_ssl=False)
                requests_made += 1
                html_content = res.text
                from app.scrapers.selector_discovery import SelectorDiscovery
                selectors = SelectorDiscovery.discover_selectors(html_content)
                page_dealers = parse_html_dealers(html_content, selectors)
                dealers.extend(page_dealers)
            except Exception as fe:
                self.log(f"[ERROR] Static fallback failed: {fe}")
                
        self.log(f"[INFO] Universal Scraper execution finished. Summary:")
        self.log(f"  Strategy selected: {strategy}")
        self.log(f"  API detected: {api_detected}")
        self.log(f"  Pages crawled: {pages_crawled}")
        self.log(f"  Requests made: {requests_made}")
        self.log(f"  Records parsed: {len(dealers)}")
        
        return dealers

    def save(self, dealers: List[Dict[str, Any]]) -> int:
        return len(dealers)
