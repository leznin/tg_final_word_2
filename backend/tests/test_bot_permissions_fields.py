"""
Tests for bot_permissions and last_info_update fields functionality
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from app.schemas.chat_info import BotPermissions


class TestBotPermissionsSchema:
    """Test BotPermissions schema validation"""

    def test_bot_permissions_schema_full(self):
        """Test BotPermissions schema with all permissions"""
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

    def test_bot_permissions_schema_minimal(self):
        """Test BotPermissions schema with minimal permissions"""
        minimal_permissions = BotPermissions()
        assert minimal_permissions.can_send_messages is False
        assert minimal_permissions.can_delete_messages is False

    def test_bot_permissions_serialization(self):
        """Test that BotPermissions can be properly serialized to JSON"""
        permissions = BotPermissions(
            can_send_messages=True,
            can_delete_messages=True,
            can_restrict_members=True,
            can_promote_members=False,
            can_post_messages=True,
            can_edit_messages=False,
            custom_title="Test Admin"
        )

        # Convert to dict (as it would be stored in DB)
        permissions_dict = permissions.model_dump()

        assert permissions_dict["can_send_messages"] is True
        assert permissions_dict["can_delete_messages"] is True
        assert permissions_dict["can_restrict_members"] is True
        assert permissions_dict["can_promote_members"] is False
        assert permissions_dict["can_post_messages"] is True
        assert permissions_dict["can_edit_messages"] is False
        assert permissions_dict["custom_title"] == "Test Admin"


class TestFrontendFilterLogic:
    """Test frontend filtering logic for bot permissions"""

    def test_filter_logic_admin_rights(self):
        """Test filtering logic for chats with admin rights"""
        # Mock chat with admin permissions
        chat = MagicMock()
        chat.last_info_update = datetime.now(timezone.utc)
        chat.bot_permissions = {
            "can_delete_messages": True,
            "can_restrict_members": True,
            "can_promote_members": True
        }

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
        assert filter_chat(chat, 'admin') is True   # Has admin rights
        assert filter_chat(chat, 'limited') is False # Not limited
        assert filter_chat(chat, 'all') is True     # All filter

    def test_filter_logic_limited_rights(self):
        """Test filtering logic for chats with limited rights"""
        # Mock chat with limited permissions
        chat = MagicMock()
        chat.last_info_update = datetime.now(timezone.utc)
        chat.bot_permissions = {
            "can_delete_messages": False,
            "can_restrict_members": False,
            "can_promote_members": False,
            "can_send_messages": True
        }

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

        assert filter_chat(chat, 'admin') is False  # No admin rights
        assert filter_chat(chat, 'limited') is True  # Limited rights

    def test_filter_logic_no_info(self):
        """Test filtering logic for chats without permission info"""
        # Mock chat without permission info
        chat = MagicMock()
        chat.last_info_update = None
        chat.bot_permissions = None

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

        assert filter_chat(chat, 'none') is True    # No info = none
        assert filter_chat(chat, 'admin') is False  # No info != admin


class TestChatInfoService:
    """Test ChatInfoService bot permissions functionality"""

    @pytest.mark.asyncio
    async def test_get_bot_permissions_admin(self):
        """Test getting bot permissions when bot is admin"""
        from app.telegram.services.chat_info import ChatInfoService

        # Mock bot
        mock_bot = AsyncMock()
        mock_bot.id = 123456

        # Mock database session
        mock_db = AsyncMock()

        # Mock chat member with admin permissions
        mock_member = MagicMock()
        mock_member.can_send_messages = True
        mock_member.can_delete_messages = True
        mock_member.can_restrict_members = True
        mock_member.can_promote_members = False
        mock_bot.get_chat_member.return_value = mock_member

        # Create service
        service = ChatInfoService(mock_bot, mock_db)

        # Test _get_bot_permissions method
        permissions = await service._get_bot_permissions(123456789)

        assert permissions is not None
        assert permissions.can_send_messages is True
        assert permissions.can_delete_messages is True
        assert permissions.can_restrict_members is True
        assert permissions.can_promote_members is False

    @pytest.mark.asyncio
    async def test_get_bot_permissions_member(self):
        """Test getting bot permissions when bot is regular member"""
        from app.telegram.services.chat_info import ChatInfoService
        from aiogram.types import ChatMemberMember, User

        # Mock bot
        mock_bot = AsyncMock()
        mock_bot.id = 123456

        # Mock database session
        mock_db = AsyncMock()

        # Mock chat member as regular member (not admin)
        mock_user = User(id=123456, is_bot=True, first_name="TestBot")
        mock_member = ChatMemberMember(
            user=mock_user,
            status="member"
        )
        mock_bot.get_chat_member.return_value = mock_member

        # Create service
        service = ChatInfoService(mock_bot, mock_db)

        # Test _get_bot_permissions method
        permissions = await service._get_bot_permissions(123456789)

        assert permissions is not None
        # Should return default permissions (all False)
        assert permissions.can_send_messages is False
        assert permissions.can_delete_messages is False

    @pytest.mark.asyncio
    async def test_get_bot_permissions_api_error(self):
        """Test handling API errors in bot permissions retrieval"""
        from app.telegram.services.chat_info import ChatInfoService
        from aiogram.exceptions import TelegramBadRequest

        # Mock bot that raises exception
        mock_bot = AsyncMock()
        mock_bot.id = 123456

        # Mock database session
        mock_db = AsyncMock()

        mock_bot.get_chat_member.side_effect = TelegramBadRequest(method="getChatMember", message="Chat not found")

        # Create service
        service = ChatInfoService(mock_bot, mock_db)

        # Test _get_bot_permissions method
        permissions = await service._get_bot_permissions(123456789)

        assert permissions is None
