#!/usr/bin/env python3
"""
Test script to simulate the edited message scenario from the JSON example
"""

import asyncio
from app.core.database import get_db
from app.services.messages import MessageService
from app.services.chats import ChatService


async def test_edited_message_scenario():
    """Test the exact scenario from the JSON example"""
    async for db in get_db():
        try:
            message_service = MessageService(db)
            chat_service = ChatService(db)

            # Get the chat that corresponds to the JSON (telegram_chat_id: -1003062613079)
            chat = await chat_service.get_chat_by_telegram_id(-1003062613079)
            if not chat:
                print("✗ Chat not found in database")
                return

            print(f"✓ Found chat: {chat.title} (ID: {chat.id})")

            # Get the message that was edited (message_id: 126)
            db_message = await message_service.get_message_by_telegram_id(chat.id, 126)
            if not db_message:
                print("✗ Message 126 not found in database")
                return

            print(f"✓ Found message in DB: ID={db_message.id}, Text='{db_message.text_content}'")

            # Simulate the telegram message data from the JSON example
            telegram_message_data = {
                'message_id': 126,
                'text': '123 4 6',  # New text from the JSON
                'caption': None,
                'from_user': {
                    'id': 415409454,
                    'is_bot': False,
                    'first_name': 'Qwerty',
                    'last_name': None,
                    'username': 's3s3s',
                    'language_code': 'ru',
                    'is_premium': True
                }
            }

            # Test comparison - should detect changes
            has_changes = await message_service.compare_message_with_telegram_data(db_message, telegram_message_data)
            print(f"✓ Message comparison: {'CHANGES DETECTED' if has_changes else 'NO CHANGES'}")

            if has_changes:
                print("✓ This would trigger: delete from chat + notify channel + update DB")
            else:
                print("✗ No changes detected - this shouldn't happen!")

            # Check if chat has linked channel
            linked_channel = await chat_service.get_linked_channel(chat.id)
            if linked_channel:
                print(f"✓ Chat has linked channel: {linked_channel.title} (Telegram ID: {linked_channel.telegram_chat_id})")
            else:
                print("⚠ Chat has no linked channel - notifications won't be sent")

            # Simulate update (what would happen after processing)
            print("\n--- Simulating message update ---")
            updated_message = await message_service.update_message_from_telegram(chat.id, telegram_message_data)
            if updated_message:
                print(f"✓ Message updated in DB: '{updated_message.text_content}'")
            else:
                print("✗ Failed to update message")

            print("\n✅ Test completed - the edited message handler should work correctly with this JSON structure")

        except Exception as e:
            print(f"✗ Error during testing: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_edited_message_scenario())
