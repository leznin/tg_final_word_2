"""
Chat moderators Pydantic schemas
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatModeratorBase(BaseModel):
    """Base chat moderator schema"""
    chat_id: int
    moderator_user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    added_by_user_id: int


class ChatModeratorCreate(ChatModeratorBase):
    """Schema for creating a chat moderator"""
    pass


class ChatModeratorUpdate(BaseModel):
    """Schema for updating a chat moderator"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None


class ChatModeratorResponse(ChatModeratorBase):
    """Schema for chat moderator response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatModeratorWithUserResponse(ChatModeratorResponse):
    """Schema for chat moderator response with user information"""
    added_by_user: Optional[dict] = None
    chat_title: Optional[str] = None


class TelegramUserForwardData(BaseModel):
    """Schema for Telegram User data from forwarded message"""
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
