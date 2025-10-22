#!/usr/bin/env python3
"""
Script to test telegram user history functionality
"""

import asyncio
from app.core.database import engine, get_db
from app.services.telegram_users import TelegramUserService
from app.schemas.telegram_users import TelegramUserData
from sqlalchemy import text

async def test_history_functionality():
    """Test the history functionality"""
    async for db in get_db():
        try:
            # First, let's create the table manually if it doesn't exist
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS telegram_user_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    telegram_user_id BIGINT NOT NULL,
                    field_name VARCHAR(50) NOT NULL,
                    old_value VARCHAR(255),
                    new_value VARCHAR(255),
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_telegram_user_history_user_id (telegram_user_id),
                    INDEX idx_telegram_user_history_changed_at (changed_at)
                )
            """))
            await db.commit()
            print("✅ Created telegram_user_history table")

            # Create service instance
            service = TelegramUserService(db)

            # Test data - simulate a user with changing name
            test_user_id = 123456789

            # First update - create user
            user_data1 = TelegramUserData(
                telegram_user_id=test_user_id,
                is_bot=False,
                first_name="John",
                last_name="Doe",
                username="johndoe"
            )

            print("📝 Creating user with initial data...")
            user1 = await service.create_or_update_user_from_telegram(user_data1)
            print(f"✅ User created: {user1.first_name} {user1.last_name} (@{user1.username})")

            # Check history - should be empty for new user
            result = await db.execute(text("SELECT COUNT(*) FROM telegram_user_history WHERE telegram_user_id = :user_id"), {"user_id": test_user_id})
            history_count = result.scalar()
            print(f"📊 History entries after creation: {history_count}")

            # Second update - change first name
            user_data2 = TelegramUserData(
                telegram_user_id=test_user_id,
                is_bot=False,
                first_name="Johnny",  # Changed!
                last_name="Doe",
                username="johndoe"
            )

            print("📝 Updating user - changing first name...")
            user2 = await service.create_or_update_user_from_telegram(user_data2)
            print(f"✅ User updated: {user2.first_name} {user2.last_name} (@{user2.username})")

            # Check history
            result = await db.execute(text("""
                SELECT field_name, old_value, new_value, changed_at
                FROM telegram_user_history
                WHERE telegram_user_id = :user_id
                ORDER BY changed_at
            """), {"user_id": test_user_id})
            history = result.fetchall()

            print(f"📊 History entries after first name change: {len(history)}")
            for entry in history:
                print(f"   • {entry[0]}: '{entry[1]}' → '{entry[2]}' at {entry[3]}")

            # Third update - change username
            user_data3 = TelegramUserData(
                telegram_user_id=test_user_id,
                is_bot=False,
                first_name="Johnny",
                last_name="Doe",
                username="johnny_doe"  # Changed!
            )

            print("📝 Updating user - changing username...")
            user3 = await service.create_or_update_user_from_telegram(user_data3)
            print(f"✅ User updated: {user3.first_name} {user3.last_name} (@{user3.username})")

            # Check final history
            result = await db.execute(text("""
                SELECT field_name, old_value, new_value, changed_at
                FROM telegram_user_history
                WHERE telegram_user_id = :user_id
                ORDER BY changed_at
            """), {"user_id": test_user_id})
            final_history = result.fetchall()

            print(f"📊 Final history entries: {len(final_history)}")
            for entry in final_history:
                print(f"   • {entry[0]}: '{entry[1]}' → '{entry[2]}' at {entry[3]}")

            # Fourth update - no changes (should not create history entries)
            user_data4 = TelegramUserData(
                telegram_user_id=test_user_id,
                is_bot=False,
                first_name="Johnny",
                last_name="Doe",
                username="johnny_doe"  # Same as before
            )

            print("📝 Updating user - no changes...")
            user4 = await service.create_or_update_user_from_telegram(user_data4)
            print(f"✅ User updated: {user4.first_name} {user4.last_name} (@{user4.username})")

            # Check history again - should be the same
            result = await db.execute(text("SELECT COUNT(*) FROM telegram_user_history WHERE telegram_user_id = :user_id"), {"user_id": test_user_id})
            final_count = result.scalar()
            print(f"📊 History entries after no-change update: {final_count}")

            if final_count == len(final_history):
                print("✅ No new history entries created for unchanged data")
            else:
                print("❌ Unexpected history entries created")

            print("🎉 Test completed successfully!")

        except Exception as e:
            print(f"❌ Error during test: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_history_functionality())
