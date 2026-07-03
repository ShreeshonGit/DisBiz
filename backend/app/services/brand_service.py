from typing import List, Optional
from uuid import UUID
from app.repositories.brand_repository import BrandRepository
from app.schemas.brand_schema import BrandCreate, BrandUpdate, generate_slug
import logging

logger = logging.getLogger(__name__)

class BrandAlreadyExistsError(ValueError):
    """Exception raised when a brand name or dealer locator url already exists."""
    pass

class BrandNotFoundError(ValueError):
    """Exception raised when a brand is not found."""
    pass

class BrandService:
    """
    Business logic layer for Brand management.
    Enforces uniqueness checks and generates slugs.
    """

    def __init__(self) -> None:
        self.repository = BrandRepository()

    def get_all_brands(self) -> List[dict]:
        """Retrieves all brands."""
        return self.repository.get_all()

    def get_brand_by_id(self, brand_id: UUID) -> dict:
        """
        Retrieves a brand by ID. Raises BrandNotFoundError if not found.
        """
        brand = self.repository.get_by_id(brand_id)
        if not brand:
            raise BrandNotFoundError(f"Brand with ID {brand_id} not found.")
        return brand

    def create_brand(self, brand_in: BrandCreate) -> dict:
        """
        Creates a new brand. Generates slug and verifies uniqueness constraints.
        """
        # Validate unique name
        existing_name = self.repository.get_by_name(brand_in.name)
        if existing_name:
            raise BrandAlreadyExistsError(f"Brand name '{brand_in.name}' is already registered.")

        # Validate unique dealer URL
        existing_url = self.repository.get_by_dealer_locator_url(brand_in.dealer_locator_url)
        if existing_url:
            raise BrandAlreadyExistsError(
                f"Dealer locator URL '{brand_in.dealer_locator_url}' is already in use by another brand."
            )

        # Generate slug and convert to repository dict
        data = brand_in.model_dump()
        data["slug"] = generate_slug(brand_in.name)

        return self.repository.create(data)

    def update_brand(self, brand_id: UUID, brand_in: BrandUpdate) -> dict:
        """
        Updates an existing brand. Validates modifications against uniqueness constraints.
        """
        # Fetch current record
        current_brand = self.repository.get_by_id(brand_id)
        if not current_brand:
            raise BrandNotFoundError(f"Brand with ID {brand_id} not found.")

        update_data = brand_in.model_dump(exclude_unset=True)

        # Validate unique name if name changes
        if "name" in update_data and update_data["name"] != current_brand["name"]:
            existing_name = self.repository.get_by_name(update_data["name"])
            if existing_name and str(existing_name["id"]) != str(brand_id):
                raise BrandAlreadyExistsError(f"Brand name '{update_data['name']}' is already registered.")
            update_data["slug"] = generate_slug(update_data["name"])

        # Validate unique locator URL if URL changes
        if "dealer_locator_url" in update_data and update_data["dealer_locator_url"] != current_brand["dealer_locator_url"]:
            existing_url = self.repository.get_by_dealer_locator_url(update_data["dealer_locator_url"])
            if existing_url and str(existing_url["id"]) != str(brand_id):
                raise BrandAlreadyExistsError(
                    f"Dealer locator URL '{update_data['dealer_locator_url']}' is already in use by another brand."
                )

        updated_brand = self.repository.update(brand_id, update_data)
        if not updated_brand:
            raise BrandNotFoundError(f"Failed to update brand. Brand with ID {brand_id} not found.")

        return updated_brand

    def delete_brand(self, brand_id: UUID) -> bool:
        """
        Deletes a brand. Raises BrandNotFoundError if the brand does not exist.
        """
        current_brand = self.repository.get_by_id(brand_id)
        if not current_brand:
            raise BrandNotFoundError(f"Brand with ID {brand_id} not found.")
        
        return self.repository.delete(brand_id)
