from typing import List, Dict, Any, Optional
import urllib.parse
import logging

logger = logging.getLogger(__name__)

class PaginationEngine:
    """
    Standard pagination parameter generator and pagination url resolver.
    Supports Next Button selectors, Page numbers, offset query parameters,
    and cursor navigation increments.
    """

    @staticmethod
    def get_next_page_url(
        current_url: str,
        strategy: str,
        current_page: int,
        records_scraped: int = 0,
        records_per_page: int = 30,
        max_pages: int = 5
    ) -> Optional[str]:
        """
        Determines the URL of the next page based on pagination strategy.
        Returns None if we have hit max_pages or no records were scraped (indicating the end).
        """
        if current_page >= max_pages or (current_page > 1 and records_scraped == 0):
            return None

        parsed = urllib.parse.urlparse(current_url)
        query = urllib.parse.parse_qs(parsed.query)

        if strategy == "PAGE_NUMBER":
            # e.g., page=2
            query["page"] = [str(current_page + 1)]
            
        elif strategy == "OFFSET":
            # e.g., offset=30, offset=60
            query["offset"] = [str(current_page * records_per_page)]
            
        elif strategy == "LOAD_MORE" or strategy == "INFINITE_SCROLL":
            # For dynamic engines, we often track cursor or offsets
            query["page"] = [str(current_page + 1)]
            query["skip"] = [str(current_page * records_per_page)]
            
        else:
            return None

        new_query = urllib.parse.urlencode(query, doseq=True)
        next_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        return next_url
