#!/usr/bin/env python3
"""
Test real webhook functionality with actual HTTP requests
"""

import asyncio
import json
import httpx
from datetime import datetime


async def test_real_webhook():
    """Test real webhook endpoint with actual HTTP request"""

    # Real webhook data from Telegram for /start command
    webhook_data = {
        "update_id": 123456789,
        "message": {
            "message_id": 123,
            "from": {
                "id": 1234567890,  # Real user ID for testing
                "is_bot": False,
                "first_name": "TestRealUser",
                "username": "testrealuser",
                "language_code": "en"
            },
            "chat": {
                "id": 1234567890,
                "first_name": "TestRealUser",
                "username": "testrealuser",
                "type": "private"
            },
            "date": int(datetime.now().timestamp()),
            "text": "/start"
        }
    }

    print("🧪 Testing real webhook with actual HTTP request...")
    print(f"📤 Sending webhook data: {json.dumps(webhook_data, indent=2)}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/webhook",
                json=webhook_data,
                headers={"Content-Type": "application/json"}
            )

            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response body: {response.text}")

            if response.status_code == 200:
                print("✅ Webhook processed successfully!")

                # Check if user was saved in database
                print("\n🔍 Checking if user was saved in database...")

                # Import here to avoid circular imports
                import sys
                sys.path.insert(0, '/Users/s3s3s/Desktop/Не удалять/fin 3/backend/app')

                from app.core.database import get_db
                from app.services.users import UserService

                async for db in get_db():
                    user_service = UserService(db)
                    saved_user = await user_service.get_user_by_telegram_id(webhook_data["message"]["from"]["id"])

                    if saved_user:
                        print("✅ User successfully saved to database!")
                        print(f"   ID: {saved_user.id}")
                        print(f"   Telegram ID: {saved_user.telegram_id}")
                        print(f"   Name: {saved_user.first_name}")
                        print(f"   Username: {saved_user.username}")

                        # Clean up test user
                        await user_service.delete_user(saved_user.id)
                        print("🧹 Test user cleaned up")
                    else:
                        print("❌ User was not saved to database")
                    break

            else:
                print("❌ Webhook processing failed!")

    except Exception as e:
        print(f"❌ Error testing webhook: {e}")
        import traceback
        traceback.print_exc()


async def test_bot_status():
    """Test if bot is properly initialized"""
    print("\n🤖 Testing bot status...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/")

            if response.status_code == 200:
                data = response.json()
                print("✅ API is running")
                print(f"   Version: {data.get('version', 'unknown')}")
                print(f"   Message: {data.get('message', 'unknown')}")
            else:
                print("❌ API is not responding properly")

    except Exception as e:
        print(f"❌ Error checking bot status: {e}")


async def main():
    """Main test function"""
    print("🚀 TESTING REAL WEBHOOK FUNCTIONALITY")
    print("=" * 50)

    await test_bot_status()
    await test_real_webhook()

    print("\n" + "=" * 50)
    print("📋 MANUAL TESTING INSTRUCTIONS:")
    print("=" * 50)
    print("1. Open Telegram and find your bot")
    print("2. Send /start command to the bot")
    print("3. Check if you receive a welcome message")
    print("4. Check database for new user record")
    print("\nIf the bot doesn't respond:")
    print("- Check if ngrok tunnel is running")
    print("- Verify webhook URL in bot settings")
    print("- Check server logs for errors")


if __name__ == "__main__":
    asyncio.run(main())
