"""
Chat moderators service with business logic
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete
from typing import List, Optional, Dict, Any
from app.models.chat_moderators import ChatModerator
from app.models.chats import Chat
from app.models.users import User
from app.schemas.chat_moderators import ChatModeratorCreate, ChatModeratorUpdate


class ChatModeratorService:
    """Service class for chat moderator operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_moderator(self, moderator_data: ChatModeratorCreate) -> ChatModerator:
        """Create a new chat moderator"""
        # Check if moderator already exists for this chat
        existing = await self.get_moderator_by_user(moderator_data.chat_id, moderator_data.moderator_user_id)
        if existing:
            return existing

        db_moderator = ChatModerator(**moderator_data.model_dump())
        self.db.add(db_moderator)
        await self.db.commit()
        await self.db.refresh(db_moderator)
        return db_moderator

    async def get_moderator(self, moderator_id: int) -> Optional[ChatModerator]:
        """Get moderator by ID"""
        result = await self.db.execute(select(ChatModerator).where(ChatModerator.id == moderator_id))
        return result.scalar_one_or_none()

    async def get_moderator_by_user(self, chat_id: int, moderator_user_id: int) -> Optional[ChatModerator]:
        """Get moderator by chat and user ID"""
        result = await self.db.execute(
            select(ChatModerator).where(
                and_(
                    ChatModerator.chat_id == chat_id,
                    ChatModerator.moderator_user_id == moderator_user_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_chat_moderators(self, chat_id: int) -> List[ChatModerator]:
        """Get all moderators for a specific chat"""
        result = await self.db.execute(
            select(ChatModerator).where(ChatModerator.chat_id == chat_id)
        )
        return result.scalars().all()

    async def get_user_moderator_chats(self, moderator_user_id: int) -> List[ChatModerator]:
        """Get all chats where user is a moderator"""
        result = await self.db.execute(
            select(ChatModerator).where(ChatModerator.moderator_user_id == moderator_user_id)
        )
        return result.scalars().all()

    async def get_all_moderators_with_chat_info(self) -> List[Dict[str, Any]]:
        """Get all moderators with chat information for frontend"""
        result = await self.db.execute(
            select(
                ChatModerator.id,
                ChatModerator.chat_id,
                Chat.title.label('chat_title'),
                ChatModerator.moderator_user_id,
                ChatModerator.username.label('moderator_username'),
                func.concat(ChatModerator.first_name, ' ', func.coalesce(ChatModerator.last_name, '')).label('moderator_name'),
                ChatModerator.added_by_user_id,
                User.username.label('added_by_username'),
                User.first_name.label('added_by_first_name'),
                User.last_name.label('added_by_last_name'),
                ChatModerator.created_at.label('added_date')
            )
            .select_from(ChatModerator)
            .join(Chat, ChatModerator.chat_id == Chat.id)
            .join(User, ChatModerator.added_by_user_id == User.id)
            .order_by(ChatModerator.created_at.desc())
        )

        moderators = []
        for row in result:
            moderator = {
                'id': row.id,
                'chat_id': row.chat_id,
                'chat_title': row.chat_title or f'Chat {row.chat_id}',
                'moderator_user_id': row.moderator_user_id,
                'moderator_username': row.moderator_username,
                'moderator_name': row.moderator_name.strip(),
                'added_by_user_id': row.added_by_user_id,
                'added_by_username': row.added_by_username,
                'added_by_first_name': row.added_by_first_name,
                'added_by_last_name': row.added_by_last_name,
                'added_date': row.added_date.isoformat() if row.added_date else None
            }
            moderators.append(moderator)

        return moderators

    async def update_moderator(self, moderator_id: int, moderator_data: ChatModeratorUpdate) -> Optional[ChatModerator]:
        """Update moderator information"""
        db_moderator = await self.get_moderator(moderator_id)
        if not db_moderator:
            return None

        for field, value in moderator_data.model_dump(exclude_unset=True).items():
            setattr(db_moderator, field, value)

        await self.db.commit()
        await self.db.refresh(db_moderator)
        return db_moderator

    async def remove_moderator(self, moderator_id: int) -> bool:
        """Remove a moderator from chat"""
        db_moderator = await self.get_moderator(moderator_id)
        if not db_moderator:
            return False

        await self.db.delete(db_moderator)
        await self.db.commit()
        return True

    async def remove_moderator_by_user(self, chat_id: int, moderator_user_id: int) -> bool:
        """Remove moderator by chat and user ID"""
        result = await self.db.execute(
            delete(ChatModerator).where(
                and_(
                    ChatModerator.chat_id == chat_id,
                    ChatModerator.moderator_user_id == moderator_user_id
                )
            )
        )
        await self.db.commit()
        return result.rowcount > 0

    async def is_user_moderator(self, chat_id: int, moderator_user_id: int) -> bool:
        """Check if user is a moderator in the chat"""
        moderator = await self.get_moderator_by_user(chat_id, moderator_user_id)
        return moderator is not None

    async def can_user_manage_moderators(self, chat_id: int, user_id: int) -> bool:
        """Check if user can manage moderators for this chat (chat owner)"""
        result = await self.db.execute(
            select(Chat).where(
                and_(
                    Chat.id == chat_id,
                    Chat.added_by_user_id == user_id,
                    Chat.is_active == True
                )
            )
        )
        chat = result.scalar_one_or_none()
        return chat is not None
