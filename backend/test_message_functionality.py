#!/usr/bin/env python3
"""
Test script for message and chat member functionality
"""

import asyncio
from app.core.database import get_db
from app.services.messages import MessageService
from app.services.chat_members import ChatMemberService
from app.schemas.messages import MessageCreate
from app.schemas.chat_members import ChatMemberCreate


async def test_message_service():
    """Test message service functionality"""
    async for db in get_db():
        try:
            message_service = MessageService(db)

            # Create a test message
            test_message = MessageCreate(
                chat_id=8,  # Using existing chat ID
                telegram_message_id=12345,
                telegram_user_id=415409454,
                message_type='text',
                text_content='Test message from automated test'
            )

            message = await message_service.create_message(test_message)
            print(f"✓ Created message with ID: {message.id}")

            # Get message back
            retrieved = await message_service.get_message(message.id)
            print(f"✓ Retrieved message: {retrieved.text_content}")

            # Get messages from chat
            messages = await message_service.get_chat_messages(8, limit=5)
            print(f"✓ Found {len(messages)} messages in chat")

        finally:
            pass


async def test_chat_member_service():
    """Test chat member service functionality"""
    async for db in get_db():
        try:
            member_service = ChatMemberService(db)

            # Create a test member
            test_member = ChatMemberCreate(
                chat_id=8,  # Using existing chat ID
                telegram_user_id=415409454,
                is_bot=False,
                first_name='Test',
                last_name='User',
                username='testuser'
            )

            member = await member_service.create_chat_member(test_member)
            print(f"✓ Created chat member with ID: {member.id}")

            # Get member back
            retrieved = await member_service.get_chat_member(member.id)
            print(f"✓ Retrieved member: {retrieved.first_name} {retrieved.last_name}")

            # Get members from chat
            members = await member_service.get_chat_members(8, limit=5)
            print(f"✓ Found {len(members)} members in chat")

        finally:
            pass


async def main():
    """Run all tests"""
    print("Testing message and chat member functionality...\n")

    try:
        print("1. Testing Message Service:")
        await test_message_service()

        print("\n2. Testing Chat Member Service:")
        await test_chat_member_service()

        print("\n✓ All tests passed!")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
