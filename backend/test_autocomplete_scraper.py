import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import json
import uuid
import asyncio
from app.scrapers.generic_scraper import GenericScraper

class TestAutocompleteScraper(unittest.IsolatedAsyncioTestCase):
    async def test_autocomplete_search_flow(self):
        """Verify GenericScraper search autocomplete engine detects fields, enters keywords, selects dropdowns, intercepts XHRs and populates diagnostics."""
        brand_id = uuid.uuid4()
        scraper = GenericScraper(
            brand_id=brand_id,
            brand_name="Mock Autocomplete Brand",
            locator_url="https://example.com/locator-with-search",
            config={
                "search_keywords": ["Noida", "Mumbai"]
            }
        )

        # 1. Create mocks for Playwright elements
        mock_input = AsyncMock()
        mock_input.is_visible = AsyncMock(return_value=True)
        mock_input.is_enabled = AsyncMock(return_value=True)
        mock_input.click = AsyncMock()
        mock_input.fill = AsyncMock()
        mock_input.press = AsyncMock()

        mock_suggestion = AsyncMock()
        mock_suggestion.is_visible = MagicMock(return_value=True)
        # Handle async is_visible check in suggestions loop
        async def async_is_visible():
            return True
        mock_suggestion.is_visible = async_is_visible
        mock_suggestion.inner_text = AsyncMock(return_value="Bosch Service Center, Noida")
        mock_suggestion.click = AsyncMock()

        # 2. Mock Page
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html></html>")
        
        async def mock_query_selector(selector):
            if "input" in selector:
                return mock_input
            return None
        mock_page.query_selector = mock_query_selector

        async def mock_query_selector_all(selector):
            if "state" in selector:
                return []
            if "suggestion" in selector or "item" in selector or "dropdown" in selector or "listbox" in selector:
                return [mock_suggestion]
            return []
        mock_page.query_selector_all = mock_query_selector_all

        # Capture response listener callback
        response_callback = None
        def mock_on(event, callback):
            nonlocal response_callback
            if event == "response":
                response_callback = callback
        mock_page.on = mock_on

        # 3. Mock Browser and Context
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()

        # 4. Patch async_playwright
        mock_p_ctx = MagicMock()
        mock_p_ctx.__aenter__ = AsyncMock(return_value=mock_p_ctx)
        mock_p_ctx.__aexit__ = AsyncMock(return_value=None)
        mock_p_ctx.chromium = MagicMock()
        mock_p_ctx.chromium.launch = AsyncMock(return_value=mock_browser)

        # 5. Set up side-effect to trigger simulated AJAX response when the search keyword is typed
        async def trigger_ajax(*args, **kwargs):
            if response_callback:
                mock_json_response = {
                    "dealers": [
                        {
                            "name": "Noida Bosch Outlet",
                            "address": "Sector 62, Noida, Uttar Pradesh 201301",
                            "city": "Noida",
                            "pincode": "201301",
                            "phone": "+91120444555",
                            "email": "noida@bosch.com"
                        }
                    ]
                }
                
                mock_response = AsyncMock()
                mock_response.url = "https://example.com/api/v1/dealers/search?query=Noida"
                mock_response.headers = {"content-type": "application/json"}
                mock_response.text = AsyncMock(return_value=json.dumps(mock_json_response))
                
                mock_request = MagicMock()
                mock_request.resource_type = "xhr"
                mock_request.headers = {}
                mock_response.request = mock_request
                
                await response_callback(mock_response)
        
        mock_input.type.side_effect = trigger_ajax

        # 6. Execute scraper in mocked Context
        with patch("app.scrapers.generic_scraper.async_playwright", return_value=mock_p_ctx):
            dealers = await scraper.extract_dealers()

        # 7. Assertions
        self.assertGreater(len(dealers), 0)
        self.assertEqual(dealers[0]["dealer_name"], "Noida Bosch Outlet")
        self.assertEqual(dealers[0]["city"], "Noida")
        self.assertEqual(dealers[0]["pincode"], "201301")

        # Verify diagnostics report logs
        self.assertEqual(scraper.search_diagnostics["search_field_detected"], "input[type='search']")
        self.assertIn("Noida", scraper.search_diagnostics["keywords_entered"])
        self.assertIn("Bosch Service Center, Noida", scraper.search_diagnostics["suggestions_detected"])
        self.assertIn("Bosch Service Center, Noida", scraper.search_diagnostics["suggestions_selected"])

if __name__ == "__main__":
    unittest.main()
