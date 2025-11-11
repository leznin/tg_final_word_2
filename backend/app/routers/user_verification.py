"""
User verification API router
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.schemas.user_verification import (
    UserVerificationRequest,
    UserVerificationResult,
    BulkVerificationRequest,
    BulkVerificationResponse,
    ActiveUsersListResponse
)
from app.services.user_verification import UserVerificationService
from app.services.chats import ChatService

router = APIRouter()

# Global verification service instance for progress tracking
_verification_service_instance: Optional[UserVerificationService] = None


def get_telegram_bot():
    """Get telegram bot instance"""
    from app.main import get_telegram_bot as get_bot
    return get_bot()


def get_verification_service(db: AsyncSession = Depends(get_db)) -> UserVerificationService:
    """Get or create verification service instance"""
    global _verification_service_instance
    telegram_bot = get_telegram_bot()
    
    if not telegram_bot or not telegram_bot.is_running:
        raise HTTPException(status_code=503, detail="Telegram bot is not available")
    
    # Always create new instance with current db session
    # but reuse the same instance for progress tracking during a verification run
    if _verification_service_instance is None or not _verification_service_instance.is_running:
        _verification_service_instance = UserVerificationService(telegram_bot.bot, db)
    
    return _verification_service_instance


@router.post("/verify-user", response_model=UserVerificationResult)
async def verify_single_user(
    request: UserVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify a single user's information using Telegram API getChatMember
    
    This endpoint checks if the user's stored username
    matches the current data from Telegram API. If auto_update is True, it will
    automatically update the database and record changes in history.
    
    Args:
        request: UserVerificationRequest with telegram_user_id, chat_id, and auto_update flag
        
    Returns:
        UserVerificationResult with verification details and any detected changes
    """
    # Get telegram bot instance
    telegram_bot = get_telegram_bot()
    if not telegram_bot or not telegram_bot.is_running:
        raise HTTPException(status_code=503, detail="Telegram bot is not available")

    # Get chat information to convert DB chat_id to telegram_chat_id
    chat_service = ChatService(db)
    chat = await chat_service.get_chat(request.chat_id)
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Create verification service
    verification_service = UserVerificationService(telegram_bot.bot, db)

    # Verify user
    result = await verification_service.verify_user_info(
        telegram_user_id=request.telegram_user_id,
        telegram_chat_id=chat.telegram_chat_id,
        auto_update=request.auto_update
    )

    return result


@router.post("/verify-active-users", response_model=BulkVerificationResponse)
async def verify_active_users(
    request: BulkVerificationRequest,
    background_tasks: BackgroundTasks,
    verification_service: UserVerificationService = Depends(get_verification_service)
):
    """
    Verify multiple active users using Telegram API getChatMember
    
    This endpoint checks all active users in the specified chat (or all chats if not specified).
    It uses the chat_members table to find where users are active and verifies their information.
    
    Args:
        request: BulkVerificationRequest with optional chat_id filter and auto_update flag
        
    Returns:
        BulkVerificationResponse with statistics and detailed results for each user
    """
    # Verify users
    result = await verification_service.verify_all_active_users(
        chat_id=request.chat_id,
        telegram_user_ids=request.telegram_user_ids,
        auto_update=request.auto_update,
        delay_between_requests=request.delay_between_requests
    )

    return result


@router.get("/active-users", response_model=ActiveUsersListResponse)
async def get_active_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of active users with their active chats
    
    This endpoint returns all users who are currently active in at least one chat,
    along with information about which chats they're in. This is useful for
    selecting which users to verify.
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        ActiveUsersListResponse with list of active users and their chats
    """
    # Get telegram bot instance (just to check if it's available)
    telegram_bot = get_telegram_bot()
    if not telegram_bot or not telegram_bot.is_running:
        raise HTTPException(status_code=503, detail="Telegram bot is not available")

    # Create verification service
    verification_service = UserVerificationService(telegram_bot.bot, db)

    # Get active users
    result = await verification_service.get_active_users_with_chats(skip=skip, limit=limit)

    return result


@router.get("/chats")
async def get_available_chats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of all available chats
    
    Returns a list of chats that can be used for user verification.
    
    Returns:
        List of chats with id, telegram_chat_id, title, and chat_type
    """
    chat_service = ChatService(db)
    chats = await chat_service.get_all_chats(skip=0, limit=1000)
    
    return {
        "chats": [
            {
                "id": chat.id,
                "telegram_chat_id": chat.telegram_chat_id,
                "title": chat.title or f"Chat {chat.telegram_chat_id}",
                "chat_type": chat.chat_type,
                "is_active": chat.is_active
            }
            for chat in chats
            if chat.is_active
        ]
    }


@router.get("/status")
async def get_verification_status():
    """
    Get current verification progress status
    
    Returns current status of verification process including:
    - is_running: whether verification is currently running
    - current_progress: number of users checked so far
    - total_users: total number of users to check
    - progress_percentage: completion percentage
    - estimated_time_remaining: estimated seconds until completion
    
    This endpoint can be polled while verification is running to show progress.
    """
    global _verification_service_instance
    
    if _verification_service_instance is None:
        return {
            "is_running": False,
            "current_progress": 0,
            "total_users": 0,
            "checked_users": 0,
            "updated_users": 0,
            "users_with_changes": 0,
            "users_with_errors": 0,
            "progress_percentage": 0,
            "estimated_time_remaining": None,
            "started_at": None
        }
    
    return _verification_service_instance.get_status()
