"""
Chat moderators API router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.chat_moderators import (
    ChatModeratorResponse,
    ChatModeratorCreate,
    ChatModeratorUpdate,
    ChatModeratorWithUserResponse
)
from app.services.chat_moderators import ChatModeratorService

router = APIRouter()


@router.get("/chat/{chat_id}", response_model=List[ChatModeratorWithUserResponse])
async def get_chat_moderators(
    chat_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all moderators for a specific chat"""
    moderator_service = ChatModeratorService(db)

    # Check if user can manage moderators for this chat
    # This will be validated in the service methods

    moderators = await moderator_service.get_chat_moderators(chat_id)
    return moderators


@router.post("/", response_model=ChatModeratorResponse)
async def create_moderator(
    moderator_data: ChatModeratorCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat moderator"""
    moderator_service = ChatModeratorService(db)

    # Check if user can manage moderators for this chat
    can_manage = await moderator_service.can_user_manage_moderators(
        moderator_data.chat_id,
        moderator_data.added_by_user_id
    )
    if not can_manage:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to manage moderators for this chat"
        )

    moderator = await moderator_service.create_moderator(moderator_data)
    return moderator


@router.put("/{moderator_id}", response_model=ChatModeratorResponse)
async def update_moderator(
    moderator_id: int,
    moderator_data: ChatModeratorUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a chat moderator"""
    moderator_service = ChatModeratorService(db)

    # Get current moderator to check permissions
    current_moderator = await moderator_service.get_moderator(moderator_id)
    if not current_moderator:
        raise HTTPException(status_code=404, detail="Moderator not found")

    # Check if user can manage moderators for this chat
    # Note: We would need to pass the user_id from authentication
    # For now, we'll assume the permission check happens at the service level

    updated_moderator = await moderator_service.update_moderator(moderator_id, moderator_data)
    if not updated_moderator:
        raise HTTPException(status_code=404, detail="Moderator not found")

    return updated_moderator


@router.delete("/{moderator_id}")
async def delete_moderator(
    moderator_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a chat moderator"""
    moderator_service = ChatModeratorService(db)

    # Get current moderator to check permissions
    current_moderator = await moderator_service.get_moderator(moderator_id)
    if not current_moderator:
        raise HTTPException(status_code=404, detail="Moderator not found")

    # Check if user can manage moderators for this chat
    # Note: We would need to pass the user_id from authentication

    success = await moderator_service.remove_moderator(moderator_id)
    if not success:
        raise HTTPException(status_code=404, detail="Moderator not found")

    return {"message": "Moderator removed successfully"}


@router.delete("/chat/{chat_id}/user/{moderator_user_id}")
async def remove_moderator_by_user(
    chat_id: int,
    moderator_user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Remove moderator by chat and user ID"""
    moderator_service = ChatModeratorService(db)

    # Check if user can manage moderators for this chat
    # Note: We would need to pass the user_id from authentication

    success = await moderator_service.remove_moderator_by_user(chat_id, moderator_user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Moderator not found")

    return {"message": "Moderator removed successfully"}


@router.get("/user/{moderator_user_id}/chats", response_model=List[ChatModeratorResponse])
async def get_user_moderator_chats(
    moderator_user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all chats where user is a moderator"""
    moderator_service = ChatModeratorService(db)
    moderators = await moderator_service.get_user_moderator_chats(moderator_user_id)
    return moderators


@router.get("/chat/{chat_id}/user/{moderator_user_id}/check")
async def check_user_is_moderator(
    chat_id: int,
    moderator_user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Check if user is a moderator in the chat"""
    moderator_service = ChatModeratorService(db)
    is_moderator = await moderator_service.is_user_moderator(chat_id, moderator_user_id)
    return {"is_moderator": is_moderator}
