"""
Service for managing chat-channel linking in Telegram bot
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Tuple
from aiogram.types import Message

from app.models.chats import Chat
from app.services.chats import ChatService
from app.services.users import UserService
from app.telegram.utils.constants import ChannelLinkingMessages


class ChatLinkingService:
    """Service for handling chat-channel linking operations in bot"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.chat_service = ChatService(db)
        self.user_service = UserService(db)

    async def get_user_chats_for_management(self, user_telegram_id: int) -> List[Chat]:
        """
        Get group chats that user can manage (chats where they added the bot)
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

        # Load linked channels for display
        for chat in chats:
            linked_channel = await self.chat_service.get_linked_channel(chat.id)
            if linked_channel:
                chat.linked_channel = linked_channel

        return chats

    async def validate_channel_access_for_user(self, user_telegram_id: int, channel_telegram_id: int) -> Tuple[bool, str]:
        """
        Validate if user has access to link a specific channel
        Returns (is_valid, error_message)
        """
        # Get user from database
        user = await self.user_service.get_user_by_telegram_id(user_telegram_id)
        if not user:
            return False, ChannelLinkingMessages.USER_NOT_FOUND

        # Check if channel exists in database and user has access to it
        channel = await self.chat_service.get_chat_by_telegram_id(channel_telegram_id)
        if not channel:
            return False, ChannelLinkingMessages.CHANNEL_NOT_FOUND

        if channel.chat_type != 'channel':
            return False, ChannelLinkingMessages.NOT_A_CHANNEL

        if channel.added_by_user_id != user.id:
            return False, ChannelLinkingMessages.NO_CHANNEL_ACCESS

        if not channel.is_active:
            return False, ChannelLinkingMessages.CHANNEL_INACTIVE

        return True, ""

    async def extract_channel_from_forwarded_message(self, message: Message) -> Optional[int]:
        """
        Extract channel ID from forwarded message
        Returns telegram_chat_id of the channel if message is forwarded from channel
        """
        # Check if message is forwarded
        if not message.forward_origin:
            return None

        # Handle different types of forward origins
        if hasattr(message.forward_origin, 'chat'):
            # For regular forwarded messages
            chat = message.forward_origin.chat
        elif hasattr(message.forward_origin, 'sender_chat'):
            # For messages forwarded from channels
            chat = message.forward_origin.sender_chat
        else:
            return None

        # Check if it's from a channel
        if chat.type != 'channel':
            return None

        return chat.id

    async def link_channel_to_chat(self, chat_id: int, channel_telegram_id: int, user_telegram_id: int) -> Tuple[bool, str]:
        """
        Link a channel to a chat
        Returns (success, message)
        """
        # Validate channel access
        is_valid, error_msg = await self.validate_channel_access_for_user(user_telegram_id, channel_telegram_id)
        if not is_valid:
            return False, error_msg

        # Get channel from database
        channel = await self.chat_service.get_chat_by_telegram_id(channel_telegram_id)
        if not channel:
            return False, ChannelLinkingMessages.CHAT_NOT_FOUND

        # Link channel to chat
        success = await self.chat_service.link_channel_to_chat(chat_id, channel.id)
        if not success:
            return False, ChannelLinkingMessages.LINKING_FAILED

        # Get chat info for response
        chat = await self.chat_service.get_chat(chat_id)

        return True, ChannelLinkingMessages.LINKING_SUCCESS_TEMPLATE.format(
            channel_name=channel.title or 'Без названия',
            chat_name=chat.title or 'Без названия'
        )

    async def unlink_channel_from_chat(self, chat_id: int, user_telegram_id: int) -> Tuple[bool, str]:
        """
        Unlink channel from a chat
        Returns (success, message)
        """
        # Get user
        user = await self.user_service.get_user_by_telegram_id(user_telegram_id)
        if not user:
            return False, ChannelLinkingMessages.USER_NOT_FOUND_SYSTEM

        # Check if user owns the chat
        chat = await self.chat_service.get_chat(chat_id)
        if not chat or chat.added_by_user_id != user.id:
            return False, ChannelLinkingMessages.NO_CHAT_ACCESS

        # Get current linked channel for message
        linked_channel = await self.chat_service.get_linked_channel(chat_id)
        channel_name = linked_channel.title or 'Без названия' if linked_channel else 'канал'

        # Unlink
        success = await self.chat_service.unlink_channel_from_chat(chat_id)
        if not success:
            return False, ChannelLinkingMessages.UNLINKING_FAILED

        return True, ChannelLinkingMessages.UNLINKING_SUCCESS_TEMPLATE.format(
            channel_name=channel_name,
            chat_name=chat.title or 'Без названия'
        )
