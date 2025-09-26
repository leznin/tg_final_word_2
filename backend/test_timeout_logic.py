#!/usr/bin/env python3
"""
Test script to verify message edit timeout logic
"""

import asyncio
from datetime import datetime, timedelta
from app.core.database import get_db
from app.services.messages import MessageService
from app.services.chats import ChatService
from app.schemas.chats import ChatUpdate


async def test_timeout_logic():
    """Test message edit timeout logic"""
    async for db in get_db():
        try:
            message_service = MessageService(db)
            chat_service = ChatService(db)

            # Get existing chat
            chat = await chat_service.get_chat_by_telegram_id(-1003062613079)
            if not chat:
                print("✗ Chat not found")
                return

            print(f"✓ Testing with chat: {chat.title} (ID: {chat.id})")
            print(f"Current timeout setting: {chat.message_edit_timeout_minutes}")

            # Test 1: Set timeout to 5 minutes
            print("\n--- Test 1: Set timeout to 5 minutes ---")
            update_data = ChatUpdate(message_edit_timeout_minutes=5)
            updated_chat = await chat_service.update_chat(chat.id, update_data)
            if updated_chat:
                print(f"✓ Timeout set to {updated_chat.message_edit_timeout_minutes} minutes")
            else:
                print("✗ Failed to update timeout")

            # Test 2: Disable editing
            print("\n--- Test 2: Disable editing ---")
            update_data = ChatUpdate(message_edit_timeout_minutes=None)
            updated_chat = await chat_service.update_chat(chat.id, update_data)
            if updated_chat and updated_chat.message_edit_timeout_minutes is None:
                print("✓ Editing disabled")
            else:
                print("✗ Failed to disable editing")

            # Test 3: Set timeout to 1 minute
            print("\n--- Test 3: Set timeout to 1 minute ---")
            update_data = ChatUpdate(message_edit_timeout_minutes=1)
            updated_chat = await chat_service.update_chat(chat.id, update_data)
            if updated_chat:
                print(f"✓ Timeout set to {updated_chat.message_edit_timeout_minutes} minutes")
            else:
                print("✗ Failed to update timeout")

            print("\n✅ All timeout settings tests completed")

        except Exception as e:
            print(f"✗ Error during testing: {e}")
        finally:
            await db.close()


if __name__ == "__main__":
    asyncio.run(test_timeout_logic())
