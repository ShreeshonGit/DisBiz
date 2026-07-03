from typing import List, Dict, Any, Optional
from bs4 import Tag
import logging

logger = logging.getLogger(__name__)

class SelectorFallbackEngine:
    """
    Intelligence layer to execute sequential selector evaluation, fallback checks,
    and performance logging of CSS selector selectors success statistics.
    """

    def __init__(self) -> None:
        # In-memory mapping to track success rates: {selector_str: {"success": int, "total": int}}
        self.selector_stats: Dict[str, Dict[str, int]] = {}

    def extract_field(self, node: Tag, selectors: Any, field_name: str) -> str:
        """
        Extracts content from a BeautifulSoup node by trying a list of selectors in order.
        If a selector successfully returns non-empty text, it registers success and returns the value.
        """
        if not selectors:
            return ""

        # Standardize selectors into a list of strings
        if isinstance(selectors, str):
            selector_list = [selectors]
        elif isinstance(selectors, list):
            selector_list = [str(s) for s in selectors]
        else:
            return ""

        for selector in selector_list:
            if not selector.strip():
                continue
                
            # Initialize stats tracking for this selector
            if selector not in self.selector_stats:
                self.selector_stats[selector] = {"success": 0, "total": 0}
            
            self.selector_stats[selector]["total"] += 1
            
            try:
                element = node.select_one(selector)
                if element:
                    text = element.get_text().strip()
                    if text:
                        # Found non-empty text: record success and return
                        self.selector_stats[selector]["success"] += 1
                        return text
            except Exception as e:
                logger.warning(f"Selector evaluation error for '{selector}' on field '{field_name}': {e}")
                
        # If all selectors fail, return empty string
        return ""

    def get_success_rate(self, selector: str) -> float:
        """
        Returns the success rate (0.0 to 1.0) of a selector.
        """
        stats = self.selector_stats.get(selector)
        if not stats or stats["total"] == 0:
            return 0.0
        return stats["success"] / stats["total"]
