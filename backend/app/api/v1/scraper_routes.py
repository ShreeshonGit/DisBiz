from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from uuid import UUID
from app.schemas.scrape_schema import (
    AutoDetectRequest, 
    PreviewRequest
)
from app.schemas.brand_schema import StandardResponse
from app.services.scraping_service import ScrapingService

router = APIRouter(prefix="/scraper", tags=["Scraper"])
scraping_service = ScrapingService()

@router.post("/detect", response_model=StandardResponse)
async def auto_detect(req: AutoDetectRequest) -> StandardResponse:
    """
    Executes auto-detection on a brand's locator URL to identify the
    rendering type (Static, Javascript, or API) and updates configuration.
    """
    try:
        result = await scraping_service.auto_detect_brand(req.brand_id)
        return StandardResponse(
            success=True,
            message="Auto-detection completed and configuration updated.",
            data=result
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Auto-detection failed: {e}"
        )

@router.post("/preview", response_model=StandardResponse)
async def preview_scrape(req: PreviewRequest) -> StandardResponse:
    """
    Runs a mock extraction in memory (max 10 records), returning normalized
    and validated outputs along with diagnosis execution logs.
    Does not write records to the database.
    """
    try:
        result = await scraping_service.preview_scrape(req.brand_id, req.override_config)
        return StandardResponse(
            success=True,
            message="Preview scrape completed successfully.",
            data=result
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preview execution failed: {e}"
        )

@router.post("/start/{brand_id}", response_model=StandardResponse)
async def start_scrape(brand_id: UUID, background_tasks: BackgroundTasks) -> StandardResponse:
    """
    Triggers a live scraping execution run asynchronously in the background.
    Parses locator configuration parameters, filters valid rows, writes to database, and captures logs.
    """
    try:
        result = await scraping_service.start_scrape_job(brand_id, background_tasks)
        return StandardResponse(
            success=True,
            message="Scraping job queued successfully in background.",
            data=result
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scrape initiation failed: {e}"
        )

@router.get("/jobs", response_model=StandardResponse)
async def get_jobs() -> StandardResponse:
    """
    Retrieves the execution logs of all scraping runs.
    """
    try:
        jobs = scraping_service.get_jobs()
        return StandardResponse(
            success=True,
            message="Scrape jobs retrieved successfully.",
            data=jobs
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch jobs: {e}"
        )

@router.get("/jobs/{id}", response_model=StandardResponse)
async def get_job(id: UUID) -> StandardResponse:
    """
    Retrieves detailed execution details for a specific scrape job.
    """
    try:
        job = scraping_service.get_job_by_id(id)
        return StandardResponse(
            success=True,
            message="Scrape job details retrieved successfully.",
            data=job
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch job details: {e}"
        )

@router.post("/cancel/{id}", response_model=StandardResponse)
async def cancel_job(id: UUID) -> StandardResponse:
    """
    Cancels a running or queued scraping job by its ID.
    """
    try:
        result = scraping_service.cancel_job(id)
        return StandardResponse(
            success=True,
            message="Scrape job cancelled successfully.",
            data=result
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel job: {e}"
        )
