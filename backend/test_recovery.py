import pytest
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch
from app.scheduler.scheduler_engine import SchedulerEngine

@pytest.mark.anyio
async def test_scheduler_state_recovery():
    # Mock repos
    schedule_repo = MagicMock()
    job_repo = MagicMock()
    brand_repo = MagicMock()
    
    brand_id = uuid.uuid4()
    sched_id = uuid.uuid4()
    
    # Mock active schedules: one running (interrupted) and one with missing next_run
    schedule_repo.get_active_schedules.return_value = [
        {
            "id": sched_id,
            "brand_id": brand_id,
            "schedule_name": "Test Schedule",
            "cron_expression": "0 * * * *",
            "status": "Running",
            "next_run": None
        }
    ]
    
    # We patch repos on the SchedulerEngine instance
    with patch('app.scheduler.scheduler_engine.ScheduleRepository', return_value=schedule_repo), \
         patch('app.scheduler.scheduler_engine.ScrapeJobRepository', return_value=job_repo), \
         patch('app.scheduler.scheduler_engine.BrandRepository', return_value=brand_repo):
         
        engine = SchedulerEngine()
        # Reset initialized state to trigger instantiation patch
        engine._initialized = False
        engine.__init__()
        
        await engine.recover_scheduler_state()
        
        # Verify next_run was calculated and updated to ACTIVE
        assert schedule_repo.update.called is True
        update_args = schedule_repo.update.call_args[0]
        update_data = schedule_repo.update.call_args[1].get("data") or schedule_repo.update.call_args[0][1]
        
        assert update_args[0] == sched_id
        assert update_data["status"] == "ACTIVE"
        assert "next_run" in update_data
