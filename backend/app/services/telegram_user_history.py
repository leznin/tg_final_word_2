"""
Telegram user history service
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from app.models.telegram_user_history import TelegramUserHistory
from app.schemas.telegram_user_history import TelegramUserHistoryCreate, TelegramUserHistoryResponse


class TelegramUserHistoryService:
    """Service for managing telegram user history"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_history(self, telegram_user_id: int, limit: int = 50) -> List[TelegramUserHistory]:
        """Get history of changes for a specific user"""
        query = (
            select(TelegramUserHistory)
            .where(TelegramUserHistory.telegram_user_id == telegram_user_id)
            .order_by(desc(TelegramUserHistory.changed_at))
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_history_entry(self, history_data: TelegramUserHistoryCreate) -> TelegramUserHistory:
        """Create a new history entry"""
        history_entry = TelegramUserHistory(**history_data.dict())
        self.db.add(history_entry)
        await self.db.commit()
        await self.db.refresh(history_entry)
        return history_entry

    async def get_latest_change(self, telegram_user_id: int, field_name: str) -> Optional[TelegramUserHistory]:
        """Get the latest change for a specific field of a user"""
        query = (
            select(TelegramUserHistory)
            .where(
                TelegramUserHistory.telegram_user_id == telegram_user_id,
                TelegramUserHistory.field_name == field_name
            )
            .order_by(desc(TelegramUserHistory.changed_at))
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
