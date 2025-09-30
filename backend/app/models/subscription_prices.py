"""
Subscription prices database model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, func
from app.core.database import Base


class SubscriptionPrice(Base):
    """Subscription prices model for AI content check subscriptions"""
    __tablename__ = "subscription_prices"

    id = Column(Integer, primary_key=True, index=True)
    subscription_type = Column(String(20), nullable=False)  # 'month', 'year'
    price_stars = Column(Integer, nullable=False)  # Price in Telegram Stars
    currency = Column(String(10), default='XTR', nullable=False)  # Currency (XTR for Telegram Stars)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

