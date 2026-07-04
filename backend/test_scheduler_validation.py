import pytest
import uuid
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from main import app
from app.schemas.schedule_schema import ScheduleCreate
from pydantic import ValidationError

client = TestClient(app)

# -----------------------------------------------------------------
# 1. Pydantic Schema Validation Tests
# -----------------------------------------------------------------

def test_schema_valid_schedule():
    """Verify ScheduleCreate parses valid inputs correctly."""
    brand_id = uuid.uuid4()
    data = {
        "brand_id": str(brand_id),
        "schedule_name": "Weekly Audit",
        "cron_expression": "0 2 * * 0",
        "priority": "HIGH",
        "max_retries": 5,
        "timezone": "IST",
        "retry_delay_minutes": 10,
        "retry_policy": "LINEAR"
    }
    model = ScheduleCreate(**data)
    assert model.schedule_name == "Weekly Audit"
    assert model.cron_expression == "0 2 * * 0"
    assert model.priority == "HIGH"
    assert model.retry_policy == "LINEAR"


def test_schema_priority_normalization():
    """Verify priority 'NORMAL' is mapped to 'MEDIUM'."""
    brand_id = uuid.uuid4()
    data = {
        "brand_id": str(brand_id),
        "schedule_name": "Normal Priority Job",
        "cron_expression": "0 * * * *",
        "priority": "NORMAL"  # Mapped to MEDIUM
    }
    model = ScheduleCreate(**data)
    assert model.priority == "MEDIUM"


def test_schema_invalid_cron():
    """Verify invalid cron formats throw ValidationError."""
    brand_id = uuid.uuid4()
    with pytest.raises(ValidationError):
        ScheduleCreate(
            brand_id=brand_id,
            schedule_name="Bad Cron",
            cron_expression="0 * * *"  # Only 4 fields
        )

    with pytest.raises(ValidationError):
        ScheduleCreate(
            brand_id=brand_id,
            schedule_name="Bad Cron Chars",
            cron_expression="a * * * *"  # Invalid chars
        )

    with pytest.raises(ValidationError):
        ScheduleCreate(
            brand_id=brand_id,
            schedule_name="Bad Cron Range",
            cron_expression="0 60 * * *"  # Hour 60 is out of bounds
        )


def test_schema_invalid_priority():
    """Verify invalid priorities throw ValidationError."""
    brand_id = uuid.uuid4()
    with pytest.raises(ValidationError):
        ScheduleCreate(
            brand_id=brand_id,
            schedule_name="Bad Priority",
            cron_expression="0 * * * *",
            priority="CRITICAL"
        )


def test_schema_invalid_retry_policy():
    """Verify invalid retry policies throw ValidationError."""
    brand_id = uuid.uuid4()
    with pytest.raises(ValidationError):
        ScheduleCreate(
            brand_id=brand_id,
            schedule_name="Bad Policy",
            cron_expression="0 * * * *",
            retry_policy="ONCE_MORE"
        )


# -----------------------------------------------------------------
# 2. Router API Validation Endpoint Tests (with Service Mocking)
# -----------------------------------------------------------------

