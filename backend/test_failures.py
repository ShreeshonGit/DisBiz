import sys
import unittest
from unittest.mock import patch, MagicMock
from uuid import uuid4
import httpx
from bs4 import BeautifulSoup

sys.path.insert(0, ".")

from app.services.scraper_recovery_manager import ScraperRecoveryManager
from app.scrapers.generic_scraper import GenericScraper
from app.scrapers.selector_fallback_engine import SelectorFallbackEngine
from app.scrapers.base_scraper import BaseScraper

class TestReliabilityAndRecovery(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.recovery_mgr = ScraperRecoveryManager()
        self.job_id = uuid4()
        self.brand_id = uuid4()

    def test_error_classification_network(self):
        """Verify network connection failure classification."""
        exc = httpx.ConnectError("Connection refused by target host")
        err_type = self.recovery_mgr.classify_exception(exc)
        self.assertEqual(err_type, "NETWORK_ERROR")

    def test_error_classification_timeout(self):
        """Verify read/write timeout failure classification."""
        exc = httpx.ReadTimeout("Request timed out during read phase")
        err_type = self.recovery_mgr.classify_exception(exc)
        self.assertEqual(err_type, "TIMEOUT_ERROR")

    def test_error_classification_selector(self):
        """Verify missing attributes or tags classification."""
        exc = AttributeError("'NoneType' object has no attribute 'get_text'")
        err_type = self.recovery_mgr.classify_exception(exc)
        self.assertEqual(err_type, "SELECTOR_ERROR")

    def test_error_classification_parse(self):
        """Verify general parsing/decoding failure classification."""
        exc = ValueError("Failed to parse JSON schema body")
        err_type = self.recovery_mgr.classify_exception(exc)
        self.assertEqual(err_type, "PARSE_ERROR")

    @patch("app.repositories.scrape_job_repository.ScrapeJobRepository.update")
    def test_record_failure_db_write(self, mock_update):
        """Verify recovery manager writes failure details to database."""
        exc = httpx.ConnectError("Failed to connect")
        self.recovery_mgr.record_failure(self.job_id, exc, retry_count=2, last_page=3)
        
        mock_update.assert_called_once()
        args, kwargs = mock_update.call_args
        self.assertEqual(args[0], self.job_id)
        self.assertEqual(args[1]["failure_reason"], "NETWORK_ERROR")
        self.assertEqual(args[1]["retry_count"], 2)
        self.assertEqual(args[1]["last_successful_page"], 3)

    def test_selector_fallback_success(self):
        """Verify selector fallback tries subsequent options and returns value."""
        fallback_engine = SelectorFallbackEngine()
        html = "<div><span class='address-fallback'>123 alternate address road</span></div>"
        soup = BeautifulSoup(html, "lxml")
        
        # Primary '.address-primary' doesn't exist, fallback '.address-fallback' exists
        selectors = [".address-primary", ".address-fallback", "p"]
        result = fallback_engine.extract_field(soup, selectors, "address")
        
        self.assertEqual(result, "123 alternate address road")
        self.assertEqual(fallback_engine.selector_stats[".address-primary"]["success"], 0)
        self.assertEqual(fallback_engine.selector_stats[".address-fallback"]["success"], 1)
        self.assertAlmostEqual(fallback_engine.get_success_rate(".address-fallback"), 1.0)
        self.assertAlmostEqual(fallback_engine.get_success_rate(".address-primary"), 0.0)

    @patch("app.repositories.scrape_job_repository.ScrapeJobRepository.get_by_id")
    @patch("app.repositories.scrape_job_repository.ScrapeJobRepository.update")
    @patch("app.repositories.brand_repository.BrandRepository.get_by_id")
    @patch("app.repositories.scraper_config_repository.ScraperConfigRepository.get_by_brand_id")
    @patch("app.scrapers.generic_scraper.GenericScraper.extract_dealers")
    async def test_job_runner_cancellation_mid_job(self, mock_extract, mock_config, mock_brand, mock_update, mock_get_job_by_id):
        """Verify scraper runner halts execution if job cancellation is registered."""
        from app.services.scraper_job_runner import ScraperJobRunner
        runner = ScraperJobRunner()

        mock_brand.return_value = {
            "name": "Lava",
            "dealer_locator_url": "https://example.com"
        }
        mock_config.return_value = {
            "scraper_type": "STATIC_HTML"
        }
        # Simulate cancellation response
        mock_get_job_by_id.return_value = {
            "status": "Cancelled"
        }

        # Run job
        await runner.run_job(self.job_id, self.brand_id)
        
        # Verify extract_dealers was NEVER called because cancellation flag checked first
        mock_extract.assert_not_called()

if __name__ == "__main__":
    unittest.main()
