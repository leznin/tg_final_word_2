"""
Auth attempts database model for tracking login attempts with fingerprint blocking
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, func
from app.core.database import Base


class AuthAttempt(Base):
    """Auth attempt model for tracking login attempts"""
    __tablename__ = "auth_attempts"

    id = Column(Integer, primary_key=True, index=True)
    fingerprint = Column(String(255), index=True, nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(Text, nullable=True)
    attempt_count = Column(Integer, default=1)  # Total attempts
    failed_count = Column(Integer, default=0)  # Failed attempts
    success_count = Column(Integer, default=0)  # Successful attempts
    blocked = Column(Boolean, default=False)
    blocked_until = Column(DateTime(timezone=True), nullable=True)
    block_reason = Column(String(255), nullable=True)
    first_attempt_at = Column(DateTime(timezone=True), server_default=func.now())
    last_attempt_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Legacy fields (will be removed after migration)
    success = Column(Boolean, nullable=True)  # For backward compatibility
    created_at = Column(DateTime(timezone=True), nullable=True)  # For backward compatibility

    class Config:
        from_attributes = True
