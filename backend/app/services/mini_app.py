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
from app.models.telegram_user_history import TelegramUserHistory
from app.schemas.mini_app import (
    TelegramUserVerifyRequest,
    TelegramUserVerifyResponse,
    UserSearchRequest,
    UserSearchResult,
    UserSearchResponse,
    UserHistoryEntry
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

    def _mask_string(self, text: str, visible_chars: int = 2) -> str:
        """Mask string with asterisks, showing only first few characters"""
        if not text or len(text) <= visible_chars:
            return text
        return text[:visible_chars] + '*' * (len(text) - visible_chars)

    def _mask_id(self, user_id: int) -> str:
        """Mask user ID, showing only last 4 digits"""
        id_str = str(user_id)
        if len(id_str) <= 4:
            return id_str
        return '*' * (len(id_str) - 4) + id_str[-4:]

    def _group_similar_users(self, users: List[TelegramUser]) -> List[Dict[str, Any]]:
        """
        Group users with similar creation dates.
        Keep first user with full data, mask others' data.
        Returns list of dicts with user data and mask info.
        """
        from collections import defaultdict
        
        # Group by account_creation_date (если одинаковая - подозрительно)
        groups = defaultdict(list)
        for user in users:
            # Группируем по дате создания аккаунта
            key = str(user.account_creation_date) if user.account_creation_date else 'no_date'
            groups[key].append(user)
        
        processed_users = []
        for group_key, group_users in groups.items():
            # Если только один пользователь в группе или нет даты, добавляем как есть
            if len(group_users) == 1 or group_key == 'no_date':
                for user in group_users:
                    processed_users.append({
                        'user': user,
                        'masked': False
                    })
            else:
                # Если несколько пользователей с одинаковой датой создания - маскируем всех кроме первого
                processed_users.append({
                    'user': group_users[0],
                    'masked': False
                })
                
                # Mark others for masking
                for similar_user in group_users[1:]:
                    processed_users.append({
                        'user': similar_user,
                        'masked': True
                    })
        
        return processed_users

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
        """Search users by ID or username only"""
        try:
            query_lower = request.query.lower().strip()

            # Build search conditions for TelegramUser (only ID and username)
            search_conditions = []

            # Check if query is a number (searching by ID)
            if query_lower.isdigit():
                telegram_id = int(query_lower)
                search_conditions.append(TelegramUser.telegram_user_id == telegram_id)
            
            # Always search by username
            search_conditions.append(func.lower(TelegramUser.username).contains(query_lower))

            # Execute search query on TelegramUser
            search_query = select(TelegramUser).where(
                or_(*search_conditions)
            ).limit(request.limit).offset(request.offset)

            result = await self.db.execute(search_query)
            users = result.scalars().all()

            # Get total count
            count_query = select(func.count()).select_from(TelegramUser).where(
                or_(*search_conditions)
            )
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()

            # Group similar users and mask duplicates
            user_data_list = self._group_similar_users(list(users))

            # Convert to response format with history
            results = []
            for user_data in user_data_list:
                user = user_data['user']
                is_masked = user_data['masked']
                
                # Get history for this user
                history_query = select(TelegramUserHistory).where(
                    TelegramUserHistory.telegram_user_id == user.telegram_user_id
                ).order_by(TelegramUserHistory.changed_at.desc())
                
                history_result = await self.db.execute(history_query)
                history_records = history_result.scalars().all()

                # Convert history to schema format
                history_entries = [
                    UserHistoryEntry(
                        id=record.id,
                        field_name=record.field_name,
                        old_value=record.old_value,
                        new_value=record.new_value,
                        changed_at=record.changed_at
                    )
                    for record in history_records
                ]

                # Apply masking if needed
                first_name = user.first_name
                last_name = user.last_name
                username = user.username
                telegram_user_id = user.telegram_user_id
                real_telegram_user_id = None
                
                if is_masked:
                    if first_name:
                        first_name = self._mask_string(first_name, 2)
                    if last_name:
                        last_name = self._mask_string(last_name, 2)
                    if username:
                        username = self._mask_string(username, 3)
                    # Mask ID - show only last 4 digits, but keep real ID
                    real_telegram_user_id = user.telegram_user_id
                    telegram_user_id = self._mask_id(user.telegram_user_id)

                results.append(UserSearchResult(
                    telegram_user_id=telegram_user_id,
                    real_telegram_user_id=real_telegram_user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    language_code=user.language_code,
                    is_premium=user.is_premium or False,
                    is_bot=user.is_bot or False,
                    account_creation_date=user.account_creation_date,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    history=history_entries
                ))

            return UserSearchResponse(
                results=results,
                total=total,
                limit=request.limit,
                offset=request.offset
            )

        except Exception as e:
            print(f"Search users error: {e}")
            # Return empty results on error
            return UserSearchResponse(
                results=[],
                total=0,
                limit=request.limit,
                offset=request.offset
            )
