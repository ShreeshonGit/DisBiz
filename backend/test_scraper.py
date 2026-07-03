import sys
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient

sys.path.insert(0, ".")

from main import app

class TestScraperAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.brand_id = "7ca647b0-81f1-4b1d-85fa-7f411cd73d8a"
        self.job_id = "550e8400-e29b-41d4-a716-446655440000"

    @patch("app.services.scraping_service.ScrapingService.auto_detect_brand")
    def test_detect_endpoint(self, mock_detect):
        """Verify POST /api/v1/scraper/detect"""
        mock_detect.return_value = {
            "brand_id": self.brand_id,
            "locator_url": "https://example.com/locator",
            "detected_locator_type": "STATIC_HTML",
            "suggested_scraper_type": "STATIC_HTML",
            "status_code": 200,
            "content_length": 1234
        }
        
        response = self.client.post("/api/v1/scraper/detect", json={"brand_id": self.brand_id})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["detected_locator_type"], "STATIC_HTML")

    @patch("app.services.scraping_service.ScrapingService.preview_scrape")
    def test_preview_endpoint(self, mock_preview):
        """Verify POST /api/v1/scraper/preview"""
        mock_preview.return_value = {
            "brand_id": self.brand_id,
            "brand_name": "Test Brand",
            "locator_url": "https://example.com/locator",
            "total_extracted": 1,
            "preview_records": [
                {
                    "name": "Dealer 1",
                    "address": "123 Street Road, Mumbai 400001",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "pincode": "400001",
                    "phone": "+919876543210",
                    "email": "dealer1@test.com",
                    "latitude": 18.97,
                    "longitude": 72.82,
                    "validation_status": "VALID",
                    "validation_errors": []
                }
            ],
            "logs": ["Job started", "Fetched page", "Preview completed"]
        }
        
        response = self.client.post("/api/v1/scraper/preview", json={"brand_id": self.brand_id})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["total_extracted"], 1)
        self.assertEqual(len(data["data"]["preview_records"]), 1)
        self.assertEqual(data["data"]["preview_records"][0]["name"], "Dealer 1")

    @patch("app.services.scraping_service.ScrapingService.start_scrape_job")
    def test_start_endpoint(self, mock_start):
        """Verify POST /api/v1/scraper/start/{brand_id}"""
        mock_start.return_value = {
            "id": self.job_id,
            "brand_id": self.brand_id,
            "status": "Queued",
            "started_at": "2026-07-03T20:00:00Z",
            "records_found": 0,
            "records_saved": 0
        }
        
        response = self.client.post(f"/api/v1/scraper/start/{self.brand_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["status"], "Queued")

    @patch("app.services.scraping_service.ScrapingService.get_jobs")
    def test_get_jobs_endpoint(self, mock_get_jobs):
        """Verify GET /api/v1/scraper/jobs"""
        mock_get_jobs.return_value = [
            {
                "id": self.job_id,
                "brand_id": self.brand_id,
                "brand_name": "Test Brand",
                "status": "Completed",
                "started_at": "2026-07-03T20:00:00Z",
                "completed_at": "2026-07-03T20:01:15Z",
                "duration_seconds": 75,
                "records_found": 15,
                "records_saved": 0,
                "error_message": None
            }
        ]
        
        response = self.client.get("/api/v1/scraper/jobs")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["data"]), 1)
        self.assertEqual(data["data"][0]["status"], "Completed")

    @patch("app.services.scraping_service.ScrapingService.get_job_by_id")
    def test_get_job_by_id_endpoint(self, mock_get_job):
        """Verify GET /api/v1/scraper/jobs/{id}"""
        mock_get_job.return_value = {
            "id": self.job_id,
            "brand_id": self.brand_id,
            "brand_name": "Test Brand",
            "status": "Completed",
            "started_at": "2026-07-03T20:00:00Z",
            "completed_at": "2026-07-03T20:01:15Z",
            "duration_seconds": 75,
            "records_found": 15,
            "records_saved": 0,
            "error_message": None
        }
        
        response = self.client.get(f"/api/v1/scraper/jobs/{self.job_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["id"], self.job_id)

    @patch("app.services.scraping_service.ScrapingService.cancel_job")
    def test_cancel_job_endpoint(self, mock_cancel):
        """Verify POST /api/v1/scraper/cancel/{id}"""
        mock_cancel.return_value = {
            "id": self.job_id,
            "brand_id": self.brand_id,
            "status": "Cancelled",
            "started_at": "2026-07-03T20:00:00Z",
            "completed_at": "2026-07-03T20:02:10Z",
            "duration_seconds": 130,
            "records_found": 0,
            "records_saved": 0,
            "error_message": None
        }
        
        response = self.client.post(f"/api/v1/scraper/cancel/{self.job_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["status"], "Cancelled")

if __name__ == "__main__":
    unittest.main()
