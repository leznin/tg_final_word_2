"""
User verification schedule Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, time


class VerificationScheduleBase(BaseModel):
    """Base schema for verification schedule"""
    enabled: bool = Field(default=False, description="Whether the schedule is enabled")
    schedule_time: time = Field(description="Time to run verification (e.g., 02:00:00)")
    interval_hours: int = Field(default=24, ge=1, le=168, description="Run every X hours (1-168)")
    auto_update: bool = Field(default=True, description="Auto-update user data if changes detected")
    chat_id: Optional[int] = Field(None, description="Optional: filter by specific chat ID")


class VerificationScheduleCreate(VerificationScheduleBase):
    """Schema for creating a verification schedule"""
    pass


class VerificationScheduleUpdate(BaseModel):
    """Schema for updating a verification schedule"""
    enabled: Optional[bool] = None
    schedule_time: Optional[time] = None
    interval_hours: Optional[int] = Field(None, ge=1, le=168)
    auto_update: Optional[bool] = None
    chat_id: Optional[int] = None


class VerificationScheduleResponse(VerificationScheduleBase):
    """Schema for verification schedule response"""
    id: int
    created_at: datetime
    updated_at: datetime
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    
    # Include chat info if available
    chat_title: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "enabled": True,
                "schedule_time": "02:00:00",
                "interval_hours": 24,
                "auto_update": True,
                "chat_id": None,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "last_run_at": "2024-01-02T02:00:00Z",
                "next_run_at": "2024-01-03T02:00:00Z",
                "chat_title": None
            }
        }
