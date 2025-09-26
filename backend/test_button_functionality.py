#!/usr/bin/env python3
"""
Test script for testing back and cancel button functionality in Telegram bot
"""

import asyncio
import sys
import os
from unittest.mock import AsyncMock, Mock, patch

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from aiogram.types import CallbackQuery, Message, User, Chat
from aiogram.fsm.context import FSMContext

from app.telegram.handlers.chat_management import (
    handle_back_to_menu,
    handle_cancel,
    handle_back_to_chats_after_success
)
from app.telegram.keyboards.chat_management import (
    get_chats_keyboard,
    get_cancel_keyboard,
    get_main_menu_keyboard,
    get_back_to_chats_keyboard
)
from app.telegram.states import ChatManagementStates
from app.core.database import get_db
from app.services.chats import ChatService
from app.telegram.services.chat_linking import ChatLinkingService
from app.models.chats import Chat as DBChat


async def test_back_button_from_chat_selection():
    """Test the back button functionality from chat selection menu"""
    print("🧪 Testing back button from chat selection menu...")

    try:
        # Create mock callback query
        mock_callback = Mock(spec=CallbackQuery)
        mock_callback.data = "back_to_menu"
        mock_callback.answer = AsyncMock()

        # Create mock user
        mock_user = Mock(spec=User)
        mock_user.id = 123456789
        mock_callback.from_user = mock_user

        # Create mock message with AsyncMock for edit_text
        mock_message = Mock(spec=Message)
        mock_message.edit_text = AsyncMock()
        mock_callback.message = mock_message

        # Create mock FSM context
        mock_state = Mock(spec=FSMContext)
        mock_state.clear = AsyncMock()

        # Test the handler
        await handle_back_to_menu(mock_callback, mock_state)

        # Verify that callback was answered
        mock_callback.answer.assert_called_once()
        print("✅ Callback was answered")

        # Verify that state was cleared
        mock_state.clear.assert_called_once()
        print("✅ FSM state was cleared")

        # Verify that message.edit_text was called with correct parameters
        mock_message.edit_text.assert_called_once()
        call_args = mock_message.edit_text.call_args

        # Check the arguments (they might be positional or keyword)
        if len(call_args[0]) >= 1:  # positional args
            text_arg = call_args[0][0]
            keyboard = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get('reply_markup')
        else:  # keyword args
            text_arg = call_args[1]['text']
            keyboard = call_args[1]['reply_markup']

        # Check the text content (should be START_MESSAGE)
        from app.telegram.utils.constants import START_MESSAGE
        assert text_arg == START_MESSAGE, f"Expected START_MESSAGE, got '{text_arg[:50]}...'"
        print("✅ Correct message text sent")

        # Check that keyboard was provided
        assert keyboard is not None, "Reply markup should be provided"

        # Verify keyboard has main menu buttons
        main_keyboard = get_main_menu_keyboard()
        assert keyboard.inline_keyboard == main_keyboard.inline_keyboard, "Should return main menu keyboard"
        print("✅ Correct keyboard returned")

        print("✅ Back button test passed!")

    except Exception as e:
        print(f"❌ Back button test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


async def test_cancel_button_during_channel_linking():
    """Test the cancel button functionality during channel linking process"""
    print("\n🧪 Testing cancel button during channel linking...")

    try:
        # Create mock callback query
        mock_callback = Mock(spec=CallbackQuery)
        mock_callback.data = "cancel_action"
        mock_callback.answer = AsyncMock()

        # Create mock user
        mock_user = Mock(spec=User)
        mock_user.id = 123456789
        mock_callback.from_user = mock_user

        # Create mock message with AsyncMock for edit_text
        mock_message = Mock(spec=Message)
        mock_message.edit_text = AsyncMock()
        mock_callback.message = mock_message

        # Create mock FSM context
        mock_state = Mock(spec=FSMContext)
        mock_state.clear = AsyncMock()

        # Test the handler
        await handle_cancel(mock_callback, mock_state)

        # Verify that callback was answered
        mock_callback.answer.assert_called_once()
        print("✅ Callback was answered")

        # Verify that state was cleared
        mock_state.clear.assert_called_once()
        print("✅ FSM state was cleared")

        # Verify that message.edit_text was called with correct parameters
        mock_message.edit_text.assert_called_once()
        call_args = mock_message.edit_text.call_args

        # Check the arguments (they might be positional or keyword)
        if len(call_args[0]) >= 1:  # positional args
            text_arg = call_args[0][0]
            keyboard = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get('reply_markup')
        else:  # keyword args
            text_arg = call_args[1]['text']
            keyboard = call_args[1]['reply_markup']

        # Check the text content (should be START_MESSAGE)
        from app.telegram.utils.constants import START_MESSAGE
        assert text_arg == START_MESSAGE, f"Expected START_MESSAGE, got '{text_arg[:50]}...'"
        print("✅ Correct cancellation message sent")

        # Check that keyboard was provided
        assert keyboard is not None, "Reply markup should be provided"

        # Verify keyboard has main menu buttons
        main_keyboard = get_main_menu_keyboard()
        assert keyboard.inline_keyboard == main_keyboard.inline_keyboard, "Should return main menu keyboard"
        print("✅ Correct keyboard returned")

        print("✅ Cancel button test passed!")

    except Exception as e:
        print(f"❌ Cancel button test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


async def test_back_to_chats_button_after_success():
    """Test the back to chats button functionality after successful linking"""
    print("\n🧪 Testing back to chats button after successful linking...")

    try:
        # Create mock callback query
        mock_callback = Mock(spec=CallbackQuery)
        mock_callback.data = "back_to_chats_after_success"

        # Create mock user
        mock_user = Mock(spec=User)
        mock_user.id = 123456789
        mock_callback.from_user = mock_user

        # Create mock message with AsyncMock for edit_text
        mock_message = Mock(spec=Message)
        mock_message.edit_text = AsyncMock()
        mock_callback.message = mock_message

        # Create mock FSM context
        mock_state = Mock(spec=FSMContext)
        mock_state.set_state = AsyncMock()

        # Create mock chats for testing
        mock_chat1 = Mock(spec=DBChat)
        mock_chat1.id = 1
        mock_chat1.title = "Test Group"
        mock_chat1.username = None
        mock_chat1.chat_type = "group"
        mock_chat1.linked_channel = None

        mock_chats = [mock_chat1]

        # Create mock database session
        mock_db = Mock()

        # Create mock linking service
        mock_linking_service = Mock(spec=ChatLinkingService)
        mock_linking_service.get_user_chats_for_management = AsyncMock(return_value=mock_chats)

        # Test the handler with mocked service
        with patch('app.telegram.handlers.chat_management.ChatLinkingService', return_value=mock_linking_service):
            await handle_back_to_chats_after_success(mock_callback, mock_db, mock_state)

        # Verify that message.edit_text was called
        mock_message.edit_text.assert_called_once()
        call_args = mock_message.edit_text.call_args

        # Check the arguments (they might be positional or keyword)
        if len(call_args[0]) >= 1:  # positional args
            text = call_args[0][0]
            keyboard = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get('reply_markup')
        else:  # keyword args
            text = call_args[1]['text']
            keyboard = call_args[1]['reply_markup']

        # Check the text content contains expected elements
        assert "Выберите групповой чат для управления:" in text, "Should contain chat selection message"
        print("✅ Correct message text sent")

        # Check that keyboard was provided
        assert keyboard is not None, "Reply markup should be provided"

        # Verify keyboard has chat selection buttons
        chats_keyboard = get_chats_keyboard(mock_chats)
        assert len(keyboard.inline_keyboard) == len(chats_keyboard.inline_keyboard), "Should have same number of buttons"
        print("✅ Correct chats keyboard returned")

        # Verify that FSM state was set to selecting_chat
        mock_state.set_state.assert_called_once_with(ChatManagementStates.selecting_chat)
        print("✅ FSM state set to selecting_chat")

        print("✅ Back to chats button test passed!")

    except Exception as e:
        print(f"❌ Back to chats button test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


async def test_keyboard_generation():
    """Test keyboard generation functions"""
    print("\n🧪 Testing keyboard generation...")

    try:
        # Test cancel keyboard
        cancel_kb = get_cancel_keyboard()
        assert len(cancel_kb.inline_keyboard) == 1, "Cancel keyboard should have 1 row"
        assert len(cancel_kb.inline_keyboard[0]) == 1, "Cancel keyboard row should have 1 button"
        assert cancel_kb.inline_keyboard[0][0].text == "❌ Отмена", "Cancel button text should be correct"
        assert cancel_kb.inline_keyboard[0][0].callback_data == "cancel_action", "Cancel button callback should be correct"
        print("✅ Cancel keyboard generated correctly")

        # Test main menu keyboard
        main_kb = get_main_menu_keyboard()
        assert len(main_kb.inline_keyboard) == 2, "Main menu should have 2 rows"
        assert main_kb.inline_keyboard[0][0].text == "📋 Управление чатами", "First button should be manage chats"
        assert main_kb.inline_keyboard[1][0].text == "ℹ️ Помощь", "Second button should be help"
        print("✅ Main menu keyboard generated correctly")

        # Test back to chats keyboard
        back_kb = get_back_to_chats_keyboard()
        assert len(back_kb.inline_keyboard) == 1, "Back to chats keyboard should have 1 row"
        assert back_kb.inline_keyboard[0][0].text == "⬅️ Назад к чатам", "Back button text should be correct"
        assert back_kb.inline_keyboard[0][0].callback_data == "back_to_chats_after_success", "Back button callback should be correct"
        print("✅ Back to chats keyboard generated correctly")

        print("✅ All keyboard generation tests passed!")

    except Exception as e:
        print(f"❌ Keyboard generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


async def run_button_tests():
    """Run all button functionality tests"""
    print("🚀 STARTING BUTTON FUNCTIONALITY TESTS")
    print("=" * 50)

    results = {}

    # Test back button from chat selection
    results["back_button"] = await test_back_button_from_chat_selection()

    # Test cancel button during channel linking
    results["cancel_button"] = await test_cancel_button_during_channel_linking()

    # Test back to chats button after success
    results["back_to_chats_button"] = await test_back_to_chats_button_after_success()

    # Test keyboard generation
    results["keyboard_generation"] = await test_keyboard_generation()

    # Summary
    print("\n" + "=" * 50)
    print("📊 BUTTON TESTS RESULTS SUMMARY:")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} | {status}")
        if success:
            passed += 1

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("🎉 All button tests passed! Button functionality is working correctly.")
    else:
        print("⚠️  Some button tests failed. Check the issues above.")
        print("\n🔧 TROUBLESHOOTING ADVICE:")
        if not results.get("back_button", False):
            print("- Back button handler may have issues with state management or message editing")
        if not results.get("cancel_button", False):
            print("- Cancel button handler may have issues with state clearing or keyboard display")
        if not results.get("back_to_chats_button", False):
            print("- Back to chats handler may have issues with database queries or state transitions")
        if not results.get("keyboard_generation", False):
            print("- Keyboard generation functions may have incorrect button text or callback data")

    return results


if __name__ == "__main__":
    asyncio.run(run_button_tests())
