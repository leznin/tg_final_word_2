"""
Chat information API router
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.chat_info import ChatInfoResponse, BulkChatInfoResponse
from app.telegram.services.chat_info import ChatInfoService

router = APIRouter()


@router.get("/chat/{telegram_chat_id}", response_model=ChatInfoResponse)
async def get_chat_info(
    telegram_chat_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific chat from Telegram API
    Note: In production, consider adding proper authentication.
    """
    # Import bot here to avoid circular imports
    from app.main import get_telegram_bot

    telegram_bot = get_telegram_bot()
    if not telegram_bot or not telegram_bot.is_running:
        raise HTTPException(status_code=503, detail="Telegram bot is not available")

    # Create service instance
    chat_info_service = ChatInfoService(telegram_bot.bot, db)

    # Get all chats to find the owner of this chat
    from app.services.chats import ChatService
    chat_service = ChatService(db)
    chat = await chat_service.get_chat_by_telegram_id(telegram_chat_id)

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Get user's telegram_id directly from the relationship ID
    from app.services.users import UserService
    user_service = UserService(db)
    user = await user_service.get_user(chat.added_by_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Chat owner not found")

    # Get chat information using the chat owner's telegram_id
    success, error_message, chat_info = await chat_info_service.get_chat_info(
        telegram_chat_id, user.telegram_id
    )

    if not success:
        raise HTTPException(status_code=400, detail=error_message)

    # Update chat information in database
    if chat_info:
        from datetime import datetime
        update_data = {
            "member_count": chat_info.member_count,
            "description": chat_info.description,
            "invite_link": chat_info.invite_link,
            "bot_permissions": chat_info.bot_permissions.model_dump() if chat_info.bot_permissions else None,
            "last_info_update": datetime.utcnow()
        }

        # Get chat from database and update
        chat = await chat_info_service.chat_service.get_chat_by_telegram_id(telegram_chat_id)
        if chat:
            for key, value in update_data.items():
                setattr(chat, key, value)
            await db.commit()
            await db.refresh(chat)

    return chat_info


@router.post("/chats/bulk-info", response_model=BulkChatInfoResponse)
async def get_all_chats_info(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Get information about all chats from Telegram API
    Note: This endpoint works with all chats in the database.
    In production, consider adding proper authentication.
    """
    # Import bot here to avoid circular imports
    from app.main import get_telegram_bot

    telegram_bot = get_telegram_bot()
    if not telegram_bot or not telegram_bot.is_running:
        raise HTTPException(status_code=503, detail="Telegram bot is not available")

    # Create service instance
    chat_info_service = ChatInfoService(telegram_bot.bot, db)

    # Get all chats from database and group by owner
    from app.services.chats import ChatService
    from app.services.users import UserService
    chat_service = ChatService(db)
    user_service = UserService(db)

    all_chats = await chat_service.get_all_chats()

    if not all_chats:
        return BulkChatInfoResponse(
            chats_info=[],
            total_chats=0,
            successful_requests=0,
            failed_requests=0,
            errors=[{"error": "No chats found in database"}]
        )

    # Group chats by their owners
    chats_by_owner = {}
    for chat in all_chats:
        owner_id = chat.added_by_user_id
        if owner_id not in chats_by_owner:
            chats_by_owner[owner_id] = []
        chats_by_owner[owner_id].append(chat)

    # Process chats for each owner
    all_results = []
    total_chats_processed = 0

    for owner_id, owner_chats in chats_by_owner.items():
        # Get user info
        user = await user_service.get_user(owner_id)
        if not user:
            continue

        # Get information for this owner's chats
        result = await chat_info_service.get_all_chats_info(user.telegram_id)
        all_results.append(result)
        total_chats_processed += result.total_chats

    # Combine all results
    combined_chats_info = []
    combined_errors = []
    total_successful = 0
    total_failed = 0

    for result in all_results:
        combined_chats_info.extend(result.chats_info)
        combined_errors.extend(result.errors)
        total_successful += result.successful_requests
        total_failed += result.failed_requests

    result = BulkChatInfoResponse(
        chats_info=combined_chats_info,
        total_chats=total_chats_processed,
        successful_requests=total_successful,
        failed_requests=total_failed,
        errors=combined_errors
    )

    # Update successful chats in database
    from datetime import datetime
    for chat_info in result.chats_info:
        try:
            update_data = {
                "member_count": chat_info.member_count,
                "description": chat_info.description,
                "invite_link": chat_info.invite_link,
                "bot_permissions": chat_info.bot_permissions.model_dump() if chat_info.bot_permissions else None,
                "last_info_update": datetime.utcnow()
            }

            # Get chat from database and update
            chat = await chat_info_service.chat_service.get_chat_by_telegram_id(chat_info.telegram_chat_id)
            if chat:
                for key, value in update_data.items():
                    setattr(chat, key, value)
        except Exception as e:
            print(f"Error updating chat {chat_info.telegram_chat_id}: {e}")

    # Commit all changes
    try:
        await db.commit()
    except Exception as e:
        print(f"Error committing chat updates: {e}")
        await db.rollback()

    return result
