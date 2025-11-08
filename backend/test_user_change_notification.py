"""
Test script for user change notifications
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.telegram_users import TelegramUserService
from app.schemas.telegram_users import TelegramUserData
from aiogram import Bot


async def test_notification():
    """Test user change notification"""
    
    # Create database engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
    )
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Create bot instance
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        
        # Create service with bot
        service = TelegramUserService(session, bot)
        
        # Example: Update a user's data
        # Replace with actual telegram user ID from your database
        test_user_id = int(input("Enter Telegram User ID to test: "))
        
        # Get current user data
        current_user = await service.get_telegram_user(test_user_id)
        if not current_user:
            print(f"User {test_user_id} not found in database")
            return
        
        print(f"Current user data:")
        print(f"  First name: {current_user.first_name}")
        print(f"  Last name: {current_user.last_name}")
        print(f"  Username: {current_user.username}")
        
        # Simulate a change
        print("\nSimulating name change...")
        updated_data = TelegramUserData(
            telegram_user_id=test_user_id,
            is_bot=current_user.is_bot,
            first_name=current_user.first_name + "_TEST",  # Change first name
            last_name=current_user.last_name,
            username=current_user.username,
            language_code=current_user.language_code,
            is_premium=current_user.is_premium,
            added_to_attachment_menu=current_user.added_to_attachment_menu,
            can_join_groups=current_user.can_join_groups,
            can_read_all_group_messages=current_user.can_read_all_group_messages,
            supports_inline_queries=current_user.supports_inline_queries,
            can_connect_to_business=current_user.can_connect_to_business,
            has_main_web_app=current_user.has_main_web_app,
            account_creation_date=current_user.account_creation_date
        )
        
        # Update user and trigger notification
        await service.create_or_update_user_from_telegram(updated_data)
        
        print("\nUpdate completed! Check the logs and group chats for notifications.")
        
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(test_notification())
