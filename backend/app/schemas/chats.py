"""
Chat Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TelegramChatData(BaseModel):
    """Schema for Telegram Chat data from API"""
    id: int
    type: str  # 'group', 'supergroup', 'channel'
    title: Optional[str] = None
    username: Optional[str] = None


class ChatBase(BaseModel):
    """Base chat schema"""
    telegram_chat_id: int
    chat_type: str
    title: Optional[str] = None
    username: Optional[str] = None
    added_by_user_id: int
    is_active: bool = True
    linked_channel_id: Optional[int] = None
    message_edit_timeout_minutes: Optional[int] = Field(None, ge=1, le=1440, description="Minutes allowed for message editing (None = disabled)")
    delete_messages_enabled: bool = False


class ChatCreate(ChatBase):
    """Schema for creating a chat"""
    pass


class ChatUpdate(BaseModel):
    """Schema for updating a chat"""
    title: Optional[str] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None
    linked_channel_id: Optional[int] = None
    message_edit_timeout_minutes: Optional[int] = Field(None, ge=1, le=1440, description="Minutes allowed for message editing (None = disabled)")


class ChatResponse(ChatBase):
    """Schema for chat response"""
    id: int
    added_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LinkedChannelInfo(BaseModel):
    """Schema for linked channel information"""
    id: int
    telegram_chat_id: int
    title: Optional[str] = None
    username: Optional[str] = None


class LinkChannelRequest(BaseModel):
    """Schema for linking a channel to a chat"""
    channel_id: int


class ChatWithUserResponse(ChatResponse):
    """Schema for chat response with user information"""
    added_by_user: Optional[dict] = None
    linked_channel: Optional[LinkedChannelInfo] = None


class ChannelWithAdmin(BaseModel):
    """Schema for channel with admin information"""
    id: int
    telegram_chat_id: int
    title: Optional[str] = None
    username: Optional[str] = None
    admin_user_id: int
    admin_username: Optional[str] = None
    admin_name: Optional[str] = None


class ChatWithLinkedChannelResponse(ChatResponse):
    """Schema for chat response with linked channel information and chat moderators"""
    linked_channel_info: Optional[ChannelWithAdmin] = None
    chat_moderators: List[dict] = []  # List of chat moderator info
