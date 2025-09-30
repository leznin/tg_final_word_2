"""
Chat subscriptions database model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from app.core.database import Base


class ChatSubscription(Base):
    """Chat subscription model for AI content check subscriptions per chat"""
    __tablename__ = "chat_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False, index=True)
    subscription_type = Column(String(20), nullable=False)  # 'month', 'year'
    price_stars = Column(Integer, nullable=False)  # Price paid in Telegram Stars
    currency = Column(String(10), default='XTR', nullable=False)  # Currency (XTR for Telegram Stars)
    start_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    telegram_payment_charge_id = Column(String(255), nullable=True)  # Telegram payment charge ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

