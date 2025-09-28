"""
Admin chats service with business logic for admin panel
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Dict, Any
from app.models.chats import Chat
from app.models.chat_moderators import ChatModerator
from app.models.users import User
from app.schemas.chats import ChatWithUserResponse


class AdminChatsService:
    """Service class for admin panel chat operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_chats_with_stats(self) -> List[Dict[str, Any]]:
        """Get all chats with additional statistics for admin panel"""
        # Get all chats with user information
        result = await self.db.execute(
            select(Chat, User.username, User.email)
            .join(User, Chat.added_by_user_id == User.id)
            .where(Chat.is_active == True)
            .order_by(Chat.created_at.desc())
        )

        chats_data = []
        for chat, user_username, user_email in result:
            # Get moderator count for this chat
            moderator_result = await self.db.execute(
                select(func.count(ChatModerator.id))
                .where(ChatModerator.chat_id == chat.id)
            )
            moderator_count = moderator_result.scalar() or 0

            # Get linked channel info if exists
            linked_channel_info = None
            if chat.linked_channel_id:
                linked_result = await self.db.execute(
                    select(Chat.title, Chat.username)
                    .where(Chat.id == chat.linked_channel_id)
                )
                linked_data = linked_result.first()
                if linked_data:
                    linked_channel_info = {
                        "title": linked_data.title,
                        "username": linked_data.username
                    }

            chat_data = {
                "id": chat.id,
                "telegram_chat_id": chat.telegram_chat_id,
                "chat_type": chat.chat_type,
                "title": chat.title,
                "username": chat.username,
                "added_by_user": {
                    "id": chat.added_by_user_id,
                    "username": user_username,
                    "email": user_email
                },
                "added_at": chat.added_at.isoformat() if chat.added_at else None,
                "created_at": chat.created_at.isoformat() if chat.created_at else None,
                "updated_at": chat.updated_at.isoformat() if chat.updated_at else None,
                "is_active": chat.is_active,
                "linked_channel_id": chat.linked_channel_id,
                "linked_channel": linked_channel_info,
                "message_edit_timeout_minutes": chat.message_edit_timeout_minutes,
                "moderator_count": moderator_count
            }
            chats_data.append(chat_data)

        return chats_data

    async def get_chat_stats_summary(self) -> Dict[str, int]:
        """Get summary statistics for chats"""
        # Total chats by type
        total_groups = await self._count_chats_by_type('group')
        total_supergroups = await self._count_chats_by_type('supergroup')
        total_channels = await self._count_chats_by_type('channel')
        total_all = total_groups + total_supergroups + total_channels

        # Chats with linked channels
        linked_result = await self.db.execute(
            select(func.count(Chat.id))
            .where(Chat.is_active == True)
            .where(Chat.linked_channel_id.isnot(None))
        )
        chats_with_channels = linked_result.scalar() or 0

        # Chats with moderators
        moderated_result = await self.db.execute(
            select(func.count(func.distinct(ChatModerator.chat_id)))
        )
        chats_with_moderators = moderated_result.scalar() or 0

        # Chats with message edit timeout
        edit_timeout_result = await self.db.execute(
            select(func.count(Chat.id))
            .where(Chat.is_active == True)
            .where(Chat.message_edit_timeout_minutes.isnot(None))
        )
        chats_with_edit_timeout = edit_timeout_result.scalar() or 0

        return {
            "total_chats": total_all,
            "groups": total_groups,
            "supergroups": total_supergroups,
            "channels": total_channels,
            "chats_with_linked_channels": chats_with_channels,
            "chats_with_moderators": chats_with_moderators,
            "chats_with_edit_timeout": chats_with_edit_timeout
        }

    async def _count_chats_by_type(self, chat_type: str) -> int:
        """Helper method to count chats by type"""
        result = await self.db.execute(
            select(func.count(Chat.id))
            .where(Chat.is_active == True)
            .where(Chat.chat_type == chat_type)
        )
        return result.scalar() or 0

    async def get_chat_detail_for_admin(self, chat_id: int) -> Dict[str, Any]:
        """Get detailed chat information for admin panel"""
        # Get chat with user info
        result = await self.db.execute(
            select(Chat, User.username, User.email)
            .join(User, Chat.added_by_user_id == User.id)
            .where(Chat.id == chat_id)
        )

        chat_data = result.first()
        if not chat_data:
            return None

        chat, user_username, user_email = chat_data

        # Get moderators
        moderators_result = await self.db.execute(
            select(ChatModerator, User.username.label('moderator_username'),
                   User.first_name, User.last_name)
            .join(User, ChatModerator.moderator_user_id == User.id)
            .where(ChatModerator.chat_id == chat.id)
            .order_by(ChatModerator.created_at.desc())
        )

        moderators = []
        for mod, mod_username, first_name, last_name in moderators_result:
            moderators.append({
                "id": mod.id,
                "moderator_user_id": mod.moderator_user_id,
                "moderator_username": mod_username,
                "first_name": first_name,
                "last_name": last_name,
                "added_by_user_id": mod.added_by_user_id,
                "created_at": mod.created_at.isoformat() if mod.created_at else None,
                "updated_at": mod.updated_at.isoformat() if mod.updated_at else None
            })

        # Get linked channel info
        linked_channel = None
        if chat.linked_channel_id:
            linked_result = await self.db.execute(
                select(Chat.id, Chat.telegram_chat_id, Chat.title, Chat.username)
                .where(Chat.id == chat.linked_channel_id)
            )
            linked_data = linked_result.first()
            if linked_data:
                linked_channel = {
                    "id": linked_data.id,
                    "telegram_chat_id": linked_data.telegram_chat_id,
                    "title": linked_data.title,
                    "username": linked_data.username
                }

        return {
            "id": chat.id,
            "telegram_chat_id": chat.telegram_chat_id,
            "chat_type": chat.chat_type,
            "title": chat.title,
            "username": chat.username,
            "added_by_user": {
                "id": chat.added_by_user_id,
                "username": user_username,
                "email": user_email
            },
            "added_at": chat.added_at.isoformat() if chat.added_at else None,
            "created_at": chat.created_at.isoformat() if chat.created_at else None,
            "updated_at": chat.updated_at.isoformat() if chat.updated_at else None,
            "is_active": chat.is_active,
            "linked_channel": linked_channel,
            "message_edit_timeout_minutes": chat.message_edit_timeout_minutes,
            "moderators": moderators,
            "moderator_count": len(moderators)
        }
