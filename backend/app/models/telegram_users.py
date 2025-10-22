"""
Telegram users database model
"""

from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, func

# Import Base - this will work since we commented the circular import in database.py
from app.core.database import Base


class TelegramUser(Base):
    """Telegram user model for storing unique Telegram user information"""
    __tablename__ = "telegram_users"

    telegram_user_id = Column(BigInteger, primary_key=True, index=True)
    is_bot = Column(Boolean, nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    username = Column(String(255), index=True, nullable=True)
    language_code = Column(String(10), nullable=True)
    is_premium = Column(Boolean, nullable=True)
    added_to_attachment_menu = Column(Boolean, nullable=True)
    can_join_groups = Column(Boolean, nullable=True)
    can_read_all_group_messages = Column(Boolean, nullable=True)
    supports_inline_queries = Column(Boolean, nullable=True)
    can_connect_to_business = Column(Boolean, nullable=True)
    has_main_web_app = Column(Boolean, nullable=True)
    account_creation_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
