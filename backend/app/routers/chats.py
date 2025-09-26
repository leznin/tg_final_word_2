"""
Chats API router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.chats import ChatResponse, ChatWithUserResponse, LinkChannelRequest
from app.services.chats import ChatService

router = APIRouter()


@router.get("/", response_model=List[ChatWithUserResponse])
async def get_chats(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all active chats with pagination"""
    chat_service = ChatService(db)
    chats = await chat_service.get_all_chats(skip, limit)
    return chats


@router.get("/by-user/{user_id}", response_model=List[ChatResponse])
async def get_chats_by_user(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all chats added by a specific user"""
    chat_service = ChatService(db)
    chats = await chat_service.get_chats_by_user(user_id, skip, limit)
    return chats


@router.get("/{chat_id}", response_model=ChatWithUserResponse)
async def get_chat(
    chat_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get chat by ID"""
    chat_service = ChatService(db)
    chat = await chat_service.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.get("/telegram/{telegram_chat_id}", response_model=ChatWithUserResponse)
async def get_chat_by_telegram_id(
    telegram_chat_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get chat by Telegram chat ID"""
    chat_service = ChatService(db)
    chat = await chat_service.get_chat_by_telegram_id(telegram_chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


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


@router.get("/{chat_id}/linked-channel", response_model=ChatResponse)
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

    return linked_channel


@router.get("/user/{user_id}/available-channels", response_model=List[ChatResponse])
async def get_available_channels_for_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all available channels for a user to link to their chats"""
    chat_service = ChatService(db)
    channels = await chat_service.get_available_channels_for_user(user_id)
    return channels
