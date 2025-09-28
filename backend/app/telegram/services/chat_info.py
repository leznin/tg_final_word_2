"""
Service for retrieving detailed chat information from Telegram API
"""

import asyncio
from typing import List, Optional, Dict, Any, Tuple
from aiogram.types import Chat as TelegramChat, ChatMemberAdministrator, ChatMemberOwner
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter

from app.services.chats import ChatService
from app.services.users import UserService
from app.schemas.chat_info import (
    ChatInfoResponse, BotPermissions, ChatAdministrator,
    ChatInfoUpdateRequest, BulkChatInfoResponse
)


class ChatInfoService:
    """Service for retrieving detailed chat information from Telegram API"""

    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.chat_service = ChatService(db)
        self.user_service = UserService(db)

    async def get_chat_info(self, telegram_chat_id: int, user_telegram_id: int) -> Tuple[bool, str, Optional[ChatInfoResponse]]:
        """
        Get detailed information about a specific chat from Telegram API

        Returns:
            (success, error_message, chat_info)
        """
        try:
            # Verify user has access to this chat
            user = await self.user_service.get_user_by_telegram_id(user_telegram_id)
            if not user:
                return False, "Пользователь не найден в системе", None

            # Check if user owns this chat
            chat = await self.chat_service.get_chat_by_telegram_id(telegram_chat_id)
            if not chat or chat.added_by_user_id != user.id:
                return False, "У вас нет доступа к этому чату", None

            # Get chat information from Telegram API
            telegram_chat = await self.bot.get_chat(telegram_chat_id)

            # Get member count (only for groups and supergroups, not for channels)
            member_count = None
            if telegram_chat.type in ['group', 'supergroup']:
                try:
                    member_count = await self.bot.get_chat_member_count(telegram_chat_id)
                except (TelegramBadRequest, TelegramForbiddenError):
                    member_count = None
            # For channels, member_count remains None as channels don't have traditional members

            # Get bot permissions in the chat
            bot_permissions = await self._get_bot_permissions(telegram_chat_id)

            # Get administrators
            try:
                administrators = await self.bot.get_chat_administrators(telegram_chat_id)
                admin_list = []
                for admin in administrators:
                    admin_data = {
                        'user': {
                            'id': admin.user.id,
                            'is_bot': admin.user.is_bot,
                            'first_name': getattr(admin.user, 'first_name', None),
                            'last_name': getattr(admin.user, 'last_name', None),
                            'username': getattr(admin.user, 'username', None),
                            'language_code': getattr(admin.user, 'language_code', None),
                        },
                        'status': admin.status,
                        'can_be_edited': getattr(admin, 'can_be_edited', None),
                        'is_anonymous': getattr(admin, 'is_anonymous', None),
                        'can_manage_chat': getattr(admin, 'can_manage_chat', None),
                        'can_delete_messages': getattr(admin, 'can_delete_messages', None),
                        'can_manage_video_chats': getattr(admin, 'can_manage_video_chats', None),
                        'can_restrict_members': getattr(admin, 'can_restrict_members', None),
                        'can_promote_members': getattr(admin, 'can_promote_members', None),
                        'can_change_info': getattr(admin, 'can_change_info', None),
                        'can_invite_users': getattr(admin, 'can_invite_users', None),
                        'can_post_messages': getattr(admin, 'can_post_messages', None),
                        'can_edit_messages': getattr(admin, 'can_edit_messages', None),
                        'can_pin_messages': getattr(admin, 'can_pin_messages', None),
                        'can_manage_topics': getattr(admin, 'can_manage_topics', None),
                        'custom_title': getattr(admin, 'custom_title', None),
                    }
                    admin_list.append(ChatAdministrator(**admin_data))
            except (TelegramBadRequest, TelegramForbiddenError):
                admin_list = []

            # Build response
            chat_info = ChatInfoResponse(
                telegram_chat_id=telegram_chat.id,
                chat_type=telegram_chat.type,
                title=getattr(telegram_chat, 'title', None),
                username=getattr(telegram_chat, 'username', None),
                description=getattr(telegram_chat, 'description', None),
                invite_link=getattr(telegram_chat, 'invite_link', None),
                member_count=member_count,
                bot_permissions=bot_permissions,
                administrators=admin_list,
                permissions=self._extract_chat_permissions(telegram_chat),
                slow_mode_delay=getattr(telegram_chat, 'slow_mode_delay', None),
                bio=getattr(telegram_chat, 'bio', None),
                has_private_forwards=getattr(telegram_chat, 'has_private_forwards', None),
                has_protected_content=getattr(telegram_chat, 'has_protected_content', None),
                sticker_set_name=getattr(telegram_chat, 'sticker_set_name', None),
                can_set_sticker_set=getattr(telegram_chat, 'can_set_sticker_set', None),
                linked_chat_id=getattr(telegram_chat, 'linked_chat_id', None),
                location=getattr(telegram_chat, 'location', None),
                join_to_send_messages=getattr(telegram_chat, 'join_to_send_messages', None),
                join_by_request=getattr(telegram_chat, 'join_by_request', None),
                has_hidden_members=getattr(telegram_chat, 'has_hidden_members', None),
                has_aggressive_anti_spam_enabled=getattr(telegram_chat, 'has_aggressive_anti_spam_enabled', None),
                emoji_status_custom_emoji_id=getattr(telegram_chat, 'emoji_status_custom_emoji_id', None),
                emoji_status_expiration_date=getattr(telegram_chat, 'emoji_status_expiration_date', None),
                available_reactions=getattr(telegram_chat, 'available_reactions', None),
                accent_color_id=getattr(telegram_chat, 'accent_color_id', None),
                background_custom_emoji_id=getattr(telegram_chat, 'background_custom_emoji_id', None),
                profile_accent_color_id=getattr(telegram_chat, 'profile_accent_color_id', None),
                profile_background_custom_emoji_id=getattr(telegram_chat, 'profile_background_custom_emoji_id', None),
                has_visible_history=getattr(telegram_chat, 'has_visible_history', None),
                unrestrict_boost_count=getattr(telegram_chat, 'unrestrict_boost_count', None),
                custom_emoji_sticker_set_name=getattr(telegram_chat, 'custom_emoji_sticker_set_name', None),
                business_intro=getattr(telegram_chat, 'business_intro', None),
                business_location=getattr(telegram_chat, 'business_location', None),
                business_opening_hours=getattr(telegram_chat, 'business_opening_hours', None),
                personal_chat=getattr(telegram_chat, 'personal_chat', None),
                birthdate=getattr(telegram_chat, 'birthdate', None),
            )

            return True, "", chat_info

        except TelegramForbiddenError as e:
            error_msg = "Бот не имеет доступа к этому чату или был заблокирован"
            print(f"TelegramForbiddenError for chat {telegram_chat_id}: {str(e)}")
            return False, error_msg, None
        except TelegramBadRequest as e:
            error_msg = f"Ошибка запроса к Telegram API: {str(e)}"
            print(f"TelegramBadRequest for chat {telegram_chat_id}: {str(e)}")
            # Check if this is a channel-related error
            if "channel" in str(e).lower() or "member" in str(e).lower():
                error_msg += " (возможно, бот не является администратором канала)"
            return False, error_msg, None
        except TelegramRetryAfter as e:
            error_msg = f"Превышен лимит запросов. Повторите через {e.retry_after} секунд"
            print(f"TelegramRetryAfter for chat {telegram_chat_id}: {str(e)}")
            return False, error_msg, None
        except Exception as e:
            error_msg = f"Неизвестная ошибка: {str(e)}"
            print(f"Unknown error for chat {telegram_chat_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, error_msg, None

    async def get_all_chats_info(self, user_telegram_id: int) -> BulkChatInfoResponse:
        """
        Get information about all user's chats from Telegram API

        Returns BulkChatInfoResponse with results and error information
        """
        print(f"Starting get_all_chats_info for user {user_telegram_id}")

        # Get user's chats
        user = await self.user_service.get_user_by_telegram_id(user_telegram_id)
        if not user:
            print(f"User {user_telegram_id} not found")
            return BulkChatInfoResponse(
                chats_info=[],
                total_chats=0,
                successful_requests=0,
                failed_requests=0,
                errors=[{"error": "Пользователь не найден в системе"}]
            )

        chats = await self.chat_service.get_chats_by_user(user.id)
        if not chats:
            print(f"No chats found for user {user_telegram_id}")
            return BulkChatInfoResponse(
                chats_info=[],
                total_chats=0,
                successful_requests=0,
                failed_requests=0,
                errors=[{"error": "У пользователя нет чатов"}]
            )

        print(f"Processing {len(chats)} chats for user {user_telegram_id}")
        for chat in chats:
            print(f"  - Chat {chat.telegram_chat_id}: {chat.title} ({chat.chat_type})")

        # Process chats concurrently with rate limiting
        semaphore = asyncio.Semaphore(5)  # Limit concurrent requests

        async def process_chat(chat):
            async with semaphore:
                print(f"Processing chat {chat.telegram_chat_id} ({chat.chat_type})")
                success, error_msg, chat_info = await self.get_chat_info(chat.telegram_chat_id, user_telegram_id)
                if success and chat_info:
                    print(f"✅ Successfully processed chat {chat.telegram_chat_id}")
                    return {"success": True, "chat_info": chat_info, "error": None}
                else:
                    print(f"❌ Failed to process chat {chat.telegram_chat_id}: {error_msg}")
                    return {"success": False, "chat_info": None, "error": f"Chat {chat.telegram_chat_id}: {error_msg}"}

        # Process all chats
        tasks = [process_chat(chat) for chat in chats]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect results
        successful_requests = 0
        failed_requests = 0
        chats_info = []
        errors = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_requests += 1
                errors.append({"chat_id": chats[i].telegram_chat_id, "error": str(result)})
            elif result["success"] and result["chat_info"]:
                successful_requests += 1
                chats_info.append(result["chat_info"])
            else:
                failed_requests += 1
                errors.append({"chat_id": chats[i].telegram_chat_id, "error": result["error"]})

        return BulkChatInfoResponse(
            chats_info=chats_info,
            total_chats=len(chats),
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            errors=errors
        )

    async def _get_bot_permissions(self, telegram_chat_id: int) -> Optional[BotPermissions]:
        """
        Get bot permissions in the specified chat
        """
        try:
            bot_member = await self.bot.get_chat_member(telegram_chat_id, self.bot.id)

            if isinstance(bot_member, (ChatMemberAdministrator, ChatMemberOwner)):
                return BotPermissions(
                    can_send_messages=bool(getattr(bot_member, 'can_send_messages', False)),
                    can_send_audios=bool(getattr(bot_member, 'can_send_audios', False)),
                    can_send_documents=bool(getattr(bot_member, 'can_send_documents', False)),
                    can_send_photos=bool(getattr(bot_member, 'can_send_photos', False)),
                    can_send_videos=bool(getattr(bot_member, 'can_send_videos', False)),
                    can_send_video_notes=bool(getattr(bot_member, 'can_send_video_notes', False)),
                    can_send_voice_notes=bool(getattr(bot_member, 'can_send_voice_notes', False)),
                    can_send_polls=bool(getattr(bot_member, 'can_send_polls', False)),
                    can_send_other_messages=bool(getattr(bot_member, 'can_send_other_messages', False)),
                    can_add_web_page_previews=bool(getattr(bot_member, 'can_add_web_page_previews', False)),
                    can_change_info=bool(getattr(bot_member, 'can_change_info', False)),
                    can_invite_users=bool(getattr(bot_member, 'can_invite_users', False)),
                    can_pin_messages=bool(getattr(bot_member, 'can_pin_messages', False)),
                    can_manage_topics=bool(getattr(bot_member, 'can_manage_topics', False)),
                    can_delete_messages=bool(getattr(bot_member, 'can_delete_messages', False)),
                    can_manage_video_chats=bool(getattr(bot_member, 'can_manage_video_chats', False)),
                    can_restrict_members=bool(getattr(bot_member, 'can_restrict_members', False)),
                    can_promote_members=bool(getattr(bot_member, 'can_promote_members', False)),
                    can_post_messages=getattr(bot_member, 'can_post_messages', None),
                    can_edit_messages=getattr(bot_member, 'can_edit_messages', None),
                    is_anonymous=bool(getattr(bot_member, 'is_anonymous', False)),
                    custom_title=getattr(bot_member, 'custom_title', None),
                )
            else:
                # Bot is not administrator
                return BotPermissions()

        except (TelegramBadRequest, TelegramForbiddenError):
            return None

    def _extract_chat_permissions(self, telegram_chat) -> Optional[Dict[str, Any]]:
        """
        Extract chat permissions from Telegram Chat object
        """
        if hasattr(telegram_chat, 'permissions') and telegram_chat.permissions:
            permissions = telegram_chat.permissions
            return {
                'can_send_messages': getattr(permissions, 'can_send_messages', None),
                'can_send_audios': getattr(permissions, 'can_send_audios', None),
                'can_send_documents': getattr(permissions, 'can_send_documents', None),
                'can_send_photos': getattr(permissions, 'can_send_photos', None),
                'can_send_videos': getattr(permissions, 'can_send_videos', None),
                'can_send_video_notes': getattr(permissions, 'can_send_video_notes', None),
                'can_send_voice_notes': getattr(permissions, 'can_send_voice_notes', None),
                'can_send_polls': getattr(permissions, 'can_send_polls', None),
                'can_send_other_messages': getattr(permissions, 'can_send_other_messages', None),
                'can_add_web_page_previews': getattr(permissions, 'can_add_web_page_previews', None),
                'can_change_info': getattr(permissions, 'can_change_info', None),
                'can_invite_users': getattr(permissions, 'can_invite_users', None),
                'can_pin_messages': getattr(permissions, 'can_pin_messages', None),
                'can_manage_topics': getattr(permissions, 'can_manage_topics', None),
            }
        return None
