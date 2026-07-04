from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any
import re

class ScheduleBase(BaseModel):
    brand_id: UUID
    schedule_name: str = Field(..., min_length=1, max_length=100)
    cron_expression: str = Field(..., description="5-field cron expression")
    priority: str = Field(default="MEDIUM", description="HIGH, MEDIUM, or LOW")
    max_retries: int = Field(default=3, ge=0, le=10)
    timezone: str = Field(default="UTC")
    retry_delay_minutes: int = Field(default=5, ge=1, le=60)
    retry_policy: str = Field(default="EXPONENTIAL", description="EXPONENTIAL, LINEAR, or IMMEDIATE")

    @field_validator("cron_expression")
    @classmethod
    def validate_cron(cls, value: str) -> str:
        parts = value.strip().split()
        if len(parts) != 5:
            raise ValueError("Cron expression must contain exactly 5 space-separated fields (minute, hour, day-of-month, month, day-of-week).")
        
        # Ranges for each field
        ranges = [
            (0, 59),  # minute
            (0, 23),  # hour
            (1, 31),  # day of month
            (1, 12),  # month
            (0, 7)    # day of week (0 or 7 are Sunday)
        ]
        
        for idx, part in enumerate(parts):
            if part == "*":
                continue
            
            # Match standard cron characters
            if not re.match(r'^[\d,\-*/]+$', part):
                raise ValueError(f"Invalid character in cron field: '{part}'")
            
            # Simple range checks for absolute numbers
            numbers = re.findall(r'\d+', part)
            r_min, r_max = ranges[idx]
            for num in map(int, numbers):
                if num < r_min or num > r_max:
                    raise ValueError(f"Value '{num}' out of allowed range ({r_min}-{r_max}) for field {idx+1}.")
                    
        return value

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: str) -> str:
        val = value.upper()
        if val == "NORMAL":
            val = "MEDIUM"
        if val not in ["HIGH", "MEDIUM", "LOW"]:
            raise ValueError("Priority must be HIGH, MEDIUM, or LOW.")
        return val

    @field_validator("retry_policy")
    @classmethod
    def validate_retry_policy(cls, value: str) -> str:
        val = value.upper()
        if val not in ["EXPONENTIAL", "LINEAR", "IMMEDIATE"]:
            raise ValueError("Retry policy must be EXPONENTIAL, LINEAR, or IMMEDIATE.")
        return val

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    schedule_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    cron_expression: Optional[str] = Field(default=None)
    priority: Optional[str] = Field(default=None)
    max_retries: Optional[int] = Field(default=None, ge=0, le=10)
    timezone: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    retry_delay_minutes: Optional[int] = Field(default=None, ge=1, le=60)
    retry_policy: Optional[str] = Field(default=None)

    @field_validator("cron_expression")
    @classmethod
    def validate_cron(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return ScheduleBase.validate_cron(value)

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return ScheduleBase.validate_priority(value)

    @field_validator("retry_policy")
    @classmethod
    def validate_retry_policy(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return ScheduleBase.validate_retry_policy(value)

class ScheduleResponse(ScheduleBase):
    id: UUID
    status: str
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    brand_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class SchedulerStatusResponse(BaseModel):
    status: str
    queue_size: int
    worker_count: int
    active_jobs: int
    success_rate: float
    total_runs: int
    uptime_seconds: float

class SchedulerLogResponse(BaseModel):
    id: UUID
    schedule_id: Optional[UUID] = None
    job_id: Optional[UUID] = None
    brand_id: UUID
    brand_name: Optional[str] = None
    action: str
    status: str
    details: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
