"""
Telegram users service with business logic
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional
from app.models.telegram_users import TelegramUser
from app.models.telegram_user_history import TelegramUserHistory
from app.schemas.telegram_users import TelegramUserCreate, TelegramUserUpdate, TelegramUserData


class TelegramUserService:
    """Service class for telegram user operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_telegram_user(self, user_data: TelegramUserCreate) -> TelegramUser:
        """Create a new telegram user"""
        db_user = TelegramUser(**user_data.model_dump())
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def get_telegram_user(self, telegram_user_id: int) -> Optional[TelegramUser]:
        """Get telegram user by telegram_user_id"""
        result = await self.db.execute(select(TelegramUser).where(TelegramUser.telegram_user_id == telegram_user_id))
        return result.scalar_one_or_none()

    async def update_telegram_user(self, telegram_user_id: int, user_data: TelegramUserUpdate) -> Optional[TelegramUser]:
        """Update telegram user"""
        db_user = await self.get_telegram_user(telegram_user_id)
        if not db_user:
            return None

        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(db_user, field, value)

        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def _record_history_change(self, telegram_user_id: int, field_name: str, old_value: Optional[str], new_value: Optional[str]) -> None:
        """Record a change in telegram user history if the value actually changed"""
        if old_value != new_value:
            history_entry = TelegramUserHistory(
                telegram_user_id=telegram_user_id,
                field_name=field_name,
                old_value=old_value,
                new_value=new_value
            )
            self.db.add(history_entry)

    async def create_or_update_user_from_telegram(self, telegram_user_data: TelegramUserData) -> TelegramUser:
        """Create or update telegram user from Telegram API data"""
        # Try to find existing user
        db_user = await self.get_telegram_user(telegram_user_data.telegram_user_id)

        if db_user:
            # Record history changes for tracked fields
            await self._record_history_change(db_user.telegram_user_id, 'first_name', db_user.first_name, telegram_user_data.first_name)
            await self._record_history_change(db_user.telegram_user_id, 'last_name', db_user.last_name, telegram_user_data.last_name)
            await self._record_history_change(db_user.telegram_user_id, 'username', db_user.username, telegram_user_data.username)

            # Update existing user - explicitly set fields
            db_user.is_bot = telegram_user_data.is_bot
            db_user.first_name = telegram_user_data.first_name
            db_user.last_name = telegram_user_data.last_name
            db_user.username = telegram_user_data.username
            db_user.language_code = telegram_user_data.language_code
            db_user.is_premium = telegram_user_data.is_premium
            db_user.added_to_attachment_menu = telegram_user_data.added_to_attachment_menu
            db_user.can_join_groups = telegram_user_data.can_join_groups
            db_user.can_read_all_group_messages = telegram_user_data.can_read_all_group_messages
            db_user.supports_inline_queries = telegram_user_data.supports_inline_queries
            db_user.can_connect_to_business = telegram_user_data.can_connect_to_business
            db_user.has_main_web_app = telegram_user_data.has_main_web_app
            db_user.account_creation_date = telegram_user_data.account_creation_date
        else:
            # Create new user
            user_data = TelegramUserCreate(**telegram_user_data.model_dump())
            db_user = TelegramUser(**user_data.model_dump())
            self.db.add(db_user)

        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user
