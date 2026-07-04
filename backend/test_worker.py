import pytest
import uuid
from unittest.mock import MagicMock, AsyncMock
from app.scheduler.worker import Worker

@pytest.mark.anyio
async def test_worker_successful_execution():
    # Mock repos
    schedule_repo = MagicMock()
    job_repo = MagicMock()
    
    # Mock job creation
    job_repo.create.return_value = {"id": str(uuid.uuid4()), "status": "Running"}
    job_repo.get_by_id.return_value = {"status": "COMPLETED", "records_saved": 42}
    
    worker = Worker(schedule_repo, job_repo)
    # Mock ScraperJobRunner
    worker.runner = MagicMock()
    worker.runner.run_job = AsyncMock()
    
    job = {
        "brand_id": uuid.uuid4(),
        "schedule_id": uuid.uuid4(),
        "priority": "NORMAL",
        "retries": 0,
        "max_retries": 3,
        "retry_delay_minutes": 5,
        "retry_policy": "EXPONENTIAL"
    }
    
    event_cb = AsyncMock()
    
    success = await worker.execute_job(job, "Worker-1", event_cb)
    
    assert success is True
    assert job_repo.create.called is True
    assert worker.runner.run_job.called is True
    assert schedule_repo.log_action.called is True
    assert event_cb.called is True
