import sys
import unittest
from unittest.mock import patch, MagicMock
from uuid import uuid4
from fastapi.testclient import TestClient

# Add current path to sys.path to find main and app
sys.path.insert(0, ".")

from main import app
from app.schemas.brand_schema import generate_slug

class TestBrandAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.sample_id = "7ca647b0-81f1-4b1d-85fa-7f411cd73d8a"
        self.sample_brand = {
            "id": self.sample_id,
            "name": "Sony Electronics",
            "slug": "sony-electronics",
            "official_website": "https://www.sony.co.in",
            "dealer_locator_url": "https://www.sony.co.in/dealerlocator",
            "industry": "Electronics",
            "category": "Consumer Electronics",
            "logo_url": "https://example.com/logo.png",
            "notes": "Premium electronics brand",
            "scraper_type": "STATIC_HTML",
            "scrape_frequency": 7,
            "scraper_enabled": True,
            "active": True,
            "last_scraped": None,
            "created_at": "2026-07-03T20:00:00Z",
            "updated_at": "2026-07-03T20:00:00Z"
        }

    def test_health_check(self):
        """Verify GET /health healthcheck endpoint"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    @patch("app.repositories.brand_repository.BrandRepository.get_all")
    def test_get_brands(self, mock_get_all):
        """Verify GET /api/v1/brands returns standard success format"""
        mock_get_all.return_value = [self.sample_brand]
        response = self.client.get("/api/v1/brands")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Brands retrieved successfully")
        self.assertEqual(len(data["data"]), 1)
        self.assertEqual(data["data"][0]["name"], "Sony Electronics")

    @patch("app.repositories.brand_repository.BrandRepository.get_by_id")
    def test_get_brand_by_id_success(self, mock_get_by_id):
        """Verify GET /api/v1/brands/{id} for existing brand"""
        mock_get_by_id.return_value = self.sample_brand
        response = self.client.get(f"/api/v1/brands/{self.sample_id}")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["id"], self.sample_id)

    @patch("app.repositories.brand_repository.BrandRepository.get_by_id")
    def test_get_brand_by_id_not_found(self, mock_get_by_id):
        """Verify GET /api/v1/brands/{id} returns 404 and standard failure format if not found"""
        mock_get_by_id.return_value = None
        random_id = str(uuid4())
        response = self.client.get(f"/api/v1/brands/{random_id}")
        self.assertEqual(response.status_code, 404)
        
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("not found", data["errors"][0])

    def test_get_brand_by_invalid_uuid(self):
        """Verify GET /api/v1/brands/{id} returns 422 standard validation error for invalid UUIDs"""
        response = self.client.get("/api/v1/brands/invalid-uuid-string")
        self.assertEqual(response.status_code, 422)
        
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("Request validation failed.", data["message"])
        self.assertTrue(len(data["errors"]) > 0)

    @patch("app.repositories.brand_repository.BrandRepository.create")
    @patch("app.repositories.brand_repository.BrandRepository.get_by_name")
    @patch("app.repositories.brand_repository.BrandRepository.get_by_dealer_locator_url")
    def test_create_brand_success(self, mock_url, mock_name, mock_create):
        """Verify POST /api/v1/brands creates brand with valid payload and auto-generated slug"""
        mock_name.return_value = None
        mock_url.return_value = None
        mock_create.return_value = self.sample_brand

        payload = {
            "name": "Sony Electronics",
            "official_website": "https://www.sony.co.in",
            "dealer_locator_url": "https://www.sony.co.in/dealerlocator",
            "industry": "Electronics",
            "category": "Consumer Electronics"
        }
        response = self.client.post("/api/v1/brands", json=payload)
        self.assertEqual(response.status_code, 201)
        
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["slug"], "sony-electronics")

    @patch("app.repositories.brand_repository.BrandRepository.get_by_name")
    def test_create_brand_duplicate_name(self, mock_name):
        """Verify duplicate brand name registration fails with 400"""
        mock_name.return_value = self.sample_brand
        
        payload = {
            "name": "Sony Electronics",
            "official_website": "https://www.sony.co.in",
            "dealer_locator_url": "https://www.sony.co.in/dealerlocator",
            "industry": "Electronics",
            "category": "Consumer Electronics"
        }
        response = self.client.post("/api/v1/brands", json=payload)
        self.assertEqual(response.status_code, 400)
        
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("already registered", data["errors"][0])

    @patch("app.repositories.brand_repository.BrandRepository.get_by_name")
    @patch("app.repositories.brand_repository.BrandRepository.get_by_dealer_locator_url")
    def test_create_brand_duplicate_dealer_url(self, mock_url, mock_name):
        """Verify duplicate dealer locator URL registration fails with 400"""
        mock_name.return_value = None
        mock_url.return_value = self.sample_brand
        
        payload = {
            "name": "Sony India",
            "official_website": "https://www.sony.co.in",
            "dealer_locator_url": "https://www.sony.co.in/dealerlocator",
            "industry": "Electronics",
            "category": "Consumer Electronics"
        }
        response = self.client.post("/api/v1/brands", json=payload)
        self.assertEqual(response.status_code, 400)
        
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("already in use", data["errors"][0])

    def test_create_brand_invalid_official_url(self):
        """Verify invalid URL formats for official website are caught by validation (422)"""
        payload = {
            "name": "Invalid URL Brand",
            "official_website": "not-a-valid-url",
            "dealer_locator_url": "https://www.google.com",
            "industry": "Electronics",
            "category": "Consumer Electronics"
        }
        response = self.client.post("/api/v1/brands", json=payload)
        self.assertEqual(response.status_code, 422)
        
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("valid absolute HTTP or HTTPS URL", data["errors"][0])

    def test_create_brand_invalid_dealer_url(self):
        """Verify invalid URL formats for dealer locator are caught by validation (422)"""
        payload = {
            "name": "Invalid URL Brand",
            "official_website": "https://www.google.com",
            "dealer_locator_url": "ftp://not-supported",
            "industry": "Electronics",
            "category": "Consumer Electronics"
        }
        response = self.client.post("/api/v1/brands", json=payload)
        self.assertEqual(response.status_code, 422)
        
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("valid absolute HTTP or HTTPS URL", data["errors"][0])

    def test_create_brand_empty_name(self):
        """Verify empty brand name triggers 422 error"""
        payload = {
            "name": "",
            "official_website": "https://www.google.com",
            "dealer_locator_url": "https://www.google.com",
            "industry": "Electronics",
            "category": "Consumer Electronics"
        }
        response = self.client.post("/api/v1/brands", json=payload)
        self.assertEqual(response.status_code, 422)
        
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("at least 1", data["errors"][0].lower())

    def test_create_brand_missing_category(self):
        """Verify missing category field triggers validation error (422)"""
        payload = {
            "name": "Missing Cat Brand",
            "official_website": "https://www.google.com",
            "dealer_locator_url": "https://www.google.com",
            "industry": "Electronics"
        }
        response = self.client.post("/api/v1/brands", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_create_brand_missing_industry(self):
        """Verify missing industry field triggers validation error (422)"""
        payload = {
            "name": "Missing Ind Brand",
            "official_website": "https://www.google.com",
            "dealer_locator_url": "https://www.google.com",
            "category": "Consumer Electronics"
        }
        response = self.client.post("/api/v1/brands", json=payload)
        self.assertEqual(response.status_code, 422)

    @patch("app.repositories.brand_repository.BrandRepository.update")
    @patch("app.repositories.brand_repository.BrandRepository.get_by_id")
    def test_update_brand_success(self, mock_get_by_id, mock_update):
        """Verify PUT /api/v1/brands/{id} edits brand details successfully"""
        mock_get_by_id.return_value = self.sample_brand
        updated = self.sample_brand.copy()
        updated["notes"] = "Updated notes"
        mock_update.return_value = updated

        payload = {"notes": "Updated notes"}
        response = self.client.put(f"/api/v1/brands/{self.sample_id}", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["notes"], "Updated notes")

    @patch("app.repositories.brand_repository.BrandRepository.delete")
    @patch("app.repositories.brand_repository.BrandRepository.get_by_id")
    def test_delete_brand_success(self, mock_get_by_id, mock_delete):
        """Verify DELETE /api/v1/brands/{id} deletes brand successfully"""
        mock_get_by_id.return_value = self.sample_brand
        mock_delete.return_value = True

        response = self.client.delete(f"/api/v1/brands/{self.sample_id}")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Brand deleted successfully")

if __name__ == "__main__":
    unittest.main()
