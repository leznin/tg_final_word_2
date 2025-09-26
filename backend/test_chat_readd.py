#!/usr/bin/env python3
"""
Test script to simulate re-adding bot to existing chat
"""

import asyncio
import sys
sys.path.insert(0, 'app')

from app.core.database import get_db
from app.services.chats import ChatService
from app.schemas.chats import TelegramChatData

async def test_chat_readd():
    """Test re-adding bot to existing chat"""

    # Use existing chat data
    telegram_chat_data = TelegramChatData(
        id=-1001234567890,  # Existing chat ID
        type='supergroup',
        title='Test Group Updated',  # Changed title
        username=None
    )

    print("🧪 Testing chat re-addition...")
    print(f"Chat ID: {telegram_chat_data.id}")
    print(f"New title: {telegram_chat_data.title}")

    async for db in get_db():
        chat_service = ChatService(db)

        # Check current state
        existing_chat = await chat_service.get_chat_by_telegram_id(telegram_chat_data.id)
        if existing_chat:
            print(f"📊 Current chat state: ID {existing_chat.id}, Active: {existing_chat.is_active}, Title: '{existing_chat.title}'")

        # Re-add bot to chat
        updated_chat = await chat_service.create_or_update_chat_from_telegram(telegram_chat_data, 1)  # Same user

        print(f"✅ Chat after update: ID {updated_chat.id}, Active: {updated_chat.is_active}, Title: '{updated_chat.title}'")

        # Check if new record was created
        all_chats = await chat_service.get_all_chats()
        print(f"📈 Total active chats: {len(all_chats)}")

        break

if __name__ == "__main__":
    asyncio.run(test_chat_readd())
