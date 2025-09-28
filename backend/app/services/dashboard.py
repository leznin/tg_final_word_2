"""
Dashboard service with business logic for statistics
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.users import User
from app.models.chats import Chat
from app.models.chat_moderators import ChatModerator


class DashboardService:
    """Service class for dashboard statistics"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_total_chats(self) -> int:
        """Get total count of active chats (groups and supergroups, excluding channels)"""
        result = await self.db.execute(
            select(func.count(Chat.id))
            .where(Chat.is_active == True)
            .where(Chat.chat_type.in_(['group', 'supergroup']))
        )
        return result.scalar() or 0

    async def get_total_channels(self) -> int:
        """Get total count of active channels"""
        result = await self.db.execute(
            select(func.count(Chat.id))
            .where(Chat.is_active == True)
            .where(Chat.chat_type == 'channel')
        )
        return result.scalar() or 0

    async def get_total_moderators(self) -> int:
        """Get total count of unique moderators (users who are admins in chats)"""
        # Count unique users from chat_moderators table
        # This represents users who have been assigned as moderators
        result = await self.db.execute(
            select(func.count(func.distinct(ChatModerator.moderator_user_id)))
        )
        return result.scalar() or 0

    async def get_total_users(self) -> int:
        """Get total count of users in the system"""
        result = await self.db.execute(
            select(func.count(User.id))
        )
        return result.scalar() or 0

    async def get_dashboard_stats(self) -> dict:
        """Get all dashboard statistics"""
        total_chats = await self.get_total_chats()
        total_channels = await self.get_total_channels()
        total_moderators = await self.get_total_moderators()
        total_users = await self.get_total_users()

        return {
            "total_chats": total_chats,
            "total_channels": total_channels,
            "total_moderators": total_moderators,
            "total_users": total_users,
        }
