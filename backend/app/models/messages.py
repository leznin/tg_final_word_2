"""
Messages database model
"""

from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Message(Base):
    """Message model for storing messages from group chats"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False, index=True)
    telegram_message_id = Column(Integer, nullable=False)
    telegram_user_id = Column(BigInteger, nullable=True, index=True)

    # Message content
    message_type = Column(String(50), nullable=False)  # 'text', 'photo', 'video', 'document', etc.
    text_content = Column(Text, nullable=True)  # Text content or caption
    media_file_id = Column(String(255), nullable=True)  # File ID for media files
    media_type = Column(String(50), nullable=True)  # Specific media type: 'photo', 'video', 'document', etc.

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationship with Chat - use lazy='raise' to prevent implicit IO
    chat = relationship("Chat", backref="messages", lazy='raise')

