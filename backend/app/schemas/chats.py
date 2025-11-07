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
    ai_content_check_enabled: bool = False
    delete_messages_enabled: bool = False


class ChatCreate(ChatBase):
    """Schema for creating a chat"""
    pass


class ChatUpdate(BaseModel):
    """Schema for updating a chat"""
    title: Optional[str] = None
    username: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    linked_channel_id: Optional[int] = None
    message_edit_timeout_minutes: Optional[int] = Field(None, ge=1, le=1440, description="Minutes allowed for message editing (None = disabled)")
    ai_content_check_enabled: Optional[bool] = None


class ChatResponse(ChatBase):
    """Schema for chat response"""
    id: int
    added_at: datetime
    created_at: datetime
    updated_at: datetime
    member_count: Optional[int] = None
    description: Optional[str] = None
    invite_link: Optional[str] = None
    bot_permissions: Optional[dict] = None
    last_info_update: Optional[datetime] = None
    welcome_message_enabled: bool = False
    welcome_message_text: Optional[str] = None
    welcome_message_media_type: Optional[str] = None
    welcome_message_media_url: Optional[str] = None
    welcome_message_lifetime_minutes: Optional[int] = None
    welcome_message_buttons: Optional[dict] = None

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


class ChatSubscriptionInfo(BaseModel):
    """Schema for chat subscription information"""
    id: int
    subscription_type: str
    price_stars: int
    currency: str
    start_date: str
    end_date: str
    is_active: bool
    telegram_payment_charge_id: Optional[str] = None
    created_at: str


class WelcomeMessageButton(BaseModel):
    """Schema for welcome message inline keyboard button"""
    text: str
    url: Optional[str] = None
    callback_data: Optional[str] = None


class WelcomeMessageSettings(BaseModel):
    """Schema for welcome message settings"""
    enabled: bool = False
    text: Optional[str] = None
    media_type: Optional[str] = None  # 'photo', 'video', None
    media_url: Optional[str] = None
    lifetime_minutes: Optional[int] = Field(None, ge=1, le=10080, description="Auto-delete after N minutes (max 7 days)")
    buttons: Optional[List[List[WelcomeMessageButton]]] = None  # Inline keyboard as rows of buttons


class WelcomeMessageUpdate(BaseModel):
    """Schema for updating welcome message settings"""
    enabled: Optional[bool] = None
    text: Optional[str] = None
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    lifetime_minutes: Optional[int] = Field(None, ge=1, le=10080, description="Auto-delete after N minutes (max 7 days)")
    buttons: Optional[List[List[WelcomeMessageButton]]] = None


class ChatWithLinkedChannelResponse(ChatResponse):
    """Schema for chat response with linked channel information and chat moderators"""
    linked_channel_info: Optional[ChannelWithAdmin] = None
    chat_moderators: List[dict] = []  # List of chat moderator info
    active_subscription: Optional[ChatSubscriptionInfo] = None
    welcome_message: Optional[WelcomeMessageSettings] = None
