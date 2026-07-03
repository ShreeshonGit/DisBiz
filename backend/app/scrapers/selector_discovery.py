from bs4 import BeautifulSoup
import re
from typing import Dict, Any, List

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
        
        # Count all class occurrences in the HTML
        class_counts = {}
        for elem in soup.find_all(class_=True):
            classes = elem.get("class")
            if isinstance(classes, list):
                for cls in classes:
                    class_counts[cls] = class_counts.get(cls, 0) + 1
            elif isinstance(classes, str):
                class_counts[classes] = class_counts.get(classes, 0) + 1
                
        # Find candidates: classes that repeat at least 2 times
        candidates = []
        for cls, count in class_counts.items():
            if count >= 2:
                score = 0.0
                cls_lower = cls.lower()
                
                # Check container keyword patterns
                keywords = ["dealer", "store", "location", "branch", "outlet", "shop", "office", "partner", "locator-item", "card", "item", "row"]
                for kw in keywords:
                    if kw in cls_lower:
                        score += 0.3
                        
                # Inspect first few matching elements for nested contact structures
                try:
                    sample_nodes = soup.select(f".{cls}")[:5]
                    child_indicators = 0
                    for node in sample_nodes:
                        text = node.get_text().strip()
                        # Phone numbers pattern match
                        if re.search(r'\+?\d{2,4}[- ]?\d{3,4}[- ]?\d{3,4}', text):
                            child_indicators += 0.2
                        # Email matches
                        if "@" in text:
                            child_indicators += 0.2
                        # Check maps/location links
                        if node.find("a", href=lambda h: h and ("maps" in h or "google.com/maps" in h)):
                            child_indicators += 0.2
                    
                    score += (child_indicators / len(sample_nodes)) if len(sample_nodes) > 0 else 0
                except Exception:
                    pass
                
                candidates.append({
                    "selector": f".{cls}",
                    "count": count,
                    "score": score
                })
                
        # Include common tag+class candidates
        tag_candidates = ["div.store", "div.dealer", "tr.dealer", "li.location", "div.location"]
        for tag in tag_candidates:
            nodes = soup.select(tag)
            if len(nodes) >= 2:
                candidates.append({
                    "selector": tag,
                    "count": len(nodes),
                    "score": 0.4
                })
                
        # Sort candidates by score descending
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        container_selector = ".dealer-item"
        if candidates:
            container_selector = candidates[0]["selector"]
            
        # Field search selector definitions
        suggestions = {
            "name": [
                ".dealer-name", ".store-name", ".location-name", ".name", "h3", "h2", ".title", ".shop-name", 
                "span.name", "div.title"
            ],
            "address": [
                ".address", ".store-address", ".location-address", "p.address", ".addr", ".address-text",
                ".formatted-address", "span.address", "div.address"
            ],
            "phone": [
                ".phone", ".tel", ".mobile", "span.phone", "a[href^='tel:']", ".telephone", ".contact-phone"
            ],
            "email": [
                ".email", "a[href^='mailto:']", ".contact-email", ".email-text"
            ],
            "pincode": [
                ".pincode", ".zip", ".postal-code", "span.pin", ".postal"
            ],
            "city": [
                ".city", ".town", "span.city", ".locality"
            ],
            "state": [
                ".state", "span.state", ".region"
            ],
            "latitude": [
                ".latitude", "[data-lat]", "[data-latitude]", ".lat"
            ],
            "longitude": [
                ".longitude", "[data-lng]", "[data-longitude]", ".lng", ".lon"
            ],
            "website": [
                "a.website", "a.store-link", "a[href^='http']", ".website", "a:has-text('Website')",
                "a:has-text('website')"
            ]
        }
        
        discovered = {
            "container": {
                "selector": container_selector,
                "confidence": candidates[0]["score"] if candidates else 0.4
            }
        }
        
        for field, selectors in suggestions.items():
            field_matches = []
            for selector in selectors:
                try:
                    nodes = soup.select(f"{container_selector} {selector}")
                    if len(nodes) > 0:
                        non_empty = [n for n in nodes if n.get_text().strip()]
                        match_rate = len(non_empty) / len(nodes) if len(nodes) > 0 else 0.0
                        
                        keyword_score = 0.0
                        if field in selector.lower():
                            keyword_score = 0.3
                            
                        confidence = 0.4 + (0.4 * match_rate) + keyword_score
                        field_matches.append({
                            "selector": selector,
                            "confidence": round(confidence, 2)
                        })
                except Exception:
                    continue
            
            if field_matches:
                field_matches.sort(key=lambda x: x["confidence"], reverse=True)
                discovered[field] = field_matches[0]
            else:
                discovered[field] = {
                    "selector": selectors[0],
                    "confidence": 0.1
                }
                
        return discovered
