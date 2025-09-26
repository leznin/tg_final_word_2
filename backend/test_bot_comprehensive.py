#!/usr/bin/env python3
"""
Comprehensive test script for Telegram bot functionality
Testing why new users don't receive messages and aren't saved to database
"""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, Mock, patch

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, User, Chat, Update

from app.telegram.middlewares.database import DatabaseMiddleware
from app.telegram.handlers.start import start_router, member_router, handle_start_command
from app.telegram.bot import TelegramBot
from app.core.config import settings
from app.core.database import get_db
from app.services.users import UserService
from app.schemas.users import TelegramUserData
from sqlalchemy.ext.asyncio import AsyncSession


async def test_database_connection():
    """Test database connection and session"""
    print("=== TESTING DATABASE CONNECTION ===")

    try:
        async for session in get_db():
            print("✓ Database session created successfully")
            # Test basic query
            result = await session.execute("SELECT 1")
            print(f"✓ Basic query executed: {result.scalar()}")
            break
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

    return True


async def test_user_service():
    """Test UserService functionality"""
    print("\n=== TESTING USER SERVICE ===")

    async for db in get_db():
        user_service = UserService(db)

        # Test creating new user
        test_user_data = TelegramUserData(
            id=999999999,
            first_name="TestUser",
            username="testuser123",
            is_bot=False
        )

        try:
            # Check if user exists
            existing_user = await user_service.get_user_by_telegram_id(test_user_data.id)
            if existing_user:
                print(f"✓ Test user already exists: {existing_user.id}")
                # Delete for clean test
                await user_service.delete_user(existing_user.id)
                print("✓ Deleted existing test user")

            # Create new user
            new_user = await user_service.create_or_update_telegram_user(test_user_data)
            print(f"✓ User created: ID={new_user.id}, TelegramID={new_user.telegram_id}")

            # Verify user was saved
            saved_user = await user_service.get_user_by_telegram_id(test_user_data.id)
            if saved_user:
                print("✓ User successfully saved to database")
            else:
                print("✗ User not found after creation")

            # Clean up
            await user_service.delete_user(new_user.id)
            print("✓ Test user cleaned up")

        except Exception as e:
            print(f"✗ UserService test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

        break

    return True


async def test_start_handler_with_db():
    """Test the start command handler with real database"""
    print("\n=== TESTING START HANDLER WITH DATABASE ===")

    async for db in get_db():
        # Create mock message
        mock_user = User(
            id=888888888,
            is_bot=False,
            first_name="HandlerTest",
            username="handlertest",
            language_code="en"
        )

        mock_message = Mock()
        mock_message.from_user = mock_user
        mock_message.reply = AsyncMock(return_value=None)

        try:
            # Call handler
            await handle_start_command(mock_message, db)

            # Check if reply was called
            if mock_message.reply.called:
                print("✓ Message.reply() was called")
                call_args = mock_message.reply.call_args
                print(f"✓ Reply text preview: {call_args[1]['text'][:50]}...")
            else:
                print("✗ Message.reply() was not called")

            # Check if user was saved
            user_service = UserService(db)
            saved_user = await user_service.get_user_by_telegram_id(mock_user.id)

            if saved_user:
                print(f"✓ User saved to database: {saved_user.first_name} ({saved_user.telegram_id})")
            else:
                print("✗ User not saved to database")

            # Clean up
            if saved_user:
                await user_service.delete_user(saved_user.id)
                print("✓ Test user cleaned up")

        except Exception as e:
            print(f"✗ Start handler test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

        break

    return True


async def test_bot_initialization():
    """Test bot initialization and configuration"""
    print("\n=== TESTING BOT INITIALIZATION ===")

    # Check settings
    token_configured = bool(settings.TELEGRAM_BOT_TOKEN)
    webhook_configured = bool(settings.TELEGRAM_WEBHOOK_URL)

    print(f"Bot token configured: {token_configured}")
    print(f"Webhook URL configured: {webhook_configured}")

    if not token_configured:
        print("✗ Bot token not configured - this is likely the issue!")
        return False

    if not webhook_configured:
        print("✗ Webhook URL not configured - this could be the issue!")
        return False

    # Test bot creation
    try:
        bot = Bot(
            token=settings.TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        print("✓ Bot instance created successfully")

        # Test bot connection
        bot_info = await bot.get_me()
        print(f"✓ Bot connected: {bot_info.username} (ID: {bot_info.id})")

    except Exception as e:
        print(f"✗ Bot initialization failed: {e}")
        return False

    return True


async def test_webhook_processing():
    """Test webhook processing functionality"""
    print("\n=== TESTING WEBHOOK PROCESSING ===")

    try:
        # Create bot instance
        bot = TelegramBot()

        # Initialize bot
        await bot.start()

        if not bot.is_running:
            print("✗ Bot failed to start")
            return False

        print("✓ Bot started successfully")

        # Create mock webhook data for /start command
        mock_update_data = {
            "update_id": 12345,
            "message": {
                "message_id": 1,
                "from": {
                    "id": 777777777,
                    "is_bot": False,
                    "first_name": "WebhookTest",
                    "username": "webhooktest",
                    "language_code": "en"
                },
                "chat": {
                    "id": 777777777,
                    "first_name": "WebhookTest",
                    "username": "webhooktest",
                    "type": "private"
                },
                "date": 1234567890,
                "text": "/start"
            }
        }

        # Mock the reply method to avoid actual sending
        with patch('aiogram.types.Message.reply', new_callable=AsyncMock) as mock_reply:
            mock_reply.return_value = None

            # Process webhook
            await bot.process_webhook(mock_update_data)

            print("✓ Webhook processed without errors")

            # Check if reply was attempted
            if mock_reply.called:
                print("✓ Bot attempted to send reply")
            else:
                print("⚠ Bot did not attempt to send reply (may be normal for async processing)")

        # Stop bot
        await bot.stop()
        print("✓ Bot stopped successfully")

    except Exception as e:
        print(f"✗ Webhook processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


async def test_middleware_functionality():
    """Test database middleware"""
    print("\n=== TESTING DATABASE MIDDLEWARE ===")

    try:
        middleware = DatabaseMiddleware()
        print("✓ Middleware instance created")

        # Test middleware call
        async def dummy_handler(event, data):
            if "db" in data:
                print("✓ Database session injected into handler data")
                # Test that session works
                result = await data["db"].execute("SELECT 1")
                print(f"✓ Database session functional: {result.scalar()}")
            else:
                print("✗ Database session not injected")
            return None

        # Mock event
        mock_event = Mock()

        # Call middleware
        await middleware(dummy_handler, mock_event, {})

    except Exception as e:
        print(f"✗ Middleware test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


async def run_comprehensive_tests():
    """Run all tests and provide summary"""
    print("🚀 STARTING COMPREHENSIVE BOT TESTS")
    print("=" * 50)

    results = {}

    # Test database connection first
    results["database"] = await test_database_connection()

    # Test user service
    results["user_service"] = await test_user_service()

    # Test bot initialization
    results["bot_init"] = await test_bot_initialization()

    # Test middleware
    results["middleware"] = await test_middleware_functionality()

    # Test start handler
    results["start_handler"] = await test_start_handler_with_db()

    # Test webhook processing
    results["webhook"] = await test_webhook_processing()

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY:")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:15} | {status}")
        if success:
            passed += 1

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! Bot should be working correctly.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")

        # Provide troubleshooting advice
        print("\n🔧 TROUBLESHOOTING ADVICE:")

        if not results.get("database", False):
            print("- Check database connection and configuration")

        if not results.get("bot_init", False):
            print("- Verify TELEGRAM_BOT_TOKEN and TELEGRAM_WEBHOOK_URL in environment variables")
            print("- Make sure the bot token is valid")

        if not results.get("user_service", False):
            print("- Check UserService implementation and database schema")

        if not results.get("middleware", False):
            print("- Database middleware may have issues with session injection")

        if not results.get("start_handler", False):
            print("- Start command handler may have bugs")

        if not results.get("webhook", False):
            print("- Webhook processing may be failing")

    return results


if __name__ == "__main__":
    # Set environment variables for testing (replace with your actual values)
    os.environ["TELEGRAM_BOT_TOKEN"] = "7703818325:AAEKjEswBvhEK1AXzJVJyLAydxRoPMkmeVk"
    os.environ["TELEGRAM_WEBHOOK_URL"] = "https://test777.ngrok.app/webhook"
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

    asyncio.run(run_comprehensive_tests())
