"""
Manager chat access service
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.manager_chat_access import ManagerChatAccess
from app.models.chats import Chat
from app.schemas.manager_chat_access import ManagerChatAccessCreate, ManagerChatAccessBulkCreate, ManagerChatInfo


class ManagerChatAccessService:
    """Service for managing manager chat access"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def assign_chat_to_manager(self, access_data: ManagerChatAccessCreate) -> ManagerChatAccess:
        """Assign a chat to a manager"""
        access = ManagerChatAccess(**access_data.model_dump())
        self.db.add(access)
        await self.db.commit()
        await self.db.refresh(access)
        return access

    async def assign_chats_to_manager(self, access_data: ManagerChatAccessBulkCreate) -> List[ManagerChatAccess]:
        """Assign multiple chats to a manager"""
        # First, remove all existing access for this manager
        await self.db.execute(
            delete(ManagerChatAccess).where(
                ManagerChatAccess.admin_user_id == access_data.admin_user_id
            )
        )
        
        # Then add new accesses
        accesses = []
        for chat_id in access_data.chat_ids:
            access = ManagerChatAccess(
                admin_user_id=access_data.admin_user_id,
                chat_id=chat_id
            )
            self.db.add(access)
            accesses.append(access)
        
        await self.db.commit()
        
        # Refresh all accesses
        for access in accesses:
            await self.db.refresh(access)
        
        return accesses

    async def get_manager_chats(self, admin_user_id: int) -> List[ManagerChatInfo]:
        """Get all chats assigned to a manager"""
        result = await self.db.execute(
            select(ManagerChatAccess, Chat)
            .join(Chat, ManagerChatAccess.chat_id == Chat.id)
            .where(ManagerChatAccess.admin_user_id == admin_user_id)
        )
        
        chats = []
        for access, chat in result:
            chats.append(ManagerChatInfo(
                chat_id=chat.id,
                telegram_chat_id=chat.telegram_chat_id,
                chat_title=chat.title,
                chat_type=chat.chat_type
            ))
        
        return chats

    async def get_manager_chat_ids(self, admin_user_id: int) -> List[int]:
        """Get list of chat IDs assigned to a manager"""
        result = await self.db.execute(
            select(ManagerChatAccess.chat_id)
            .where(ManagerChatAccess.admin_user_id == admin_user_id)
        )
        return result.scalars().all()

    async def remove_chat_access(self, admin_user_id: int, chat_id: int) -> bool:
        """Remove manager's access to a specific chat"""
        result = await self.db.execute(
            delete(ManagerChatAccess).where(
                ManagerChatAccess.admin_user_id == admin_user_id,
                ManagerChatAccess.chat_id == chat_id
            )
        )
        await self.db.commit()
        return result.rowcount > 0

    async def has_chat_access(self, admin_user_id: int, chat_id: int) -> bool:
        """Check if manager has access to a specific chat"""
        result = await self.db.execute(
            select(ManagerChatAccess).where(
                ManagerChatAccess.admin_user_id == admin_user_id,
                ManagerChatAccess.chat_id == chat_id
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_chat_managers(self, chat_id: int) -> List[int]:
        """Get list of manager IDs who have access to a chat"""
        result = await self.db.execute(
            select(ManagerChatAccess.admin_user_id)
            .where(ManagerChatAccess.chat_id == chat_id)
        )
        return result.scalars().all()
