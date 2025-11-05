"""
User verification schedule database model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Time, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserVerificationSchedule(Base):
    """User verification schedule model"""
    __tablename__ = "user_verification_schedule"

    id = Column(Integer, primary_key=True, index=True)
    
    # Schedule settings
    enabled = Column(Boolean, default=False, nullable=False)
    schedule_time = Column(Time, nullable=False)  # Time to run verification (e.g., "02:00:00")
    interval_hours = Column(Integer, default=24, nullable=False)  # Run every X hours (default: 24 = daily)
    
    # Verification settings
    auto_update = Column(Boolean, default=True, nullable=False)  # Auto-update user data
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=True)  # Optional: filter by specific chat
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_run_at = Column(DateTime(timezone=True), nullable=True)  # When was it last executed
    next_run_at = Column(DateTime(timezone=True), nullable=True)  # When should it run next
    
    # Relationship with Chat
    chat = relationship("Chat", backref="verification_schedules")

    class Config:
        from_attributes = True
