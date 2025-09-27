"""
Telegram Bot implementation using aiogram
"""

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramRetryAfter

from app.core.config import settings
from app.telegram.middlewares.database import DatabaseMiddleware
from app.telegram.middlewares.bot import BotMiddleware
from app.telegram.handlers.start import start_router, member_router
from app.telegram.handlers.messages import message_router
from app.telegram.handlers.chat_management import chat_management_router


class TelegramBot:
    """Telegram Bot class using aiogram"""

    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.webhook_url = settings.TELEGRAM_WEBHOOK_URL
        self.bot = None
        self.dispatcher = None
        self.running = False

    async def start(self):
        """Start the bot with webhook"""
        if not self.token:
            return

        if not self.webhook_url:
            return

        # Initialize bot and dispatcher
        self.bot = Bot(
            token=self.token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dispatcher = Dispatcher()

        # Register middlewares
        self.dispatcher.update.middleware(DatabaseMiddleware())
        self.dispatcher.update.middleware(BotMiddleware(self.bot))

        # Register handlers
        self.dispatcher.include_router(start_router)
        self.dispatcher.include_router(member_router)
        self.dispatcher.include_router(message_router)
        self.dispatcher.include_router(chat_management_router)

        # Set webhook with retry logic
        max_retries = 5
        base_delay = 1.0

        for attempt in range(max_retries):
            try:
                await self.bot.set_webhook(
                    url=self.webhook_url,
                    drop_pending_updates=True
                )
                break  # Success, exit retry loop
            except TelegramRetryAfter as e:
                if attempt == max_retries - 1:
                    raise  # Re-raise on last attempt

                delay = base_delay * (2 ** attempt)  # Exponential backoff
                print(f"Webhook setup failed due to rate limit. Retrying in {delay:.1f} seconds... (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(delay)
            except Exception as e:
                print(f"Unexpected error setting webhook: {e}")
                raise

        self.running = True

    async def stop(self):
        """Stop the bot"""
        if self.bot and self.webhook_url:
            await self.bot.delete_webhook()

        self.running = False

    async def process_webhook(self, webhook_data: dict):
        """Process incoming webhook data"""
        if not self.dispatcher or not self.bot:
            return

        # Process update through aiogram
        from aiogram.types import Update
        update = Update(**webhook_data)
        await self.dispatcher.feed_update(self.bot, update)

    @property
    def is_running(self) -> bool:
        """Check if bot is running"""
        return self.running
