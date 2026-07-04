import os
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class NetworkRecorder:
    """
    Sniffs and records browser network request telemetry.
    Saves JSON bodies locally and classifies dealer endpoints.
    """

    def __init__(self, brand_name: str) -> None:
        self.brand_name = brand_name
        self.recorded_requests: List[Dict[str, Any]] = []
        self.json_counter = 0
        
        # Create debug directory if not exists
        os.makedirs("debug", exist_ok=True)
        
        self.signature_keywords = [
            "dealer", "store", "locator", "branch", "partner", "outlet",
            "search", "find", "location", "autocomplete", "nearby"
        ]

    async def record_response(self, response) -> None:
        """Processes and logs an intercepted page response."""
        try:
            url = response.url
            method = response.request.method
            status = response.status
            content_type = response.headers.get("content-type", "").lower()
            
            body_text = ""
            try:
                body_text = await response.text()
            except Exception:
                pass
                
            resp_size = len(body_text) if body_text else 0
            
            # Classification
            url_lower = url.lower()
            is_dealer_related = any(kw in url_lower for kw in self.signature_keywords)
            
            entry = {
                "url": url,
                "method": method,
                "status": status,
                "content_type": content_type,
                "response_size": resp_size,
                "is_dealer_related": is_dealer_related,
                "resource_type": response.request.resource_type
            }
            self.recorded_requests.append(entry)
            
            # Save JSON responses
            is_json = "application/json" in content_type or body_text.strip().startswith(("{", "["))
            if is_json and resp_size > 0:
                try:
                    parsed_json = json.loads(body_text)
                    self.json_counter += 1
                    file_path = f"debug/json_response_{self.json_counter}.json"
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump({
                            "url": url,
                            "method": method,
                            "status": status,
                            "content_type": content_type,
                            "body": parsed_json
                        }, f, indent=2)
                except Exception:
                    pass
                    
        except Exception as e:
            logger.debug(f"Failed to record response: {e}")

    def get_dealer_endpoints(self) -> List[str]:
        """Returns a list of URLs identified as dealer-related APIs."""
        endpoints = []
        for r in self.recorded_requests:
            if r["is_dealer_related"] and ("application/json" in r["content_type"] or r["resource_type"] in ["xhr", "fetch"]):
                endpoints.append(r["url"])
        return list(set(endpoints))
