"""
Admin chats API router for admin panel
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from app.core.database import get_db
from app.services.admin_chats import AdminChatsService

router = APIRouter()


@router.get("/", response_model=List[Dict[str, Any]])
async def get_admin_chats(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all chats with statistics for admin panel"""
    admin_chats_service = AdminChatsService(db)
    chats = await admin_chats_service.get_all_chats_with_stats()

    # Apply pagination
    start_idx = skip
    end_idx = skip + limit
    return chats[start_idx:end_idx]


@router.get("/stats", response_model=Dict[str, int])
async def get_chats_stats(db: AsyncSession = Depends(get_db)):
    """Get chat statistics summary for admin panel"""
    admin_chats_service = AdminChatsService(db)
    return await admin_chats_service.get_chat_stats_summary()


@router.get("/{chat_id}", response_model=Dict[str, Any])
async def get_admin_chat_detail(
    chat_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed chat information for admin panel"""
    admin_chats_service = AdminChatsService(db)
    chat_detail = await admin_chats_service.get_chat_detail_for_admin(chat_id)

    if not chat_detail:
        raise HTTPException(status_code=404, detail="Chat not found")

    return chat_detail
