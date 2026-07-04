import logging
from typing import Tuple, Any
from playwright.async_api import Playwright, Browser

logger = logging.getLogger(__name__)

class BrowserManager:
    """
    Coordinates browser engine selection and handles failover retries.
    Order: Chromium -> Firefox -> WebKit.
    """

    @staticmethod
    async def launch_with_fallback(
        p: Playwright,
        headless: bool = True
    ) -> Tuple[Browser, str]:
        """
        Attempts to launch Chromium, falling back to Firefox or WebKit on failure.
        Returns a tuple of (BrowserInstance, BrowserNameString).
        """
        engines = [
            ("chromium", p.chromium),
            ("firefox", p.firefox),
            ("webkit", p.webkit)
        ]
        
        last_error = None
        for name, launcher in engines:
            try:
                logger.info(f"[BrowserManager] Attempting to launch browser: {name}")
                browser = await launcher.launch(headless=headless)
                logger.info(f"[BrowserManager] Successfully booted browser: {name}")
                return browser, name
            except Exception as e:
                logger.warning(f"[BrowserManager] Failed to launch {name}: {e}")
                last_error = e
                
        # If all fail, raise the last exception
        raise RuntimeError(f"All browser engines (Chromium, Firefox, WebKit) failed to launch. Last error: {last_error}")
