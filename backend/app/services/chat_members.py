"""
Chat members service with business logic
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from typing import List, Optional
from app.models.chat_members import ChatMember
from app.schemas.chat_members import ChatMemberCreate, ChatMemberUpdate, TelegramUserData
from app.utils.account_age import get_account_creation_date


class ChatMemberService:
    """Service class for chat member operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chat_member(self, member_data: ChatMemberCreate) -> ChatMember:
        """Create a new chat member"""
        db_member = ChatMember(**member_data.model_dump())
        self.db.add(db_member)
        await self.db.commit()
        await self.db.refresh(db_member)
        return db_member

    async def get_chat_member(self, member_id: int) -> Optional[ChatMember]:
        """Get chat member by ID"""
        result = await self.db.execute(select(ChatMember).where(ChatMember.id == member_id))
        return result.scalar_one_or_none()

    async def get_chat_member_by_telegram_id(self, chat_id: int, telegram_user_id: int) -> Optional[ChatMember]:
        """Get chat member by chat_id and telegram_user_id"""
        result = await self.db.execute(
            select(ChatMember)
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

    async def create_or_update_member_from_telegram(self, chat_id: int, telegram_user_data: TelegramUserData) -> ChatMember:
        """Create or update chat member from Telegram API data"""
        # Try to find existing member
        db_member = await self.get_chat_member_by_telegram_id(chat_id, telegram_user_data.id)

        # Calculate account creation date if not already known
        account_creation_date = None
        if not db_member or not db_member.account_creation_date:
            try:
                account_creation_date = await get_account_creation_date(telegram_user_data.id)
            except Exception as e:
                print(f"Error calculating account creation date for user {telegram_user_data.id}: {e}")

        if db_member:
            # Update existing member - explicitly set fields, excluding id
            db_member.is_bot = telegram_user_data.is_bot
            db_member.first_name = telegram_user_data.first_name
            db_member.last_name = telegram_user_data.last_name
            db_member.username = telegram_user_data.username
            db_member.language_code = telegram_user_data.language_code
            db_member.is_premium = telegram_user_data.is_premium
            db_member.added_to_attachment_menu = telegram_user_data.added_to_attachment_menu
            db_member.can_join_groups = telegram_user_data.can_join_groups
            db_member.can_read_all_group_messages = telegram_user_data.can_read_all_group_messages
            db_member.supports_inline_queries = telegram_user_data.supports_inline_queries
            db_member.can_connect_to_business = telegram_user_data.can_connect_to_business
            db_member.has_main_web_app = telegram_user_data.has_main_web_app

            # Update account creation date if we calculated it
            if account_creation_date:
                db_member.account_creation_date = account_creation_date
        else:
            # Create new member
            member_data = ChatMemberCreate(
                chat_id=chat_id,
                telegram_user_id=telegram_user_data.id,
                account_creation_date=account_creation_date,
                **telegram_user_data.model_dump()
            )
            db_member = ChatMember(**member_data.model_dump())
            self.db.add(db_member)

        await self.db.commit()
        await self.db.refresh(db_member)
        return db_member

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
