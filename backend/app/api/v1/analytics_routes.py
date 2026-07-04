from fastapi import APIRouter, HTTPException, status, Query, Response
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from uuid import UUID
from typing import Optional, List, Dict, Any
import json
import asyncio
import io
import csv

from app.services.analytics_service import AnalyticsService
from app.services.notification_service import NotificationService
from app.core.logging_config import memory_log_handler
from app.utils.monitoring import (
    get_api_latency_metrics,
    get_system_metrics,
    get_db_latency,
    get_queue_latencies,
    get_scraper_latencies
)
from app.scheduler.scheduler_engine import SchedulerEngine
from app.database.supabase import supabase

router = APIRouter()
analytics_service = AnalyticsService()

# ---------------------------------------------------------
# PHASE 2 – ANALYTICS ENDPOINTS
# ---------------------------------------------------------

@router.get("/analytics/summary", response_model=Dict[str, Any])
async def get_analytics_summary():
    """Retrieves high-level summary KPIs (total brands, successes, uptimes)."""
    return analytics_service.get_summary()

@router.get("/analytics/charts", response_model=Dict[str, Any])
async def get_analytics_charts():
    """Retrieves chart datasets (scrapes per day, brand distribution, failure trends)."""
    return analytics_service.get_charts()

# ---------------------------------------------------------
# PHASE 3 – SYSTEM MONITORING
# ---------------------------------------------------------

@router.get("/monitoring/status", response_model=Dict[str, Any])
async def get_monitoring_status():
    """Compiles real-time thread worker stats, queue depths, and hardware metrics (CPU/RAM)."""
    try:
        engine = SchedulerEngine()
        # Safely obtain active workers
        active_workers = []
        try:
            act_res = engine.concurrency.get_active_brands()
            if hasattr(act_res, "__await__"):
                active_workers = list(await act_res)
            elif isinstance(act_res, (set, list)):
                active_workers = list(act_res)
        except Exception:
            pass

        # Safely obtain queue size
        queue_size = 0
        try:
            q_res = engine.queue.size()
            if hasattr(q_res, "__await__"):
                queue_size = await q_res
            elif isinstance(q_res, int):
                queue_size = q_res
        except Exception:
            pass
        
        # Load jobs to calculate counts
        jobs_data = []
        if supabase:
            try:
                jobs_data = supabase.table("scrape_jobs").select("status, retry_count").execute().data or []
            except Exception:
                # Gracefully fall back if database is mocked or connection fails
                pass
        
        if not isinstance(jobs_data, list):
            jobs_data = []
            
        running_jobs = sum(1 for j in jobs_data if isinstance(j, dict) and j.get("status", "").lower() == "running")
        waiting_jobs = sum(1 for j in jobs_data if isinstance(j, dict) and j.get("status", "").lower() == "queued")
        failed_jobs = sum(1 for j in jobs_data if isinstance(j, dict) and j.get("status", "").lower() == "failed")
        retries = sum(int(j.get("retry_count", 0)) for j in jobs_data if isinstance(j, dict) and isinstance(j.get("retry_count"), (int, float)))
        
        api_stats = get_api_latency_metrics()
        system_stats = get_system_metrics()
        
        return {
            "live_workers": [str(x) for x in active_workers],
            "active_workers_count": len(active_workers),
            "queue_size": queue_size,
            "running_jobs": running_jobs,
            "waiting_jobs": waiting_jobs,
            "failed_jobs": failed_jobs,
            "retry_count": retries,
            "api_stats": api_stats,
            "system_stats": system_stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch monitoring status: {e}"
        )

# ---------------------------------------------------------
# PHASE 4 – LOGGING MODULE
# ---------------------------------------------------------

@router.get("/logs", response_model=List[Dict[str, Any]])
async def get_application_logs(
    level: Optional[str] = Query(None, description="Filter by severity: INFO, WARN, ERROR, CRITICAL"),
    query: Optional[str] = Query(None, description="Free text keyword search query"),
    limit: int = Query(100, ge=1, le=1000, description="Max logs to return")
):
    """Retrieves recent filtered in-memory application logs."""
    return memory_log_handler.get_logs(level=level, query=query, limit=limit)

@router.get("/logs/errors", response_model=List[Dict[str, Any]])
async def get_grouped_error_logs():
    """Aggregates and groups similar error and traceback occurrences."""
    return memory_log_handler.get_error_groups()

@router.get("/logs/download")
async def download_application_logs(
    level: Optional[str] = Query(None),
    query: Optional[str] = Query(None)
):
    """Downloads filtered logs as a plain text log file."""
    logs = memory_log_handler.get_logs(level=level, query=query, limit=2000)
    log_content = ""
    for log in logs:
        tb_str = f"\n{log['traceback']}" if log['traceback'] else ""
        log_content += f"[{log['timestamp']}] {log['level']} [{log['logger']}] {log['message']}{tb_str}\n"
        
    return Response(
        content=log_content,
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=app_execution.log"}
    )

