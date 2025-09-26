#!/usr/bin/env python3
"""
Test script for media message processing
"""

import asyncio
from app.core.database import get_db
from app.services.messages import MessageService
from app.schemas.messages import TelegramMessageData


async def test_media_message_processing():
    """Test processing of media messages"""
    async for db in get_db():
        try:
            message_service = MessageService(db)

            # Simulate photo message from Telegram
            message_data = {
                'message_id': 128,
                'date': 1758825243,
                'from_user': {
                    'id': 7475114939,
                    'is_bot': False,
                    'first_name': 'Cyprus Flowers',
                    'username': 'cyprus_flowers',
                    'language_code': 'ru'
                },
                'photo': [
                    {
                        'file_id': 'AgACAgQAAyEFAAS2i8RXAAOAaNWLG5T-Neg0LnX4hmLd_cptm4UAAlzaMRv2NLFSqFVR5VvcpfwBAAMCAANzAAM2BA',
                        'file_unique_id': 'AQADXNoxG_Y0sVJ4',
                        'file_size': 597,
                        'width': 90,
                        'height': 29
                    },
                    {
                        'file_id': 'AgACAgQAAyEFAAS2i8RXAAOAaNWLG5T-Neg0LnX4hmLd_cptm4UAAlzaMRv2NLFSqFVR5VvcpfwBAAMCAANtAAM2BA',
                        'file_unique_id': 'AQADXNoxG_Y0sVJy',
                        'file_size': 5134,
                        'width': 320,
                        'height': 103
                    },
                    {
                        'file_id': 'AgACAgQAAyEFAAS2i8RXAAOAaNWLG5T-Neg0LnX4hmLd_cptm4UAAlzaMRv2NLFSqFVR5VvcpfwBAAMCAAN4AAM2BA',
                        'file_unique_id': 'AQADXNoxG_Y0sVJ9',
                        'file_size': 10293,
                        'width': 680,
                        'height': 218
                    }
                ]
            }

            # Test message creation
            message = await message_service.create_message_from_telegram(8, message_data)
            if message:
                print(f"✓ Created media message with ID: {message.id}")
                print(f"  - Message type: {message.message_type}")
                print(f"  - Media file ID: {message.media_file_id}")
                print(f"  - Media type: {message.media_type}")
            else:
                print("✗ Failed to create media message")

        finally:
            pass


async def main():
    """Run tests"""
    print("Testing media message processing...\n")

    try:
        await test_media_message_processing()
        print("\n✓ Media message processing test completed!")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
