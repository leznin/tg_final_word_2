"""
OpenRouter Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class OpenRouterModel(BaseModel):
    """Schema for OpenRouter model information"""
    id: str
    name: str
    description: Optional[str] = None
    pricing: Optional[Dict[str, Any]] = None
    context_length: Optional[int] = None
    supports_function_calling: Optional[bool] = None
    supports_vision: Optional[bool] = None


class OpenRouterBalance(BaseModel):
    """Schema for OpenRouter balance information"""
    credits: float
    total_credits: float = 0.0
    total_usage: float = 0.0
    currency: str = "USD"


class OpenRouterBase(BaseModel):
    """Base OpenRouter settings schema"""
    api_key: str = Field(..., min_length=1, max_length=255)
    selected_model: Optional[str] = Field(None, max_length=100)
    balance: Optional[float] = None
    prompt: Optional[str] = None
    is_active: bool = True


class OpenRouterCreate(OpenRouterBase):
    """Schema for creating OpenRouter settings"""
    pass


class OpenRouterUpdate(BaseModel):
    """Schema for updating OpenRouter settings"""
    api_key: Optional[str] = Field(None, min_length=1, max_length=255)
    selected_model: Optional[str] = Field(None, max_length=100)
    balance: Optional[float] = None
    prompt: Optional[str] = None
    is_active: Optional[bool] = None


class OpenRouterResponse(OpenRouterBase):
    """Schema for OpenRouter settings response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OpenRouterModelsResponse(BaseModel):
    """Schema for OpenRouter models list response"""
    models: List[OpenRouterModel]


class OpenRouterBalanceResponse(BaseModel):
    """Schema for OpenRouter balance response"""
    balance: OpenRouterBalance
    last_updated: str
