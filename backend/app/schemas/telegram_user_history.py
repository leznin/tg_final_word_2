"""
Telegram user history Pydantic schemas
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TelegramUserHistoryBase(BaseModel):
    """Base telegram user history schema"""
    telegram_user_id: int
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_at: datetime


class TelegramUserHistoryCreate(TelegramUserHistoryBase):
    """Schema for creating a telegram user history entry"""
    pass


class TelegramUserHistoryResponse(TelegramUserHistoryBase):
    """Schema for telegram user history response"""
    id: int

    class Config:
        from_attributes = True
