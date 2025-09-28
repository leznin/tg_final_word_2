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
    chat_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get chat detail by ID (internal ID or Telegram chat ID)"""
    from app.services.chat_moderators import ChatModeratorService

    chat_service = ChatService(db)
    moderator_service = ChatModeratorService(db)

    # Determine if chat_id is a Telegram chat ID (starts with "-" or is negative number)
    # or internal database ID
    try:
        chat_id_int = int(chat_id)
        if chat_id.startswith("-") or chat_id_int < 0:
            # This is a Telegram chat ID
            chat = await chat_service.get_chat_by_telegram_id(chat_id_int)
            actual_chat_id = chat.id if chat else None
        else:
            # This is an internal database ID
            chat = await chat_service.get_chat(chat_id_int)
            actual_chat_id = chat_id_int
    except ValueError:
        # If conversion to int fails, assume it's a Telegram chat ID string
        if chat_id.startswith("-"):
            try:
                telegram_chat_id = int(chat_id)
                chat = await chat_service.get_chat_by_telegram_id(telegram_chat_id)
                actual_chat_id = chat.id if chat else None
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid chat ID format")
        else:
            raise HTTPException(status_code=400, detail="Invalid chat ID format")

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Get moderators for this chat
    all_moderators = await ChatModeratorService(db).get_all_moderators_with_chat_info()
    moderators = [mod for mod in all_moderators if mod['chat_id'] == actual_chat_id]

    # Get channels linked to this chat (chats that have this chat as their linked_channel_id)
    linked_chats = await chat_service.get_chats_linked_to_channel(actual_chat_id)

    # Format channels to match frontend expectations
    channels = []
    for linked_chat in linked_chats:
        channel_info = {
            "id": linked_chat.id,
            "channel_id": linked_chat.telegram_chat_id,
            "admin_user_id": linked_chat.added_by_user_id,
            "created_date": linked_chat.added_at.isoformat() if linked_chat.added_at else ""
        }
        channels.append(channel_info)

    # Count linked channels for the chat info
    channel_count_result = await db.execute(
        select(func.count(Chat.id))
        .where(Chat.linked_channel_id == actual_chat_id)
        .where(Chat.is_active == True)
    )
    channel_count = channel_count_result.scalar() or 0

    # Get linked channel if exists
    linked_channel_data = None
    if chat.linked_channel_id:
        linked_channel = await chat_service.get_chat(chat.linked_channel_id)
        if linked_channel:
            # Get admin info for the linked channel
            from app.models.users import User
            admin_result = await db.execute(
                select(User).where(User.id == linked_channel.added_by_user_id)
            )
            admin = admin_result.scalar_one_or_none()

            linked_channel_data = {
                "id": linked_channel.id,
                "telegram_chat_id": linked_channel.telegram_chat_id,
                "title": linked_channel.title,
                "username": linked_channel.username,
                "admin_user_id": linked_channel.added_by_user_id,
                "admin_username": admin.username if admin else None,
                "admin_name": f"{admin.first_name or ''} {admin.last_name or ''}".strip() if admin else None
            }

    # Format chat data to match ChatDetail interface
    chat_data = {
        "id": chat.id,
        "chat_id": chat.telegram_chat_id,
        "chat_title": chat.title or "",
        "chat_type": chat.chat_type,
        "admin_user_id": chat.added_by_user_id,
        "added_date": chat.added_at.isoformat() if chat.added_at else "",
        "is_active": chat.is_active,
        "delete_messages_enabled": False,  # TODO: implement this feature
        "max_edit_time_minutes": chat.message_edit_timeout_minutes or 0,
        "linked_channel": linked_channel_data
    }

    return {
        "chat": chat_data,
        "moderators": moderators,
        "channels": channels
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
    chat_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Deactivate chat (mark as inactive)"""
    chat_service = ChatService(db)

    # Determine chat by ID type
    try:
        chat_id_int = int(chat_id)
        if chat_id.startswith("-") or chat_id_int < 0:
            chat = await chat_service.get_chat_by_telegram_id(chat_id_int)
        else:
            chat = await chat_service.get_chat(chat_id_int)
    except ValueError:
        if chat_id.startswith("-"):
            try:
                telegram_chat_id = int(chat_id)
                chat = await chat_service.get_chat_by_telegram_id(telegram_chat_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid chat ID format")
        else:
            raise HTTPException(status_code=400, detail="Invalid chat ID format")

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Deactivate the chat
    chat.is_active = False
    await db.commit()

    return {"message": "Chat deactivated successfully"}


@router.post("/{chat_id}/link-channel")
async def link_channel_to_chat(
    chat_id: str,
    request: LinkChannelRequest,
    db: AsyncSession = Depends(get_db)
):
    """Link a channel to a chat for message forwarding"""
    chat_service = ChatService(db)

    # Determine chat by ID type
    try:
        chat_id_int = int(chat_id)
        if chat_id.startswith("-") or chat_id_int < 0:
            chat = await chat_service.get_chat_by_telegram_id(chat_id_int)
            if chat:
                actual_chat_id = chat.id
            else:
                raise HTTPException(status_code=404, detail="Chat not found")
        else:
            actual_chat_id = chat_id_int
            chat = await chat_service.get_chat(actual_chat_id)
    except ValueError:
        if chat_id.startswith("-"):
            try:
                telegram_chat_id = int(chat_id)
                chat = await chat_service.get_chat_by_telegram_id(telegram_chat_id)
                if chat:
                    actual_chat_id = chat.id
                else:
                    raise HTTPException(status_code=404, detail="Chat not found")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid chat ID format")
        else:
            raise HTTPException(status_code=400, detail="Invalid chat ID format")

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Link channel to chat using internal ID
    success = await chat_service.link_channel_to_chat(actual_chat_id, request.channel_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to link channel. Channel may not exist or chat/channel validation failed")

    return {"message": "Channel linked successfully"}


@router.delete("/{chat_id}/link-channel")
async def unlink_channel_from_chat(
    chat_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Remove channel link from a chat"""
    chat_service = ChatService(db)

    # Determine chat by ID type
    try:
        chat_id_int = int(chat_id)
        if chat_id.startswith("-") or chat_id_int < 0:
            chat = await chat_service.get_chat_by_telegram_id(chat_id_int)
            if chat:
                actual_chat_id = chat.id
            else:
                raise HTTPException(status_code=404, detail="Chat not found")
        else:
            actual_chat_id = chat_id_int
            chat = await chat_service.get_chat(actual_chat_id)
    except ValueError:
        if chat_id.startswith("-"):
            try:
                telegram_chat_id = int(chat_id)
                chat = await chat_service.get_chat_by_telegram_id(telegram_chat_id)
                if chat:
                    actual_chat_id = chat.id
                else:
                    raise HTTPException(status_code=404, detail="Chat not found")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid chat ID format")
        else:
            raise HTTPException(status_code=400, detail="Invalid chat ID format")

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Unlink channel from chat using internal ID
    success = await chat_service.unlink_channel_from_chat(actual_chat_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to unlink channel")

    return {"message": "Channel unlinked successfully"}


@router.get("/{chat_id}/linked-channel")
async def get_linked_channel(
    chat_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the linked channel for a chat"""
    chat_service = ChatService(db)

    # Determine chat by ID type
    try:
        chat_id_int = int(chat_id)
        if chat_id.startswith("-") or chat_id_int < 0:
            chat = await chat_service.get_chat_by_telegram_id(chat_id_int)
            if chat:
                actual_chat_id = chat.id
            else:
                raise HTTPException(status_code=404, detail="Chat not found")
        else:
            actual_chat_id = chat_id_int
            chat = await chat_service.get_chat(actual_chat_id)
    except ValueError:
        if chat_id.startswith("-"):
            try:
                telegram_chat_id = int(chat_id)
                chat = await chat_service.get_chat_by_telegram_id(telegram_chat_id)
                if chat:
                    actual_chat_id = chat.id
                else:
                    raise HTTPException(status_code=404, detail="Chat not found")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid chat ID format")
        else:
            raise HTTPException(status_code=400, detail="Invalid chat ID format")

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Get linked channel using internal ID
    linked_channel = await chat_service.get_linked_channel(actual_chat_id)
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
