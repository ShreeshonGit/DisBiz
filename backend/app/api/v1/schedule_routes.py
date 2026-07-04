from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from fastapi.encoders import jsonable_encoder
from uuid import UUID
from typing import Optional, List, Dict, Any
import json
import asyncio

from app.schemas.brand_schema import StandardResponse
from app.schemas.schedule_schema import (
    ScheduleCreate, 
    ScheduleUpdate, 
    ScheduleResponse,
    SchedulerStatusResponse,
    SchedulerLogResponse
)
from app.services.schedule_service import ScheduleService

router = APIRouter(tags=["Scheduler"])
schedule_service = ScheduleService()

@router.get("/schedules", response_model=StandardResponse)
async def get_schedules() -> StandardResponse:
    """Retrieves all scraper schedules."""
    try:
        schedules = schedule_service.get_all_schedules()
        return StandardResponse(
            success=True,
            message="Schedules retrieved successfully.",
            data=jsonable_encoder(schedules)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch schedules: {e}"
        )

@router.get("/schedules/{id}", response_model=StandardResponse)
async def get_schedule(id: UUID) -> StandardResponse:
    """Retrieves a specific schedule by ID."""
    try:
        schedule = schedule_service.get_schedule_by_id(id)
        return StandardResponse(
            success=True,
            message="Schedule details retrieved successfully.",
            data=jsonable_encoder(schedule)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch schedule: {e}"
        )

@router.post("/schedules", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(req: ScheduleCreate) -> StandardResponse:
    """Creates a new cron schedule entry for a brand."""
    try:
        created = schedule_service.create_schedule(req.model_dump(mode="json"))
        return StandardResponse(
            success=True,
            message="Schedule created successfully.",
            data=jsonable_encoder(created)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create schedule: {e}"
        )

@router.put("/schedules/{id}", response_model=StandardResponse)
async def update_schedule(id: UUID, req: ScheduleUpdate) -> StandardResponse:
    """Updates configuration parameters of an existing schedule."""
    try:
        updated = schedule_service.update_schedule(id, req.model_dump(exclude_unset=True, mode="json"))
        return StandardResponse(
            success=True,
            message="Schedule updated successfully.",
            data=jsonable_encoder(updated)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update schedule: {e}"
        )

@router.delete("/schedules/{id}", response_model=StandardResponse)
async def delete_schedule(id: UUID) -> StandardResponse:
    """Deletes a schedule entry."""
    try:
        schedule_service.delete_schedule(id)
        return StandardResponse(
            success=True,
            message="Schedule deleted successfully."
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete schedule: {e}"
        )

@router.post("/schedules/{id}/pause", response_model=StandardResponse)
async def pause_schedule(id: UUID) -> StandardResponse:
    """Pauses a schedule execution."""
    try:
        updated = schedule_service.pause_schedule(id)
        return StandardResponse(
            success=True,
            message="Schedule paused successfully.",
            data=jsonable_encoder(updated)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause schedule: {e}"
        )

@router.post("/schedules/{id}/resume", response_model=StandardResponse)
async def resume_schedule(id: UUID) -> StandardResponse:
    """Resumes a paused schedule execution."""
    try:
        updated = schedule_service.resume_schedule(id)
        return StandardResponse(
            success=True,
            message="Schedule resumed successfully.",
            data=jsonable_encoder(updated)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume schedule: {e}"
        )

@router.post("/schedules/{id}/run", response_model=StandardResponse)
async def run_schedule(id: UUID) -> StandardResponse:
    """Queues a schedule run immediately with HIGH priority."""
    try:
        schedule = await schedule_service.run_schedule_now(id)
        return StandardResponse(
            success=True,
            message="Schedule queued for execution immediately.",
            data=jsonable_encoder(schedule)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger schedule run: {e}"
        )

@router.get("/scheduler/status", response_model=StandardResponse)
async def get_scheduler_status() -> StandardResponse:
    """Retrieves engine stats and metrics."""
    try:
        stats = schedule_service.get_scheduler_status()
        return StandardResponse(
            success=True,
            message="Scheduler status retrieved successfully.",
            data=jsonable_encoder(stats)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch status: {e}"
        )

@router.get("/scheduler/queue", response_model=StandardResponse)
async def get_scheduler_queue() -> StandardResponse:
    """Retrieves a list of all jobs currently pending in the Priority Queue."""
    try:
        items = await schedule_service.engine.queue.get_items()
        # Convert UUID to string for JSON serialization
        items_serialized = []
        for it in items:
            it_copy = dict(it)
            it_copy["brand_id"] = str(it_copy["brand_id"])
            if it_copy.get("schedule_id"):
                it_copy["schedule_id"] = str(it_copy["schedule_id"])
            it_copy["queued_at"] = it_copy["queued_at"].isoformat()
            items_serialized.append(it_copy)
            
        return StandardResponse(
            success=True,
            message="Scheduler queue retrieved successfully.",
            data=jsonable_encoder(items_serialized)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch queue: {e}"
        )

@router.get("/scheduler/workers", response_model=StandardResponse)
async def get_scheduler_workers() -> StandardResponse:
    """Retrieves active running brands and allocation statuses."""
    try:
        active_brands = list(await schedule_service.engine.concurrency.get_active_brands())
        workers = {
            "active_workers_count": len(active_brands),
            "max_workers": schedule_service.engine.concurrency.max_concurrent_jobs,
            "running_brands": [str(x) for x in active_brands]
        }
        return StandardResponse(
            success=True,
            message="Scheduler workers retrieved successfully.",
            data=jsonable_encoder(workers)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch workers: {e}"
        )

@router.get("/scheduler/logs", response_model=StandardResponse)
async def get_scheduler_logs() -> StandardResponse:
    """Retrieves recent action event logs from the scheduler."""
    try:
        logs = schedule_service.get_scheduler_logs()
        return StandardResponse(
            success=True,
            message="Scheduler logs retrieved successfully.",
            data=jsonable_encoder(logs)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch logs: {e}"
        )

@router.get("/scheduler/stream")
async def stream_scheduler_events():
    """Streams live job progress and worker release events using Server-Sent Events."""
    async def event_generator():
        q = await schedule_service.engine.register_listener()
        try:
            while True:
                # Blocks until an event is broadcasted
                event_data = await q.get()
                yield f"data: {json.dumps(event_data)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            schedule_service.engine.unregister_listener(q)
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")
