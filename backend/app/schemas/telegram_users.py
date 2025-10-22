"""
Telegram users Pydantic schemas
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TelegramUserBase(BaseModel):
    """Base telegram user schema"""
    telegram_user_id: int
    is_bot: Optional[bool] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = None
    added_to_attachment_menu: Optional[bool] = None
    can_join_groups: Optional[bool] = None
    can_read_all_group_messages: Optional[bool] = None
    supports_inline_queries: Optional[bool] = None
    can_connect_to_business: Optional[bool] = None
    has_main_web_app: Optional[bool] = None
    account_creation_date: Optional[datetime] = None


class TelegramUserCreate(TelegramUserBase):
    """Schema for creating a telegram user"""
    pass


class TelegramUserUpdate(BaseModel):
    """Schema for updating a telegram user"""
    is_bot: Optional[bool] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = None
    added_to_attachment_menu: Optional[bool] = None
    can_join_groups: Optional[bool] = None
    can_read_all_group_messages: Optional[bool] = None
    supports_inline_queries: Optional[bool] = None
    can_connect_to_business: Optional[bool] = None
    has_main_web_app: Optional[bool] = None
    account_creation_date: Optional[datetime] = None


class TelegramUserResponse(TelegramUserBase):
    """Schema for telegram user response"""
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TelegramUserData(BaseModel):
    """Schema for Telegram User data from API"""
    telegram_user_id: int
    is_bot: bool
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = None
    added_to_attachment_menu: Optional[bool] = None
    can_join_groups: Optional[bool] = None
    can_read_all_group_messages: Optional[bool] = None
    supports_inline_queries: Optional[bool] = None
    can_connect_to_business: Optional[bool] = None
    has_main_web_app: Optional[bool] = None
    account_creation_date: Optional[datetime] = None
