"""
OpenRouter service with business logic and API integration
"""

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.openrouter import OpenRouterSettings
from app.schemas.openrouter import (
    OpenRouterCreate, OpenRouterUpdate, OpenRouterResponse,
    OpenRouterModel, OpenRouterBalance, OpenRouterModelsResponse,
    OpenRouterBalanceResponse
)


class OpenRouterService:
    """Service class for OpenRouter operations"""

    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_settings(self) -> Optional[OpenRouterSettings]:
        """Get OpenRouter settings (returns first record or None)"""
        result = await self.db.execute(
            select(OpenRouterSettings).where(OpenRouterSettings.is_active == True).limit(1)
        )
        return result.scalar_one_or_none()

    async def save_settings(self, settings_data: OpenRouterCreate) -> OpenRouterSettings:
        """Create or update OpenRouter settings"""
        # Get existing settings
        existing = await self.get_settings()

        if existing:
            # Update existing
            for field, value in settings_data.model_dump().items():
                setattr(existing, field, value)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            # Create new
            db_settings = OpenRouterSettings(**settings_data.model_dump())
            self.db.add(db_settings)
            await self.db.commit()
            await self.db.refresh(db_settings)
            return db_settings

    async def update_settings(self, settings_data: OpenRouterUpdate) -> Optional[OpenRouterSettings]:
        """Update existing OpenRouter settings"""
        existing = await self.get_settings()
        if not existing:
            return None

        for field, value in settings_data.model_dump(exclude_unset=True).items():
            setattr(existing, field, value)

        await self.db.commit()
        await self.db.refresh(existing)
        return existing

    async def get_models(self) -> List[OpenRouterModel]:
        """Get available models from OpenRouter API"""
        try:
            settings = await self.get_settings()
            if not settings:
                raise ValueError("OpenRouter settings not configured")

            headers = {
                "Authorization": f"Bearer {settings.api_key}",
                "Content-Type": "application/json"
            }

            response = await self.client.get(
                f"{self.OPENROUTER_BASE_URL}/models",
                headers=headers
            )

            if response.status_code != 200:
                raise ValueError(f"OpenRouter API error: {response.status_code} - {response.text}")

            data = response.json()
            models = []

            for model_data in data.get("data", []):
                model = OpenRouterModel(
                    id=model_data.get("id", ""),
                    name=model_data.get("name", ""),
                    description=model_data.get("description", ""),
                    pricing=model_data.get("pricing", {}),
                    context_length=model_data.get("context_length"),
                    supports_function_calling=model_data.get("supports_function_calling"),
                    supports_vision=model_data.get("supports_vision")
                )
                models.append(model)

            return models

        except Exception as e:
            raise ValueError(f"Failed to fetch models: {str(e)}")

    async def get_balance(self) -> OpenRouterBalance:
        """Get account balance from OpenRouter API"""
        try:
            settings = await self.get_settings()
            if not settings:
                raise ValueError("OpenRouter settings not configured")

            headers = {
                "Authorization": f"Bearer {settings.api_key}",
                "Content-Type": "application/json"
            }

            response = await self.client.get(
                f"{self.OPENROUTER_BASE_URL}/credits",
                headers=headers
            )

            if response.status_code != 200:
                raise ValueError(f"OpenRouter API error: {response.status_code} - {response.text}")

            data = response.json().get("data", {})

            # Calculate balance: total_credits - total_usage
            total_credits = data.get("total_credits", 0.0)
            total_usage = data.get("total_usage", 0.0)
            balance_amount = total_credits - total_usage

            balance = OpenRouterBalance(
                credits=balance_amount,
                total_credits=total_credits,
                total_usage=total_usage,
                currency="USD"
            )

            # Update balance in database
            settings.balance = balance.credits
            await self.db.commit()

            return balance

        except Exception as e:
            raise ValueError(f"Failed to fetch balance: {str(e)}")

    async def validate_api_key(self, api_key: str) -> bool:
        """Validate OpenRouter API key"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            response = await self.client.get(
                f"{self.OPENROUTER_BASE_URL}/auth/key",
                headers=headers
            )

            return response.status_code == 200

        except Exception:
            return False

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