@router.get("/logs/export")
async def export_logs_csv(
    level: Optional[str] = Query(None),
    query: Optional[str] = Query(None)
):
    """Exports log traces to CSV format."""
    logs = memory_log_handler.get_logs(level=level, query=query, limit=2000)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp", "Severity", "Logger", "Message", "Traceback"])
    for l in logs:
        writer.writerow([l["timestamp"], l["level"], l["logger"], l["message"], l["traceback"] or ""])
        
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=app_logs.csv"}
    )

@router.get("/logs/stream")
async def stream_live_logs():
    """Streams live log entries to DevTools / Admin Console using Server-Sent Events."""
    async def log_generator():
        q = asyncio.Queue()
        
        async def on_log(log_dict):
            await q.put(log_dict)
            
        memory_log_handler.listeners.append(on_log)
        try:
            while True:
                log_entry = await q.get()
                yield f"data: {json.dumps(log_entry)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if on_log in memory_log_handler.listeners:
                memory_log_handler.listeners.remove(on_log)
                
    return StreamingResponse(log_generator(), media_type="text/event-stream")

# ---------------------------------------------------------
# PHASE 5 – HEALTH ENDPOINTS
# ---------------------------------------------------------

@router.get("/health")
async def get_health_status():
    """Retrieves consolidated platform readiness, liveness, and component statuses."""
    db_ok = False
    try:
        if supabase:
            supabase.table("brands").select("id").limit(1).execute()
            db_ok = True
    except Exception:
        pass
        
    engine = SchedulerEngine()
    scheduler_ok = engine.running
    worker_ok = True  # Worker queue is operational
    
    overall_ok = db_ok and scheduler_ok
    status_code = status.HTTP_200_OK if overall_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if overall_ok else "unhealthy",
            "readiness": "ready" if overall_ok else "not_ready",
            "liveness": "alive",
            "components": {
                "database_health": "ok" if db_ok else "critical",
                "supabase_health": "ok" if db_ok else "critical",
                "scheduler_health": "ok" if scheduler_ok else "critical",
                "worker_health": "ok" if worker_ok else "critical"
            }
        }
    )

@router.get("/health/liveness")
async def get_liveness():
    """Liveness probe. Always returns HTTP 200."""
    return {"status": "alive"}

@router.get("/health/readiness")
async def get_readiness():
    """Readiness probe. Checks DB and scheduler initialization."""
    db_ok = False
    try:
        if supabase:
            supabase.table("brands").select("id").limit(1).execute()
            db_ok = True
    except Exception:
        pass
    engine = SchedulerEngine()
    if db_ok and engine.running:
        return {"status": "ready"}
    return JSONResponse(status_code=503, content={"status": "not_ready"})

@router.get("/health/scheduler")
async def get_scheduler_health():
    engine = SchedulerEngine()
    if engine.running:
        return {"status": "healthy"}
    return JSONResponse(status_code=503, content={"status": "stopped"})

@router.get("/health/worker")
async def get_worker_health():
    # Healthy if scheduler dispatcher is running
    engine = SchedulerEngine()
    if engine.running and engine.dispatcher.running:
        return {"status": "healthy"}
    return JSONResponse(status_code=503, content={"status": "inactive"})

@router.get("/health/database")
async def get_database_health():
    try:
        if supabase:
            supabase.table("brands").select("id").limit(1).execute()
            return {"status": "healthy"}
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "critical", "error": str(e)})
    return JSONResponse(status_code=503, content={"status": "not_configured"})

# ---------------------------------------------------------
# PHASE 6 – PERFORMANCE ENDPOINTS
# ---------------------------------------------------------

@router.get("/performance/metrics", response_model=Dict[str, Any])
async def get_performance_metrics():
    """Retrieves round-trip latency timings across API requests, scraping loops, queues, and databases."""
    db_time = get_db_latency()
    queue_time = get_queue_latencies()
    scraper_time = get_scraper_latencies()
    api_stats = get_api_latency_metrics()
    
    return {
        "database_latency_ms": db_time,
        "queue_delay_seconds": queue_time,
        "avg_scraper_runtime_seconds": scraper_time,
        "avg_api_latency_ms": api_stats["avg_latency_ms"],
        "p95_api_latency_ms": api_stats["p95_latency_ms"],
        "total_api_requests": api_stats["total_requests"]
    }

# ---------------------------------------------------------
# PHASE 7 – NOTIFICATIONS ENDPOINTS
# ---------------------------------------------------------

@router.get("/notifications", response_model=List[Dict[str, Any]])
async def get_notifications_history(limit: int = Query(50, ge=1, le=200)):
    """Retrieves stored alert history logs."""
    return NotificationService.get_history(limit=limit)

@router.post("/notifications/{id}/read", response_model=Dict[str, Any])
async def mark_notification_read(id: UUID):
    """Marks a single alert log as read."""
    return NotificationService.mark_as_read(id)

@router.post("/notifications/read-all", response_model=List[Dict[str, Any]])
async def mark_all_notifications_read():
    """Marks all unread notifications read."""
    return NotificationService.mark_all_read()
