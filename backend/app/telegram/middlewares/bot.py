"""
Bot middleware for Telegram bot to inject bot instance into handlers
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject


class BotMiddleware(BaseMiddleware):
    """
    Middleware to inject bot instance into handler data
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Inject bot instance into handler data
        """
        data["bot"] = self.bot
        return await handler(event, data)
