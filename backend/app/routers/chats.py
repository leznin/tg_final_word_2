"""
Chats API router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.core.database import get_db
from app.schemas.chats import ChatResponse, ChatWithUserResponse, LinkChannelRequest, ChatWithLinkedChannelResponse
from app.services.chats import ChatService
from app.models.chats import Chat

router = APIRouter()


@router.get("/")
async def get_chats(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all active chats (groups and supergroups) with linked channel information"""
    chat_service = ChatService(db)
    chats = await chat_service.get_chats_with_linked_channels_info(skip, limit)

    return {"chats": chats}


@router.get("/by-user/{user_id}")
async def get_chats_by_user(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all chats added by a specific user"""
    chat_service = ChatService(db)
    chats = await chat_service.get_chats_by_user(user_id, skip, limit)

    # Convert to the format expected by frontend
    chats_data = []
    for chat in chats:
        # Count linked channels
        channel_count_result = await db.execute(
            select(func.count(Chat.id))
            .where(Chat.linked_channel_id == chat.id)
            .where(Chat.is_active == True)
        )
        channel_count = channel_count_result.scalar() or 0

        chat_data = {
            "id": chat.id,
            "chat_id": chat.telegram_chat_id,
            "chat_title": chat.title or "",
            "chat_type": chat.chat_type,
            "admin_user_id": chat.added_by_user_id,
            "added_date": chat.added_at.isoformat() if chat.added_at else "",
            "delete_messages_enabled": False,  # TODO: implement this feature
            "max_edit_time_minutes": chat.message_edit_timeout_minutes or 0,
            "channel_count": channel_count,
            "linked_channel_id": chat.linked_channel_id,
        }
        chats_data.append(chat_data)

    return chats_data


@router.get("/{chat_id}")
async def get_chat(
    chat_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get chat by ID"""
    chat_service = ChatService(db)
    chat = await chat_service.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Count linked channels
    channel_count_result = await db.execute(
        select(func.count(Chat.id))
        .where(Chat.linked_channel_id == chat.id)
        .where(Chat.is_active == True)
    )
    channel_count = channel_count_result.scalar() or 0

    return {
        "id": chat.id,
        "chat_id": chat.telegram_chat_id,
        "chat_title": chat.title or "",
        "chat_type": chat.chat_type,
        "admin_user_id": chat.added_by_user_id,
        "added_date": chat.added_at.isoformat() if chat.added_at else "",
        "delete_messages_enabled": False,  # TODO: implement this feature
        "max_edit_time_minutes": chat.message_edit_timeout_minutes or 0,
        "channel_count": channel_count,
        "linked_channel_id": chat.linked_channel_id,
    }


@router.get("/telegram/{telegram_chat_id}")
async def get_chat_by_telegram_id(
    telegram_chat_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get chat by Telegram chat ID"""
    chat_service = ChatService(db)
    chat = await chat_service.get_chat_by_telegram_id(telegram_chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Count linked channels
    channel_count_result = await db.execute(
        select(func.count(Chat.id))
        .where(Chat.linked_channel_id == chat.id)
        .where(Chat.is_active == True)
    )
    channel_count = channel_count_result.scalar() or 0

    return {
        "id": chat.id,
        "chat_id": chat.telegram_chat_id,
        "chat_title": chat.title or "",
        "chat_type": chat.chat_type,
        "admin_user_id": chat.added_by_user_id,
        "added_date": chat.added_at.isoformat() if chat.added_at else "",
        "delete_messages_enabled": False,  # TODO: implement this feature
        "max_edit_time_minutes": chat.message_edit_timeout_minutes or 0,
        "channel_count": channel_count,
        "linked_channel_id": chat.linked_channel_id,
    }


@router.delete("/{chat_id}")
async def deactivate_chat(
    chat_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Deactivate chat (mark as inactive)"""
    chat_service = ChatService(db)
    chat = await chat_service.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Deactivate the chat
    chat.is_active = False
    await db.commit()

    return {"message": "Chat deactivated successfully"}


@router.post("/{chat_id}/link-channel")
async def link_channel_to_chat(
    chat_id: int,
    request: LinkChannelRequest,
    db: AsyncSession = Depends(get_db)
):
    """Link a channel to a chat for message forwarding"""
    chat_service = ChatService(db)

    # Verify chat exists
    chat = await chat_service.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Link channel to chat
    success = await chat_service.link_channel_to_chat(chat_id, request.channel_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to link channel. Channel may not exist or chat/channel validation failed")

    return {"message": "Channel linked successfully"}


@router.delete("/{chat_id}/link-channel")
async def unlink_channel_from_chat(
    chat_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Remove channel link from a chat"""
    chat_service = ChatService(db)

    # Verify chat exists
    chat = await chat_service.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Unlink channel from chat
    success = await chat_service.unlink_channel_from_chat(chat_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to unlink channel")

    return {"message": "Channel unlinked successfully"}


@router.get("/{chat_id}/linked-channel")
async def get_linked_channel(
    chat_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get the linked channel for a chat"""
    chat_service = ChatService(db)

    # Verify chat exists
    chat = await chat_service.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Get linked channel
    linked_channel = await chat_service.get_linked_channel(chat_id)
    if not linked_channel:
        raise HTTPException(status_code=404, detail="No linked channel found")

    # Count linked channels
    channel_count_result = await db.execute(
        select(func.count(Chat.id))
        .where(Chat.linked_channel_id == linked_channel.id)
        .where(Chat.is_active == True)
    )
    channel_count = channel_count_result.scalar() or 0

    return {
        "id": linked_channel.id,
        "chat_id": linked_channel.telegram_chat_id,
        "chat_title": linked_channel.title or "",
        "chat_type": linked_channel.chat_type,
        "admin_user_id": linked_channel.added_by_user_id,
        "added_date": linked_channel.added_at.isoformat() if linked_channel.added_at else "",
        "delete_messages_enabled": False,  # TODO: implement this feature
        "max_edit_time_minutes": linked_channel.message_edit_timeout_minutes or 0,
        "channel_count": channel_count,
        "linked_channel_id": linked_channel.linked_channel_id,
    }


@router.get("/user/{user_id}/available-channels")
async def get_available_channels_for_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all available channels for a user to link to their chats"""
    chat_service = ChatService(db)
    channels = await chat_service.get_available_channels_for_user(user_id)

    # Convert to the format expected by frontend
    channels_data = []
    for channel in channels:
        # Count linked channels
        channel_count_result = await db.execute(
            select(func.count(Chat.id))
            .where(Chat.linked_channel_id == channel.id)
            .where(Chat.is_active == True)
        )
        channel_count = channel_count_result.scalar() or 0

        channel_data = {
            "id": channel.id,
            "chat_id": channel.telegram_chat_id,
            "chat_title": channel.title or "",
            "chat_type": channel.chat_type,
            "admin_user_id": channel.added_by_user_id,
            "added_date": channel.added_at.isoformat() if channel.added_at else "",
            "delete_messages_enabled": False,  # TODO: implement this feature
            "max_edit_time_minutes": channel.message_edit_timeout_minutes or 0,
            "channel_count": channel_count,
            "linked_channel_id": channel.linked_channel_id,
        }
        channels_data.append(channel_data)

    return channels_data
