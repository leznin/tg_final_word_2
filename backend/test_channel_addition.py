#!/usr/bin/env python3
"""
Test script to simulate channel addition update
"""

import asyncio
import sys
sys.path.insert(0, 'app')

from aiogram.types import Update, ChatMemberUpdated, Chat, User
from app.core.database import get_db
from app.telegram.handlers.start import handle_my_chat_member


async def test_channel_addition():
    """Test channel addition scenario"""

    # Create mock update data based on the provided JSON
    mock_update_data = {
        "update_id": 277110958,
        "my_chat_member": {
            "chat": {
                "id": -1003008079966,
                "title": "тест канал",
                "type": "channel"
            },
            "from": {
                "id": 415409454,
                "is_bot": False,
                "first_name": "Qwerty",
                "username": "s3s3s",
                "language_code": "ru",
                "is_premium": True
            },
            "date": 1758812697,
            "old_chat_member": {
                "user": {
                    "id": 7703818325,
                    "is_bot": True,
                    "first_name": "i_unicorn_i",
                    "username": "i_unicorn_i_bot"
                },
                "status": "left"
            },
            "new_chat_member": {
                "user": {
                    "id": 7703818325,
                    "is_bot": True,
                    "first_name": "i_unicorn_i",
                    "username": "i_unicorn_i_bot"
                },
                "status": "administrator",
                "can_be_edited": False,
                "can_manage_chat": True,
                "can_change_info": True,
                "can_post_messages": False,
                "can_edit_messages": False,
                "can_delete_messages": True,
                "can_invite_users": True,
                "can_restrict_members": True,
                "can_promote_members": False,
                "can_manage_video_chats": False,
                "can_post_stories": False,
                "can_edit_stories": False,
                "can_delete_stories": False,
                "can_manage_direct_messages": False,
                "is_anonymous": False,
                "can_manage_voice_chats": False
            }
        }
    }

    print("🧪 Testing channel addition update...")
    print(f"Update data: {mock_update_data}")

    try:
        # Convert to aiogram Update object
        update = Update(**mock_update_data)

        print(f"✅ Update object created: {update.update_id}")
        print(f"   Chat type: {update.my_chat_member.chat.type}")
        print(f"   Old status: {update.my_chat_member.old_chat_member.status}")
        print(f"   New status: {update.my_chat_member.new_chat_member.status}")
        print(f"   From user: {update.my_chat_member.from_user}")

        # Test with database
        async for db in get_db():
            await handle_my_chat_member(update.my_chat_member, db)
            break

        print("✅ Handler executed successfully")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_channel_addition())
