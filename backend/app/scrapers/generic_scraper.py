from typing import List, Dict, Any, Optional
from uuid import UUID
import json
import re
import urllib.parse
import asyncio
import traceback
import random
import sys
from playwright.async_api import async_playwright
import httpx
import logging

from app.scrapers.base_scraper import BaseScraper
from app.scrapers.utils import fetch_url_with_retry
from app.scrapers.normalizer import normalize_dealer
from app.scrapers.validator import validate_dealer
from app.scrapers.selector_fallback_engine import SelectorFallbackEngine
from app.scrapers.selector_discovery import SelectorDiscovery

# Modular components
from app.scrapers.human_mode import HumanMode
from app.scrapers.network_recorder import NetworkRecorder
from app.scrapers.blocking_detector import BlockingDetector
from app.scrapers.diagnostic_reporter import DiagnosticReporter
from app.scrapers.browser_manager import BrowserManager
from app.scrapers.parser_utils import (
    find_dealers_in_json,
    parse_dealers_from_json_list,
    parse_html_dealers,
    safe_json_load
)

logger = logging.getLogger(__name__)

class GenericScraper(BaseScraper):
    """
    Universal Autonomous Scraper implementation.
    Includes automated failover browsers, human interaction simulation,
    network sniffing, Cloudflare/Captcha detection, and detailed failure reports.
    """

    def __init__(self, brand_id: UUID, brand_name: str, locator_url: str, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(brand_id, brand_name, locator_url, config)
        self.fallback_engine = SelectorFallbackEngine()
        self.search_diagnostics = {
            "search_field_detected": None,
            "keywords_entered": [],
            "suggestions_detected": [],
            "suggestions_selected": [],
            "ajax_requests_fired": [],
            "dealer_endpoints_discovered": [],
            "dealers_extracted_count": 0
        }
        self.recovery_attempts = []

    def validate_url(self) -> bool:
        url_regex = re.compile(
            r'^(?:http|ftp)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_regex.match(self.locator_url))

    async def detect_locator_type(self) -> str:
        try:
            res = await fetch_url_with_retry(self.locator_url, verify_ssl=False)
            from app.scrapers.utils import detect_content_type
            return detect_content_type(res)
        except Exception:
            return "UNKNOWN"

    async def fetch_page(self) -> str:
        res = await fetch_url_with_retry(self.locator_url, verify_ssl=False)
        return res.text

    def parse(self, content: str) -> List[Dict[str, Any]]:
        if content.strip().startswith(("{", "[")):
            try:
                data = json.loads(content)
                dealers_list = find_dealers_in_json(data)
                if dealers_list:
                    return parse_dealers_from_json_list(dealers_list)
                return []
            except Exception:
                return []
        else:
            selectors = self.config.get("css_selector_config") or {}
            if not selectors.get("container"):
                selectors = {k: v.get("selector") if isinstance(v, dict) else v for k, v in SelectorDiscovery.discover_selectors(content).items()}
            return parse_html_dealers(content, selectors)

    async def preview(self, limit: int = 10) -> List[Dict[str, Any]]:
        raw_records = await self.extract_dealers()
        return raw_records[:limit]

    async def extract_dealers(self) -> List[Dict[str, Any]]:
        self.log(f"[STEP] Initiating universal scraping sequence for brand: {self.brand_name}")
        dealers = []
        api_detected = False
        strategy = "STATIC_HTML"
        pages_crawled = 0
        requests_made = 0
        
        # Priority 1: Fast HTTPX Diagnostic Check
        try:
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
            if hasattr(res, "headers") and res.headers:
                try:
                    raw_ct = res.headers.get("content-type", "")
                    if isinstance(raw_ct, str):
                        content_type = raw_ct.lower()
                except Exception:
                    pass
            body_text = res.text or ""
            
            is_json_body = "application/json" in content_type or body_text.strip().startswith(("{", "["))
            if is_json_body:
                strategy = "API"
                data = safe_json_load(res)
                dealers_list = find_dealers_in_json(data)
                if dealers_list:
                    return parse_dealers_from_json_list(dealers_list)
        except Exception:
            pass

        # Priority 2: Playwright Chromium browser automation with fallbacks
        try:
            # Check event loop compatibility on Windows
            loop_compatible = True
            try:
                current_loop = asyncio.get_running_loop()
                if sys.platform == "win32" and "SelectorEventLoop" in type(current_loop).__name__:
                    loop_compatible = False
            except RuntimeError:
                loop_compatible = False

            if not loop_compatible:
                self.log("[EventLoop] Incompatible or missing event loop. Delegating Playwright to isolated Proactor loop...")
                dealers = await self._run_in_isolated_thread(self._run_playwright_session)
            else:
                dealers = await self._run_playwright_session()
        except Exception as e:
            # Exception was already logged and reports generated inside session wrapper
            raise e

        self.search_diagnostics["dealers_extracted_count"] = len(dealers)
        self.log(f"[DIAGNOSTICS_REPORT] {json.dumps(self.search_diagnostics, indent=2)}")
        return dealers

    async def _run_in_isolated_thread(self, coro_func) -> List[Dict[str, Any]]:
        import threading
        import sys
        res_holder = []
        err_holder = []
        
        def thread_worker():
            if sys.platform == "win32":
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                res = loop.run_until_complete(coro_func())
                res_holder.append(res)
            except Exception as e:
                err_holder.append(e)
            finally:
                try:
                    # Clean up all pending tasks in the loop before closing
                    pending = asyncio.all_tasks(loop)
                    if pending:
                        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    loop.close()
                except Exception:
                    pass
                    
        t = threading.Thread(target=thread_worker)
        t.start()
        # Join thread asynchronously using run_in_executor to avoid blocking the main event loop
        await asyncio.get_running_loop().run_in_executor(None, t.join)
        
        if err_holder:
            raise err_holder[0]
        return res_holder[0] if res_holder else []

    async def _run_playwright_session(self) -> List[Dict[str, Any]]:
        dealers = []
        strategy = "STATIC_HTML"
        browser = None
        page = None
        browser_name = "chromium"
        try:
            async with async_playwright() as p:
                try:
                    browser, browser_name = await BrowserManager.launch_with_fallback(p, headless=True)
                except Exception as b_err:
                    self.recovery_attempts.append(f"Browser Launch Failed: {b_err}")
                    raise b_err

                viewport = HumanMode.get_random_viewport()
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                
                context = await browser.new_context(
                    viewport=viewport,
                    user_agent=user_agent,
                    ignore_https_errors=True,
                    locale="en-US",
                    timezone_id="Asia/Kolkata"
                )
                await HumanMode.configure_context(context, user_agent)
                
                page = await context.new_page()
                
                # Network recording
                recorder = NetworkRecorder(self.brand_name)
                captured_apis = []
                
                async def handle_response(response):
                    await recorder.record_response(response)
                    url = response.url
                    if url not in self.search_diagnostics["ajax_requests_fired"]:
                        self.search_diagnostics["ajax_requests_fired"].append(url)
                        
                    try:
                        content_type = response.headers.get("content-type", "").lower()
                        is_xhr = response.request.resource_type in ["xhr", "fetch"]
                        if not is_xhr:
                            is_xhr = "application/json" in content_type or "/api/" in url.lower() or "graphql" in url.lower()
                        if is_xhr:
                            text = await response.text()
                            keywords = ["dealer", "store", "outlet", "address", "city", "latitude", "longitude", "phone", "email"]
                            url_lower = url.lower()
                            text_lower = text.lower()
                            
                            if any(kw in url_lower for kw in keywords) or any(kw in text_lower for kw in keywords):
                                if "application/json" in content_type or text.strip().startswith(("{", "[")):
                                    body = json.loads(text)
                                    dealers_list = find_dealers_in_json(body)
                                    if dealers_list:
                                        if url not in self.search_diagnostics["dealer_endpoints_discovered"]:
                                            self.search_diagnostics["dealer_endpoints_discovered"].append(url)
                                        parsed = parse_dealers_from_json_list(dealers_list)
                                        captured_apis.append({
                                            "url": url,
                                            "headers": response.request.headers,
                                            "dealers": dealers_list,
                                            "body": body,
                                            "parsed_dealers": parsed
                                        })
                                elif "text/html" in content_type:
                                    discovered_selectors = SelectorDiscovery.discover_selectors(text)
                                    if discovered_selectors.get("container"):
                                        parsed = parse_html_dealers(text, discovered_selectors)
                                        if parsed:
                                            if url not in self.search_diagnostics["dealer_endpoints_discovered"]:
                                                self.search_diagnostics["dealer_endpoints_discovered"].append(url)
                                            captured_apis.append({
                                                "url": url,
                                                "headers": response.request.headers,
                                                "dealers": parsed,
                                                "body": text,
                                                "parsed_dealers": parsed,
                                                "is_html": True
                                            })
                    except Exception:
                        pass
                        
                page.on("response", handle_response)
                
                # Navigate
                self.log("[STEP] Opening target locator URL in Playwright...")
                await page.goto(self.locator_url, wait_until="domcontentloaded", timeout=45000)
                
                await DiagnosticReporter.take_timeline_screenshot(page, "loaded")
                
                # Cloudflare & Captcha check on load
                html_snapshot = await page.content()
                if not isinstance(html_snapshot, str):
                    html_snapshot = ""
                page_title = await page.title()
                if not isinstance(page_title, str):
                    page_title = ""
                
                cf_check = BlockingDetector.detect_cloudflare(html_snapshot, page_title)
                if cf_check:
                    self.log("[Cloudflare detected] Blocked by verification page.")
                    raise RuntimeError("Cloudflare detected")
                    
                captcha_check = BlockingDetector.detect_captcha(html_snapshot)
                if captcha_check:
                    self.log("[Captcha detected] Blocked by CAPTCHA challenge.")
                    raise RuntimeError("Captcha detected")
                
                # Handle cookie consent banners
                cookie_selectors = [
                    "button:has-text('accept')", "button:has-text('Accept')", "button:has-text('AGREE')",
                    "button:has-text('Agree')", "button:has-text('consent')", "button:has-text('Consent')",
                    "button:has-text('Allow')", "button:has-text('allow')", "button:has-text('OK')"
                ]
                await HumanMode.move_mouse_randomly(page)
                for selector in cookie_selectors:
                    try:
                        elem = await page.query_selector(selector)
                        if elem and await elem.is_visible():
                            await elem.click()
                            await page.wait_for_timeout(1000)
                    except Exception:
                        pass
                await DiagnosticReporter.take_timeline_screenshot(page, "cookie")
                
                # Search Interaction Engine
                search_input = None
                detected_selector = None
                search_selectors = [
                    "input[type='search']", "input[placeholder*='search' i]", "input[placeholder*='city' i]",
                    "input[placeholder*='location' i]", "input[type='text']"
                ]
                for sel in search_selectors:
                    try:
                        elem = await page.query_selector(sel)
                        if elem and await elem.is_visible() and await elem.is_enabled():
                            search_input = elem
                            detected_selector = sel
                            break
                    except Exception:
                        pass
                        
                if search_input:
                    self.search_diagnostics["search_field_detected"] = detected_selector
                    keywords = self.config.get("search_keywords") or ["Noida", "Delhi", "Mumbai"]
                    for keyword in keywords:
                        self.log(f"[Search Engine] Typing keyword: {keyword}")
                        if keyword not in self.search_diagnostics["keywords_entered"]:
                            self.search_diagnostics["keywords_entered"].append(keyword)
                            
                        await search_input.click()
                        await search_input.fill("")
                        await page.wait_for_timeout(300)
                        await HumanMode.type_like_human(search_input, keyword)
                        await page.wait_for_timeout(2000)
                        await DiagnosticReporter.take_timeline_screenshot(page, "search")
                        
                        # Check dropdowns
                        suggestion_selectors = [
                            ".pac-container .pac-item", "[class*='suggestion' i]", "ul[role='listbox'] li"
                        ]
                        suggestions = []
                        sugg_texts = []
                        for sugg_sel in suggestion_selectors:
                            try:
                                elems = await page.query_selector_all(sugg_sel)
                                visible = [el for el in elems if await el.is_visible()]
                                if visible:
                                    suggestions = visible
                                    sugg_texts = [await el.inner_text() for el in visible]
                                    for txt in sugg_texts:
                                        if txt not in self.search_diagnostics["suggestions_detected"]:
                                            self.search_diagnostics["suggestions_detected"].append(txt)
                                    break
                            except Exception:
                                pass
                                
                        if suggestions:
                            target = suggestions[0]
                            sugg_text = sugg_texts[0] if sugg_texts else "First Suggestion"
                            if sugg_text not in self.search_diagnostics["suggestions_selected"]:
                                self.search_diagnostics["suggestions_selected"].append(sugg_text)
                            await target.click()
                        else:
                            await search_input.press("Enter")
                        await page.wait_for_timeout(2000)
                        await DiagnosticReporter.take_timeline_screenshot(page, "dropdown")
                else:
                    # Select option state fallback
                    state_selects = await page.query_selector_all("select[name*='state'], select[id*='state']")
                    if state_selects:
                        select_elem = state_selects[0]
                        options = await select_elem.query_selector_all("option")
                        option_values = [await opt.get_attribute("value") for opt in options]
                        option_values = [v for v in option_values if v and v.strip() and v.lower() not in ["", "select", "all"]]
                        for val in option_values[:3]:
                            await select_elem.select_option(val)
                            await page.wait_for_timeout(1000)
                            submit_btns = await page.query_selector_all("button[type='submit'], input[type='submit']")
                            if submit_btns:
                                await submit_btns[0].click()
                                await page.wait_for_timeout(2000)
                                
                await HumanMode.scroll_smoothly(page, "down", 500)
                await page.wait_for_timeout(3000)
                await DiagnosticReporter.take_timeline_screenshot(page, "results")
                
                # Fetch final dealers
                if captured_apis:
                    strategy = "API"
                    for cap in captured_apis:
                        parsed = cap["dealers"] if cap.get("is_html") else parse_dealers_from_json_list(cap["dealers"])
                        for d in parsed:
                            if d not in dealers:
                                dealers.append(d)
                else:
                    strategy = "PLAYWRIGHT"
                    html_content = await page.content()
                    selectors = SelectorDiscovery.discover_selectors(html_content)
                    if selectors.get("container"):
                        page_dealers = parse_html_dealers(html_content, selectors)
                        for d in page_dealers:
                            if d not in dealers:
                                dealers.append(d)
                                
                # Save DOM snapshot
                final_html = await page.content()
                DiagnosticReporter.save_html_snapshot(final_html, "final_dom.html")
                
                await browser.close()
                
        except Exception as e:
            # Failure block: Log, generate snapshot, and write failure markdown report
            self.recovery_attempts.append("Playwright Failover Retry")
            
            cf_detected = False
            captcha_detected = False
            try:
                if page:
                    fail_html = await page.content()
                    if not isinstance(fail_html, str):
                        fail_html = ""
                    fail_title = await page.title()
                    if not isinstance(fail_title, str):
                        fail_title = ""
                    DiagnosticReporter.save_html_snapshot(fail_html, "final_dom.html")
                    DiagnosticReporter.save_html_snapshot(fail_html, "sleepwell_failure.html")
                    await DiagnosticReporter.take_timeline_screenshot(page, "failure")
                    
                    if BlockingDetector.detect_cloudflare(fail_html, fail_title):
                        cf_detected = True
                    if BlockingDetector.detect_captcha(fail_html):
                        captcha_detected = True
            except Exception:
                pass
                
            reason = "Timeout or browser connection error"
            if cf_detected or "cloudflare" in str(e).lower():
                reason = "Cloudflare detected"
            elif captcha_detected or "captcha" in str(e).lower():
                reason = "Captcha detected"
            else:
                reason = f"Playwright Failure: {e}"
                
            self.log(f"[CRITICAL] {reason}")
            
            DiagnosticReporter.write_failure_report(
                browser_used=browser_name,
                strategy_chosen=strategy,
                ajax_calls=self.search_diagnostics["ajax_requests_fired"],
                dealer_apis=self.search_diagnostics["dealer_endpoints_discovered"],
                dealers_parsed=len(dealers),
                reason_stopped=reason,
                recovery_attempts=self.recovery_attempts,
                suggested_action="Verify captcha parameters, rotate proxies, or customize search selectors."
            )
            raise RuntimeError(reason) from e
            
        return dealers

    def save(self, dealers: List[Dict[str, Any]]) -> int:
        return len(dealers)
