"""
Test script to verify the edit timeout fix
"""
import asyncio
from datetime import datetime, timedelta
from app.core.database import get_db
from app.services.chats import ChatService
from app.services.messages import MessageService
from app.telegram.handlers.messages import handle_edited_message
from aiogram import types, Bot
from unittest.mock import AsyncMock, MagicMock


async def test_edit_timeout_logic():
    """Test the fixed edit timeout logic"""
    print("🧪 Testing edit timeout logic fix...")

    async for db in get_db():
        chat_service = ChatService(db)
        message_service = MessageService(db)

        # Get test chat
        chat = await chat_service.get_chat_by_telegram_id(-1003062613079)  # тест чат
        if not chat:
            print("❌ Test chat not found")
            return

        print(f"✓ Found test chat: {chat.title} (ID: {chat.id})")
        print(f"✓ Current timeout setting: {chat.message_edit_timeout_minutes or 'disabled'}")

        # Get a recent message from the chat
        recent_messages = await message_service.get_recent_messages(chat.id, hours=1)
        if not recent_messages:
            print("❌ No recent messages found in chat")
            return

        test_message = recent_messages[0]
        print(f"✓ Found test message: ID={test_message.id}, Text='{test_message.text_content}', Created: {test_message.created_at}")

        # Create mock objects for testing
        mock_bot = MagicMock(spec=Bot)
        mock_bot.delete_message = AsyncMock()
        mock_bot.send_message = AsyncMock()

        # Create mock edited message
        mock_message = MagicMock(spec=types.Message)
        mock_message.chat = MagicMock()
        mock_message.chat.id = chat.telegram_chat_id
        mock_message.chat.type = 'supergroup'
        mock_message.message_id = test_message.telegram_message_id
        mock_message.text = "Edited test message"
        mock_message.caption = None
        mock_message.edit_date = int(datetime.now().timestamp())

        mock_message.from_user = MagicMock()
        mock_message.from_user.id = 415409454
        mock_message.from_user.full_name = "Test User"

        # Mock media attributes
        mock_message.photo = None
        mock_message.video = None
        mock_message.document = None
        mock_message.audio = None
        mock_message.voice = None
        mock_message.animation = None
        mock_message.sticker = None
        mock_message.video_note = None

        print("\n--- Testing scenarios ---")

        # Scenario 1: Timeout disabled (should delete and notify)
        original_timeout = chat.message_edit_timeout_minutes
        from app.schemas.chats import ChatUpdate
        await chat_service.update_chat(chat.id, ChatUpdate(message_edit_timeout_minutes=None))

        print("1. Testing with editing disabled (timeout = None):")
        try:
            await handle_edited_message(mock_message, db, mock_bot)
            print("✓ Handler completed without errors")
        except Exception as e:
            print(f"✗ Handler failed: {e}")

        # Scenario 2: Short timeout (1 minute) with expired message (should delete and notify)
        await chat_service.update_chat(chat.id, ChatUpdate(message_edit_timeout_minutes=1))

        print("2. Testing with 1 minute timeout on old message (should delete and notify):")
        try:
            await handle_edited_message(mock_message, db, mock_bot)
            print("✓ Handler completed without errors")
        except Exception as e:
            print(f"✗ Handler failed: {e}")

        # Restore original timeout
        await chat_service.update_chat(chat.id, ChatUpdate(message_edit_timeout_minutes=original_timeout))

        print(f"\n✅ Edit timeout logic test completed. Timeout restored to: {original_timeout or 'disabled'}")


if __name__ == "__main__":
    asyncio.run(test_edit_timeout_logic())
