"""
Database middleware for Telegram bot
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db


class DatabaseMiddleware(BaseMiddleware):
    """
    Middleware to inject database session into handler data
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Inject database session into handler data
        """
        async for session in get_db():
            data["db"] = session
            return await handler(event, data)

