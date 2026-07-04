import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import json
import uuid
import os
import shutil
from app.scrapers.generic_scraper import GenericScraper
from app.scrapers.blocking_detector import BlockingDetector
from app.scrapers.browser_manager import BrowserManager
from app.scrapers.network_recorder import NetworkRecorder
from app.scrapers.diagnostic_reporter import DiagnosticReporter

class TestUniversalDiagnostics(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Create temporary folders for test telemetry
        os.makedirs("debug", exist_ok=True)

    def tearDown(self):
        # Clean up generated test artifacts
        if os.path.exists("debug"):
            shutil.rmtree("debug", ignore_errors=True)

    def test_cloudflare_detection(self):
        """Verify BlockingDetector flags Cloudflare checks on title/DOM indicators."""
        html = "<html><body><div id='cf-browser-verification'>Just a moment...</div></body></html>"
        title = "Attention Required! | Cloudflare"
        
        self.assertEqual(BlockingDetector.detect_cloudflare(html, title), "Cloudflare detected")
        self.assertEqual(BlockingDetector.detect_cloudflare("Normal site page", "Sample Title"), None)

    def test_captcha_detection(self):
        """Verify BlockingDetector flags reCAPTCHA, hCaptcha, or Turnstile injections."""
        html_grecaptcha = "<html><body><div class='g-recaptcha'></div></body></html>"
        html_turnstile = "<html><body><script src='https://challenges.cloudflare.com/turnstile/v0/api.js'></script></body></html>"
        
        self.assertEqual(BlockingDetector.detect_captcha(html_grecaptcha), "Captcha detected")
        self.assertEqual(BlockingDetector.detect_captcha(html_turnstile), "Captcha detected")
        self.assertEqual(BlockingDetector.detect_captcha("<html>Normal Page</html>"), None)

    async def test_browser_retry_fallback(self):
        """Verify BrowserManager tries Chromium, then Firefox, then WebKit before raising error."""
        mock_p = MagicMock()
        mock_p.chromium.launch = AsyncMock(side_effect=RuntimeError("Chrome down"))
        mock_p.firefox.launch = AsyncMock(side_effect=RuntimeError("Firefox down"))
        mock_p.webkit.launch = AsyncMock(return_value="WebKitInstance")
        
        browser, engine = await BrowserManager.launch_with_fallback(mock_p, headless=True)
        self.assertEqual(browser, "WebKitInstance")
        self.assertEqual(engine, "webkit")
        self.assertEqual(mock_p.chromium.launch.call_count, 1)
        self.assertEqual(mock_p.firefox.launch.call_count, 1)

    async def test_network_recorder_and_json_saves(self):
        """Verify NetworkRecorder sniffs endpoints, detects signatures, and logs JSON payloads."""
        recorder = NetworkRecorder("TestBrand")
        
        mock_request = MagicMock()
        mock_request.method = "GET"
        mock_request.resource_type = "xhr"
        
        mock_resp = AsyncMock()
        mock_resp.url = "https://example.com/api/v1/store/locator?city=Noida"
        mock_resp.status = 200
        mock_resp.headers = {"content-type": "application/json"}
        mock_resp.text = AsyncMock(return_value='{"stores": [{"name": "Store Noida"}]}')
        mock_resp.request = mock_request
        
        await recorder.record_response(mock_resp)
        
        # Verify classification and saving
        self.assertEqual(len(recorder.recorded_requests), 1)
        self.assertTrue(recorder.recorded_requests[0]["is_dealer_related"])
        self.assertIn("https://example.com/api/v1/store/locator?city=Noida", recorder.get_dealer_endpoints())
        
        # Verify JSON file written to debug/json_response_1.json
        self.assertTrue(os.path.exists("debug/json_response_1.json"))
        with open("debug/json_response_1.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data["body"]["stores"][0]["name"], "Store Noida")

    def test_diagnostic_report_and_snapshots(self):
        """Verify DiagnosticReporter saves DOM content and failure reports correctly."""
        DiagnosticReporter.save_html_snapshot("<html>Test DOM</html>", "test_snap.html")
        self.assertTrue(os.path.exists("debug/test_snap.html"))
        
        DiagnosticReporter.write_failure_report(
            browser_used="firefox",
            strategy_chosen="API",
            ajax_calls=["https://ajax.com"],
            dealer_apis=["https://api.com"],
            dealers_parsed=0,
            reason_stopped="Captcha detected",
            recovery_attempts=["Firefox Booted"],
            suggested_action="Try Rotate Cookies"
        )
        
        self.assertTrue(os.path.exists("debug/Failure_Report.md"))
        with open("debug/Failure_Report.md", "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Captcha detected", content)
            self.assertIn("Browser Engine Used**: firefox", content)

    async def test_scraper_cloudflare_exception_propagation(self):
        """Verify GenericScraper does not swallow blocking exceptions and writes failure package."""
        brand_id = uuid.uuid4()
        scraper = GenericScraper(
            brand_id=brand_id,
            brand_name="Test Sleepwell",
            locator_url="https://example.com/sleepwell",
            config={}
        )
        
        # Mock Playwright execution to throw Exception simulating Cloudflare page load
        mock_page = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html><title>Attention Required! | Cloudflare</title></html>")
        mock_page.title = AsyncMock(return_value="Attention Required! | Cloudflare")
        mock_page.screenshot = AsyncMock()
        mock_page.goto = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        
        mock_p_ctx = MagicMock()
        mock_p_ctx.__aenter__ = AsyncMock(return_value=mock_p_ctx)
        mock_p_ctx.__aexit__ = AsyncMock(return_value=None)
        mock_p_ctx.chromium.launch = AsyncMock(return_value=mock_browser)
        
        with patch("app.scrapers.generic_scraper.async_playwright", return_value=mock_p_ctx):
            with self.assertRaises(RuntimeError) as context:
                await scraper.extract_dealers()
                
            self.assertIn("Cloudflare detected", str(context.exception))
            self.assertTrue(os.path.exists("debug/Failure_Report.md"))
            self.assertTrue(os.path.exists("debug/sleepwell_failure.html"))

if __name__ == "__main__":
    unittest.main()
