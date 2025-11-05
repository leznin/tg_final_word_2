"""
User verification schedule service
"""

from typing import Optional, List
from datetime import datetime, timedelta, time as dt_time, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models.user_verification_schedule import UserVerificationSchedule
from app.models.chats import Chat
from app.schemas.user_verification_schedule import (
    VerificationScheduleCreate,
    VerificationScheduleUpdate,
    VerificationScheduleResponse
)


class VerificationScheduleService:
    """Service for managing user verification schedules"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_schedule(
        self, 
        schedule_data: VerificationScheduleCreate
    ) -> UserVerificationSchedule:
        """Create a new verification schedule"""
        # Calculate next run time
        next_run = self._calculate_next_run(
            schedule_data.schedule_time,
            schedule_data.interval_hours
        )

        schedule = UserVerificationSchedule(
            enabled=schedule_data.enabled,
            schedule_time=schedule_data.schedule_time,
            interval_hours=schedule_data.interval_hours,
            auto_update=schedule_data.auto_update,
            chat_id=schedule_data.chat_id,
            next_run_at=next_run
        )

        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)

        return schedule

    async def get_schedule(self, schedule_id: int) -> Optional[UserVerificationSchedule]:
        """Get schedule by ID"""
        query = (
            select(UserVerificationSchedule)
            .options(joinedload(UserVerificationSchedule.chat))
            .where(UserVerificationSchedule.id == schedule_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_schedules(self) -> List[UserVerificationSchedule]:
        """Get all verification schedules"""
        query = (
            select(UserVerificationSchedule)
            .options(joinedload(UserVerificationSchedule.chat))
            .order_by(UserVerificationSchedule.id)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_enabled_schedules(self) -> List[UserVerificationSchedule]:
        """Get all enabled verification schedules"""
        query = (
            select(UserVerificationSchedule)
            .options(joinedload(UserVerificationSchedule.chat))
            .where(UserVerificationSchedule.enabled == True)
            .order_by(UserVerificationSchedule.id)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_schedule(
        self,
        schedule_id: int,
        schedule_data: VerificationScheduleUpdate
    ) -> Optional[UserVerificationSchedule]:
        """Update verification schedule"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return None

        # Update fields
        update_dict = schedule_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(schedule, field, value)

        # Recalculate next run time if schedule_time or interval_hours changed
        if 'schedule_time' in update_dict or 'interval_hours' in update_dict:
            schedule.next_run_at = self._calculate_next_run(
                schedule.schedule_time,
                schedule.interval_hours
            )

        schedule.updated_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(schedule)

        return schedule

    async def delete_schedule(self, schedule_id: int) -> bool:
        """Delete verification schedule"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return False

        await self.db.delete(schedule)
        await self.db.commit()
        return True

    async def update_last_run(
        self,
        schedule_id: int,
        last_run_at: datetime
    ) -> Optional[UserVerificationSchedule]:
        """Update last run timestamp and calculate next run"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return None

        schedule.last_run_at = last_run_at
        schedule.next_run_at = self._calculate_next_run(
            schedule.schedule_time,
            schedule.interval_hours,
            from_datetime=last_run_at
        )
        
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    async def get_schedules_to_run(self) -> List[UserVerificationSchedule]:
        """Get schedules that should run now"""
        current_time = datetime.now()  # Use local time instead of UTC
        
        query = (
            select(UserVerificationSchedule)
            .options(joinedload(UserVerificationSchedule.chat))
            .where(
                UserVerificationSchedule.enabled == True,
                UserVerificationSchedule.next_run_at <= current_time
            )
            .order_by(UserVerificationSchedule.id)
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    def _calculate_next_run(
        self,
        schedule_time: dt_time,
        interval_hours: int,
        from_datetime: Optional[datetime] = None
    ) -> datetime:
        """Calculate next run time based on schedule time and interval"""
        # Use local time instead of UTC to match user's timezone
        base_datetime = from_datetime or datetime.now()
        
        # If we have a last run time, calculate from it
        if from_datetime is not None:
            # Simply add interval_hours to the last run time
            return from_datetime + timedelta(hours=interval_hours)
        
        # For initial schedule creation, find next occurrence of schedule_time
        today = base_datetime.date()
        scheduled_datetime = datetime.combine(today, schedule_time)
        
        # If scheduled time has passed today, move to tomorrow's scheduled time
        if scheduled_datetime <= base_datetime:
            # Move to next day's scheduled time
            tomorrow = today + timedelta(days=1)
            scheduled_datetime = datetime.combine(tomorrow, schedule_time)
        
        return scheduled_datetime

    async def to_response(
        self,
        schedule: UserVerificationSchedule
    ) -> VerificationScheduleResponse:
        """Convert schedule model to response schema"""
        response_data = {
            "id": schedule.id,
            "enabled": schedule.enabled,
            "schedule_time": schedule.schedule_time,
            "interval_hours": schedule.interval_hours,
            "auto_update": schedule.auto_update,
            "chat_id": schedule.chat_id,
            "created_at": schedule.created_at,
            "updated_at": schedule.updated_at,
            "last_run_at": schedule.last_run_at,
            "next_run_at": schedule.next_run_at,
            "chat_title": schedule.chat.title if schedule.chat else None
        }
        
        return VerificationScheduleResponse(**response_data)
