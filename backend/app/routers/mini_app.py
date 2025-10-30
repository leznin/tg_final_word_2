"""
Mini app API router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.mini_app import (
    TelegramUserVerifyRequest,
    TelegramUserVerifyResponse,
    UserSearchRequest,
    UserSearchResponse
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
    """Search users by username, first name, or last name"""
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

    service = MiniAppService(db)
    return await service.search_users(request)
