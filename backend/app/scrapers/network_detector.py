import re
import json
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class NetworkDetector:
    """
    Analyzes page markup and scripts to detect dynamic REST APIs, Fetch, XHR,
    or GraphQL endpoints used by dealer locators.
    """

    @staticmethod
    def detect_api(html_content: str, url: str) -> Optional[Dict[str, Any]]:
        """
        Scans HTML text for AJAX/fetch/axios patterns.
        If a JSON API is detected, returns metadata containing endpoint details.
        """
        # Common endpoint patterns
        api_pattern = re.compile(
            r'(https?://[a-zA-Z0-9.-]+(?:/api/|/getDealer|/store-locator/|/stores\.json|/locations\?)[a-zA-Z0-9_/.-]*)',
            re.IGNORECASE
        )
        matches = api_pattern.findall(html_content)
        
        # Specific fallback patterns for Lava
        if "lavamobiles.com" in url:
            # We already reverse engineered the endpoint and headers
            return {
                "detected_endpoint": "https://webapi.lavamobiles.com/api/dealer-locator-service/dealer",
                "request_headers": {
                    "Content-Type": "application/json",
                    "api-key-HS256240625lava": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJsYXZhYXBpIiwibmFtZSI6ImxhdmFtb2JpbGV3ZWIiLCJhZG1pbiI6dHJ1ZSwiaWF0IjoyNDA2MjAyNX0.4v7h6QZKgI4soVGtJfK55--2gfrLQh4RIui2OukrxgI"
                },
                "request_payload": {"pincode": ""},
                "http_method": "GET"
            }
            
        if matches:
            endpoint = matches[0]
            # Clean trailing punctuation
            endpoint = re.sub(r'[\'"",;})\]\s]+$', '', endpoint)
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            return {
                "detected_endpoint": endpoint,
                "request_headers": headers,
                "request_payload": {},
                "http_method": "GET"
            }
            
        # Detect admin-ajax or wordpress endpoints
        if "wp-admin/admin-ajax.php" in html_content:
            wp_idx = html_content.find("wp-admin/admin-ajax.php")
            start = max(0, wp_idx - 50)
            end = min(len(html_content), wp_idx + 100)
            snippet = html_content[start:end]
            
            # extract full domain if present
            domain_match = re.search(r'(https?://[a-zA-Z0-9.-]+/wp-admin/admin-ajax.php)', snippet)
            endpoint = domain_match.group(1) if domain_match else "/wp-admin/admin-ajax.php"
            
            return {
                "detected_endpoint": endpoint,
                "request_headers": {"Content-Type": "application/x-www-form-urlencoded"},
                "request_payload": {"action": "get_stores"},
                "http_method": "POST"
            }

        return None
