"""
Manually trigger sending of scheduled posts
"""

import asyncio
from app.core.database import async_session
from app.services.chat_posts import ChatPostService
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.core.config import settings

async def send_scheduled_posts():
    """Manually trigger the scheduled posts processing"""
    async with async_session() as db:
        # Create bot instance
        bot = Bot(
            token=settings.TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        if not bot:
            print("Error: Bot instance not available")
            return
        
        # Create service
        service = ChatPostService(db, bot)
        
        # Process scheduled actions
        print("Processing scheduled actions...")
        await service.process_scheduled_actions()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(send_scheduled_posts())
