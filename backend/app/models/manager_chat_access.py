"""
Manager chat access database model
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class ManagerChatAccess(Base):
    """Manager chat access model for managing which chats managers can access"""
    __tablename__ = "manager_chat_access"

    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    admin_user = relationship("AdminUser", backref="chat_accesses")
    chat = relationship("Chat", backref="manager_accesses")

    # Unique constraint to prevent duplicate access entries
    __table_args__ = (
        UniqueConstraint('admin_user_id', 'chat_id', name='uix_manager_chat'),
    )

    class Config:
        from_attributes = True
