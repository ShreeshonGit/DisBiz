import unittest
from uuid import uuid4
from app.scrapers.sleepwell_scraper import SleepwellScraper

class TestSleepwellScraper(unittest.TestCase):
    def test_sleepwell_scraper_fallback(self):
        """Verify SleepwellScraper returns mock records when no selectors are configured."""
        brand_id = uuid4()
        scraper = SleepwellScraper(
            brand_id=brand_id,
            brand_name="Sleepwell",
            locator_url="https://sleepwellmypartner.com/",
            config={}
        )
        dealers = scraper.parse("<html>random</html>")
        self.assertEqual(len(dealers), 2)
        self.assertEqual(dealers[0]["dealer_name"], "Sleepwell World - Connaught Place")
        
    def test_sleepwell_scraper_generic(self):
        """Verify SleepwellScraper delegates parsing to parent GenericScraper if selectors exist."""
        brand_id = uuid4()
        config = {
            "css_selector_config": {
                "container": "div.store-card",
                "name": "h3.title",
                "address": "p.addr"
            }
        }
        scraper = SleepwellScraper(
            brand_id=brand_id,
            brand_name="Sleepwell",
            locator_url="https://sleepwellmypartner.com/",
            config=config
        )
        html = """
        <div class="store-card">
            <h3 class="title">Sleepwell Outlet A</h3>
            <p class="addr">123 Lane, Delhi 110001</p>
        </div>
        """
        dealers = scraper.parse(html)
        self.assertEqual(len(dealers), 1)
        self.assertEqual(dealers[0]["dealer_name"], "Sleepwell Outlet A")
        self.assertEqual(dealers[0]["address"], "123 Lane, Delhi 110001")

if __name__ == "__main__":
    unittest.main()
