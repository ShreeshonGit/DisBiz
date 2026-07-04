import time
from datetime import datetime, timedelta
from uuid import UUID
from typing import Dict, Any, List
from app.database.supabase import supabase
from app.scheduler.scheduler_engine import SchedulerEngine
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    """
    Analytics & Dashboard Aggregation Service.
    Queries Supabase schemas for scrapes, dealer discoveries, uptime, and daily trend logs.
    """
    def __init__(self):
        self.engine = SchedulerEngine()

    def get_summary(self) -> Dict[str, Any]:
        try:
            client = supabase
            if not client:
                raise RuntimeError("Supabase not initialized")
            
            # 1. Brands
            total_brands = len(client.table("brands").select("id").execute().data or [])
            active_brands = len(client.table("brands").select("id").eq("active", True).execute().data or [])
            
            # 2. Dealers
            total_dealers = len(client.table("dealers").select("id").execute().data or [])
            
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_iso = today_start.isoformat()
            dealers_today = len(client.table("dealers").select("id").gte("created_at", today_iso).execute().data or [])
            
            # 3. Jobs
            jobs_data = client.table("scrape_jobs").select("status, started_at, duration_seconds").execute().data or []
            
            successful_scrapes = sum(1 for j in jobs_data if j.get("status", "").lower() == "completed")
            failed_scrapes = sum(1 for j in jobs_data if j.get("status", "").lower() == "failed")
            
            total_jobs = len(jobs_data)
            success_rate = 100.0
            if total_jobs > 0:
                success_rate = (successful_scrapes / total_jobs) * 100.0
                
            completed_durations = [
                j["duration_seconds"] for j in jobs_data 
                if j.get("status", "").lower() == "completed" and j.get("duration_seconds")
            ]
            avg_duration = sum(completed_durations) / len(completed_durations) if completed_durations else 0.0
            
            # Today/Week/Month job counts
            now = datetime.now()
            today_start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start_dt = now - timedelta(days=7)
            month_start_dt = now - timedelta(days=30)
            
            jobs_today = 0
            jobs_week = 0
            jobs_month = 0
            
            for j in jobs_data:
                try:
                    start_str = j.get("started_at", "")
                    if start_str:
                        start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00")).replace(tzinfo=None)
                        if start_dt >= today_start_dt:
                            jobs_today += 1
                        if start_dt >= week_start_dt:
                            jobs_week += 1
                        if start_dt >= month_start_dt:
                            jobs_month += 1
                except Exception:
                    pass
                    
            # 4. Scheduler & Worker uptime
            scheduler_uptime = 0.0
            if hasattr(self.engine, "monitor") and self.engine.monitor:
                scheduler_uptime = time.time() - self.engine.monitor.start_time
            worker_uptime = scheduler_uptime
            
            return {
                "total_brands": total_brands,
                "active_brands": active_brands,
                "total_dealers": total_dealers,
                "dealers_added_today": dealers_today,
                "successful_scrapes": successful_scrapes,
                "failed_scrapes": failed_scrapes,
                "success_rate": round(success_rate, 1),
                "avg_scrape_duration": round(avg_duration, 2),
                "jobs_today": jobs_today,
                "jobs_this_week": jobs_week,
                "jobs_this_month": jobs_month,
                "scheduler_uptime": round(scheduler_uptime, 1),
                "worker_uptime": round(worker_uptime, 1)
            }
        except Exception as e:
            logger.error(f"Error compiling analytics summary: {e}")
            return {
                "total_brands": 0,
                "active_brands": 0,
                "total_dealers": 0,
                "dealers_added_today": 0,
                "successful_scrapes": 0,
                "failed_scrapes": 0,
                "success_rate": 100.0,
                "avg_scrape_duration": 0.0,
                "jobs_today": 0,
                "jobs_this_week": 0,
                "jobs_this_month": 0,
                "scheduler_uptime": 0.0,
                "worker_uptime": 0.0
            }

    def get_charts(self) -> Dict[str, Any]:
        try:
            client = supabase
            if not client:
                raise RuntimeError("Supabase not initialized")
            
            # Fetch brands for name mapping
            brands_data = client.table("brands").select("id, name").execute().data or []
            brand_id_to_name = {b["id"]: b["name"] for b in brands_data}
            
            # Fetch dealers for brand-wise counts and dealers over time
            dealers_data = client.table("dealers").select("brand_id, created_at").execute().data or []
            
            # Brand-wise dealer counts
            brand_counts = {}
            for d in dealers_data:
                bid = d["brand_id"]
                name = brand_id_to_name.get(bid, bid)
                brand_counts[name] = brand_counts.get(name, 0) + 1
            brand_wise_dealers = [{"brand_name": k, "dealer_count": v} for k, v in brand_counts.items()]
            
            # Dealers discovered over time (grouped by date)
            dealers_by_date = {}
            for d in dealers_data:
                try:
                    dt_str = d["created_at"].split("T")[0]
                    dealers_by_date[dt_str] = dealers_by_date.get(dt_str, 0) + 1
                except Exception:
                    pass
            sorted_dates = sorted(dealers_by_date.keys())
            dealers_over_time = []
            cumulative = 0
            for date in sorted_dates:
                cumulative += dealers_by_date[date]
                dealers_over_time.append({"date": date, "count": cumulative})
                
            # Jobs for success/failure/scrapes per day
            jobs_data = client.table("scrape_jobs").select("status, started_at, error_message").execute().data or []
            
            # Scrapes per day (last 7 days)
            scrapes_by_date = {}
            now = datetime.now()
            for i in range(7):
                d_str = (now - timedelta(days=i)).strftime("%Y-%m-%d")
                scrapes_by_date[d_str] = {"successful": 0, "failed": 0}
                
            for j in jobs_data:
                try:
                    d_str = j["started_at"].split("T")[0]
                    if d_str in scrapes_by_date:
                        status = j.get("status", "").lower()
                        if status == "completed":
                            scrapes_by_date[d_str]["successful"] += 1
                        else:
                            scrapes_by_date[d_str]["failed"] += 1
                except Exception:
                    pass
            scrapes_per_day = [{"date": k, "successful": v["successful"], "failed": v["failed"]} for k, v in sorted(scrapes_by_date.items())]
            
            # Failure trend (top error messages)
            error_counts = {}
            for j in jobs_data:
                if j.get("status", "").lower() == "failed" and j.get("error_message"):
                    err = j["error_message"]
                    key = err[:50] + "..." if len(err) > 50 else err
                    error_counts[key] = error_counts.get(key, 0) + 1
            failure_trend = [{"error": k, "count": v} for k, v in error_counts.items()]
            
            # Scheduler activity (hourly distribution of enqueued jobs)
            activity_by_hour = {f"{h:02d}:00": 0 for h in range(24)}
            for j in jobs_data:
                try:
                    t_str = j["started_at"].split("T")[1]
                    hour = int(t_str.split(":")[0])
                    key = f"{hour:02d}:00"
                    activity_by_hour[key] += 1
                except Exception:
                    pass
            scheduler_activity = [{"hour": k, "job_count": v} for k, v in sorted(activity_by_hour.items())]
            
            return {
                "scrapes_per_day": scrapes_per_day,
                "dealers_over_time": dealers_over_time,
                "failure_trend": failure_trend,
                "brand_wise_dealers": brand_wise_dealers,
                "scheduler_activity": scheduler_activity
            }
        except Exception as e:
            logger.error(f"Error compiling charts: {e}")
            return {
                "scrapes_per_day": [],
                "dealers_over_time": [],
                "failure_trend": [],
                "brand_wise_dealers": [],
                "scheduler_activity": []
            }
