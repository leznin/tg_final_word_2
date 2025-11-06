"""
Chat Posts database model
"""

from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ChatPost(Base):
    """Model for storing posts sent to Telegram chats"""
    __tablename__ = "chat_posts"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False, index=True)
    telegram_message_id = Column(BigInteger, nullable=True, index=True)  # Null until sent
    
    # Scheduling
    scheduled_send_at = Column(DateTime(timezone=True), nullable=True, index=True)  # When to send
    is_sent = Column(Boolean, default=False, nullable=False)  # Whether already sent
    sent_at = Column(DateTime(timezone=True), nullable=True)  # Actual send time
    
    # Content
    content_text = Column(Text, nullable=True)
    
    # Media information
    media_type = Column(String(50), nullable=True)  # 'photo', 'video', 'document', None
    media_file_id = Column(String(255), nullable=True)  # Telegram file_id
    media_url = Column(String(500), nullable=True)  # URL if uploaded via admin panel
    media_filename = Column(String(255), nullable=True)  # Original filename
    
    # Pin settings
    is_pinned = Column(Boolean, default=False, nullable=False)
    pin_duration_minutes = Column(Integer, nullable=True)  # Duration to keep pinned
    scheduled_unpin_at = Column(DateTime(timezone=True), nullable=True)  # When to unpin
    
    # Delete settings
    delete_after_minutes = Column(Integer, nullable=True)  # Delete after N minutes
    scheduled_delete_at = Column(DateTime(timezone=True), nullable=True)  # When to delete
    
    # Inline keyboard
    reply_markup = Column(JSON, nullable=True)  # Inline keyboard markup as JSON
    
    # Metadata
    created_by_user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    chat = relationship("Chat", backref="posts")
    created_by = relationship("AdminUser")
