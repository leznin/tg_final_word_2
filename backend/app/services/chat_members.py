"""
Chat members service with business logic
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from app.models.chat_members import ChatMember
from app.schemas.chat_members import ChatMemberCreate, ChatMemberUpdate
from app.schemas.telegram_users import TelegramUserData
from app.services.telegram_users import TelegramUserService


class ChatMemberService:
    """Service class for chat member operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chat_member(self, member_data: ChatMemberCreate) -> ChatMember:
        """Create a new chat member"""
        db_member = ChatMember(**member_data.model_dump())
        self.db.add(db_member)
        await self.db.commit()
        # Don't refresh to avoid triggering lazy-loaded relationships
        # await self.db.refresh(db_member)
        return db_member

    async def get_chat_member(self, member_id: int) -> Optional[ChatMember]:
        """Get chat member by ID"""
        result = await self.db.execute(select(ChatMember).where(ChatMember.id == member_id))
        return result.scalar_one_or_none()

    async def get_chat_member_by_telegram_id(self, chat_id: int, telegram_user_id: int) -> Optional[ChatMember]:
        """Get chat member by chat_id and telegram_user_id with telegram_user data"""
        result = await self.db.execute(
            select(ChatMember)
            .options(selectinload(ChatMember.telegram_user))
            .where(ChatMember.chat_id == chat_id)
            .where(ChatMember.telegram_user_id == telegram_user_id)
        )
        return result.scalar_one_or_none()

    async def get_chat_members(self, chat_id: int, skip: int = 0, limit: int = 100) -> List[ChatMember]:
        """Get all members of a specific chat"""
        result = await self.db.execute(
            select(ChatMember)
            .where(ChatMember.chat_id == chat_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_chat_members_with_search(self, chat_id: int, skip: int = 0, limit: int = 30, search: str = "") -> List[ChatMember]:
        """Get members of a specific chat with search functionality"""
        from app.models.telegram_users import TelegramUser
        from sqlalchemy import Text, cast

        query = select(ChatMember).join(TelegramUser).options(selectinload(ChatMember.telegram_user)).where(ChatMember.chat_id == chat_id)

        # Add search conditions if search parameter is provided
        if search:
            search_filter = or_(
                TelegramUser.first_name.ilike(f"%{search}%"),
                TelegramUser.last_name.ilike(f"%{search}%"),
                TelegramUser.username.ilike(f"%{search}%"),
                cast(ChatMember.telegram_user_id, Text).ilike(f"%{search}%")
            )
            query = query.where(search_filter)

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_chat_member(self, member_id: int, member_data: ChatMemberUpdate) -> Optional[ChatMember]:
        """Update chat member"""
        db_member = await self.get_chat_member(member_id)
        if not db_member:
            return None

        for field, value in member_data.model_dump(exclude_unset=True).items():
            setattr(db_member, field, value)

        await self.db.commit()
        await self.db.refresh(db_member)
        return db_member

    async def create_or_update_member_from_telegram(self, chat_id: int, telegram_user_data: TelegramUserData, bot=None) -> ChatMember:
        """Create or update chat member from Telegram API data"""
        # First, create or update the telegram user
        telegram_user_service = TelegramUserService(self.db, bot)
        telegram_user = await telegram_user_service.create_or_update_user_from_telegram(telegram_user_data)

        # Then, check if the chat membership already exists
        db_member = await self.get_chat_member_by_telegram_id(chat_id, telegram_user_data.telegram_user_id)

        if not db_member:
            # Create new chat membership
            member_data = ChatMemberCreate(
                chat_id=chat_id,
                telegram_user_id=telegram_user_data.telegram_user_id
            )
            db_member = ChatMember(**member_data.model_dump())
            self.db.add(db_member)
        else:
            # Update existing membership - set status to active and clear left_at
            db_member.status = 'active'
            db_member.left_at = None  # Clear the left timestamp since user is back

        await self.db.commit()
        # Don't refresh to avoid triggering lazy-loaded relationships
        # await self.db.refresh(db_member)
        return db_member


    async def update_member_status(self, chat_id: int, telegram_user_id: int, status: str, left_at: datetime = None) -> Optional[ChatMember]:
        """Update member status (left, banned, kicked)"""
        db_member = await self.get_chat_member_by_telegram_id(chat_id, telegram_user_id)

        if db_member:
            db_member.status = status
            if left_at:
                db_member.left_at = left_at
            elif status in ['left', 'banned', 'kicked']:
                db_member.left_at = datetime.now()

            await self.db.commit()
            # Don't refresh to avoid triggering lazy-loaded relationships
            # await self.db.refresh(db_member)


        return db_member

    async def remove_member_from_chat(self, chat_id: int, telegram_user_id: int, reason: str = 'left') -> bool:
        """Mark member as removed from chat (left, banned, or kicked)"""
        return await self.update_member_status(chat_id, telegram_user_id, reason) is not None

    async def delete_chat_member(self, member_id: int) -> bool:
        """Delete chat member (though we typically don't delete members, just update)"""
        db_member = await self.get_chat_member(member_id)
        if not db_member:
            return False

        await self.db.delete(db_member)
        await self.db.commit()
        return True

    async def get_member_count(self, chat_id: int) -> int:
        """Get count of members in a chat"""
        result = await self.db.execute(
            select(func.count(ChatMember.id))
            .where(ChatMember.chat_id == chat_id)
        )
        return result.scalar()
