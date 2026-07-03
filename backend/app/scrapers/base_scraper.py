from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from uuid import UUID

class BaseScraper(ABC):
    """
    Abstract Base Class for all scrapers in the hybrid architecture.
    Provides common initialization fields and defines the core scraping lifecycle interface.
    """

    def __init__(self, brand_id: UUID, brand_name: str, locator_url: str, config: Optional[Dict[str, Any]] = None) -> None:
        self.brand_id = brand_id
        self.brand_name = brand_name
        self.locator_url = locator_url
        self.config = config or {}
        self.logs: List[str] = []

    def log(self, message: str) -> None:
        """Appends a structured log statement to the scraper's run history."""
        timestamp = time_str = ""
        try:
            from datetime import datetime
            time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except ImportError:
            pass
        log_msg = f"[{time_str}] {message}"
        self.logs.append(log_msg)

    @abstractmethod
    def validate_url(self) -> bool:
        """Validates if the provided locator_url is well-formed and matches the expected brand domain."""
        pass

    @abstractmethod
    async def detect_locator_type(self) -> str:
        """
        Analyzes the target URL responses to auto-detect its type:
        STATIC_HTML, JAVASCRIPT, API, or UNKNOWN.
        """
        pass

    @abstractmethod
    async def fetch_page(self) -> str:
        """Fetches the target locator page content, dynamically using HTTPX or Playwright."""
        pass

    @abstractmethod
    def parse(self, html_content: str) -> List[Dict[str, Any]]:
        """Parses raw HTML/API content into structured, raw dealer dictionary records."""
        pass

    @abstractmethod
    async def preview(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Runs a mock-scrape execution retrieving only the first 'limit' rows.
        Does not perform database write operations.
        """
        pass

    @abstractmethod
    async def extract_dealers(self) -> List[Dict[str, Any]]:
        """Executes the full scraping process, fetching, parsing, normalizing, and validating records."""
        pass

    @abstractmethod
    def save(self, dealers: List[Dict[str, Any]]) -> int:
        """Saves the extracted records. Under Sprint 3.1, this is a skeleton return count only."""
        pass
