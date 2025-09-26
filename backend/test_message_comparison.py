#!/usr/bin/env python3
"""
Test script for message comparison functionality
"""

import asyncio
from app.core.database import get_db
from app.services.messages import MessageService
from app.schemas.messages import MessageCreate
from app.models.messages import Message


async def test_message_comparison():
    """Test message comparison functionality"""
    async for db in get_db():
        try:
            message_service = MessageService(db)

            # Create a test message in database
            test_message = MessageCreate(
                chat_id=8,  # Using existing chat ID
                telegram_message_id=99999,  # Unique ID for test
                telegram_user_id=415409454,
                message_type='text',
                text_content='Original test message'
            )

            db_message = await message_service.create_message(test_message)
            print(f"✓ Created test message with ID: {db_message.id}")

            # Test 1: Same text message (should return False - no changes)
            telegram_data_same = {
                'message_id': 99999,
                'text': 'Original test message'
            }
            has_changes = await message_service.compare_message_with_telegram_data(db_message, telegram_data_same)
            print(f"✓ Test 1 - Same text: {'CHANGED' if has_changes else 'UNCHANGED'}")

            # Test 2: Changed text message (should return True - has changes)
            telegram_data_changed_text = {
                'message_id': 99999,
                'text': 'Modified test message'
            }
            has_changes = await message_service.compare_message_with_telegram_data(db_message, telegram_data_changed_text)
            print(f"✓ Test 2 - Changed text: {'CHANGED' if has_changes else 'UNCHANGED'}")

            # Test 3: Changed to photo message (should return True - has changes)
            telegram_data_photo = {
                'message_id': 99999,
                'photo': [{'file_id': 'test_photo_id'}],
                'caption': 'Original test message'
            }
            has_changes = await message_service.compare_message_with_telegram_data(db_message, telegram_data_photo)
            print(f"✓ Test 3 - Changed to photo: {'CHANGED' if has_changes else 'UNCHANGED'}")

            # Test 4: Empty text vs None (should return False - no changes)
            telegram_data_empty = {
                'message_id': 99999,
                'text': ''
            }
            has_changes = await message_service.compare_message_with_telegram_data(db_message, telegram_data_empty)
            print(f"✓ Test 4 - Empty text vs original: {'CHANGED' if has_changes else 'UNCHANGED'}")

            # Create a photo message for testing media changes
            photo_message = MessageCreate(
                chat_id=8,
                telegram_message_id=99998,
                telegram_user_id=415409454,
                message_type='photo',
                text_content='Photo caption',
                media_file_id='original_photo_id',
                media_type='photo'
            )
            db_photo_message = await message_service.create_message(photo_message)
            print(f"✓ Created test photo message with ID: {db_photo_message.id}")

            # Test 5: Same photo message (should return False - no changes)
            telegram_data_same_photo = {
                'message_id': 99998,
                'photo': [{'file_id': 'original_photo_id'}],
                'caption': 'Photo caption'
            }
            has_changes = await message_service.compare_message_with_telegram_data(db_photo_message, telegram_data_same_photo)
            print(f"✓ Test 5 - Same photo: {'CHANGED' if has_changes else 'UNCHANGED'}")

            # Test 6: Changed photo file (should return True - has changes)
            telegram_data_changed_photo = {
                'message_id': 99998,
                'photo': [{'file_id': 'new_photo_id'}],
                'caption': 'Photo caption'
            }
            has_changes = await message_service.compare_message_with_telegram_data(db_photo_message, telegram_data_changed_photo)
            print(f"✓ Test 6 - Changed photo file: {'CHANGED' if has_changes else 'UNCHANGED'}")

            # Test 7: Changed photo caption (should return True - has changes)
            telegram_data_changed_caption = {
                'message_id': 99998,
                'photo': [{'file_id': 'original_photo_id'}],
                'caption': 'New photo caption'
            }
            has_changes = await message_service.compare_message_with_telegram_data(db_photo_message, telegram_data_changed_caption)
            print(f"✓ Test 7 - Changed photo caption: {'CHANGED' if has_changes else 'UNCHANGED'}")

            # Test update functionality
            print("\n--- Testing update functionality ---")
            update_data = {
                'message_id': 99999,
                'text': 'Updated message content'
            }
            updated_message = await message_service.update_message_from_telegram(8, update_data)
            if updated_message:
                print(f"✓ Updated message text to: {updated_message.text_content}")
            else:
                print("✗ Failed to update message")

            # Verify the update
            retrieved = await message_service.get_message(db_message.id)
            print(f"✓ Verified updated message: {retrieved.text_content}")

            print("\n✓ All message comparison tests completed!")

        except Exception as e:
            print(f"✗ Error during testing: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Clean up test messages
            try:
                # Delete test messages
                test_ids = [99999, 99998]
                for msg_id in test_ids:
                    test_msg = await message_service.get_message_by_telegram_id(8, msg_id)
                    if test_msg:
                        await db.delete(test_msg)
                        print(f"✓ Cleaned up test message {msg_id}")
                await db.commit()
            except Exception as e:
                print(f"Warning: Could not clean up test messages: {e}")


if __name__ == "__main__":
    asyncio.run(test_message_comparison())
