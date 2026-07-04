import re
from typing import Optional

class BlockingDetector:
    """
    Analyzes page content, headers, and DOM markup to discover and report
    bot blocking systems (such as Cloudflare or CAPTCHA challenges).
    """

    @staticmethod
    def detect_cloudflare(html_content: str, page_title: str) -> Optional[str]:
        """
        Scans DOM text and titles for Cloudflare verification patterns.
        Returns 'Cloudflare detected' if found, else None.
        """
        cloudflare_indicators = [
            "Checking your browser",
            "cf-browser-verification",
            "cf_clearance",
            "Attention Required",
            "Please turn on JavaScript and cookies",
            "security cloudflare",
            "cloudflare-challenge",
            "cf-cookie-error"
        ]
        
        # Check title
        title_lower = page_title.lower()
        if "attention required" in title_lower or "cloudflare" in title_lower:
            return "Cloudflare detected"
            
        # Check html body
        for indicator in cloudflare_indicators:
            if indicator.lower() in html_content.lower():
                return "Cloudflare detected"
                
        return None

    @staticmethod
    def detect_captcha(html_content: str) -> Optional[str]:
        """
        Scans page source code for popular CAPTCHA script inclusions.
        Returns 'Captcha detected' if found, else None.
        """
        captcha_patterns = [
            r"google\.com/recaptcha",
            r"recaptcha/api\.js",
            r"hcaptcha\.com/1/api\.js",
            r"hcaptcha-container",
            r"challenges\.cloudflare\.com/turnstile",
            r"cf-turnstile",
            r"g-recaptcha"
        ]
        
        for pattern in captcha_patterns:
            if re.search(pattern, html_content, re.IGNORECASE):
                return "Captcha detected"
                
        # Simple text checks
        text_indicators = ["recaptcha", "hcaptcha", "turnstile", "please verify you are a human"]
        html_lower = html_content.lower()
        for indicator in text_indicators:
            if indicator in html_lower:
                return "Captcha detected"
                
        return None
