"""
Tests for chat info router functionality with bot_permissions and last_info_update
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.schemas.chat_info import BotPermissions


class TestChatInfoRouter:
    """Test chat info router updates bot_permissions and last_info_update"""

    @pytest.mark.asyncio
    async def test_get_chat_info_updates_database_fields(self, client, db_session):
        """Test that /chat-info endpoint updates bot_permissions and last_info_update in database"""
        from app.models.chats import Chat
        from app.services.chats import ChatService

        # Create test chat
        test_chat = Chat(
            telegram_chat_id=123456789,
            chat_type="supergroup",
            title="Test Chat",
            added_by_user_id=1,
            ai_content_check_enabled=False
        )
        db_session.add(test_chat)
        await db_session.commit()
        await db_session.refresh(test_chat)

        # Mock the ChatInfoService to return test data
        mock_permissions = BotPermissions(
            can_send_messages=True,
            can_delete_messages=True,
            can_restrict_members=True,
            can_promote_members=False
        )

        mock_chat_info = MagicMock()
        mock_chat_info.member_count = 42
        mock_chat_info.description = "Test description"
        mock_chat_info.invite_link = "https://t.me/test"
        mock_chat_info.bot_permissions = mock_permissions

        with patch('app.routers.chat_info.ChatInfoService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_chat_info.return_value = (mock_chat_info, None)
            mock_service_class.return_value = mock_service

            # Make request to chat-info endpoint
            response = client.post("/chat-info", json={"telegram_chat_id": 123456789})

            assert response.status_code == 200

            # Check that database was updated
            chat_service = ChatService(db_session)
            updated_chat = await chat_service.get_chat_by_telegram_id(123456789)

            assert updated_chat is not None
            assert updated_chat.member_count == 42
            assert updated_chat.description == "Test description"
            assert updated_chat.invite_link == "https://t.me/test"
            assert updated_chat.bot_permissions is not None
            assert updated_chat.bot_permissions["can_send_messages"] is True
            assert updated_chat.bot_permissions["can_delete_messages"] is True
            assert updated_chat.bot_permissions["can_restrict_members"] is True
            assert updated_chat.bot_permissions["can_promote_members"] is False
            assert updated_chat.last_info_update is not None
            assert isinstance(updated_chat.last_info_update, datetime)

    @pytest.mark.asyncio
    async def test_get_chat_info_bulk_updates_multiple_chats(self, client, db_session):
        """Test that bulk chat info update works for multiple chats"""
        from app.models.chats import Chat

        # Create multiple test chats
        chats = []
        for i in range(3):
            chat = Chat(
                telegram_chat_id=100000000 + i,
                chat_type="supergroup",
                title=f"Test Chat {i}",
                added_by_user_id=1,
                ai_content_check_enabled=False
            )
            chats.append(chat)

        db_session.add_all(chats)
        await db_session.commit()

        # Mock successful responses for all chats
        mock_permissions = BotPermissions(can_send_messages=True, can_delete_messages=False)

        with patch('app.routers.chat_info.ChatInfoService') as mock_service_class:
            mock_service = AsyncMock()

            # Mock get_all_chats_info to return success for all chats
            mock_result = MagicMock()
            mock_result.successful_requests = 3
            mock_result.total_chats = 3
            mock_result.failed_requests = 0
            mock_result.errors = []
            mock_result.chats_info = []

            mock_service.get_all_chats_info.return_value = mock_result
            mock_service_class.return_value = mock_service

            # Make request to bulk update endpoint
            response = client.post("/chat-info/bulk")

            assert response.status_code == 200
            data = response.json()
            assert data["successful_requests"] == 3
            assert data["total_chats"] == 3
            assert data["failed_requests"] == 0

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

    @pytest.mark.asyncio
    async def test_chat_info_handles_service_errors(self, client):
        """Test that router handles service errors gracefully"""
        with patch('app.routers.chat_info.ChatInfoService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_chat_info.return_value = (None, "Chat not found")
            mock_service_class.return_value = mock_service

            response = client.post("/chat-info", json={"telegram_chat_id": 999999999})

            assert response.status_code == 400
            data = response.json()
            assert "error" in data
            assert data["error"] == "Chat not found"

    @pytest.mark.asyncio
    async def test_last_info_update_timestamp_accuracy(self, client, db_session):
        """Test that last_info_update is set to current time accurately"""
        from app.models.chats import Chat
        from app.services.chats import ChatService

        # Create test chat
        test_chat = Chat(
            telegram_chat_id=987654321,
            chat_type="group",
            title="Timestamp Test Chat",
            added_by_user_id=1,
            ai_content_check_enabled=False
        )
        db_session.add(test_chat)
        await db_session.commit()

        # Record time before request
        time_before = datetime.now(timezone.utc)

        # Mock successful chat info response
        mock_permissions = BotPermissions(can_send_messages=True)
        mock_chat_info = MagicMock()
        mock_chat_info.bot_permissions = mock_permissions

        with patch('app.routers.chat_info.ChatInfoService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_chat_info.return_value = (mock_chat_info, None)
            mock_service_class.return_value = mock_service

            # Make request
            response = client.post("/chat-info", json={"telegram_chat_id": 987654321})
            assert response.status_code == 200

            # Record time after request
            time_after = datetime.now(timezone.utc)

            # Check database update
            chat_service = ChatService(db_session)
            updated_chat = await chat_service.get_chat_by_telegram_id(987654321)

            assert updated_chat.last_info_update is not None
            # Timestamp should be between before and after times
            assert time_before <= updated_chat.last_info_update <= time_after
