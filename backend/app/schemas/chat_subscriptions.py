"""
Chat subscriptions Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChatSubscriptionBase(BaseModel):
    """Base chat subscription schema"""
    chat_id: int = Field(..., description="Chat ID")
    subscription_type: str = Field(..., description="Type of subscription: 'month' or 'year'")
    price_stars: int = Field(..., gt=0, description="Price paid in Telegram Stars")
    currency: str = Field(default='XTR', description="Currency code (XTR for Telegram Stars)")
    start_date: datetime = Field(..., description="Subscription start date")
    end_date: datetime = Field(..., description="Subscription end date")
    is_active: bool = True
    telegram_payment_charge_id: Optional[str] = Field(None, description="Telegram payment charge ID")


class ChatSubscriptionCreate(ChatSubscriptionBase):
    """Schema for creating a chat subscription"""
    pass


class ChatSubscriptionUpdate(BaseModel):
    """Schema for updating a chat subscription"""
    subscription_type: Optional[str] = Field(None, description="Type of subscription: 'month' or 'year'")
    price_stars: Optional[int] = Field(None, gt=0, description="Price paid in Telegram Stars")
    currency: Optional[str] = Field(None, description="Currency code (XTR for Telegram Stars)")
    start_date: Optional[datetime] = Field(None, description="Subscription start date")
    end_date: Optional[datetime] = Field(None, description="Subscription end date")
    is_active: Optional[bool] = None
    telegram_payment_charge_id: Optional[str] = Field(None, description="Telegram payment charge ID")


class ChatSubscriptionResponse(ChatSubscriptionBase):
    """Schema for chat subscription response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatSubscriptionWithChatInfo(ChatSubscriptionResponse):
    """Schema for chat subscription response with chat information"""
    chat_title: Optional[str] = None
    chat_telegram_id: Optional[int] = None
    chat_username: Optional[str] = None

