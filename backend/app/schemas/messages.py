"""
Messages Pydantic schemas
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageBase(BaseModel):
    """Base message schema"""
    chat_id: int
    telegram_message_id: int
    telegram_user_id: Optional[int] = None
    message_type: str
    text_content: Optional[str] = None
    media_file_id: Optional[str] = None
    media_type: Optional[str] = None


class MessageCreate(MessageBase):
    """Schema for creating a message"""
    pass


class MessageUpdate(BaseModel):
    """Schema for updating a message"""
    text_content: Optional[str] = None
    media_file_id: Optional[str] = None
    media_type: Optional[str] = None


class MessageResponse(MessageBase):
    """Schema for message response"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TelegramMessageData(BaseModel):
    """Schema for Telegram Message data from API"""
    message_id: int
    date: datetime
    from_user: Optional[dict] = None  # Will be parsed from aiogram User
    text: Optional[str] = None
    caption: Optional[str] = None
    # Media fields will be handled dynamically based on message content
    photo: Optional[list] = None
    video: Optional[dict] = None
    document: Optional[dict] = None
    audio: Optional[dict] = None
    voice: Optional[dict] = None
    animation: Optional[dict] = None
    sticker: Optional[dict] = None
    video_note: Optional[dict] = None
