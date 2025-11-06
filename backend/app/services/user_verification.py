"""
User verification service for checking user info via Telegram API getChatMember
"""

import asyncio
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter

from app.models.chat_members import ChatMember
from app.models.telegram_users import TelegramUser
from app.models.chats import Chat
from app.services.telegram_users import TelegramUserService
from app.schemas.telegram_users import TelegramUserData
from app.schemas.user_verification import (
    UserVerificationResult, BulkVerificationResponse,
    UserChangeDetail, ActiveUserInfo, ActiveUsersListResponse
)


class UserVerificationService:
    """Service for verifying and updating user information via Telegram API"""

    def __init__(self, bot, db: AsyncSession):
        """
        Initialize the service
        
        Args:
            bot: Telegram bot instance (from aiogram)
            db: Database session
        """
        self.bot = bot
        self.db = db
        self.telegram_user_service = TelegramUserService(db)
        
        # Progress tracking
        self.is_running = False
        self.current_progress = 0
        self.total_users = 0
        self.checked_users = 0
        self.updated_users = 0
        self.users_with_changes = 0
        self.users_with_errors = 0
        self.started_at = None
        self.estimated_time_remaining = None

    async def verify_user_info(
        self,
        telegram_user_id: int,
        telegram_chat_id: int,
        auto_update: bool = True
    ) -> UserVerificationResult:
        """
        Verify single user information using Telegram API getChatMember
        
        Args:
            telegram_user_id: Telegram user ID to verify
            telegram_chat_id: Telegram chat ID where to check the user
            auto_update: Whether to automatically update user data if changes detected
            
        Returns:
            UserVerificationResult with verification details
        """
        try:
            # Get chat information from database for the title
            chat_query = select(Chat).where(Chat.telegram_chat_id == telegram_chat_id)
            chat_result = await self.db.execute(chat_query)
            chat = chat_result.scalar_one_or_none()
            chat_title = chat.title if chat else None
            chat_db_id = chat.id if chat else None

            # Get current user data from database
            current_user = await self.telegram_user_service.get_telegram_user(telegram_user_id)

            # Get actual user data from Telegram API
            try:
                chat_member = await self.bot.get_chat_member(telegram_chat_id, telegram_user_id)
            except TelegramBadRequest as e:
                return UserVerificationResult(
                    telegram_user_id=telegram_user_id,
                    chat_id=telegram_chat_id,
                    chat_title=chat_title,
                    is_updated=False,
                    has_changes=False,
                    changes={},
                    current_status=None,
                    checked_at=datetime.utcnow(),
                    error=f"Telegram API error: {str(e)}"
                )
            except TelegramForbiddenError as e:
                return UserVerificationResult(
                    telegram_user_id=telegram_user_id,
                    chat_id=telegram_chat_id,
                    chat_title=chat_title,
                    is_updated=False,
                    has_changes=False,
                    changes={},
                    current_status=None,
                    checked_at=datetime.utcnow(),
                    error=f"Bot doesn't have access: {str(e)}"
                )

            # Extract user data from chat_member
            telegram_user = chat_member.user
            user_status = chat_member.status

            # Compare data and detect changes
            changes = {}
            has_changes = False

            # Check first_name
            old_first_name = current_user.first_name if current_user else None
            new_first_name = telegram_user.first_name
            if old_first_name != new_first_name:
                changes["first_name"] = UserChangeDetail(
                    old_value=old_first_name,
                    new_value=new_first_name
                )
                has_changes = True

            # Check last_name
            old_last_name = current_user.last_name if current_user else None
            new_last_name = telegram_user.last_name
            if old_last_name != new_last_name:
                changes["last_name"] = UserChangeDetail(
                    old_value=old_last_name,
                    new_value=new_last_name
                )
                has_changes = True

            # Check username
            old_username = current_user.username if current_user else None
            new_username = telegram_user.username
            if old_username != new_username:
                changes["username"] = UserChangeDetail(
                    old_value=old_username,
                    new_value=new_username
                )
                has_changes = True

            # Update data if requested and changes detected
            is_updated = False
            if auto_update and (has_changes or not current_user):
                # Prepare user data for update
                telegram_user_data = TelegramUserData(
                    telegram_user_id=telegram_user.id,
                    is_bot=telegram_user.is_bot,
                    first_name=telegram_user.first_name,
                    last_name=telegram_user.last_name,
                    username=telegram_user.username,
                    language_code=getattr(telegram_user, 'language_code', None),
                    is_premium=getattr(telegram_user, 'is_premium', None),
                    added_to_attachment_menu=getattr(telegram_user, 'added_to_attachment_menu', None),
                    can_join_groups=getattr(telegram_user, 'can_join_groups', None),
                    can_read_all_group_messages=getattr(telegram_user, 'can_read_all_group_messages', None),
                    supports_inline_queries=getattr(telegram_user, 'supports_inline_queries', None),
                    can_connect_to_business=getattr(telegram_user, 'can_connect_to_business', None),
                    has_main_web_app=getattr(telegram_user, 'has_main_web_app', None),
                    account_creation_date=None
                )

                # This will automatically record history changes
                await self.telegram_user_service.create_or_update_user_from_telegram(telegram_user_data)
                is_updated = True

            return UserVerificationResult(
                telegram_user_id=telegram_user_id,
                chat_id=telegram_chat_id,
                chat_title=chat_title,
                is_updated=is_updated,
                has_changes=has_changes,
                changes=changes,
                current_status=user_status,
                checked_at=datetime.utcnow(),
                error=None
            )

        except Exception as e:
            return UserVerificationResult(
                telegram_user_id=telegram_user_id,
                chat_id=telegram_chat_id,
                chat_title=None,
                is_updated=False,
                has_changes=False,
                changes={},
                current_status=None,
                checked_at=datetime.utcnow(),
                error=f"Unexpected error: {str(e)}"
            )

    async def verify_all_active_users(
        self,
        chat_id: Optional[int] = None,
        telegram_user_ids: Optional[List[int]] = None,
        auto_update: bool = True,
        delay_between_requests: float = 0.5
    ) -> BulkVerificationResponse:
        """
        Verify multiple users using Telegram API getChatMember
        
        Args:
            chat_id: Optional database chat ID to filter users
            telegram_user_ids: Optional list of specific user IDs to check
            auto_update: Whether to automatically update user data
            delay_between_requests: Delay in seconds between API requests
            
        Returns:
            BulkVerificationResponse with all verification results
        """
        self.is_running = True
        self.current_progress = 0
        self.checked_users = 0
        self.updated_users = 0
        self.users_with_changes = 0
        self.users_with_errors = 0
        started_at = datetime.utcnow()
        self.started_at = started_at
        results = []

        try:
            # Build query to get active chat members
            query = (
                select(ChatMember, Chat, TelegramUser)
                .join(Chat, ChatMember.chat_id == Chat.id)
                .join(TelegramUser, ChatMember.telegram_user_id == TelegramUser.telegram_user_id)
                .where(ChatMember.status == 'active')
            )

            # Filter by chat if specified
            if chat_id:
                query = query.where(ChatMember.chat_id == chat_id)

            # Filter by specific user IDs if specified
            if telegram_user_ids:
                query = query.where(ChatMember.telegram_user_id.in_(telegram_user_ids))

            # Execute query
            result = await self.db.execute(query)
            members_data = result.all()
            
            # Set total users
            self.total_users = len(members_data)

            # Verify each user
            for idx, (member, chat, telegram_user) in enumerate(members_data, 1):
                # Verify user in this specific chat
                verification_result = await self.verify_user_info(
                    telegram_user_id=member.telegram_user_id,
                    telegram_chat_id=chat.telegram_chat_id,
                    auto_update=auto_update
                )
                results.append(verification_result)
                
                # Update progress tracking
                self.current_progress = idx
                self.checked_users = idx
                if verification_result.is_updated:
                    self.updated_users += 1
                if verification_result.has_changes:
                    self.users_with_changes += 1
                if verification_result.error:
                    self.users_with_errors += 1
                
                # Calculate estimated time remaining
                if idx > 0:
                    elapsed = (datetime.utcnow() - started_at).total_seconds()
                    avg_time_per_user = elapsed / idx
                    remaining_users = self.total_users - idx
                    self.estimated_time_remaining = remaining_users * avg_time_per_user

                # Add delay to avoid rate limiting
                if delay_between_requests > 0:
                    await asyncio.sleep(delay_between_requests)

            # Calculate statistics
            completed_at = datetime.utcnow()
            total_checked = len(results)
            total_updated = sum(1 for r in results if r.is_updated)
            total_errors = sum(1 for r in results if r.error is not None)
            total_with_changes = sum(1 for r in results if r.has_changes)
            duration_seconds = (completed_at - started_at).total_seconds()

            return BulkVerificationResponse(
                total_checked=total_checked,
                total_updated=total_updated,
                total_errors=total_errors,
                total_with_changes=total_with_changes,
                results=results,
                started_at=started_at,
                completed_at=completed_at,
                duration_seconds=duration_seconds
            )

        except Exception as e:
            completed_at = datetime.utcnow()
            duration_seconds = (completed_at - started_at).total_seconds()

            return BulkVerificationResponse(
                total_checked=len(results),
                total_updated=sum(1 for r in results if r.is_updated),
                total_errors=len(results) + 1,  # +1 for the main error
                total_with_changes=sum(1 for r in results if r.has_changes),
                results=results,
                started_at=started_at,
                completed_at=completed_at,
                duration_seconds=duration_seconds
            )
        finally:
            self.is_running = False
            self.estimated_time_remaining = None

    async def get_active_users_with_chats(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> ActiveUsersListResponse:
        """
        Get list of active users with their active chats
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            ActiveUsersListResponse with list of active users
        """
        # Get unique active users with their chats
        query = (
            select(TelegramUser, Chat)
            .join(ChatMember, ChatMember.telegram_user_id == TelegramUser.telegram_user_id)
            .join(Chat, ChatMember.chat_id == Chat.id)
            .where(ChatMember.status == 'active')
            .where(Chat.is_active == True)
        )

        result = await self.db.execute(query)
        all_data = result.all()

        # Group by user
        users_dict: Dict[int, ActiveUserInfo] = {}
        
        for telegram_user, chat in all_data:
            user_id = telegram_user.telegram_user_id
            
            if user_id not in users_dict:
                users_dict[user_id] = ActiveUserInfo(
                    telegram_user_id=user_id,
                    first_name=telegram_user.first_name,
                    last_name=telegram_user.last_name,
                    username=telegram_user.username,
                    is_bot=telegram_user.is_bot,
                    active_chats=[]
                )
            
            # Add chat to user's active chats
            users_dict[user_id].active_chats.append({
                "chat_id": chat.id,
                "telegram_chat_id": chat.telegram_chat_id,
                "title": chat.title,
                "chat_type": chat.chat_type
            })

        # Convert to list and apply pagination
        users_list = list(users_dict.values())
        total = len(users_list)
        paginated_users = users_list[skip:skip + limit]

        return ActiveUsersListResponse(
            users=paginated_users,
            total=total,
            skip=skip,
            limit=limit
        )

    def get_status(self) -> Dict[str, Any]:
        """
        Get current verification status with progress information
        
        Returns:
            Dictionary with current status, progress, and statistics
        """
        if not self.is_running:
            return {
                "is_running": False,
                "current_progress": 0,
                "total_users": 0,
                "checked_users": 0,
                "updated_users": 0,
                "users_with_changes": 0,
                "users_with_errors": 0,
                "progress_percentage": 0,
                "estimated_time_remaining": None,
                "started_at": None
            }
        
        progress_percentage = 0
        if self.total_users > 0:
            progress_percentage = round((self.current_progress / self.total_users) * 100, 2)
        
        return {
            "is_running": self.is_running,
            "current_progress": self.current_progress,
            "total_users": self.total_users,
            "checked_users": self.checked_users,
            "updated_users": self.updated_users,
            "users_with_changes": self.users_with_changes,
            "users_with_errors": self.users_with_errors,
            "progress_percentage": progress_percentage,
            "estimated_time_remaining": self.estimated_time_remaining,
            "started_at": self.started_at.isoformat() if self.started_at else None
        }
