"""
Chat members database model
"""

from sqlalchemy import Column, Integer, BigInteger, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ChatMember(Base):
    """Chat member model for linking users to group chats"""
    __tablename__ = "chat_members"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False, index=True)
    telegram_user_id = Column(BigInteger, ForeignKey("telegram_users.telegram_user_id"), nullable=False, index=True)

    # Member status
    status = Column(String(20), default='active')  # 'active', 'left', 'banned', 'kicked'

    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True), nullable=True)  # Time when member left/banned
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    chat = relationship("Chat", backref="members")
    telegram_user = relationship("TelegramUser", backref="chat_memberships")
