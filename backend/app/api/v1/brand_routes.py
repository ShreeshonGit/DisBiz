from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from app.schemas.brand_schema import BrandCreate, BrandUpdate, StandardResponse
from app.services.brand_service import BrandService, BrandAlreadyExistsError, BrandNotFoundError

router = APIRouter(prefix="/brands", tags=["Brands"])
brand_service = BrandService()

@router.get("", response_model=StandardResponse)
async def get_brands() -> StandardResponse:
    """
    Get all brands.
    Returns standard response containing list of brand records.
    """
    brands = brand_service.get_all_brands()
    return StandardResponse(
        success=True,
        message="Brands retrieved successfully",
        data=brands
    )

@router.get("/{id}", response_model=StandardResponse)
async def get_brand(id: UUID) -> StandardResponse:
    """
    Get a single brand by its unique UUID.
    """
    try:
        brand = brand_service.get_brand_by_id(id)
        return StandardResponse(
            success=True,
            message="Brand retrieved successfully",
            data=brand
        )
    except BrandNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_440_NOT_FOUND if False else status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(brand_in: BrandCreate) -> StandardResponse:
    """
    Create a new brand entry.
    Slug is automatically generated. Validates name and url uniqueness.
    """
    try:
        new_brand = brand_service.create_brand(brand_in)
        return StandardResponse(
            success=True,
            message="Brand created successfully",
            data=new_brand
        )
    except BrandAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{id}", response_model=StandardResponse)
async def update_brand(id: UUID, brand_in: BrandUpdate) -> StandardResponse:
    """
    Update an existing brand by its UUID.
    Can modify partial fields. Performs validation checks on modifications.
    """
    try:
        updated_brand = brand_service.update_brand(id, brand_in)
        return StandardResponse(
            success=True,
            message="Brand updated successfully",
            data=updated_brand
        )
    except BrandNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except BrandAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{id}", response_model=StandardResponse)
async def delete_brand(id: UUID) -> StandardResponse:
    """
    Delete a brand record by its UUID.
    """
    try:
        brand_service.delete_brand(id)
        return StandardResponse(
            success=True,
            message="Brand deleted successfully"
        )
    except BrandNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
