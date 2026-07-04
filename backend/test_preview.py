import pytest
import uuid
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.scraping_service import ScrapingService
from app.schemas.scrape_schema import PreviewResponse

@pytest.mark.anyio
async def test_preview_scrape_missing_validation_keys():
    """
    Verifies that preview_scrape processes raw records missing
    validation_status, validation_errors, and returns a normalized PreviewResponse.
    """
    brand_id = uuid.uuid4()
    
    # 1. Mock BrandRepository
    mock_brand_repo = MagicMock()
    mock_brand_repo.get_by_id.return_value = {
        "id": str(brand_id),
        "name": "Mock Auto Brand",
        "dealer_locator_url": "https://example.com/dealers"
    }
    
    # 2. Mock Scraper config
    mock_config_repo = MagicMock()
    mock_config_repo.get_by_brand_id.return_value = {}

    # 3. Mock Scraper instance
    mock_scraper = MagicMock()
    # Mock records returning raw attributes WITHOUT validation_status or validation_errors
    mock_scraper.preview = AsyncMock(return_value=[
        {
            "name": "Tata Motors Mumbai",
            "address": "456 Express Way, Mumbai",
            # missing city, state, pincode, phone, email, lat, lng, validation_status, validation_errors
        }
    ])
    mock_scraper.logs = ["Initialized test", "Scraped Tata Motors"]

    # Patch modules and repositories
    with patch("app.services.scraping_service.BrandRepository", return_value=mock_brand_repo), \
         patch("app.services.scraping_service.ScraperConfigRepository", return_value=mock_config_repo), \
         patch("app.services.scraping_service.ScraperFactory.get_scraper", return_value=mock_scraper):
         
        service = ScrapingService()
        result = await service.preview_scrape(brand_id)
        
        # Verify schema mapping and defaults
        assert isinstance(result, PreviewResponse)
        assert result.total_extracted == 1
        assert len(result.preview_records) == 1
        
        dealer = result.preview_records[0]
        # Check standard fields normalized from raw "name" key
        assert dealer.name == "Tata Motors Mumbai"
        assert dealer.address == "456 Express Way, Mumbai"
        
        # Check validation defaults populated automatically
        assert dealer.validation_status == "INVALID"  # Invalid because PIN code and required fields are missing
        assert len(dealer.validation_errors) > 0
        assert any("PIN code" in err for err in dealer.validation_errors)
