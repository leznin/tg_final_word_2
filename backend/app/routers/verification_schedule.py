"""
User verification schedule API router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.user_verification_schedule import (
    VerificationScheduleCreate,
    VerificationScheduleUpdate,
    VerificationScheduleResponse
)
from app.services.user_verification_schedule import VerificationScheduleService

router = APIRouter()


@router.post("/schedules", response_model=VerificationScheduleResponse)
async def create_schedule(
    schedule_data: VerificationScheduleCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new verification schedule
    
    Args:
        schedule_data: Schedule configuration
        
    Returns:
        Created schedule
    """
    schedule_service = VerificationScheduleService(db)
    schedule = await schedule_service.create_schedule(schedule_data)
    return await schedule_service.to_response(schedule)


@router.get("/schedules", response_model=List[VerificationScheduleResponse])
async def get_all_schedules(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all verification schedules
    
    Returns:
        List of all schedules
    """
    schedule_service = VerificationScheduleService(db)
    schedules = await schedule_service.get_all_schedules()
    return [await schedule_service.to_response(s) for s in schedules]


@router.get("/schedules/{schedule_id}", response_model=VerificationScheduleResponse)
async def get_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific verification schedule
    
    Args:
        schedule_id: Schedule ID
        
    Returns:
        Schedule details
    """
    schedule_service = VerificationScheduleService(db)
    schedule = await schedule_service.get_schedule(schedule_id)
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return await schedule_service.to_response(schedule)


@router.put("/schedules/{schedule_id}", response_model=VerificationScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_data: VerificationScheduleUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a verification schedule
    
    Args:
        schedule_id: Schedule ID
        schedule_data: Updated schedule data
        
    Returns:
        Updated schedule
    """
    schedule_service = VerificationScheduleService(db)
    schedule = await schedule_service.update_schedule(schedule_id, schedule_data)
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return await schedule_service.to_response(schedule)


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a verification schedule
    
    Args:
        schedule_id: Schedule ID
        
    Returns:
        Success message
    """
    schedule_service = VerificationScheduleService(db)
    success = await schedule_service.delete_schedule(schedule_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return {"message": "Schedule deleted successfully"}


@router.post("/schedules/{schedule_id}/toggle")
async def toggle_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Toggle schedule enabled/disabled status
    
    Args:
        schedule_id: Schedule ID
        
    Returns:
        Updated schedule
    """
    schedule_service = VerificationScheduleService(db)
    schedule = await schedule_service.get_schedule(schedule_id)
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Toggle enabled status
    update_data = VerificationScheduleUpdate(enabled=not schedule.enabled)
    schedule = await schedule_service.update_schedule(schedule_id, update_data)
    
    return await schedule_service.to_response(schedule)
