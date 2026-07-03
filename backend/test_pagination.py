import sys
import unittest

sys.path.insert(0, ".")

from app.scrapers.pagination_engine import PaginationEngine

class TestPaginationEngine(unittest.TestCase):
    def test_page_number_strategy(self):
        """Verify PAGE_NUMBER strategy increments ?page= query parameter."""
        base_url = "https://example.com/locator?city=Delhi"
        next_url = PaginationEngine.get_next_page_url(
            current_url=base_url,
            strategy="PAGE_NUMBER",
            current_page=1,
            records_scraped=30,
            max_pages=5
        )
        self.assertEqual(next_url, "https://example.com/locator?city=Delhi&page=2")

    def test_offset_strategy(self):
        """Verify OFFSET strategy increments offset query parameter by multiples of limit."""
        base_url = "https://example.com/locator?limit=30"
        next_url = PaginationEngine.get_next_page_url(
            current_url=base_url,
            strategy="OFFSET",
            current_page=2,
            records_scraped=30,
            records_per_page=30,
            max_pages=5
        )
        self.assertEqual(next_url, "https://example.com/locator?limit=30&offset=60")

    def test_max_pages_cutoff(self):
        """Verify pagination stops (returns None) when exceeding max_pages limit."""
        base_url = "https://example.com/locator"
        next_url = PaginationEngine.get_next_page_url(
            current_url=base_url,
            strategy="PAGE_NUMBER",
            current_page=5,
            records_scraped=30,
            max_pages=5
        )
        self.assertIsNone(next_url)

    def test_no_records_cutoff(self):
        """Verify pagination stops if zero records were extracted on the last page."""
        base_url = "https://example.com/locator"
        next_url = PaginationEngine.get_next_page_url(
            current_url=base_url,
            strategy="PAGE_NUMBER",
            current_page=2,
            records_scraped=0,
            max_pages=5
        )
        self.assertIsNone(next_url)

if __name__ == "__main__":
    unittest.main()
