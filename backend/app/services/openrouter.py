"""
OpenRouter service with business logic and API integration
"""

import httpx
import uuid
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
        # Create HTTP client with settings that ensure no state persistence between requests
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=False,  # Disable redirects to prevent state issues
        )

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

    async def check_message_content(self, message_text: str) -> Dict[str, Any]:
        """
        Check if message contains prohibited content using OpenRouter AI
        Returns dict with 'violates' (bool) and 'description' (str) fields

        IMPORTANT: Each call to this method must be treated as a completely independent
        conversation. No context or history should be maintained between calls.
        Each request contains only the system prompt and the current message to check.
        """
        try:
            settings = await self.get_settings()
            if not settings or not settings.is_active:
                print("OpenRouter settings not configured or inactive")
                return {"violates": False, "description": "OK"}

            if not settings.selected_model:
                print("No model selected for OpenRouter")
                return {"violates": False, "description": "OK"}

            if not message_text or not message_text.strip():
                return {"violates": False, "description": "OK"}

            headers = {
                "Authorization": f"Bearer {settings.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/openrouter/openrouter",
                "X-Title": "Telegram Content Moderator"
            }

            # Prepare system prompt
            system_prompt = ""
            if settings.prompt:
                try:
                    import json
                    prompt_data = json.loads(settings.prompt)
                    if "system_prompt" in prompt_data:
                        system_data = prompt_data["system_prompt"]
                        system_prompt = f"""Task: {system_data.get('task', '')}
Input: {system_data.get('input', '')}
Output: {system_data.get('output', '')}

Rules:
"""
                        for rule in system_data.get('rules', []):
                            system_prompt += f"- {rule.get('category', '')}: {rule.get('description', '')}\n"

                        system_prompt += f"\n{system_data.get('instructions', '')}"
                    else:
                        system_prompt = settings.prompt
                except (json.JSONDecodeError, KeyError):
                    system_prompt = settings.prompt

            # Generate unique request ID to ensure complete independence
            # This guarantees that each content check is treated as a separate conversation
            request_id = str(uuid.uuid4())

            # Prepare the request payload
            payload = {
                "model": settings.selected_model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": message_text.strip()
                    }
                ],
                "temperature": 0.1,  # Low temperature for consistent responses
                "max_tokens": 200,   # More tokens for JSON response with description
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "response_format": {"type": "json_object"},  # Force JSON response
                "stream": False,     # Disable streaming for single responses
                "user": f"content_check_{request_id}",  # Unique user identifier per request
            }

            response = await self.client.post(
                f"{self.OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30.0
            )

            if response.status_code != 200:
                print(f"OpenRouter API error: {response.status_code} - {response.text}")
                return {"violates": False, "description": "OK"}

            response_data = response.json()

            # Extract the response content
            if "choices" in response_data and len(response_data["choices"]) > 0:
                content = response_data["choices"][0].get("message", {}).get("content", "").strip()

                try:
                    # Parse JSON response from AI
                    ai_response = json.loads(content)

                    # Extract violates and description fields
                    violates = ai_response.get("violates", False)
                    description = ai_response.get("description", "OK")

                    return {"violates": violates, "description": description}

                except json.JSONDecodeError as e:
                    print(f"Failed to parse AI response as JSON: {content}, error: {e}")
                    return {"violates": False, "description": "OK"}
            else:
                print(f"Invalid response structure from OpenRouter: {response_data}")
                return {"violates": False, "description": "OK"}

        except Exception as e:
            print(f"Error checking message content with OpenRouter: {str(e)}")
            return {"violates": False, "description": "OK"}

    async def translate_message(self, message_text: str, target_language: str) -> str:
        """
        Translate message to target language using OpenRouter AI
        Returns translated message or original message if translation fails
        """
        try:
            settings = await self.get_settings()
            if not settings or not settings.is_active:
                print("OpenRouter settings not configured or inactive for translation")
                return message_text

            if not settings.selected_model:
                print("No model selected for OpenRouter translation")
                return message_text

            if not message_text or not message_text.strip():
                return message_text

            # Always attempt translation - let AI decide if translation is needed
            # Only skip if target_language is None or empty
            if not target_language:
                return message_text

            headers = {
                "Authorization": f"Bearer {settings.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/openrouter/openrouter",
                "X-Title": "Telegram Message Translator"
            }

            # System prompt for translation
            system_prompt = f"""You are a professional translator. Translate the given message to {target_language}.

STRICT RULES:
- If the message is already in {target_language}, return it as-is.
- If the message needs translation, provide ONLY the translated text.
- NEVER add any comments, explanations, notes, or extra text.
- NEVER mention what language the message is in.
- NEVER explain your translation process.
- Return ONLY the message text, nothing else.
- Preserve HTML formatting and links exactly as they appear.
- Maintain the original tone and style."""

            # Generate unique request ID
            request_id = str(uuid.uuid4())

            # Prepare the request payload
            payload = {
                "model": settings.selected_model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": message_text.strip()
                    }
                ],
                "temperature": 0.1,  # Low temperature for consistent translations
                "max_tokens": len(message_text) * 2,  # Allow enough tokens for translation
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "stream": False,
                "user": f"translation_{request_id}",
            }

            response = await self.client.post(
                f"{self.OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30.0
            )

            if response.status_code != 200:
                print(f"OpenRouter API error during translation: {response.status_code} - {response.text}")
                return message_text

            response_data = response.json()

            # Extract the response content
            if "choices" in response_data and len(response_data["choices"]) > 0:
                translated_text = response_data["choices"][0].get("message", {}).get("content", "").strip()

                # Return translated text if it's not empty, otherwise return original
                return translated_text if translated_text else message_text
            else:
                print(f"Invalid response structure from OpenRouter during translation: {response_data}")
                return message_text

        except Exception as e:
            print(f"Error translating message with OpenRouter: {str(e)}")
            return message_text

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
