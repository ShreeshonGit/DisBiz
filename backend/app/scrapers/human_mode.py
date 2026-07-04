import random
import asyncio
from typing import Dict, Any
from playwright.async_api import Page, BrowserContext

class HumanMode:
    """
    Implements anti-bot evasion techniques including mouse movements,
    randomized scroll intervals, spoofed user-agent/languages, and variable typing speeds.
    """

    @staticmethod
    def get_random_viewport() -> Dict[str, int]:
        """Returns a randomized desktop viewport dimension."""
        width = random.choice([1280, 1366, 1440, 1536, 1600, 1920])
        height = random.choice([720, 768, 900, 1024, 1080])
        return {"width": width, "height": height}

    @staticmethod
    def get_spoofed_headers(user_agent: str) -> Dict[str, str]:
        """Returns a dict of spoofed headers matching browser type."""
        return {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        }

    @staticmethod
    async def configure_context(context: BrowserContext, user_agent: str) -> None:
        """Applies spoofed languages, timezones, and permissions to context."""
        try:
            # Spoof languages and timezone
            await context.set_extra_http_headers({
                "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
            })
            # Overwrite navigator properties via initialization script
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en', 'hi'] });
            """)
        except Exception:
            pass

    @staticmethod
    async def move_mouse_randomly(page: Page) -> None:
        """Simulates realistic, curved mouse movements across the screen."""
        try:
            viewport = page.viewport_size
            if not viewport:
                viewport = {"width": 1280, "height": 800}
                
            steps = random.randint(5, 12)
            start_x = random.randint(100, 300)
            start_y = random.randint(100, 300)
            
            await page.mouse.move(start_x, start_y)
            
            for _ in range(steps):
                target_x = random.randint(10, viewport["width"] - 10)
                target_y = random.randint(10, viewport["height"] - 10)
                await page.mouse.move(target_x, target_y, steps=random.randint(3, 7))
                await asyncio.sleep(random.uniform(0.1, 0.3))
        except Exception:
            pass

    @staticmethod
    async def scroll_smoothly(page: Page, direction: str = "down", distance: int = 400) -> None:
        """Simulates smooth page scrolling to trigger lazy loading."""
        try:
            steps = random.randint(3, 6)
            step_distance = distance // steps
            sign = 1 if direction == "down" else -1
            
            for _ in range(steps):
                await page.evaluate(f"window.scrollBy(0, {sign * step_distance})")
                await asyncio.sleep(random.uniform(0.2, 0.5))
        except Exception:
            pass

    @staticmethod
    async def type_like_human(element: Any, text: str) -> None:
        """Types text inside the specified element with randomized speed intervals."""
        try:
            for char in text:
                await element.type(char)
                await asyncio.sleep(random.uniform(0.05, 0.18))
        except Exception:
            # Fallback to direct type if element structure differs
            try:
                await element.type(text, delay=random.randint(60, 130))
            except Exception:
                await element.fill(text)
