import pytest
import uuid
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def mock_schedule_service():
    with patch("app.api.v1.schedule_routes.schedule_service") as mock:
        yield mock

def test_get_schedules_endpoint(mock_schedule_service):
    mock_schedule_service.get_all_schedules.return_value = [
        {"id": str(uuid.uuid4()), "schedule_name": "Hourly Scrape", "cron_expression": "0 * * * *"}
    ]
    
    res = client.get("/api/v1/schedules")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["data"]) == 1
    assert data["data"][0]["schedule_name"] == "Hourly Scrape"

def test_get_schedule_by_id_endpoint(mock_schedule_service):
    sched_id = uuid.uuid4()
    mock_schedule_service.get_schedule_by_id.return_value = {
        "id": str(sched_id),
        "schedule_name": "Daily",
        "cron_expression": "0 2 * * *"
    }
    
    res = client.get(f"/api/v1/schedules/{sched_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["schedule_name"] == "Daily"

def test_create_schedule_endpoint(mock_schedule_service):
    brand_id = uuid.uuid4()
    sched_id = uuid.uuid4()
    
    mock_schedule_service.create_schedule.return_value = {
        "id": str(sched_id),
        "brand_id": str(brand_id),
        "schedule_name": "Hourly",
        "cron_expression": "0 * * * *"
    }
    
    payload = {
        "brand_id": str(brand_id),
        "schedule_name": "Hourly",
        "cron_expression": "0 * * * *",
        "priority": "MEDIUM",
        "max_retries": 3,
        "timezone": "UTC"
    }
    
    res = client.post("/api/v1/schedules", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["success"] is True
    assert data["data"]["schedule_name"] == "Hourly"

def test_pause_schedule_endpoint(mock_schedule_service):
    sched_id = uuid.uuid4()
    mock_schedule_service.pause_schedule.return_value = {"id": str(sched_id), "status": "PAUSED"}
    
    res = client.post(f"/api/v1/schedules/{sched_id}/pause")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["status"] == "PAUSED"

def test_resume_schedule_endpoint(mock_schedule_service):
    sched_id = uuid.uuid4()
    mock_schedule_service.resume_schedule.return_value = {"id": str(sched_id), "status": "ACTIVE"}
    
    res = client.post(f"/api/v1/schedules/{sched_id}/resume")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["status"] == "ACTIVE"

def test_get_scheduler_status_endpoint(mock_schedule_service):
    mock_schedule_service.get_scheduler_status.return_value = {
        "uptime_seconds": 100,
        "total_runs": 10,
        "success_rate": 90.0,
        "queue_size": 2,
        "active_workers": 1,
        "worker_utilization": 33.3
    }
    
    res = client.get("/api/v1/scheduler/status")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["success_rate"] == 90.0
