"""
Search boost purchases model for tracking additional search attempts purchases
"""

from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class SearchBoostPurchase(Base):
    """Model for tracking purchases of additional search attempts"""
    
    __tablename__ = "search_boost_purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    telegram_user_id = Column(Integer, nullable=False, index=True)
    boost_amount = Column(Integer, default=10, nullable=False)  # Number of additional searches purchased
    price_stars = Column(Integer, nullable=False)  # Price paid in Telegram Stars
    currency = Column(String(10), default='XTR', nullable=False)  # Currency (XTR for Telegram Stars)
    telegram_payment_charge_id = Column(String(255), nullable=True)  # Telegram payment charge ID
    purchased_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    used_searches = Column(Integer, default=0, nullable=False)  # Number of searches used from this boost
    is_active = Column(Boolean, default=True, nullable=False)  # Whether boost still has unused searches
    
    # Relationship to User table
    user = relationship("User", backref="search_boost_purchases")

    def __repr__(self):
        return f"<SearchBoostPurchase(id={self.id}, user_id={self.user_id}, boost_amount={self.boost_amount}, used={self.used_searches}, active={self.is_active})>"


class SearchBoostPrice(Base):
    """Model for storing search boost pricing configuration"""
    
    __tablename__ = "search_boost_prices"

    id = Column(Integer, primary_key=True, index=True)
    boost_amount = Column(Integer, default=10, nullable=False)  # Number of searches in boost pack
    price_stars = Column(Integer, nullable=False)  # Price in Telegram Stars
    currency = Column(String(10), default='XTR', nullable=False)  # Currency (XTR for Telegram Stars)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<SearchBoostPrice(id={self.id}, boost_amount={self.boost_amount}, price_stars={self.price_stars}, active={self.is_active})>"
