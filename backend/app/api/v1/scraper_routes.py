from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from uuid import UUID
from typing import Optional
import io
import csv
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

@router.get("/export/dealers")
async def export_dealers(brand_id: Optional[UUID] = None, format: str = "csv"):
    """
    Exports dealer data as CSV or JSON stream.
    """
    try:
        if brand_id:
            from app.repositories.dealer_repository import DealerRepository
            dealers = DealerRepository().get_by_brand_id(brand_id)
        else:
            from app.database.supabase import supabase
            if supabase is None:
                raise RuntimeError("Database connection not initialized.")
            res = supabase.table("dealers").select("*").execute()
            dealers = res.data or []

        if format == "json":
            return {"success": True, "data": dealers}

        output = io.StringIO()
        writer = csv.writer(output)
        
        headers = [
            "id", "brand_id", "dealer_name", "address", "city", "state", "pincode", 
            "latitude", "longitude", "phone", "email", "website", "formatted_address", 
            "country", "quality_score", "created_at"
        ]
        writer.writerow(headers)
        
        for d in dealers:
            writer.writerow([d.get(h) for h in headers])
            
        output.seek(0)
        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=dealers.csv"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export dealers: {e}"
        )

@router.get("/export/jobs")
async def export_jobs(format: str = "csv"):
    """
    Exports scrape jobs summary details.
    """
    try:
        jobs = scraping_service.get_jobs()
        if format == "json":
            return {"success": True, "data": jobs}
            
        output = io.StringIO()
        writer = csv.writer(output)
        
        headers = [
            "id", "brand_id", "brand_name", "status", "started_at", "completed_at", 
            "duration_seconds", "records_found", "records_scraped", "records_saved", 
            "retry_count", "failure_reason", "last_successful_page"
        ]
        writer.writerow(headers)
        
        for j in jobs:
            writer.writerow([j.get(h) for h in headers])
            
        output.seek(0)
        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=scrape_jobs.csv"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export jobs: {e}"
        )

@router.get("/dealers/search", response_model=StandardResponse)
async def search_dealers(
    query: Optional[str] = None,
    brand_id: Optional[UUID] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    pincode: Optional[str] = None,
    sort_by: str = "name",
    sort_order: str = "asc",
    page: int = 1,
    limit: int = 10
) -> StandardResponse:
    """
    Search and filter authorized dealers.
    """
    try:
        from app.repositories.dealer_repository import DealerRepository
        repo = DealerRepository()
        result = repo.search(
            query=query,
            brand_id=brand_id,
            city=city,
            state=state,
            pincode=pincode,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            limit=limit
        )
        return StandardResponse(
            success=True,
            message="Dealers retrieved successfully.",
            data=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search dealers: {e}"
        )
