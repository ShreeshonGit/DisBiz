import time
import sys
import os
import psutil
from collections import deque
from typing import Dict, Any, List
from datetime import datetime
from app.database.supabase import supabase
from app.scheduler.scheduler_engine import SchedulerEngine

# Deques to maintain request latency stats
API_REQUESTS_LIMIT = 100
api_latencies = deque(maxlen=API_REQUESTS_LIMIT)
api_paths = deque(maxlen=API_REQUESTS_LIMIT)

def record_api_request(path: str, method: str, duration_ms: float, status_code: int):
    """
    Records latency metrics for a completed API request.
    """
    api_latencies.append(duration_ms)
    api_paths.append({
        "path": path,
        "method": method,
        "duration": duration_ms,
        "status_code": status_code,
        "timestamp": time.time()
    })

def get_api_latency_metrics() -> Dict[str, Any]:
    """
    Calculates average and p95 latencies for recent API calls.
    """
    latencies = list(api_latencies)
    if not latencies:
        return {
            "avg_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
            "total_requests": 0
        }
    avg = sum(latencies) / len(latencies)
    sorted_lats = sorted(latencies)
    p95_idx = int(len(sorted_lats) * 0.95)
    p95 = sorted_lats[min(p95_idx, len(sorted_lats) - 1)]
    return {
        "avg_latency_ms": round(avg, 2),
        "p95_latency_ms": round(p95, 2),
        "total_requests": len(latencies)
    }

def get_system_metrics() -> Dict[str, Any]:
    """
    Gets CPU and RAM usage.
    """
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    return {
        "cpu_usage_percent": cpu,
        "memory_usage_percent": mem.percent,
        "memory_used_mb": round(mem.used / (1024 * 1024), 2),
        "memory_total_mb": round(mem.total / (1024 * 1024), 2)
    }

def get_db_latency() -> float:
    """
    Measures the direct connection latency to Supabase.
    """
    start = time.time()
    try:
        if supabase:
            supabase.table("brands").select("id").limit(1).execute()
            return round((time.time() - start) * 1000, 2)
    except Exception:
        pass
    return 0.0

def get_queue_latencies() -> float:
    """
    Calculates the average delay between job creation and execution start.
    """
    try:
        if supabase:
            jobs = supabase.table("scrape_jobs").select("created_at, start_time").limit(100).execute().data or []
            delays = []
            for j in jobs:
                try:
                    c_at = datetime.fromisoformat(j["created_at"].replace("Z", "+00:00")).replace(tzinfo=None)
                    s_at = datetime.fromisoformat(j["start_time"].replace("Z", "+00:00")).replace(tzinfo=None)
                    delay = (s_at - c_at).total_seconds()
                    if delay >= 0:
                        delays.append(delay)
                except Exception:
                    pass
            if delays:
                return round(sum(delays) / len(delays), 2)
    except Exception:
        pass
    return 0.0

def get_scraper_latencies() -> float:
    """
    Gets average duration of completed scraper job runs.
    """
    try:
        if supabase:
            jobs = supabase.table("scrape_jobs").select("duration_seconds").eq("status", "Completed").limit(100).execute().data or []
            durations = [j["duration_seconds"] for j in jobs if j.get("duration_seconds")]
            if durations:
                return round(sum(durations) / len(durations), 2)
    except Exception:
        pass
    return 0.0
