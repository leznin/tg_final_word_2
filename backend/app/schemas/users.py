"""
User Pydantic schemas
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class TelegramUserData(BaseModel):
    """Schema for Telegram User data from API"""
    id: int
    is_bot: Optional[bool] = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = False
    added_to_attachment_menu: Optional[bool] = False
    can_join_groups: Optional[bool] = False
    can_read_all_group_messages: Optional[bool] = False
    supports_inline_queries: Optional[bool] = False


class UserBase(BaseModel):
    """Base user schema"""
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: bool = False
    is_bot: bool = False
    can_send_messages: bool = True
    blocked_at: Optional[datetime] = None
    is_active: bool = True
    is_admin: bool = False


class UserCreate(UserBase):
    """Schema for creating a user"""
    pass


class UserUpdate(UserBase):
    """Schema for updating a user"""
    pass


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
