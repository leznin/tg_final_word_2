"""
Tests for bot_permissions and last_info_update fields functionality
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from app.models.chats import Chat
from app.schemas.chat_info import BotPermissions
from app.telegram.services.chat_info import ChatInfoService
from app.services.chats import ChatService


class TestChatInfoFields:
    """Test bot_permissions and last_info_update fields"""

    @pytest.mark.asyncio
    async def test_chat_model_has_bot_permissions_field(self, db_session):
        """Test that Chat model has bot_permissions field"""
        chat = Chat(
            telegram_chat_id=123456,
            chat_type="group",
            title="Test Chat",
            added_by_user_id=1,
            ai_content_check_enabled=False
        )

        # Set bot permissions
        permissions = {"can_send_messages": True, "can_delete_messages": False}
        chat.bot_permissions = permissions
        chat.last_info_update = datetime.now(timezone.utc)

        db_session.add(chat)
        await db_session.commit()
        await db_session.refresh(chat)

        assert chat.bot_permissions == permissions
        assert chat.last_info_update is not None
        assert isinstance(chat.last_info_update, datetime)

    @pytest.mark.asyncio
    async def test_chat_service_update_bot_permissions(self, db_session):
        """Test that chat service can update bot permissions"""
        # Create test chat
        chat = Chat(
            telegram_chat_id=123456,
            chat_type="group",
            title="Test Chat",
            added_by_user_id=1,
            ai_content_check_enabled=False
        )
        db_session.add(chat)
        await db_session.commit()

        # Update bot permissions
        chat_service = ChatService(db_session)
        update_data = {
            "bot_permissions": {"can_send_messages": True, "can_delete_messages": True},
            "last_info_update": datetime.now(timezone.utc)
        }

        updated_chat = await chat_service.update_chat(chat.id, update_data)
        assert updated_chat is not None
        assert updated_chat.bot_permissions == {"can_send_messages": True, "can_delete_messages": True}
        assert updated_chat.last_info_update is not None

    def test_bot_permissions_schema(self):
        """Test BotPermissions schema validation"""
        # Test with all permissions
        permissions = BotPermissions(
            can_send_messages=True,
            can_send_audios=False,
            can_send_documents=True,
            can_send_photos=False,
            can_send_videos=True,
            can_send_video_notes=False,
            can_send_voice_notes=True,
            can_send_polls=False,
            can_send_other_messages=True,
            can_add_web_page_previews=False,
            can_change_info=True,
            can_invite_users=False,
            can_pin_messages=True,
            can_manage_topics=False,
            can_delete_messages=True,
            can_manage_video_chats=False,
            can_restrict_members=True,
            can_promote_members=False,
            can_post_messages=None,
            can_edit_messages=None,
            is_anonymous=False,
            custom_title=None
        )

        assert permissions.can_send_messages is True
        assert permissions.can_delete_messages is True
        assert permissions.can_restrict_members is True

        # Test with minimal permissions
        minimal_permissions = BotPermissions()
        assert minimal_permissions.can_send_messages is False
        assert minimal_permissions.can_delete_messages is False

    @pytest.mark.asyncio
    async def test_chat_info_service_updates_fields(self):
        """Test that ChatInfoService updates bot_permissions and last_info_update"""
        # Mock bot
        mock_bot = AsyncMock()
        mock_bot.id = 123456

        # Mock chat member with admin permissions
        mock_member = MagicMock()
        mock_member.can_send_messages = True
        mock_member.can_delete_messages = True
        mock_member.can_restrict_members = True
        mock_member.can_promote_members = False
        mock_bot.get_chat_member.return_value = mock_member

        # Create service
        service = ChatInfoService(mock_bot)

        # Test _get_bot_permissions method
        permissions = await service._get_bot_permissions(123456789)

        assert permissions is not None
        assert permissions.can_send_messages is True
        assert permissions.can_delete_messages is True
        assert permissions.can_restrict_members is True
        assert permissions.can_promote_members is False

    @pytest.mark.asyncio
    async def test_chat_info_service_handles_bot_not_admin(self):
        """Test that service handles case when bot is not admin"""
        from aiogram.types import ChatMember, ChatMemberMember

        # Mock bot
        mock_bot = AsyncMock()
        mock_bot.id = 123456

        # Mock chat member as regular member (not admin)
        mock_member = ChatMemberMember(
            user=MagicMock(id=123456, is_bot=True),
            status="member"
        )
        mock_bot.get_chat_member.return_value = mock_member

        # Create service
        service = ChatInfoService(mock_bot)

        # Test _get_bot_permissions method
        permissions = await service._get_bot_permissions(123456789)

        assert permissions is not None
        # Should return default permissions (all False)
        assert permissions.can_send_messages is False
        assert permissions.can_delete_messages is False

    @pytest.mark.asyncio
    async def test_chat_info_service_handles_api_errors(self):
        """Test that service handles Telegram API errors gracefully"""
        from aiogram.exceptions import TelegramBadRequest

        # Mock bot that raises exception
        mock_bot = AsyncMock()
        mock_bot.id = 123456
        mock_bot.get_chat_member.side_effect = TelegramBadRequest("Chat not found")

        # Create service
        service = ChatInfoService(mock_bot)

        # Test _get_bot_permissions method
        permissions = await service._get_bot_permissions(123456789)

        assert permissions is None

    @pytest.mark.asyncio
    async def test_frontend_filter_logic(self, db_session):
        """Test that frontend filter logic works correctly"""
        # Create test chats with different permissions
        chat1 = Chat(
            telegram_chat_id=111111,
            chat_type="group",
            title="Admin Chat",
            added_by_user_id=1,
            ai_content_check_enabled=False,
            bot_permissions={"can_delete_messages": True, "can_restrict_members": True, "can_promote_members": True},
            last_info_update=datetime.now(timezone.utc)
        )

        chat2 = Chat(
            telegram_chat_id=222222,
            chat_type="group",
            title="Limited Chat",
            added_by_user_id=1,
            ai_content_check_enabled=False,
            bot_permissions={"can_delete_messages": False, "can_restrict_members": False, "can_promote_members": False},
            last_info_update=datetime.now(timezone.utc)
        )

        chat3 = Chat(
            telegram_chat_id=333333,
            chat_type="group",
            title="No Info Chat",
            added_by_user_id=1,
            ai_content_check_enabled=False,
            bot_permissions=None,
            last_info_update=None
        )

        db_session.add_all([chat1, chat2, chat3])
        await db_session.commit()

        # Test filtering logic (similar to frontend)
        def filter_chat(chat, bot_permissions_filter):
            if bot_permissions_filter == 'all':
                return True
            if not chat.last_info_update:
                return bot_permissions_filter == 'none'
            if not chat.bot_permissions:
                return bot_permissions_filter == 'none'

            has_admin_rights = (
                chat.bot_permissions.get('can_delete_messages', False) or
                chat.bot_permissions.get('can_restrict_members', False) or
                chat.bot_permissions.get('can_promote_members', False)
            )

            if bot_permissions_filter == 'admin':
                return has_admin_rights
            if bot_permissions_filter == 'limited':
                return not has_admin_rights
            if bot_permissions_filter == 'none':
                return False

            return True

        # Test filtering
        assert filter_chat(chat1, 'admin') is True   # Has admin rights
        assert filter_chat(chat1, 'limited') is False # Not limited
        assert filter_chat(chat2, 'admin') is False  # No admin rights
        assert filter_chat(chat2, 'limited') is True  # Limited rights
        assert filter_chat(chat3, 'none') is True    # No info = none
        assert filter_chat(chat3, 'admin') is False  # No info != admin

    @pytest.mark.asyncio
    async def test_database_migration_applied(self, db_session):
        """Test that database migration added the required fields"""
        from sqlalchemy import inspect

        # Check that fields exist in database
        inspector = inspect(db_session.bind)
        columns = inspector.get_columns('chats')

        column_names = [col['name'] for col in columns]

        assert 'bot_permissions' in column_names
        assert 'last_info_update' in column_names
        assert 'ai_content_check_enabled' in column_names

        # Check column types
        bot_permissions_col = next(col for col in columns if col['name'] == 'bot_permissions')
        last_info_update_col = next(col for col in columns if col['name'] == 'last_info_update')

        assert bot_permissions_col['type'].__class__.__name__ == 'JSON' or 'JSON' in str(bot_permissions_col['type'])
        assert 'datetime' in str(last_info_update_col['type']).lower() or 'timestamp' in str(last_info_update_col['type']).lower()
