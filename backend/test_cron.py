import pytest
from datetime import datetime
from app.scheduler.cron_parser import validate_cron_expression, calculate_next_run

def test_cron_validation():
    # Valid expressions
    assert validate_cron_expression("0 * * * *")[0] is True
    assert validate_cron_expression("0 2 * * *")[0] is True
    assert validate_cron_expression("0 3 * * 1")[0] is True
    assert validate_cron_expression("0 1 1 * *")[0] is True
    assert validate_cron_expression("*/15 * * * *")[0] is True
    
    # Invalid expressions
    assert validate_cron_expression("0 * * *")[0] is False  # Only 4 fields
    assert validate_cron_expression("0 * * * * *")[0] is False  # 6 fields
    assert validate_cron_expression("60 * * * *")[0] is False  # Minute out of range (0-59)
    assert validate_cron_expression("0 24 * * *")[0] is False  # Hour out of range (0-23)
    assert validate_cron_expression("invalid cron")[0] is False

def test_cron_next_run_calculation():
    base_time = datetime(2026, 7, 4, 12, 0, 0)  # A Saturday
    
    # 1. Step minutes (*/15 * * * *) -> should run at 12:15
    next_run = calculate_next_run("*/15 * * * *", base_time)
    assert next_run.minute == 15
    assert next_run.hour == 12
    
    # 2. Hourly (0 * * * *) -> should run at 13:00
    next_run = calculate_next_run("0 * * * *", base_time)
    assert next_run.minute == 0
    assert next_run.hour == 13
    
    # 3. Daily at 2 AM (0 2 * * *) -> should run on 2026-07-05 at 2:00 AM
    next_run = calculate_next_run("0 2 * * *", base_time)
    assert next_run.hour == 2
    assert next_run.day == 5
    
    # 4. Weekly at 3 AM on Monday (0 3 * * 1) -> Monday is 2026-07-06
    next_run = calculate_next_run("0 3 * * 1", base_time)
    assert next_run.hour == 3
    assert next_run.day == 6
    assert next_run.weekday() == 0  # Monday
