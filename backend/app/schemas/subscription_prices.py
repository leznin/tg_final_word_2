"""
Subscription prices Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SubscriptionPriceBase(BaseModel):
    """Base subscription price schema"""
    subscription_type: str = Field(..., description="Type of subscription: 'month' or 'year'")
    price_stars: int = Field(..., gt=0, description="Price in Telegram Stars")
    currency: str = Field(default='XTR', description="Currency code (XTR for Telegram Stars)")
    is_active: bool = True


class SubscriptionPriceCreate(SubscriptionPriceBase):
    """Schema for creating a subscription price"""
    pass


class SubscriptionPriceUpdate(BaseModel):
    """Schema for updating a subscription price"""
    subscription_type: Optional[str] = Field(None, description="Type of subscription: 'month' or 'year'")
    price_stars: Optional[int] = Field(None, gt=0, description="Price in Telegram Stars")
    currency: Optional[str] = Field(None, description="Currency code (XTR for Telegram Stars)")
    is_active: Optional[bool] = None


class SubscriptionPriceResponse(SubscriptionPriceBase):
    """Schema for subscription price response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

