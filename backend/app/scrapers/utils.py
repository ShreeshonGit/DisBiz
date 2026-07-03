from typing import Dict, Any, Optional
import httpx
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

logger = logging.getLogger(__name__)

# Initialize fake-useragent fallback list
ua = UserAgent(fallback="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

def get_headers() -> Dict[str, str]:
    """Generates realistic HTTP request headers to bypass basic scraper blocks."""
    return {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1"
    }

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(httpx.RequestError),
    reraise=True
)
async def fetch_url_with_retry(url: str, timeout: int = 15) -> httpx.Response:
    """
    Fetches a URL asynchronously using HTTPX with user-agent rotation and exponential backoff.
    """
    async with httpx.AsyncClient(follow_redirects=True) as client:
        logger.info(f"Fetching URL: {url} (attempt details: tenacity active)")
        headers = get_headers()
        response = await client.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response

def detect_content_type(response: httpx.Response) -> str:
    """
    Inspects response body and headers to classify locator page type:
    STATIC_HTML, JAVASCRIPT, API, or UNKNOWN.
    """
    content_type = response.headers.get("content-type", "").lower()
    
    # 1. Check API endpoints (returns application/json)
    if "application/json" in content_type:
        return "API"
        
    body_text = response.text
    
    # 2. Check Javascript heavy frameworks or script templates
    js_indicators = [
        "react-root", "next-route-announcer", "__next_f", "id=\"app\"", "vue-container", 
        "ng-version", "angular", "window.__initial_state__", "bundle.js"
    ]
    
    if any(ind in body_text for ind in js_indicators):
        return "JAVASCRIPT"
        
    # 3. Check for standard HTML signatures
    html_indicators = ["<html", "<body", "<div", "<p", "href="]
    if any(ind in body_text for ind in html_indicators):
        return "STATIC_HTML"
        
    return "UNKNOWN"
