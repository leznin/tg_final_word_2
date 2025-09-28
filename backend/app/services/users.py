"""
User service with business logic
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from app.models.users import User
from app.models.chats import Chat
from app.models.chat_moderators import ChatModerator
from app.schemas.users import UserCreate, UserUpdate, TelegramUserData, UserWithChatsResponse
from app.schemas.chats import ChatWithLinkedChannelResponse, ChannelWithAdmin


class UserService:
    """Service class for user operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        db_user = User(**user_data.model_dump())
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        result = await self.db.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        result = await self.db.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user"""
        db_user = await self.get_user(user_id)
        if not db_user:
            return None

        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(db_user, field, value)

        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        db_user = await self.get_user(user_id)
        if not db_user:
            return False

        await self.db.delete(db_user)
        await self.db.commit()
        return True

    async def create_or_update_telegram_user(self, telegram_user_data: TelegramUserData) -> User:
        """Create or update user from Telegram API data"""
        # Try to find existing user by telegram_id
        db_user = await self.get_user_by_telegram_id(telegram_user_data.id)

        if db_user:
            # Update existing user
            db_user.first_name = telegram_user_data.first_name
            db_user.last_name = telegram_user_data.last_name
            db_user.username = telegram_user_data.username
            db_user.language_code = telegram_user_data.language_code
            if telegram_user_data.is_premium is not None:
                db_user.is_premium = telegram_user_data.is_premium
            if telegram_user_data.is_bot is not None:
                db_user.is_bot = telegram_user_data.is_bot
            # If user was blocked before, restore ability to send messages
            if not db_user.can_send_messages:
                db_user.can_send_messages = True
                db_user.blocked_at = None
        else:
            # Create new user
            db_user = User(
                telegram_id=telegram_user_data.id,
                first_name=telegram_user_data.first_name,
                last_name=telegram_user_data.last_name,
                username=telegram_user_data.username,
                language_code=telegram_user_data.language_code,
                is_premium=telegram_user_data.is_premium if telegram_user_data.is_premium is not None else False,
                is_bot=telegram_user_data.is_bot if telegram_user_data.is_bot is not None else False,
                can_send_messages=True
            )
            self.db.add(db_user)

        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def block_user(self, telegram_id: int) -> bool:
        """Block user (set can_send_messages to False)"""
        db_user = await self.get_user_by_telegram_id(telegram_id)
        if not db_user:
            return False

        db_user.can_send_messages = False
        db_user.blocked_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(db_user)
        return True

    async def get_users_with_chats(self, skip: int = 0, limit: int = 100) -> List[UserWithChatsResponse]:
        """Get all users with their chats information including linked channels and moderators"""
        # Get all users with pagination
        users_result = await self.db.execute(
            select(User).offset(skip).limit(limit)
        )
        users = users_result.scalars().all()

        result = []
        for user in users:
            user_data = UserWithChatsResponse.model_validate(user)

            # Get all chats added by this user
            chats_result = await self.db.execute(
                select(Chat)
                .where(Chat.added_by_user_id == user.id)
                .where(Chat.is_active == True)
            )
            chats = chats_result.scalars().all()

            # Process each chat to add linked channel and moderator info
            chats_data = []
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
                    linked_channel = await self.db.execute(
                        select(Chat).where(Chat.id == chat.linked_channel_id)
                    )
                    linked_channel = linked_channel.scalar_one_or_none()

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

                chats_data.append(chat_data)

            user_data.chats = chats_data
            result.append(user_data)

        return result
