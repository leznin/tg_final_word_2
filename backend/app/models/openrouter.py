"""
OpenRouter settings database model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, func
from app.core.database import Base


class OpenRouterSettings(Base):
    """OpenRouter settings model"""
    __tablename__ = "openrouter_settings"

    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String(255), nullable=False)
    selected_model = Column(String(100), nullable=True)
    balance = Column(Float, nullable=True)
    prompt = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
