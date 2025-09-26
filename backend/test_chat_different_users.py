#!/usr/bin/env python3
"""
Test script to simulate adding bot to same chat by different users
"""

import asyncio
import sys
sys.path.insert(0, 'app')

from app.core.database import get_db
from app.services.chats import ChatService
from app.services.users import UserService
from app.schemas.chats import TelegramChatData
from app.schemas.users import TelegramUserData

async def test_chat_different_users():
    """Test adding bot to same chat by different users"""

    # Create a test user first
    async for db in get_db():
        user_service = UserService(db)

        # Create second test user
        user_data = TelegramUserData(
            id=999999999,  # Different user ID
            is_bot=False,
            first_name='TestUser2',
            username='testuser2'
        )

        user2 = await user_service.create_or_update_telegram_user(user_data)
        print(f"👤 Created test user: ID {user2.id}, Telegram ID {user2.telegram_id}")

        # Now test chat operations
        chat_service = ChatService(db)

        telegram_chat_data = TelegramChatData(
            id=-1009999999999,  # New test chat
            type='channel',
            title='Test Channel for Users',
            username=None
        )

        print(f"\n🧪 Testing chat with different users...")

        # First user adds bot
        print(f"1️⃣ User {user2.id} adds bot to chat")
        chat1 = await chat_service.create_or_update_chat_from_telegram(telegram_chat_data, user2.id)
        print(f"   Created chat ID {chat1.id}, added by user {chat1.added_by_user_id}")

        # Second user adds bot (same chat)
        print(f"2️⃣ User 1 adds bot to same chat")
        chat2 = await chat_service.create_or_update_chat_from_telegram(telegram_chat_data, 1)  # Different user
        print(f"   Updated chat ID {chat2.id}, added by user {chat2.added_by_user_id}")

        # Check final state
        final_chat = await chat_service.get_chat_by_telegram_id(telegram_chat_data.id)
        print(f"\n📊 Final chat state: ID {final_chat.id}, Added by user {final_chat.added_by_user_id}")

        # Check total chats count
        all_chats = await chat_service.get_all_chats()
        print(f"📈 Total active chats: {len(all_chats)}")

        # Clean up
        await chat_service.deactivate_chat(telegram_chat_data.id)
        print("🧹 Test chat deactivated")

        break

if __name__ == "__main__":
    asyncio.run(test_chat_different_users())
