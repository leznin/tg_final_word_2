"""
Telegram user history database model for tracking name and username changes
"""

from sqlalchemy import Column, BigInteger, String, DateTime, func, Integer

# Import Base - this will work since we commented the circular import in database.py
from app.core.database import Base


class TelegramUserHistory(Base):
    """Telegram user history model for tracking changes in user data"""
    __tablename__ = "telegram_user_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id = Column(BigInteger, nullable=False, index=True)
    field_name = Column(String(50), nullable=False)  # 'first_name', 'last_name', 'username'
    old_value = Column(String(255), nullable=True)
    new_value = Column(String(255), nullable=True)
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
