"""
Chat members Pydantic schemas
"""

from pydantic import BaseModel
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from .telegram_users import TelegramUserResponse


class MemberStatus(str, Enum):
    ACTIVE = "active"
    LEFT = "left"
    BANNED = "banned"
    KICKED = "kicked"


class ChatMemberBase(BaseModel):
    """Base chat member schema"""
    chat_id: int
    telegram_user_id: int
    status: MemberStatus = MemberStatus.ACTIVE
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None


class ChatMemberCreate(ChatMemberBase):
    """Schema for creating a chat member"""
    pass


class ChatMemberUpdate(BaseModel):
    """Schema for updating a chat member"""
    status: Optional[MemberStatus] = None
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None


class ChatMemberResponse(ChatMemberBase):
    """Schema for chat member response"""
    id: int
    created_at: datetime
    updated_at: datetime
    telegram_user: Optional["TelegramUserResponse"] = None

    class Config:
        from_attributes = True
