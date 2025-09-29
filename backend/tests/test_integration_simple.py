"""
Simple integration test for bot_permissions and last_info_update fields
"""
import pytest
from datetime import datetime, timezone
from app.models.chats import Chat


@pytest.mark.asyncio
async def test_chat_model_with_restored_fields(db_session):
    """Test that Chat model works with restored database fields"""
    # Create chat with all required fields
    chat = Chat(
        telegram_chat_id=999999999,
        chat_type="supergroup",
        title="Integration Test Chat",
        username="integration_test",
        added_by_user_id=1,
        ai_content_check_enabled=True,
        member_count=50,
        description="Test chat for integration testing",
        invite_link="https://t.me/integration_test",
        bot_permissions={
            "can_send_messages": True,
            "can_delete_messages": True,
            "can_restrict_members": True,
            "can_promote_members": False,
            "can_pin_messages": True
        },
        last_info_update=datetime.now(timezone.utc)
    )

    # Save to database
    db_session.add(chat)
    await db_session.commit()
    await db_session.refresh(chat)

    # Verify all fields are properly stored and retrieved
    assert chat.id is not None
    assert chat.telegram_chat_id == 999999999
    assert chat.chat_type == "supergroup"
    assert chat.title == "Integration Test Chat"
    assert chat.username == "integration_test"
    assert chat.ai_content_check_enabled is True
    assert chat.member_count == 50
    assert chat.description == "Test chat for integration testing"
    assert chat.invite_link == "https://t.me/integration_test"

    # Verify bot_permissions
    assert chat.bot_permissions is not None
    assert chat.bot_permissions["can_send_messages"] is True
    assert chat.bot_permissions["can_delete_messages"] is True
    assert chat.bot_permissions["can_restrict_members"] is True
    assert chat.bot_permissions["can_promote_members"] is False
    assert chat.bot_permissions["can_pin_messages"] is True

    # Verify last_info_update
    assert chat.last_info_update is not None
    assert isinstance(chat.last_info_update, datetime)

    print("✅ All fields successfully stored and retrieved from database")


@pytest.mark.asyncio
async def test_null_values_handling(db_session):
    """Test that null values are properly handled"""
    # Create chat with null values for bot_permissions and last_info_update
    chat = Chat(
        telegram_chat_id=888888888,
        chat_type="group",
        title="Null Values Test",
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

    print("✅ Null values properly handled")


@pytest.mark.asyncio
async def test_json_field_complexity(db_session):
    """Test that JSON field can store complex nested structures"""
    complex_permissions = {
        "can_send_messages": True,
        "can_delete_messages": True,
        "can_restrict_members": True,
        "custom_permissions": {
            "advanced_features": True,
            "moderation_tools": ["ban", "mute", "warn"],
            "metadata": {
                "version": "1.0",
                "features_enabled": ["ai_check", "auto_mod"]
            }
        }
    }

    chat = Chat(
        telegram_chat_id=777777777,
        chat_type="supergroup",
        title="Complex JSON Test",
        added_by_user_id=1,
        ai_content_check_enabled=True,
        bot_permissions=complex_permissions,
        last_info_update=datetime.now(timezone.utc)
    )

    db_session.add(chat)
    await db_session.commit()
    await db_session.refresh(chat)

    # Verify complex structure is preserved
    assert chat.bot_permissions == complex_permissions
    assert chat.bot_permissions["custom_permissions"]["advanced_features"] is True
    assert "ban" in chat.bot_permissions["custom_permissions"]["moderation_tools"]
    assert chat.bot_permissions["custom_permissions"]["metadata"]["version"] == "1.0"

    print("✅ Complex JSON structures properly stored and retrieved")
