import os
import traceback
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DiagnosticReporter:
    """
    Manages screenshot timelines, HTML snapshots, error captures,
    and writes out Failure_Report.md diagnostics reports on scrape failures.
    """

    @staticmethod
    def save_html_snapshot(html_content: str, filename: str) -> None:
        """Saves current DOM content to specified file in debug directory."""
        try:
            os.makedirs("debug", exist_ok=True)
            file_path = os.path.join("debug", filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"[Diagnostics] Saved HTML snapshot to: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save HTML snapshot: {e}")

    @staticmethod
    async def take_timeline_screenshot(page, step_name: str) -> None:
        """Captures a screenshot at specific steps in the interaction timeline."""
        try:
            os.makedirs("debug", exist_ok=True)
            # Map step_name to chronologically indexed filenames
            timeline = {
                "loaded": "01_loaded.png",
                "cookie": "02_cookie.png",
                "search": "03_search.png",
                "dropdown": "04_dropdown.png",
                "results": "05_results.png",
                "failure": "06_failure.png"
            }
            filename = timeline.get(step_name, f"timeline_{step_name}.png")
            file_path = os.path.join("debug", filename)
            await page.screenshot(path=file_path)
            logger.info(f"[Diagnostics] Captured screenshot step '{step_name}': {file_path}")
        except Exception as e:
            logger.error(f"Failed to capture timeline screenshot for '{step_name}': {e}")

    @staticmethod
    def write_failure_report(
        browser_used: str,
        strategy_chosen: str,
        ajax_calls: List[str],
        dealer_apis: List[str],
        dealers_parsed: int,
        reason_stopped: str,
        recovery_attempts: List[str],
        suggested_action: str
    ) -> None:
        """Generates Failure_Report.md documenting the diagnostic session."""
        try:
            os.makedirs("debug", exist_ok=True)
            report_path = "debug/Failure_Report.md"
            
            ajax_block = "\n".join([f"- {url}" for url in ajax_calls[:15]])
            if len(ajax_calls) > 15:
                ajax_block += f"\n- ... and {len(ajax_calls) - 15} more"
                
            dealer_block = "\n".join([f"- {url}" for url in dealer_apis]) if dealer_apis else "None"
            recovery_block = "\n".join([f"- {attempt}" for attempt in recovery_attempts]) if recovery_attempts else "None"
            
            report = f"""# Scraper Execution Failure Diagnostic Report

## 1. Executive Summary
- **Primary Reason Stopped**: {reason_stopped}
- **Suggested Next Action**: {suggested_action}

## 2. Scraping Environment & Strategy
- **Browser Engine Used**: {browser_used}
- **Target Strategy Attempted**: {strategy_chosen}
- **Dealers Extracted**: {dealers_parsed}

## 3. Network Discovery Telemetry
### Discovered Dealer APIs
{dealer_block}

### All AJAX Requests Fired
{ajax_block}

## 4. Recovery & Diagnostic Timeline
### Recovery Attempts Made
{recovery_block}

---
*Report generated automatically by Autonomous Scraper Diagnostics System.*
"""
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)
            logger.info(f"[Diagnostics] Generated failure report: {report_path}")
        except Exception as e:
            logger.error(f"Failed to write failure report: {e}")
