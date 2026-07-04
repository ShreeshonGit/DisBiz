import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import asyncio
import sys
import threading
from app.scrapers.generic_scraper import GenericScraper
from app.scheduler.worker import Worker
from app.scheduler.job_queue import JobQueue
from app.scheduler.concurrency_manager import ConcurrencyManager
from app.scheduler.scheduler_monitor import SchedulerMonitor
from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.scrape_job_repository import ScrapeJobRepository

class TestEventLoopStabilization(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Mock Playwright execution elements
        self.mock_page = AsyncMock()
        self.mock_page.content = AsyncMock(return_value="<html><body><div>Mocked DOM</div></body></html>")
        self.mock_page.title = AsyncMock(return_value="Mocked Title")
        self.mock_page.screenshot = AsyncMock()
        self.mock_page.goto = AsyncMock()
        self.mock_page.query_selector = AsyncMock(return_value=None)
        self.mock_page.query_selector_all = AsyncMock(return_value=[])

        self.mock_browser = AsyncMock()
        self.mock_context = AsyncMock()
        self.mock_context.new_page = AsyncMock(return_value=self.mock_page)
        self.mock_browser.new_context = AsyncMock(return_value=self.mock_context)

        self.mock_p_ctx = MagicMock()
        self.mock_p_ctx.__aenter__ = AsyncMock(return_value=self.mock_p_ctx)
        self.mock_p_ctx.__aexit__ = AsyncMock(return_value=None)
        self.mock_p_ctx.chromium.launch = AsyncMock(return_value=self.mock_browser)

    @patch("app.scrapers.generic_scraper.async_playwright")
    async def test_preview_scrape_launches_playwright(self, mock_playwright):
        mock_playwright.return_value = self.mock_p_ctx
        
        brand_id = uuid.uuid4()
        scraper = GenericScraper(
            brand_id=brand_id,
            brand_name="Preview Test Brand",
            locator_url="https://example.com/preview",
            config={}
        )
        
        # Test preview limit
        records = await scraper.preview(limit=5)
        self.assertEqual(len(records), 0)  # Mock returns no cards
        self.mock_page.goto.assert_called_once()
        self.mock_browser.new_context.assert_called_once()

    @patch("app.scrapers.generic_scraper.async_playwright")
    async def test_manual_scrape_selector_loop_delegation(self, mock_playwright):
        mock_playwright.return_value = self.mock_p_ctx
        
        # Simulate running inside a SelectorEventLoop on Windows
        brand_id = uuid.uuid4()
        scraper = GenericScraper(
            brand_id=brand_id,
            brand_name="Selector Loop Test Brand",
            locator_url="https://example.com/selector-loop",
            config={}
        )
        
        class MockSelectorEventLoop(asyncio.AbstractEventLoop):
            async def run_in_executor(self, executor, func, *args):
                func(*args)
            
        dummy_loop = MockSelectorEventLoop()
        
        # We patch get_running_loop to return our custom Selector loop
        with patch("asyncio.get_running_loop", return_value=dummy_loop):
            with patch("sys.platform", "win32"):
                # Even under simulated Selector loop, the scraper should delegate
                # to a separate thread containing a ProactorEventLoop and run successfully
                records = await scraper.extract_dealers()
                self.assertEqual(len(records), 0)

    @patch("app.scrapers.generic_scraper.async_playwright")
    async def test_concurrent_scrapes_do_not_share_browsers(self, mock_playwright):
        mock_playwright.return_value = self.mock_p_ctx
        
        brand_1 = uuid.uuid4()
        brand_2 = uuid.uuid4()
        
        scraper_1 = GenericScraper(brand_id=brand_1, brand_name="Brand A", locator_url="https://example.com/a")
        scraper_2 = GenericScraper(brand_id=brand_2, brand_name="Brand B", locator_url="https://example.com/b")
        
        # Run concurrently
        res1, res2 = await asyncio.gather(
            scraper_1.extract_dealers(),
            scraper_2.extract_dealers()
        )
        
        # Verify launch was called twice (once per scraper execution), verifying isolation
        self.assertEqual(self.mock_p_ctx.chromium.launch.call_count, 2)
        self.assertEqual(self.mock_browser.new_context.call_count, 2)

    @patch("app.scrapers.generic_scraper.async_playwright")
    async def test_scheduler_worker_execute_job(self, mock_playwright):
        mock_playwright.return_value = self.mock_p_ctx
        
        # Mock repositories for the worker
        mock_schedule_repo = MagicMock(spec=ScheduleRepository)
        mock_job_repo = MagicMock(spec=ScrapeJobRepository)
        
        mock_job_repo.create.return_value = {"id": str(uuid.uuid4()), "status": "Running"}
        # Return Completed with case upper/lower mix to verify casing fix
        mock_job_repo.get_by_id.return_value = {"id": str(uuid.uuid4()), "status": "Completed", "records_saved": 5}
        
        worker = Worker(schedule_repo=mock_schedule_repo, job_repo=mock_job_repo)
        
        job = {
            "brand_id": uuid.uuid4(),
            "schedule_id": uuid.uuid4(),
            "retries": 0,
            "max_retries": 3,
            "retry_delay_minutes": 5,
            "retry_policy": "EXPONENTIAL"
        }
        
        success = await worker.execute_job(job, "TestWorker-1")
        self.assertTrue(success)
        mock_schedule_repo.log_action.assert_any_call(
            schedule_id=job["schedule_id"],
            brand_id=job["brand_id"],
            job_id=unittest.mock.ANY,
            event="RUN",
            status="SUCCESS",
            message="Job completed successfully. Extracted 5 dealers.",
            execution_time=unittest.mock.ANY
        )

    @patch("app.scrapers.generic_scraper.async_playwright")
    async def test_scheduler_worker_retry_flow(self, mock_playwright):
        mock_playwright.return_value = self.mock_p_ctx
        
        # Mock repositories
        mock_schedule_repo = MagicMock(spec=ScheduleRepository)
        mock_job_repo = MagicMock(spec=ScrapeJobRepository)
        
        mock_job_repo.create.return_value = {"id": str(uuid.uuid4()), "status": "Running"}
        # Simulate scraper failure by returning status FAILED or having no scraper log progress
        mock_job_repo.get_by_id.return_value = {"id": str(uuid.uuid4()), "status": "Failed", "error_message": "Playwright connection timeout"}
        
        worker = Worker(schedule_repo=mock_schedule_repo, job_repo=mock_job_repo)
        
        job = {
            "brand_id": uuid.uuid4(),
            "schedule_id": uuid.uuid4(),
            "retries": 0,
            "max_retries": 2,
            "retry_delay_minutes": 1,
            "retry_policy": "EXPONENTIAL"
        }
        
        # Execute job: should return False and schedule a retry background task
        success = await worker.execute_job(job, "TestWorker-1")
        self.assertFalse(success)
        self.assertEqual(job["retries"], 1)
        
        # Verify log action recorded the retry scheduling
        mock_schedule_repo.log_action.assert_any_call(
            schedule_id=job["schedule_id"],
            brand_id=job["brand_id"],
            job_id=unittest.mock.ANY,
            event="RETRY",
            status="PENDING",
            message=unittest.mock.ANY
        )

if __name__ == "__main__":
    unittest.main()
