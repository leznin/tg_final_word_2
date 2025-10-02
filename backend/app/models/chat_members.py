"""
Chat members database model
"""

from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ChatMember(Base):
    """Chat member model for logging users in group chats"""
    __tablename__ = "chat_members"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False, index=True)
    telegram_user_id = Column(BigInteger, nullable=False, index=True)

    # User information from Telegram API
    is_bot = Column(Boolean, nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    language_code = Column(String(10), nullable=True)
    is_premium = Column(Boolean, nullable=True)
    added_to_attachment_menu = Column(Boolean, nullable=True)
    can_join_groups = Column(Boolean, nullable=True)
    can_read_all_group_messages = Column(Boolean, nullable=True)
    supports_inline_queries = Column(Boolean, nullable=True)
    can_connect_to_business = Column(Boolean, nullable=True)
    has_main_web_app = Column(Boolean, nullable=True)

    # Account information
    account_creation_date = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship with Chat
    chat = relationship("Chat", backref="members")
