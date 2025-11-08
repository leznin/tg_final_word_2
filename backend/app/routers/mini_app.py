"""
Mini app API router
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.config import settings
from app.models.users import User
from app.schemas.mini_app import (
    TelegramUserVerifyRequest,
    TelegramUserVerifyResponse,
    UserSearchRequest,
    UserSearchResponse,
    SearchLimitResponse
)
from app.services.mini_app import MiniAppService

router = APIRouter()


@router.post("/verify-user", response_model=TelegramUserVerifyResponse)
async def verify_telegram_user(
    request: TelegramUserVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify and create/update Telegram user from mini app data"""
    service = MiniAppService(db)
    return await service.verify_telegram_user(request)


@router.post("/search-users", response_model=UserSearchResponse)
async def search_users(
    request: UserSearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """Search users by username, first name, or last name with rate limiting (10 per day)"""
    if not request.query or len(request.query.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Search query must be at least 2 characters long"
        )

    if request.limit and (request.limit < 1 or request.limit > 100):
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100"
        )

    if request.offset and request.offset < 0:
        raise HTTPException(
            status_code=400,
            detail="Offset must be non-negative"
        )

    # Get user by telegram_user_id
    user_query = await db.execute(
        select(User).where(User.telegram_id == request.telegram_user_id)
    )
    user = user_query.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    service = MiniAppService(db)
    
    # Check if user has reached limit
    can_search, remaining = await service._check_search_limit(user.id)
    if not can_search:
        raise HTTPException(
            status_code=429,
            detail=f"Daily search limit reached. You can perform {MiniAppService.MAX_SEARCHES_PER_DAY} searches per day."
        )
    
    return await service.search_users(request, user.id)


@router.get("/search-limits/{telegram_user_id}", response_model=SearchLimitResponse)
async def get_search_limits(
    telegram_user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get current search limits for a user"""
    # Get user by telegram_user_id
    user_query = await db.execute(
        select(User).where(User.telegram_id == telegram_user_id)
    )
    user = user_query.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    service = MiniAppService(db)
    return await service.get_search_limits(user.id)


@router.get("/user-photo/{user_id}")
async def get_user_photo(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get user profile photo URL"""
    service = MiniAppService(db)
    file_path = await service.get_user_profile_photo(user_id)
    
    if not file_path:
        raise HTTPException(
            status_code=404,
            detail="User photo not found"
        )
    
    # Construct the full URL to the photo
    photo_url = f"https://api.telegram.org/file/bot{settings.TELEGRAM_BOT_TOKEN}/{file_path}"
    
    # Return redirect to the photo URL
    return RedirectResponse(url=photo_url)
