"""
Broadcast Pydantic schemas
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class InlineKeyboardButton(BaseModel):
    """Schema for inline keyboard button"""
    text: str
    url: Optional[str] = None
    callback_data: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Перейти на сайт",
                "url": "https://example.com"
            }
        }


class InlineKeyboardRow(BaseModel):
    """Schema for inline keyboard row"""
    buttons: List[InlineKeyboardButton]


class InlineKeyboardMarkup(BaseModel):
    """Schema for inline keyboard markup"""
    inline_keyboard: List[InlineKeyboardRow]


class MediaFile(BaseModel):
    """Schema for media file"""
    type: str  # 'photo', 'video', 'document'
    url: str  # URL to the file or file_id
    filename: Optional[str] = None
    caption: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "type": "photo",
                "url": "https://example.com/image.jpg",
                "filename": "image.jpg",
                "caption": "Описание фото"
            }
        }


class BroadcastMessageRequest(BaseModel):
    """Schema for broadcast message request"""
    message: str
    original_message: Optional[str] = None  # Original message before translation
    media: Optional[MediaFile] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello! We have an important update for you.",
                "original_message": "Привет! У нас есть важное обновление для вас.",
                "media": {
                    "type": "photo",
                    "url": "https://example.com/image.jpg",
                    "caption": "Посмотрите на это фото!"
                },
                "reply_markup": {
                    "inline_keyboard": [
                        [
                            {"text": "Перейти на сайт", "url": "https://example.com"},
                            {"text": "Подробнее", "callback_data": "more_info"}
                        ]
                    ]
                }
            }
        }


class BroadcastResult(BaseModel):
    """Schema for broadcast result"""
    total_users: int
    sent_successfully: int
    blocked_users: int
    failed_sends: int
    duration_seconds: float
    started_at: datetime
    completed_at: datetime

    class Config:
        from_attributes = True


class BroadcastStatus(BaseModel):
    """Schema for broadcast status during execution"""
    is_running: bool
    current_progress: int
    total_users: int
    sent_successfully: int
    blocked_users: int
    failed_sends: int
    estimated_time_remaining: Optional[float] = None
    started_at: Optional[datetime] = None
