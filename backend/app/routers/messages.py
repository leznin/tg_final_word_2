"""
Messages API router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.messages import MessageResponse
from app.services.messages import MessageService

router = APIRouter()


@router.get("/chat/{chat_id}", response_model=List[MessageResponse])
async def get_chat_messages(
    chat_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get messages from a specific chat"""
    message_service = MessageService(db)

    # Verify chat exists (optional - could be removed if not needed)
    # For now, we'll assume chat validation is done elsewhere

    messages = await message_service.get_chat_messages(chat_id, skip, limit)
    return messages


@router.get("/chat/{chat_id}/recent", response_model=List[MessageResponse])
async def get_recent_chat_messages(
    chat_id: int,
    hours: int = 24,
    db: AsyncSession = Depends(get_db)
):
    """Get recent messages from a chat within specified hours"""
    message_service = MessageService(db)
    messages = await message_service.get_recent_messages(chat_id, hours)
    return messages


@router.get("/chat/{chat_id}/count")
async def get_chat_message_count(
    chat_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get message count for a specific chat"""
    message_service = MessageService(db)
    count = await message_service.get_message_count(chat_id)
    return {"chat_id": chat_id, "message_count": count}


@router.get("/count")
async def get_total_message_count(
    db: AsyncSession = Depends(get_db)
):
    """Get total message count across all chats"""
    message_service = MessageService(db)
    count = await message_service.get_total_message_count()
    return {"total_messages": count}


@router.delete("/cleanup")
async def cleanup_old_messages(
    hours: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Delete messages older than specified hours. Default is 50 hours."""
    message_service = MessageService(db)
    deleted_count = await message_service.delete_old_messages(hours)
    return {
        "message": f"Deleted {deleted_count} messages older than {hours} hours",
        "deleted_count": deleted_count
    }
