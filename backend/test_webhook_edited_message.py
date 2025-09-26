#!/usr/bin/env python3
"""
Test script to simulate webhook processing of edited message
"""

import asyncio
import json
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from app.core.database import get_db
from app.telegram.middlewares.database import DatabaseMiddleware
from app.telegram.middlewares.bot import BotMiddleware
from app.telegram.handlers.messages import message_router
from app.core.config import settings


async def test_webhook_edited_message():
    """Test processing of edited message webhook"""

    # Sample edited message JSON from user
    webhook_data = {
        "update_id": 277111217,
        "edited_message": {
            "message_id": 126,
            "from": {
                "id": 415409454,
                "is_bot": False,
                "first_name": "Qwerty",
                "username": "s3s3s",
                "language_code": "ru",
                "is_premium": True
            },
            "chat": {
                "id": -1003062613079,
                "title": "тест чат",
                "type": "supergroup"
            },
            "date": 1758824913,
            "edit_date": 1758826052,
            "text": "123 4 6"
        }
    }

    print("Testing webhook processing of edited message...")
    print(f"Webhook data: {json.dumps(webhook_data, indent=2)}")

    try:
        # Initialize bot and dispatcher (similar to main app)
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token:
            print("No bot token found")
            return

        bot = Bot(
            token=bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dispatcher = Dispatcher()

        # Register middlewares
        dispatcher.update.middleware(DatabaseMiddleware())
        dispatcher.update.middleware(BotMiddleware(bot))

        # Register our message router
        dispatcher.include_router(message_router)

        # Process the webhook update
        update = Update(**webhook_data)
        print("Processing update through aiogram dispatcher...")

        await dispatcher.feed_update(bot, update)

        print("✅ Webhook processed successfully")

    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_webhook_edited_message())
