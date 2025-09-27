"""
Chat moderators database model
"""

from sqlalchemy import Column, Integer, BigInteger, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ChatModerator(Base):
    """Chat moderator model for managing moderators in group chats"""
    __tablename__ = "chat_moderators"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False, index=True)
    moderator_user_id = Column(BigInteger, nullable=False, index=True)

    # Moderator information (from forwarded message)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)

    # Who added this moderator
    added_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    chat = relationship("Chat", backref="moderators")
    added_by_user = relationship("User", backref="added_moderators", foreign_keys=[added_by_user_id])
