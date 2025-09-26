#!/usr/bin/env python3
"""
Test script to simulate channel linking functionality
"""

import asyncio
import sys
sys.path.insert(0, 'app')

from aiogram.types import Update, Message, User, Chat as TGChat
from app.core.database import get_db
from app.telegram.services.chat_linking import ChatLinkingService


async def test_channel_linking():
    """Test channel linking functionality"""

    print("🧪 Testing channel linking functionality...")

    try:
        # Test 1: Extract channel ID from forwarded message
        print("\n📝 Test 1: Extracting channel ID from forwarded message")

        # Create mock forwarded message from channel
        mock_forward_data = {
            "message_id": 123,
            "from": {
                "id": 415409454,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser"
            },
            "chat": {
                "id": 415409454,
                "type": "private"
            },
            "date": 1730000000,
            "forward_origin": {
                "type": "channel",
                "chat": {
                    "id": -1003008079966,
                    "title": "Test Channel",
                    "username": "testchannel",
                    "type": "channel"
                },
                "message_id": 456,
                "date": 1729000000
            },
            "text": "Test forwarded message"
        }

        # Convert to aiogram Message object
        message = Message(**mock_forward_data)

        async for db in get_db():
            linking_service = ChatLinkingService(db)

            # Test extraction
            channel_id = await linking_service.extract_channel_from_forwarded_message(message)

            if channel_id == -1003008079966:
                print("✅ Successfully extracted channel ID:", channel_id)
            else:
                print("❌ Failed to extract channel ID, got:", channel_id)

            break

        # Test 2: Test with invalid forward (not from channel)
        print("\n📝 Test 2: Testing invalid forward (not from channel)")

        mock_invalid_forward = {
            "message_id": 124,
            "from": {
                "id": 415409454,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser"
            },
            "chat": {
                "id": 415409454,
                "type": "private"
            },
            "date": 1730000000,
            "text": "Regular message"
        }

        message_invalid = Message(**mock_invalid_forward)

        async for db in get_db():
            linking_service = ChatLinkingService(db)
            channel_id = await linking_service.extract_channel_from_forwarded_message(message_invalid)

            if channel_id is None:
                print("✅ Correctly identified non-forwarded message")
            else:
                print("❌ Incorrectly extracted channel ID from non-forwarded message:", channel_id)

            break

        # Test 3: Test channel access validation
        print("\n📝 Test 3: Testing channel access validation")

        # This test requires existing data in database
        # We'll test with a non-existent user/channel combination
        async for db in get_db():
            linking_service = ChatLinkingService(db)

            is_valid, error_msg = await linking_service.validate_channel_access_for_user(
                user_telegram_id=999999,  # Non-existent user
                channel_telegram_id=-1003008079966
            )

            if not is_valid:
                print("✅ Correctly validated channel access (user not found):", error_msg)
            else:
                print("❌ Unexpectedly allowed access for non-existent user")

            break

        print("\n🎉 Channel linking tests completed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_chat_listing():
    """Test chat listing functionality"""

    print("\n🧪 Testing chat listing functionality...")

    try:
        async for db in get_db():
            linking_service = ChatLinkingService(db)

            # Test with a known user ID (adjust based on your test data)
            test_user_id = 415409454  # Adjust this based on your test data

            chats = await linking_service.get_user_chats_for_management(test_user_id)

            print(f"✅ Found {len(chats)} chats for user {test_user_id}")

            for chat in chats:
                linked_status = ""
                if chat.chat_type != 'channel' and hasattr(chat, 'linked_channel') and chat.linked_channel:
                    linked_status = f" -> linked to {chat.linked_channel.title}"

                print(f"  - {chat.chat_type}: {chat.title or 'No title'} (ID: {chat.id}){linked_status}")

            break

    except Exception as e:
        print(f"❌ Chat listing test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Starting channel linking tests...")
    asyncio.run(test_channel_linking())
    asyncio.run(test_chat_listing())
    print("✅ All tests completed!")
