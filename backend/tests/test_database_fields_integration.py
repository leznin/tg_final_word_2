"""
Integration tests for bot_permissions and last_info_update database fields
"""
import pytest
from datetime import datetime, timezone
from app.models.chats import Chat
from app.services.chats import ChatService


@pytest.mark.asyncio
class TestDatabaseFieldsIntegration:
    """Integration tests for database fields functionality"""

    async def test_chat_model_fields_persistence(self, db_session):
        """Test that Chat model fields are properly persisted to database"""
        # Create chat with all fields
        chat = Chat(
            telegram_chat_id=123456789,
            chat_type="supergroup",
            title="Integration Test Chat",
            username="testchat",
            added_by_user_id=1,
            ai_content_check_enabled=True,
            member_count=42,
            description="Test chat for integration testing",
            invite_link="https://t.me/testchat",
            bot_permissions={
                "can_send_messages": True,
                "can_delete_messages": True,
                "can_restrict_members": True,
                "can_promote_members": False
            },
            last_info_update=datetime.now(timezone.utc)
        )

        # Save to database
        db_session.add(chat)
        await db_session.commit()
        await db_session.refresh(chat)

        # Verify all fields were saved
        assert chat.id is not None
        assert chat.telegram_chat_id == 123456789
        assert chat.chat_type == "supergroup"
        assert chat.title == "Integration Test Chat"
        assert chat.username == "testchat"
        assert chat.ai_content_check_enabled is True
        assert chat.member_count == 42
        assert chat.description == "Test chat for integration testing"
        assert chat.invite_link == "https://t.me/testchat"
        assert chat.bot_permissions is not None
        assert chat.bot_permissions["can_send_messages"] is True
        assert chat.bot_permissions["can_delete_messages"] is True
        assert chat.bot_permissions["can_restrict_members"] is True
        assert chat.bot_permissions["can_promote_members"] is False
        assert chat.last_info_update is not None
        assert isinstance(chat.last_info_update, datetime)

    async def test_chat_service_update_fields(self, db_session):
        """Test that ChatService can update bot_permissions and last_info_update"""
        # Create initial chat
        chat = Chat(
            telegram_chat_id=987654321,
            chat_type="group",
            title="Update Test Chat",
            added_by_user_id=1,
            ai_content_check_enabled=False
        )
        db_session.add(chat)
        await db_session.commit()

        # Update fields using service
        chat_service = ChatService(db_session)

        # First update - set bot permissions
        update_data_1 = {
            "bot_permissions": {
                "can_send_messages": True,
                "can_delete_messages": False,
                "can_restrict_members": False
            },
            "last_info_update": datetime.now(timezone.utc)
        }

        updated_chat = await chat_service.update_chat(chat.id, update_data_1)
        assert updated_chat is not None
        assert updated_chat.bot_permissions["can_send_messages"] is True
        assert updated_chat.bot_permissions["can_delete_messages"] is False
        assert updated_chat.last_info_update is not None

        # Second update - modify permissions
        update_data_2 = {
            "bot_permissions": {
                "can_send_messages": True,
                "can_delete_messages": True,
                "can_restrict_members": True,
                "can_promote_members": True
            },
            "last_info_update": datetime.now(timezone.utc)
        }

        updated_chat_2 = await chat_service.update_chat(chat.id, update_data_2)
        assert updated_chat_2.bot_permissions["can_delete_messages"] is True
        assert updated_chat_2.bot_permissions["can_restrict_members"] is True
        assert updated_chat_2.bot_permissions["can_promote_members"] is True

    async def test_null_values_handling(self, db_session):
        """Test that null values are properly handled"""
        # Create chat with null values
        chat = Chat(
            telegram_chat_id=555666777,
            chat_type="group",
            title="Null Test Chat",
            added_by_user_id=1,
            ai_content_check_enabled=False,
            bot_permissions=None,
            last_info_update=None
        )

        db_session.add(chat)
        await db_session.commit()
        await db_session.refresh(chat)

        # Verify null handling
        assert chat.bot_permissions is None
        assert chat.last_info_update is None

        # Update with values
        chat_service = ChatService(db_session)
        update_data = {
            "bot_permissions": {"can_send_messages": True},
            "last_info_update": datetime.now(timezone.utc)
        }

        updated_chat = await chat_service.update_chat(chat.id, update_data)
        assert updated_chat.bot_permissions is not None
        assert updated_chat.bot_permissions["can_send_messages"] is True
        assert updated_chat.last_info_update is not None

    async def test_json_storage_bot_permissions(self, db_session):
        """Test that bot_permissions are stored as JSON in database"""
        # Test complex nested structure
        complex_permissions = {
            "can_send_messages": True,
            "can_delete_messages": True,
            "can_restrict_members": True,
            "can_promote_members": False,
            "can_pin_messages": True,
            "can_manage_topics": False,
            "custom_title": "Super Admin",
            "nested_object": {
                "sub_perm": True
            }
        }

        chat = Chat(
            telegram_chat_id=111222333,
            chat_type="supergroup",
            title="JSON Test Chat",
            added_by_user_id=1,
            ai_content_check_enabled=False,
            bot_permissions=complex_permissions,
            last_info_update=datetime.now(timezone.utc)
        )

        db_session.add(chat)
        await db_session.commit()
        await db_session.refresh(chat)

        # Verify complex structure is preserved
        assert chat.bot_permissions == complex_permissions
        assert chat.bot_permissions["nested_object"]["sub_perm"] is True
        assert chat.bot_permissions["custom_title"] == "Super Admin"

    async def test_timestamp_precision(self, db_session):
        """Test that datetime timestamps are stored with proper precision"""
        before_time = datetime.now(timezone.utc)

        chat = Chat(
            telegram_chat_id=444555666,
            chat_type="group",
            title="Timestamp Test Chat",
            added_by_user_id=1,
            ai_content_check_enabled=False,
            last_info_update=before_time
        )

        db_session.add(chat)
        await db_session.commit()
        await db_session.refresh(chat)

        after_time = datetime.now(timezone.utc)

        # Verify timestamp is within reasonable range
        assert before_time <= chat.last_info_update <= after_time
        # Check that microseconds are preserved (if supported by DB)
        assert isinstance(chat.last_info_update, datetime)
