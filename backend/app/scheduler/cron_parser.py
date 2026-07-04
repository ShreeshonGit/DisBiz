import re
from datetime import datetime, timedelta
from typing import Tuple

def validate_cron_expression(expression: str) -> Tuple[bool, str]:
    """
    Validates a 5-field cron expression.
    Returns (is_valid, error_message).
    """
    parts = expression.strip().split()
    if len(parts) != 5:
        return False, "Cron expression must contain exactly 5 fields."
        
    ranges = [
        (0, 59),  # minute
        (0, 23),  # hour
        (1, 31),  # day of month
        (1, 12),  # month
        (0, 7)    # day of week (0/7 are Sunday)
    ]
    
    for idx, part in enumerate(parts):
        if part == "*":
            continue
        # Check allowed characters: digits, comma, hyphen, slash, asterisk
        if not re.match(r'^[\d,\-*/]+$', part):
            return False, f"Invalid character in field {idx+1}: '{part}'"
            
        # Parse numbers and check bounds
        nums = re.findall(r'\d+', part)
        r_min, r_max = ranges[idx]
        for num in map(int, nums):
            if num < r_min or num > r_max:
                return False, f"Value '{num}' out of range ({r_min}-{r_max}) in field {idx+1}."
                
    return True, ""

def calculate_next_run(expression: str, base_time: datetime = None) -> datetime:
    """
    Calculates the next run datetime for a validated 5-field cron expression.
    """
    if base_time is None:
        base_time = datetime.now()
        
    is_valid, err = validate_cron_expression(expression)
    if not is_valid:
        raise ValueError(f"Invalid cron expression: {err}")
        
    parts = expression.strip().split()
    
    # 1. Step intervals: e.g. */15 * * * *
    if parts[0].startswith("*/"):
        step = int(parts[0].split("/")[1])
        minutes_to_add = step - (base_time.minute % step)
        next_run = base_time + timedelta(minutes=minutes_to_add)
        return next_run.replace(second=0, microsecond=0)
        
    # 2. Hourly: 0 * * * *
    if parts[0] == "0" and parts[1] == "*":
        next_run = base_time + timedelta(hours=1)
        return next_run.replace(minute=0, second=0, microsecond=0)
        
    # 3. Monthly: 0 1 1 * * (1:00 AM on the 1st of month)
    if parts[0] == "0" and parts[1].isdigit() and parts[2].isdigit():
        target_hour = int(parts[1])
        target_day = int(parts[2])
        next_run = base_time.replace(day=target_day, hour=target_hour, minute=0, second=0, microsecond=0)
        if next_run <= base_time:
            if next_run.month == 12:
                next_run = next_run.replace(year=next_run.year + 1, month=1)
            else:
                next_run = next_run.replace(month=next_run.month + 1)
        return next_run

    # 4. Weekly: 0 3 * * 1 (3:00 AM on Monday)
    if parts[0] == "0" and parts[1].isdigit() and parts[4].isdigit():
        target_hour = int(parts[1])
        target_wday = int(parts[4])  # 1 = Monday, 0/7 = Sunday
        next_run = base_time.replace(hour=target_hour, minute=0, second=0, microsecond=0)
        current_wday = next_run.weekday()
        target_wday_iso = 6 if target_wday in [0, 7] else target_wday - 1
        days_ahead = target_wday_iso - current_wday
        if days_ahead <= 0:
            days_ahead += 7
        next_run += timedelta(days=days_ahead)
        return next_run

    # 5. Daily: 0 2 * * * (2:00 AM daily)
    if parts[0] == "0" and parts[1].isdigit():
        target_hour = int(parts[1])
        next_run = base_time.replace(hour=target_hour, minute=0, second=0, microsecond=0)
        if next_run <= base_time:
            next_run += timedelta(days=1)
        return next_run

    # Fallback default: next hour
    next_run = base_time + timedelta(hours=1)
    return next_run.replace(second=0, microsecond=0)
