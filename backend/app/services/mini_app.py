"""
Mini app service with business logic
"""

import hashlib
import hmac
import json
from urllib.parse import unquote, parse_qs
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from typing import List, Optional, Dict, Any
from app.models.users import User
from app.models.telegram_users import TelegramUser
from app.schemas.mini_app import (
    TelegramUserVerifyRequest,
    TelegramUserVerifyResponse,
    UserSearchRequest,
    UserSearchResult,
    UserSearchResponse
)
from app.core.config import settings


class MiniAppService:
    """Service class for mini app operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _verify_telegram_init_data(self, init_data: str) -> Optional[Dict[str, Any]]:
        """
        Verify Telegram Web App initData and extract user information.
        Returns user data if verification successful, None otherwise.
        """
        try:
            # Parse initData (URL-encoded string)
            params = parse_qs(init_data, keep_blank_values=True)

            # Extract hash
            received_hash = params.get('hash', [None])[0]
            if not received_hash:
                return None

            # Remove hash from params for verification
            params.pop('hash', None)

            # Create data_check_string
            data_check_arr = []
            for key in sorted(params.keys()):
                value = params[key][0] if params[key] else ''
                data_check_arr.append(f"{key}={value}")

            data_check_string = '\n'.join(data_check_arr)

            # Calculate HMAC-SHA256
            secret_key = hmac.new(
                key='WebAppData'.encode(),
                msg=settings.TELEGRAM_BOT_TOKEN.encode(),
                digestmod=hashlib.sha256
            ).digest()

            calculated_hash = hmac.new(
                key=secret_key,
                msg=data_check_string.encode(),
                digestmod=hashlib.sha256
            ).hexdigest()

            # Compare hashes
            if not hmac.compare_digest(calculated_hash, received_hash):
                return None

            # Extract user data from 'user' parameter if present
            user_data = None
            if 'user' in params:
                try:
                    user_data = json.loads(unquote(params['user'][0]))
                except (json.JSONDecodeError, KeyError):
                    pass

            return user_data

        except Exception as e:
            print(f"Error verifying Telegram initData: {e}")
            return None

    async def verify_telegram_user(self, request: TelegramUserVerifyRequest) -> TelegramUserVerifyResponse:
        """Verify and potentially create/update Telegram user using initData"""
        try:
            # Verify initData and extract user information
            user_data = self._verify_telegram_init_data(request.init_data)

            if not user_data:
                return TelegramUserVerifyResponse(
                    verified=False,
                    telegram_user_id=0,
                    message="Invalid or expired Telegram Web App data"
                )

            telegram_user_id = user_data.get('id')
            if not telegram_user_id:
                return TelegramUserVerifyResponse(
                    verified=False,
                    telegram_user_id=0,
                    message="User ID not found in Telegram data"
                )

            # Try to find existing user by telegram_id
            user = await self.db.execute(
                select(User).where(User.telegram_id == telegram_user_id)
            )
            db_user = user.scalar_one_or_none()

            if db_user:
                # Update existing user data
                db_user.first_name = user_data.get('first_name')
                db_user.last_name = user_data.get('last_name')
                db_user.username = user_data.get('username')
                db_user.language_code = user_data.get('language_code')
                if user_data.get('is_premium') is not None:
                    db_user.is_premium = user_data.get('is_premium', False)
                if user_data.get('is_bot') is not None:
                    db_user.is_bot = user_data.get('is_bot', False)
                await self.db.commit()
                await self.db.refresh(db_user)

                return TelegramUserVerifyResponse(
                    verified=True,
                    telegram_user_id=telegram_user_id,
                    message="User verified and updated successfully",
                    user_data={
                        "id": db_user.id,
                        "username": db_user.username,
                        "first_name": db_user.first_name,
                        "last_name": db_user.last_name
                    }
                )
            else:
                # Create new user
                new_user = User(
                    telegram_id=telegram_user_id,
                    first_name=user_data.get('first_name'),
                    last_name=user_data.get('last_name'),
                    username=user_data.get('username'),
                    language_code=user_data.get('language_code'),
                    is_premium=user_data.get('is_premium', False),
                    is_bot=user_data.get('is_bot', False),
                    can_send_messages=True,
                    is_active=True,
                    is_admin=False
                )
                self.db.add(new_user)
                await self.db.commit()
                await self.db.refresh(new_user)

                return TelegramUserVerifyResponse(
                    verified=True,
                    telegram_user_id=telegram_user_id,
                    message="New user created successfully",
                    user_data={
                        "id": new_user.id,
                        "username": new_user.username,
                        "first_name": new_user.first_name,
                        "last_name": new_user.last_name
                    }
                )

        except Exception as e:
            return TelegramUserVerifyResponse(
                verified=False,
                telegram_user_id=0,
                message=f"Verification failed: {str(e)}"
            )

    async def search_users(self, request: UserSearchRequest) -> UserSearchResponse:
        """Search users by username, first name, or last name"""
        try:
            query_lower = request.query.lower().strip()

            # Build search conditions
            search_conditions = [
                func.lower(User.username).contains(query_lower),
                func.lower(User.first_name).contains(query_lower),
                func.lower(User.last_name).contains(query_lower)
            ]

            # Execute search query
            search_query = select(User).where(
                or_(*search_conditions)
            ).limit(request.limit).offset(request.offset)

            result = await self.db.execute(search_query)
            users = result.scalars().all()

            # Get total count
            count_query = select(func.count()).select_from(User).where(
                or_(*search_conditions)
            )
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()

            # Convert to response format
            results = []
            for user in users:
                results.append(UserSearchResult(
                    id=user.id,
                    telegram_id=user.telegram_id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    language_code=user.language_code,
                    is_premium=user.is_premium,
                    is_bot=user.is_bot,
                    created_at=user.created_at,
                    updated_at=user.updated_at
                ))

            return UserSearchResponse(
                results=results,
                total=total,
                limit=request.limit,
                offset=request.offset
            )

        except Exception as e:
            # Return empty results on error
            return UserSearchResponse(
                results=[],
                total=0,
                limit=request.limit,
                offset=request.offset
            )
