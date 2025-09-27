"""
Service for managing chat moderators in Telegram bot
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Tuple
from aiogram.types import Message

from app.models.chats import Chat
from app.models.chat_moderators import ChatModerator
from app.services.chats import ChatService
from app.services.users import UserService
from app.services.chat_moderators import ChatModeratorService
from app.schemas.chat_moderators import ChatModeratorCreate


class ModeratorManagementService:
    """Service for handling chat moderator operations in bot"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.chat_service = ChatService(db)
        self.user_service = UserService(db)
        self.moderator_service = ChatModeratorService(db)

    async def get_user_chats_for_moderator_management(self, user_telegram_id: int) -> List[Chat]:
        """
        Get group chats that user can manage moderators for (chats where they added the bot)
        Only returns group and supergroup chats, excludes channels
        """
        # First get user from database
        user = await self.user_service.get_user_by_telegram_id(user_telegram_id)
        if not user:
            return []

        # Get all chats added by this user
        all_chats = await self.chat_service.get_chats_by_user(user.id)

        # Filter to only include group and supergroup chats (exclude channels)
        chats = [chat for chat in all_chats if chat.chat_type in ['group', 'supergroup']]

        # Load moderators count for display
        for chat in chats:
            moderators = await self.moderator_service.get_chat_moderators(chat.id)
            chat.moderators_count = len(moderators)

        return chats

    async def extract_user_from_forwarded_message(self, message: Message) -> Optional[dict]:
        """
        Extract user information from forwarded message
        Returns user data dict if message is forwarded from a user
        """
        # Check if message is forwarded
        if not message.forward_origin:
            return None

        # Handle different types of forward origins
        if hasattr(message.forward_origin, 'sender_user'):
            # For messages forwarded from users
            user = message.forward_origin.sender_user
        elif hasattr(message.forward_origin, 'sender_chat') and message.forward_origin.sender_chat.type == 'private':
            # For messages forwarded from private chats (users)
            chat = message.forward_origin.sender_chat
            # Create a mock user object from chat info
            user = type('User', (), {
                'id': chat.id,
                'first_name': chat.first_name,
                'last_name': chat.last_name,
                'username': chat.username,
                'is_bot': False
            })()
        else:
            return None

        # Return user information
        return {
            'id': user.id,
            'first_name': getattr(user, 'first_name', None),
            'last_name': getattr(user, 'last_name', None),
            'username': getattr(user, 'username', None),
            'is_bot': getattr(user, 'is_bot', False)
        }

    async def add_moderator_from_forwarded_message(
        self,
        chat_id: int,
        user_telegram_id: int,
        forwarded_user_data: dict
    ) -> Tuple[bool, str]:
        """
        Add a moderator to a chat from forwarded message data
        Returns (success, message)
        """
        # Get user who is adding the moderator
        user = await self.user_service.get_user_by_telegram_id(user_telegram_id)
        if not user:
            return False, "Пользователь не найден в системе"

        # Check if user can manage moderators for this chat
        can_manage = await self.moderator_service.can_user_manage_moderators(chat_id, user.id)
        if not can_manage:
            return False, "У вас нет прав для управления модераторами этого чата"

        # Check if the forwarded user is not a bot
        if forwarded_user_data.get('is_bot', False):
            return False, "Нельзя назначить бота модератором"

        # Check if user is trying to add themselves
        if forwarded_user_data['id'] == user_telegram_id:
            return False, "Нельзя назначить самого себя модератором"

        # Get chat info for messages
        chat = await self.chat_service.get_chat(chat_id)
        if not chat:
            return False, "Чат не найден"

        # Create moderator
        moderator_data = ChatModeratorCreate(
            chat_id=chat_id,
            moderator_user_id=forwarded_user_data['id'],
            first_name=forwarded_user_data.get('first_name'),
            last_name=forwarded_user_data.get('last_name'),
            username=forwarded_user_data.get('username'),
            added_by_user_id=user.id
        )

        moderator = await self.moderator_service.create_moderator(moderator_data)

        # Create success message
        moderator_name = self._format_user_name(forwarded_user_data)
        chat_name = chat.title or 'Без названия'

        return True, f"✅ Пользователь {moderator_name} назначен модератором в чате '{chat_name}'"

    async def get_chat_moderators_for_display(self, chat_id: int, user_telegram_id: int) -> Tuple[List[ChatModerator], str]:
        """
        Get moderators for a chat with permission check
        Returns (moderators, error_message)
        """
        # Get user
        user = await self.user_service.get_user_by_telegram_id(user_telegram_id)
        if not user:
            return [], "Пользователь не найден в системе"

        # Check permissions
        can_manage = await self.moderator_service.can_user_manage_moderators(chat_id, user.id)
        if not can_manage:
            return [], "У вас нет прав для просмотра модераторов этого чата"

        # Get moderators
        moderators = await self.moderator_service.get_chat_moderators(chat_id)
        return moderators, ""

    async def remove_moderator(
        self,
        chat_id: int,
        moderator_user_id: int,
        user_telegram_id: int
    ) -> Tuple[bool, str]:
        """
        Remove a moderator from chat
        Returns (success, message)
        """
        # Get user who is removing the moderator
        user = await self.user_service.get_user_by_telegram_id(user_telegram_id)
        if not user:
            return False, "Пользователь не найден в системе"

        # Check if user can manage moderators for this chat
        can_manage = await self.moderator_service.can_user_manage_moderators(chat_id, user.id)
        if not can_manage:
            return False, "У вас нет прав для управления модераторами этого чата"

        # Get chat info
        chat = await self.chat_service.get_chat(chat_id)
        if not chat:
            return False, "Чат не найден"

        # Get moderator info before removal
        moderator = await self.moderator_service.get_moderator_by_user(chat_id, moderator_user_id)
        if not moderator:
            return False, "Модератор не найден"

        # Remove moderator
        success = await self.moderator_service.remove_moderator_by_user(chat_id, moderator_user_id)
        if not success:
            return False, "Не удалось удалить модератора"

        # Create success message
        moderator_name = self._format_moderator_name(moderator)
        chat_name = chat.title or 'Без названия'

        return True, f"✅ Модератор {moderator_name} удален из чата '{chat_name}'"

    def _format_user_name(self, user_data: dict) -> str:
        """Format user name from forwarded message data"""
        first_name = user_data.get('first_name', '')
        last_name = user_data.get('last_name', '')
        username = user_data.get('username', '')

        name_parts = [first_name, last_name]
        display_name = ' '.join(filter(None, name_parts)).strip()

        if username:
            display_name += f" (@{username})"

        if not display_name:
            display_name = f"ID: {user_data['id']}"

        return display_name

    def _format_moderator_name(self, moderator: ChatModerator) -> str:
        """Format moderator name from database record"""
        first_name = moderator.first_name or ''
        last_name = moderator.last_name or ''
        username = moderator.username or ''

        name_parts = [first_name, last_name]
        display_name = ' '.join(filter(None, name_parts)).strip()

        if username:
            display_name += f" (@{username})"

        if not display_name:
            display_name = f"ID: {moderator.moderator_user_id}"

        return display_name
