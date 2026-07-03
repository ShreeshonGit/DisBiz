import sys
import unittest

sys.path.insert(0, ".")

from app.scrapers.selector_discovery import SelectorDiscovery

class TestSelectorDiscovery(unittest.TestCase):
    def test_dom_inspection_heuristics(self):
        """Verify discover_selectors identifies container and attribute CSS classes with confidence."""
        mock_html = """
        <html>
            <body>
                <div class="dealer-card">
                    <h3 class="store-name">Apex Electronics Delhi</h3>
                    <p class="store-address">Main Nehru Marg, Block 3, Delhi 110001</p>
                    <span class="phone">011-98765432</span>
                    <a href="mailto:apex@electronics.com" class="email">Mail Us</a>
                </div>
                <div class="dealer-card">
                    <h3 class="store-name">Apex Electronics Noida</h3>
                    <p class="store-address">Sector 15, Noida, UP 201301</p>
                    <span class="phone">0120-1234567</span>
                    <a href="mailto:noida@apex.com" class="email">Mail Us</a>
                </div>
            </body>
        </html>
        """
        suggestions = SelectorDiscovery.discover_selectors(mock_html)
        
        # Check container discovery
        self.assertEqual(suggestions["container"]["selector"], ".dealer-card")
        self.assertGreaterEqual(suggestions["container"]["confidence"], 0.8)
        
        # Check attribute selector class name heuristics
        self.assertEqual(suggestions["name"]["selector"], ".store-name")
        self.assertEqual(suggestions["address"]["selector"], ".store-address")
        self.assertEqual(suggestions["phone"]["selector"], ".phone")
        self.assertEqual(suggestions["email"]["selector"], ".email")

if __name__ == "__main__":
    unittest.main()