@patch("app.api.v1.schedule_routes.schedule_service")
def test_create_schedule_api_success(mock_service):
    """Verify API POST /api/v1/schedules succeeds with valid fields."""
    brand_id = uuid.uuid4()
    sched_id = uuid.uuid4()
    
    mock_service.create_schedule.return_value = {
        "id": str(sched_id),
        "brand_id": str(brand_id),
        "schedule_name": "Good Job",
        "cron_expression": "30 5 * * *",
        "priority": "LOW",
        "retry_delay_minutes": 5,
        "retry_policy": "IMMEDIATE"
    }

    payload = {
        "brand_id": str(brand_id),
        "schedule_name": "Good Job",
        "cron_expression": "30 5 * * *",
        "priority": "LOW",
        "retry_delay_minutes": 5,
        "retry_policy": "IMMEDIATE"
    }

    res = client.post("/api/v1/schedules", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["success"] is True
    assert data["data"]["schedule_name"] == "Good Job"
    assert data["data"]["priority"] == "LOW"


def test_create_schedule_api_validation_failures():
    """Verify API POST /api/v1/schedules raises 422 for malformed requests."""
    # Missing brand_id
    res = client.post("/api/v1/schedules", json={
        "schedule_name": "No Brand",
        "cron_expression": "0 * * * *"
    })
    assert res.status_code == 422
    assert "validation" in res.json()["message"].lower()

    # Missing schedule_name
    res = client.post("/api/v1/schedules", json={
        "brand_id": str(uuid.uuid4()),
        "cron_expression": "0 * * * *"
    })
    assert res.status_code == 422

    # Invalid Cron Expression
    res = client.post("/api/v1/schedules", json={
        "brand_id": str(uuid.uuid4()),
        "schedule_name": "Bad Cron",
        "cron_expression": "* * * * * *"  # 6 fields
    })
    assert res.status_code == 422


# -----------------------------------------------------------------
# 3. Service Layer and Queue Integration Mock Tests
# -----------------------------------------------------------------

@pytest.mark.anyio
@patch("app.services.schedule_service.ScheduleRepository")
@patch("app.services.schedule_service.BrandRepository")
async def test_create_schedule_duplicate_prevention(mock_brand_repo_class, mock_sched_repo_class):
    """Verify Service Layer raises ValueError on duplicate schedule names."""
    from app.services.schedule_service import ScheduleService
    
    mock_brand_repo = mock_brand_repo_class.return_value
    mock_sched_repo = mock_sched_repo_class.return_value
    
    brand_id = uuid.uuid4()
    mock_brand_repo.get_by_id.return_value = {"id": str(brand_id), "name": "Tata"}
    
    # Existing schedules with identical name
    mock_sched_repo.get_by_brand_id.return_value = [
        {"schedule_name": "Nightly Sync", "brand_id": str(brand_id)}
    ]
    
    service = ScheduleService()
    
    with pytest.raises(ValueError) as exc:
        service.create_schedule({
            "brand_id": str(brand_id),
            "schedule_name": "Nightly Sync",
            "cron_expression": "0 0 * * *",
            "priority": "MEDIUM"
        })
    assert "already exists" in str(exc.value)


@pytest.mark.anyio
@patch("app.services.schedule_service.ScheduleRepository")
async def test_run_schedule_now_queues_correctly(mock_sched_repo_class):
    """Verify run_schedule_now injects active job parameters into Priority Queue."""
    from app.services.schedule_service import ScheduleService
    
    mock_sched_repo = mock_sched_repo_class.return_value
    sched_id = uuid.uuid4()
    brand_id = uuid.uuid4()
    
    schedule_data = {
        "id": str(sched_id),
        "brand_id": str(brand_id),
        "schedule_name": "Adhoc Trigger",
        "cron_expression": "0 * * * *",
        "priority": "LOW",
        "max_retries": 4,
        "retry_delay_minutes": 12,
        "retry_policy": "LINEAR"
    }
    mock_sched_repo.get_by_id.return_value = schedule_data
    
    service = ScheduleService()
    service.engine.queue = MagicMock()
    service.engine.queue.enqueue = AsyncMock()
    
    await service.run_schedule_now(sched_id)
    
    # Assert manual run log created and enqueued with correct retry parameters
    mock_sched_repo.log_action.assert_called_with(
        schedule_id=sched_id,
        brand_id=brand_id,
        action="RUN_NOW",
        status="PENDING",
        details="Manual ad-hoc run triggered."
    )
    
    service.engine.queue.enqueue.assert_called_with(
        brand_id=brand_id,
        schedule_id=sched_id,
        priority="HIGH",
        max_retries=4,
        retry_delay_minutes=12,
        retry_policy="LINEAR"
    )
