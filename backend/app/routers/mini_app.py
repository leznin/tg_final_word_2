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
    SearchLimitResponse,
    SearchBoostAvailabilityResponse,
    SearchBoostPriceResponse
)
from app.services.mini_app import MiniAppService
from app.services.search_boost import SearchBoostService
from aiogram import Bot
from aiogram.types import LabeledPrice

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


# Search Boost (Additional Searches) endpoints

@router.get("/search-boost/price", response_model=SearchBoostPriceResponse)
async def get_search_boost_price(
    db: AsyncSession = Depends(get_db)
):
    """Get current search boost price configuration"""
    service = SearchBoostService(db)
    price = await service.get_price_response()
    
    if not price:
        raise HTTPException(
            status_code=404,
            detail="Search boost price not configured"
        )
    
    return price


@router.get("/search-boost/availability/{telegram_user_id}", response_model=SearchBoostAvailabilityResponse)
async def check_boost_availability(
    telegram_user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Check if user can purchase more search boosts today (max 2 per day)"""
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
    
    service = SearchBoostService(db)
    return await service.check_purchase_availability(user.id)


@router.post("/search-boost/create-invoice/{telegram_user_id}")
async def create_boost_invoice(
    telegram_user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Create Telegram invoice for search boost purchase"""
    from fastapi import HTTPException
    
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
    
    # Check availability
    boost_service = SearchBoostService(db)
    availability = await boost_service.check_purchase_availability(user.id)
    
    if not availability.can_purchase:
        raise HTTPException(
            status_code=400,
            detail=availability.reason or "Cannot purchase more boosts today"
        )
    
    # Get price
    price = await boost_service.get_active_price()
    if not price:
        raise HTTPException(
            status_code=404,
            detail="Boost price not configured"
        )
    
    # Create invoice through bot
    try:
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        
        prices = [LabeledPrice(label="XTR", amount=price.price_stars)]
        payload = f"boost:{telegram_user_id}"
        
        invoice_link = await bot.create_invoice_link(
            title="Additional Searches",
            description=f"Get {price.boost_amount} additional user searches",
            prices=prices,
            provider_token="",  # Empty for Telegram Stars
            payload=payload,
            currency="XTR"
        )
        
        await bot.session.close()
        
        return {
            "invoice_link": invoice_link,
            "price_stars": price.price_stars,
            "boost_amount": price.boost_amount
        }
        
    except Exception as e:
        print(f"Error creating invoice: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create invoice"
        )
