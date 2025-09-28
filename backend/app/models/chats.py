"""
Chat database model
"""

from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, func, ForeignKey, SmallInteger, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class Chat(Base):
    """Chat model for Telegram groups and channels"""
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    telegram_chat_id = Column(BigInteger, unique=True, index=True, nullable=False)
    chat_type = Column(String(20), nullable=False)  # 'group', 'supergroup', 'channel'
    title = Column(String(255), nullable=True)
    username = Column(String(50), nullable=True)
    added_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Link to a channel for forwarding messages from this chat
    linked_channel_id = Column(Integer, ForeignKey("chats.id"), nullable=True)

    # Message edit timeout in minutes (None = editing disabled)
    message_edit_timeout_minutes = Column(SmallInteger, nullable=True)

    # Additional information from Telegram API
    member_count = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    invite_link = Column(String(255), nullable=True)
    bot_permissions = Column(JSONB, nullable=True)  # Bot permissions as JSON
    last_info_update = Column(DateTime(timezone=True), nullable=True)

    # Relationship with User who added the bot
    added_by_user = relationship("User", backref="added_chats")

    # Self-referencing relationship for linked channel
    linked_channel = relationship("Chat", remote_side=[id], backref="linked_chats", foreign_keys=[linked_channel_id])
