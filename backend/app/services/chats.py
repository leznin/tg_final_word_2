"""
Chat service with business logic
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from app.models.chats import Chat
from app.models.users import User
from app.models.chat_moderators import ChatModerator
from app.schemas.chats import ChatCreate, ChatUpdate, TelegramChatData, LinkedChannelInfo, ChatWithLinkedChannelResponse, ChannelWithAdmin


class ChatService:
    """Service class for chat operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chat(self, chat_data: ChatCreate) -> Chat:
        """Create a new chat"""
        db_chat = Chat(**chat_data.model_dump())
        self.db.add(db_chat)
        await self.db.commit()
        await self.db.refresh(db_chat)
        return db_chat

    async def get_chat(self, chat_id: int) -> Optional[Chat]:
        """Get chat by ID"""
        result = await self.db.execute(select(Chat).where(Chat.id == chat_id))
        return result.scalar_one_or_none()

    async def get_chat_by_telegram_id(self, telegram_chat_id: int) -> Optional[Chat]:
        """Get chat by Telegram chat ID"""
        result = await self.db.execute(select(Chat).where(Chat.telegram_chat_id == telegram_chat_id))
        return result.scalar_one_or_none()

    async def get_chats_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Chat]:
        """Get all chats added by a specific user"""
        result = await self.db.execute(
            select(Chat)
            .where(Chat.added_by_user_id == user_id)
            .where(Chat.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_all_chats(self, skip: int = 0, limit: int = 100) -> List[Chat]:
        """Get all active chats with pagination"""
        result = await self.db.execute(
            select(Chat)
            .where(Chat.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def update_chat(self, chat_id: int, chat_data: ChatUpdate) -> Optional[Chat]:
        """Update chat"""
        db_chat = await self.get_chat(chat_id)
        if not db_chat:
            return None

        for field, value in chat_data.model_dump(exclude_unset=True).items():
            setattr(db_chat, field, value)

        await self.db.commit()
        await self.db.refresh(db_chat)
        return db_chat

    async def deactivate_chat(self, telegram_chat_id: int) -> bool:
        """Deactivate chat (when bot is removed)"""
        db_chat = await self.get_chat_by_telegram_id(telegram_chat_id)
        if not db_chat:
            return False

        db_chat.is_active = False
        await self.db.commit()
        await self.db.refresh(db_chat)
        return True

    async def create_or_update_chat_from_telegram(self, telegram_chat_data: TelegramChatData, added_by_user_id: int) -> Chat:
        """Create or update chat from Telegram API data"""
        # Try to find existing chat by telegram_chat_id (both active and inactive)
        db_chat = await self.get_chat_by_telegram_id(telegram_chat_data.id)

        if db_chat:
            # Update existing chat - never create duplicates for same telegram_chat_id
            db_chat.chat_type = telegram_chat_data.type
            db_chat.title = telegram_chat_data.title
            db_chat.username = telegram_chat_data.username
            db_chat.is_active = True
            # Update who added the bot this time and when
            db_chat.added_by_user_id = added_by_user_id
            db_chat.added_at = func.now()  # Update timestamp to show last addition
        else:
            # Create new chat only if it doesn't exist at all
            db_chat = Chat(
                telegram_chat_id=telegram_chat_data.id,
                chat_type=telegram_chat_data.type,
                title=telegram_chat_data.title,
                username=telegram_chat_data.username,
                added_by_user_id=added_by_user_id,
                is_active=True
            )
            self.db.add(db_chat)

        await self.db.commit()
        await self.db.refresh(db_chat)
        return db_chat

    async def link_channel_to_chat(self, chat_id: int, channel_id: int) -> bool:
        """Link a channel to a chat for message forwarding"""
        # Verify that channel exists and is actually a channel
        channel = await self.get_chat(channel_id)
        if not channel or channel.chat_type != 'channel':
            return False

        # Verify that chat exists and is not a channel
        chat = await self.get_chat(chat_id)
        if not chat or chat.chat_type == 'channel':
            return False

        # Update chat with linked channel
        chat.linked_channel_id = channel_id
        await self.db.commit()
        await self.db.refresh(chat)
        return True

    async def unlink_channel_from_chat(self, chat_id: int) -> bool:
        """Remove channel link from a chat"""
        chat = await self.get_chat(chat_id)
        if not chat:
            return False

        chat.linked_channel_id = None
        await self.db.commit()
        await self.db.refresh(chat)
        return True

    async def get_linked_channel(self, chat_id: int) -> Optional[Chat]:
        """Get the linked channel for a chat"""
        chat = await self.get_chat(chat_id)
        if not chat or not chat.linked_channel_id:
            return None

        return await self.get_chat(chat.linked_channel_id)

    async def get_chats_linked_to_channel(self, channel_id: int) -> List[Chat]:
        """Get all chats linked to a specific channel"""
        result = await self.db.execute(
            select(Chat)
            .where(Chat.linked_channel_id == channel_id)
            .where(Chat.is_active == True)
        )
        return result.scalars().all()

    async def get_available_channels_for_user(self, user_id: int) -> List[Chat]:
        """Get all channels that a user can link to their chats"""
        result = await self.db.execute(
            select(Chat)
            .where(Chat.added_by_user_id == user_id)
            .where(Chat.chat_type == 'channel')
            .where(Chat.is_active == True)
        )
        return result.scalars().all()

    async def get_chats_with_linked_channels_info(self, skip: int = 0, limit: int = 100) -> List[ChatWithLinkedChannelResponse]:
        """Get all active chats (groups and supergroups) with linked channel information including admin and moderators"""
        # Get all chats that are groups or supergroups
        chats_result = await self.db.execute(
            select(Chat)
            .where(Chat.is_active == True)
            .where(Chat.chat_type.in_(['group', 'supergroup']))
            .offset(skip)
            .limit(limit)
        )
        chats = chats_result.scalars().all()

        result = []
        for chat in chats:
            chat_data = ChatWithLinkedChannelResponse.model_validate(chat)

            # Get moderators for the chat
            chat_moderators_result = await self.db.execute(
                select(ChatModerator).where(ChatModerator.chat_id == chat.id)
            )
            chat_moderators = chat_moderators_result.scalars().all()

            # Prepare chat moderator info
            chat_moderators_info = []
            for mod in chat_moderators:
                mod_info = {
                    'id': mod.id,
                    'moderator_user_id': mod.moderator_user_id,
                    'first_name': mod.first_name,
                    'last_name': mod.last_name,
                    'username': mod.username,
                    'added_date': mod.created_at.isoformat() if mod.created_at else None
                }
                chat_moderators_info.append(mod_info)

            chat_data.chat_moderators = chat_moderators_info

            if chat.linked_channel_id:
                # Get linked channel information
                linked_channel = await self.get_chat(chat.linked_channel_id)
                if linked_channel:
                    # Get admin information for the channel
                    admin_result = await self.db.execute(
                        select(User).where(User.id == linked_channel.added_by_user_id)
                    )
                    admin = admin_result.scalar_one_or_none()

                    # Create channel info with admin
                    channel_info = ChannelWithAdmin(
                        id=linked_channel.id,
                        telegram_chat_id=linked_channel.telegram_chat_id,
                        title=linked_channel.title,
                        username=linked_channel.username,
                        admin_user_id=linked_channel.added_by_user_id,
                        admin_username=admin.username if admin else None,
                        admin_name=f"{admin.first_name or ''} {admin.last_name or ''}".strip() if admin else None
                    )

                    chat_data.linked_channel_info = channel_info

            result.append(chat_data)

        return result
