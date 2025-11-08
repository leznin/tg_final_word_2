"""
Mini app Pydantic schemas
"""

from pydantic import BaseModel
from typing import Optional, List, Union
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
    session_token: Optional[str] = None  # Session token for frontend


class UserSearchRequest(BaseModel):
    """Schema for user search request"""
    query: str
    limit: Optional[int] = 20
    offset: Optional[int] = 0


class UserHistoryEntry(BaseModel):
    """Schema for user history entry"""
    id: int
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_at: datetime


class UserSearchResult(BaseModel):
    """Schema for individual user search result"""
    telegram_user_id: Union[int, str]  # Can be int or masked string
    real_telegram_user_id: Optional[int] = None  # Real ID for masked accounts
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: bool = False
    is_bot: bool = False
    account_creation_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    history: List[UserHistoryEntry] = []


class UserSearchResponse(BaseModel):
    """Schema for user search response"""
    results: List[UserSearchResult]
    total: int
    limit: int
    offset: int
