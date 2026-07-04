import unittest
import uuid
import json
import logging
from fastapi.testclient import TestClient
from main import app
from app.core.logging_config import memory_log_handler, setup_memory_logging

# Instantiate TestClient once at the module level to avoid starting duplicate
# scheduler instances in lifespan loops for every test method.
client = TestClient(app)
setup_memory_logging()

class TestSprint42Features(unittest.TestCase):
    def test_health_check_endpoints(self):
        """Verify liveness, readiness, and subcomponent health endpoints return HTTP 200/503."""
        # 1. Main root health check
        res_root = client.get("/health")
        self.assertEqual(res_root.status_code, 200)
        self.assertEqual(res_root.json(), {"status": "ok"})

        # 2. Detailed health check
        res = client.get("/api/v1/health")
        self.assertIn(res.status_code, [200, 503])
        self.assertIn("status", res.json())
        self.assertIn("components", res.json())
        
        # 3. Liveness
        res_live = client.get("/api/v1/health/liveness")
        self.assertEqual(res_live.status_code, 200)
        self.assertEqual(res_live.json()["status"], "alive")
        
        # 4. Readiness
        res_ready = client.get("/api/v1/health/readiness")
        self.assertIn(res_ready.status_code, [200, 503])
        
        # 5. Scheduler health
        res_sched = client.get("/api/v1/health/scheduler")
        self.assertIn(res_sched.status_code, [200, 503])

        # 6. Worker health
        res_work = client.get("/api/v1/health/worker")
        self.assertIn(res_work.status_code, [200, 503])

        # 7. Database health
        res_db = client.get("/api/v1/health/database")
        self.assertIn(res_db.status_code, [200, 503])

    def test_analytics_endpoints(self):
        """Verify summary metrics and chart datasets endpoints return structured JSON."""
        # 1. Summary
        res_sum = client.get("/api/v1/analytics/summary")
        self.assertEqual(res_sum.status_code, 200)
        data = res_sum.json()
        self.assertIn("total_brands", data)
        self.assertIn("total_dealers", data)
        self.assertIn("success_rate", data)
        self.assertIn("scheduler_uptime", data)
        
        # 2. Charts
        res_charts = client.get("/api/v1/analytics/charts")
        self.assertEqual(res_charts.status_code, 200)
        charts = res_charts.json()
        self.assertIn("scrapes_per_day", charts)
        self.assertIn("dealers_over_time", charts)
        self.assertIn("failure_trend", charts)
        self.assertIn("brand_wise_dealers", charts)
        self.assertIn("scheduler_activity", charts)

    def test_monitoring_status(self):
        """Verify active workers, queue status, and hardware telemetries are compiled correctly."""
        res = client.get("/api/v1/monitoring/status")
        if res.status_code != 200:
            print(f"\nMONITORING ERROR DETAILS: {res.text}\n")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("live_workers", data)
        self.assertIn("queue_size", data)
        self.assertIn("system_stats", data)
        self.assertIn("cpu_usage_percent", data["system_stats"])
        self.assertIn("memory_usage_percent", data["system_stats"])

    def test_logging_and_grouping_endpoints(self):
        """Verify log retrieval, severity level queries, exporting, and downloads."""
        # Trigger some log statements to populate memory log handler
        logger = logging.getLogger("TestSprint42Features")
        logger.info("Sprint 4.2 Logging Unit Test Event")
        logger.error("Sprint 4.2 Dummy Error Event")
        
        # 1. Standard retrieval
        res = client.get("/api/v1/logs?limit=10")
        self.assertEqual(res.status_code, 200)
        logs = res.json()
        self.assertGreater(len(logs), 0)
        
        # 2. Severity level filtering
        res_err = client.get("/api/v1/logs?level=ERROR&limit=10")
        self.assertEqual(res_err.status_code, 200)
        errs = res_err.json()
        if errs:
            self.assertEqual(errs[0]["level"], "ERROR")
            
        # 3. Keyword query search
        res_q = client.get("/api/v1/logs?query=Dummy&limit=10")
        self.assertEqual(res_q.status_code, 200)
        self.assertGreater(len(res_q.json()), 0)
        
        # 4. Grouped errors
        res_groups = client.get("/api/v1/logs/errors")
        self.assertEqual(res_groups.status_code, 200)
        self.assertIsInstance(res_groups.json(), list)
        
        # 5. Export plain text logs
        res_dl = client.get("/api/v1/logs/download?query=Dummy")
        self.assertEqual(res_dl.status_code, 200)
        self.assertIn("attachment", res_dl.headers.get("content-disposition", ""))
        self.assertIn("app_execution.log", res_dl.headers.get("content-disposition", ""))
        
        # 6. Export CSV logs
        res_csv = client.get("/api/v1/logs/export?query=Dummy")
        self.assertEqual(res_csv.status_code, 200)
        self.assertIn("attachment", res_csv.headers.get("content-disposition", ""))
        self.assertIn("app_logs.csv", res_csv.headers.get("content-disposition", ""))

    def test_performance_metrics_endpoint(self):
        """Verify performance metrics returns latencies for api, queue, database and scrapers."""
        res = client.get("/api/v1/performance/metrics")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("database_latency_ms", data)
        self.assertIn("queue_delay_seconds", data)
        self.assertIn("avg_scraper_runtime_seconds", data)
        self.assertIn("avg_api_latency_ms", data)

    def test_notifications_endpoints(self):
        """Verify notification list retrieving and marking read/unread operations."""
        # 1. Fetch notifications
        res_list = client.get("/api/v1/notifications?limit=10")
        self.assertEqual(res_list.status_code, 200)
        self.assertIsInstance(res_list.json(), list)
        
        # 2. Mark all as read
        res_read_all = client.post("/api/v1/notifications/read-all")
        self.assertEqual(res_read_all.status_code, 200)
        self.assertIsInstance(res_read_all.json(), list)

if __name__ == "__main__":
    unittest.main()
