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
    telegram_user_id: int  # User performing the search


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


class SearchLimitResponse(BaseModel):
    """Schema for search limit information"""
    total_searches_today: int
    max_searches_per_day: int
    remaining_searches: int
    reset_time: datetime  # When the limit will reset
    boost_searches_available: int = 0  # Additional searches available from purchases
    can_purchase_boost: bool = True  # Whether user can buy more boosts today


class SearchStatsEntry(BaseModel):
    """Schema for individual search statistics entry"""
    user_id: int
    telegram_user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    total_searches: int
    last_search_at: datetime
    searches_today: int


class SearchStatsResponse(BaseModel):
    """Schema for admin search statistics response"""
    total_users: int
    total_searches_all_time: int
    total_searches_today: int
    stats: List[SearchStatsEntry]


# Search Boost (Additional Searches) Schemas

class SearchBoostPriceResponse(BaseModel):
    """Schema for search boost price information"""
    id: int
    boost_amount: int  # Number of additional searches (default: 10)
    price_stars: int  # Price in Telegram Stars
    currency: str = 'XTR'
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SearchBoostPriceUpdate(BaseModel):
    """Schema for updating search boost price"""
    price_stars: int


class SearchBoostAvailabilityResponse(BaseModel):
    """Schema for checking if user can purchase more boosts"""
    can_purchase: bool
    purchases_today: int
    max_purchases_per_day: int = 2
    remaining_purchases: int
    reason: Optional[str] = None


class SearchBoostPurchaseRequest(BaseModel):
    """Schema for initiating search boost purchase"""
    telegram_user_id: int


class SearchBoostPurchaseResponse(BaseModel):
    """Schema for search boost purchase response"""
    id: int
    user_id: int
    telegram_user_id: int
    boost_amount: int
    price_stars: int
    purchased_at: datetime
    used_searches: int
    is_active: bool
