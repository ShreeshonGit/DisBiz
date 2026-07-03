from bs4 import BeautifulSoup
import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class SelectorDiscovery:
    """
    DOM analyzer that inspects HTML tags, classes, and microdata formats to discover
    and suggest candidate CSS selectors for dealer profile attributes with confidence scores.
    """

    @staticmethod
    def discover_selectors(html_content: str) -> Dict[str, Any]:
        """
        Scans raw HTML content for patterns indicating dealer nodes,
        and extracts suggestions for Name, Address, Phone, Email, City, State, PIN, and Website.
        """
        soup = BeautifulSoup(html_content, "lxml")
        
        # 1. Look for container candidates
        container_candidates = [
            ".dealer-card", ".store-item", ".location-card", ".store-locator-item",
            ".dealer-item", ".store-card", "div.store", "div.dealer", "tr.dealer",
            ".shop-card", ".location-item"
        ]
        
        container_selector = ".dealer-item"
        for sel in container_candidates:
            if len(soup.select(sel)) >= 2:
                container_selector = sel
                break

        # 2. Extract attribute suggestions based on keyword searches in class names
        suggestions = {
            "container": container_selector,
            "name": [".dealer-name", ".store-name", "h3", "h2", ".title", ".shop-name"],
            "address": [".address", ".store-address", ".location-address", "p.address", ".addr"],
            "phone": [".phone", ".tel", ".mobile", "span.phone", "a[href^='tel:']"],
            "email": [".email", "a[href^='mailto:']", ".contact-email"],
            "pincode": [".pincode", ".zip", ".postal-code", "span.pin"],
            "city": [".city", ".town", "span.city"],
            "state": [".state", "span.state"],
            "latitude": [".latitude", "[data-lat]", "[data-latitude]"],
            "longitude": [".longitude", "[data-lng]", "[data-longitude]"],
            "website": ["a.website", "a.store-link", "a[href^='http']"]
        }

        # Validate existence of selectors on the page and compute confidence
        discovered = {}
        for field, selectors in suggestions.items():
            if field == "container":
                discovered["container"] = {
                    "selector": container_selector,
                    "confidence": 0.9 if container_selector != ".dealer-item" else 0.4
                }
                continue

            field_matches = []
            for selector in selectors:
                try:
                    # Search inside container or page
                    nodes = soup.select(f"{container_selector} {selector}")
                    if len(nodes) > 0:
                        non_empty = [n for n in nodes if n.get_text().strip()]
                        match_rate = len(non_empty) / len(nodes) if len(nodes) > 0 else 0.0
                        confidence = 0.5 + (0.4 * match_rate)
                        
                        field_matches.append({
                            "selector": selector,
                            "confidence": round(confidence, 2)
                        })
                except Exception:
                    continue

            # Sort matches by confidence
            if field_matches:
                field_matches.sort(key=lambda x: x["confidence"], reverse=True)
                discovered[field] = field_matches[0]
            else:
                # Fallback default
                discovered[field] = {
                    "selector": selectors[0],
                    "confidence": 0.3
                }

        return discovered
