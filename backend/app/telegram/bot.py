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
from app.telegram.handlers.payments import payment_router
from app.telegram.handlers.chat_member_updates import chat_member_router


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

        # Register handlers (payment router first for successful_payment handling)
        self.dispatcher.include_router(payment_router)
        self.dispatcher.include_router(start_router)
        self.dispatcher.include_router(member_router)
        self.dispatcher.include_router(chat_member_router)
        self.dispatcher.include_router(message_router)
        self.dispatcher.include_router(chat_management_router)

        # Set webhook with retry logic
        max_retries = 5
        base_delay = 1.0

        for attempt in range(max_retries):
            try:
                await self.bot.set_webhook(
                    url=self.webhook_url,
                    allowed_updates=[
                        "message", "edited_message", "callback_query",
                        "pre_checkout_query", "successful_payment",
                        "my_chat_member", "chat_member"
                    ],
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
            print("❌ Dispatcher or bot not initialized")
            return

        print(f"🔄 WEBHOOK RECEIVED: {webhook_data.get('update_id', 'unknown')}")
        if 'pre_checkout_query' in webhook_data:
            print("💳 WEBHOOK CONTAINS PRE_CHECKOUT_QUERY")
        if 'message' in webhook_data:
            message = webhook_data['message']
            if 'successful_payment' in message:
                print("🎉 WEBHOOK CONTAINS SUCCESSFUL_PAYMENT MESSAGE")
                print(f"   Payment data: {message['successful_payment']}")
        if 'callback_query' in webhook_data:
            print("🔘 WEBHOOK CONTAINS CALLBACK_QUERY")

        # Process update through aiogram
        from aiogram.types import Update
        update = Update(**webhook_data)
        await self.dispatcher.feed_update(self.bot, update)

    @property
    def is_running(self) -> bool:
        """Check if bot is running"""
        return self.running
