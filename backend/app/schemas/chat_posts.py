"""
Chat Posts Pydantic schemas
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, timezone
from app.schemas.broadcast import InlineKeyboardMarkup


class MediaUpload(BaseModel):
    """Schema for media upload information"""
    type: str  # 'photo', 'video', 'document'
    url: Optional[str] = None
    file_id: Optional[str] = None
    filename: Optional[str] = None


class ChatPostCreate(BaseModel):
    """Schema for creating a new chat post"""
    chat_id: int
    content_text: Optional[str] = None
    media: Optional[MediaUpload] = None
    
    # Scheduling
    scheduled_send_at: Optional[datetime] = None  # When to send the post
    send_immediately: bool = True  # If True, send right away
    
    # Pin settings
    pin_message: bool = False
    pin_duration_minutes: Optional[int] = None
    
    # Delete settings
    delete_after_minutes: Optional[int] = None
    
    # Inline keyboard
    reply_markup: Optional[InlineKeyboardMarkup] = None
    
    @field_validator('scheduled_send_at')
    @classmethod
    def convert_to_utc(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Convert datetime to UTC timezone"""
        if v is None:
            return None
        
        # If timezone-aware, convert to UTC
        if v.tzinfo is not None:
            return v.astimezone(timezone.utc)
        
        # If naive, assume it's already UTC
        return v.replace(tzinfo=timezone.utc)


class ChatPostUpdate(BaseModel):
    """Schema for updating a chat post"""
    content_text: Optional[str] = None
    # Note: Cannot update media in Telegram, only text
    
    # Scheduling - can update for unsent posts
    scheduled_send_at: Optional[datetime] = None
    
    # Pin settings - can update even for sent posts
    pin_message: Optional[bool] = None
    pin_duration_minutes: Optional[int] = None
    
    # Delete settings - can update even for sent posts
    delete_after_minutes: Optional[int] = None
    
    # Inline keyboard - can update even for sent posts
    reply_markup: Optional[InlineKeyboardMarkup] = None
    
    @field_validator('scheduled_send_at')
    @classmethod
    def convert_to_utc(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Convert datetime to UTC timezone"""
        if v is None:
            return None
        
        # If timezone-aware, convert to UTC
        if v.tzinfo is not None:
            return v.astimezone(timezone.utc)
        
        # If naive, assume it's already UTC
        return v.replace(tzinfo=timezone.utc)


class ChatPostResponse(BaseModel):
    """Schema for chat post response"""
    id: int
    chat_id: int
    telegram_message_id: Optional[int] = None
    scheduled_send_at: Optional[datetime] = None
    is_sent: bool
    sent_at: Optional[datetime] = None
    content_text: Optional[str] = None
    media_type: Optional[str] = None
    media_file_id: Optional[str] = None
    media_url: Optional[str] = None
    media_filename: Optional[str] = None
    is_pinned: bool
    pin_duration_minutes: Optional[int] = None
    scheduled_unpin_at: Optional[datetime] = None
    delete_after_minutes: Optional[int] = None
    scheduled_delete_at: Optional[datetime] = None
    created_by_user_id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatPostListResponse(BaseModel):
    """Schema for paginated list of chat posts"""
    posts: list[ChatPostResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PinPostRequest(BaseModel):
    """Schema for pinning a post"""
    pin_duration_minutes: Optional[int] = None


class MediaUploadResponse(BaseModel):
    """Schema for media upload response"""
    url: str
    filename: str
    content_type: str
    size: int
