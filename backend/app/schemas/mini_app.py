"""
Mini app Pydantic schemas
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TelegramUserVerifyRequest(BaseModel):
    """Schema for Telegram user verification from mini app"""
    init_data: str  # Telegram Web App initData for verification


class TelegramUserVerifyResponse(BaseModel):
    """Schema for Telegram user verification response"""
    verified: bool
    telegram_user_id: int
    message: str
    user_data: Optional[dict] = None


class UserSearchRequest(BaseModel):
    """Schema for user search request"""
    query: str
    limit: Optional[int] = 20
    offset: Optional[int] = 0


class UserSearchResult(BaseModel):
    """Schema for individual user search result"""
    id: int
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: bool = False
    is_bot: bool = False
    created_at: datetime
    updated_at: datetime


class UserSearchResponse(BaseModel):
    """Schema for user search response"""
    results: List[UserSearchResult]
    total: int
    limit: int
    offset: int
