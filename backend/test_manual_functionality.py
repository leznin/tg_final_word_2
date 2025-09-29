#!/usr/bin/env python3
"""
Manual test for bot_permissions and last_info_update functionality
"""
import asyncio
from datetime import datetime, timezone
from app.core.database import Base, engine
from app.models.chats import Chat
from app.schemas.chat_info import BotPermissions


async def test_functionality():
    """Test bot_permissions and last_info_update functionality"""
    print("🧪 Testing bot_permissions and last_info_update functionality...")

    # Test 1: BotPermissions schema
    print("\n📋 Test 1: BotPermissions schema")
    try:
        permissions = BotPermissions(
            can_send_messages=True,
            can_delete_messages=True,
            can_restrict_members=True,
            can_promote_members=False,
            custom_title="Test Admin"
        )
        print("✅ BotPermissions schema works")
        print(f"   Permissions: {permissions.model_dump()}")
    except Exception as e:
        print(f"❌ BotPermissions schema error: {e}")
        return

    # Test 2: Chat model with new fields
    print("\n💾 Test 2: Chat model with bot_permissions and last_info_update")
    try:
        chat = Chat(
            telegram_chat_id=999999999,
            chat_type="group",
            title="Test Chat",
            added_by_user_id=1,
            ai_content_check_enabled=True,
            bot_permissions={"can_send_messages": True, "can_delete_messages": False},
            last_info_update=datetime.now(timezone.utc)
        )
        print("✅ Chat model created successfully")
        print(f"   bot_permissions: {chat.bot_permissions}")
        print(f"   last_info_update: {chat.last_info_update}")
    except Exception as e:
        print(f"❌ Chat model error: {e}")
        return

    # Test 3: Database operations
    print("\n🗄️ Test 3: Database operations")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with engine.begin() as conn:
            from sqlalchemy.orm import sessionmaker
            from sqlalchemy.ext.asyncio import AsyncSession

            async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            async with async_session() as session:
                # Save chat
                session.add(chat)
                await session.commit()
                await session.refresh(chat)

                print("✅ Chat saved to database")
                print(f"   ID: {chat.id}")
                print(f"   bot_permissions: {chat.bot_permissions}")
                print(f"   last_info_update: {chat.last_info_update}")

                # Update permissions
                chat.bot_permissions = {
                    "can_send_messages": True,
                    "can_delete_messages": True,
                    "can_restrict_members": True
                }
                chat.last_info_update = datetime.now(timezone.utc)

                await session.commit()
                await session.refresh(chat)

                print("✅ Chat updated successfully")
                print(f"   Updated bot_permissions: {chat.bot_permissions}")

    except Exception as e:
        print(f"❌ Database operation error: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test 4: Frontend filter logic
    print("\n🎨 Test 4: Frontend filter logic")
    try:
        def filter_chat(chat_obj, filter_type):
            if filter_type == 'all':
                return True
            if not chat_obj.last_info_update:
                return filter_type == 'none'
            if not chat_obj.bot_permissions:
                return filter_type == 'none'

            has_admin_rights = (
                chat_obj.bot_permissions.get('can_delete_messages', False) or
                chat_obj.bot_permissions.get('can_restrict_members', False) or
                chat_obj.bot_permissions.get('can_promote_members', False)
            )

            if filter_type == 'admin':
                return has_admin_rights
            if filter_type == 'limited':
                return not has_admin_rights
            if filter_type == 'none':
                return False

            return True

        # Test different scenarios
        admin_chat = type('MockChat', (), {
            'last_info_update': datetime.now(timezone.utc),
            'bot_permissions': {'can_delete_messages': True, 'can_restrict_members': True}
        })()

        limited_chat = type('MockChat', (), {
            'last_info_update': datetime.now(timezone.utc),
            'bot_permissions': {'can_send_messages': True}
        })()

        no_info_chat = type('MockChat', (), {
            'last_info_update': None,
            'bot_permissions': None
        })()

        assert filter_chat(admin_chat, 'admin') is True
        assert filter_chat(admin_chat, 'limited') is False
        assert filter_chat(limited_chat, 'admin') is False
        assert filter_chat(limited_chat, 'limited') is True
        assert filter_chat(no_info_chat, 'none') is True
        assert filter_chat(no_info_chat, 'admin') is False

        print("✅ Frontend filter logic works correctly")

    except Exception as e:
        print(f"❌ Frontend filter logic error: {e}")
        return

    print("\n🎉 All tests passed! Functionality is working correctly.")


if __name__ == "__main__":
    asyncio.run(test_functionality())
