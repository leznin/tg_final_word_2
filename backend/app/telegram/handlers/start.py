"""
Start command handler for Telegram bot
"""

from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.telegram.utils.constants import START_MESSAGE
from app.telegram.keyboards.chat_management import get_main_menu_keyboard
from app.services.users import UserService
from app.services.chats import ChatService
from app.schemas.users import TelegramUserData
from app.schemas.chats import TelegramChatData
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner

# Create router for start handler
start_router = Router()


# Create router for member status handler
member_router = Router()


def extract_bot_permissions(chat_member) -> dict:
    """
    Extract bot permissions from ChatMemberAdministrator or ChatMemberOwner object
    """
    if isinstance(chat_member, (ChatMemberAdministrator, ChatMemberOwner)):
        return {
            'can_send_messages': bool(getattr(chat_member, 'can_send_messages', False)),
            'can_send_audios': bool(getattr(chat_member, 'can_send_audios', False)),
            'can_send_documents': bool(getattr(chat_member, 'can_send_documents', False)),
            'can_send_photos': bool(getattr(chat_member, 'can_send_photos', False)),
            'can_send_videos': bool(getattr(chat_member, 'can_send_videos', False)),
            'can_send_video_notes': bool(getattr(chat_member, 'can_send_video_notes', False)),
            'can_send_voice_notes': bool(getattr(chat_member, 'can_send_voice_notes', False)),
            'can_send_polls': bool(getattr(chat_member, 'can_send_polls', False)),
            'can_send_other_messages': bool(getattr(chat_member, 'can_send_other_messages', False)),
            'can_add_web_page_previews': bool(getattr(chat_member, 'can_add_web_page_previews', False)),
            'can_change_info': bool(getattr(chat_member, 'can_change_info', False)),
            'can_invite_users': bool(getattr(chat_member, 'can_invite_users', False)),
            'can_pin_messages': bool(getattr(chat_member, 'can_pin_messages', False)),
            'can_manage_topics': bool(getattr(chat_member, 'can_manage_topics', False)),
            'can_delete_messages': bool(getattr(chat_member, 'can_delete_messages', False)),
            'can_manage_video_chats': bool(getattr(chat_member, 'can_manage_video_chats', False)),
            'can_restrict_members': bool(getattr(chat_member, 'can_restrict_members', False)),
            'can_promote_members': bool(getattr(chat_member, 'can_promote_members', False)),
            'can_post_messages': getattr(chat_member, 'can_post_messages', None),
            'can_edit_messages': getattr(chat_member, 'can_edit_messages', None),
            'is_anonymous': bool(getattr(chat_member, 'is_anonymous', False)),
            'custom_title': getattr(chat_member, 'custom_title', None),
        }
    return {}


@member_router.my_chat_member()
async def handle_my_chat_member(update: types.ChatMemberUpdated, db: AsyncSession) -> None:
    """
    Handle bot member status changes (blocking/unblocking and chat management)
    """
    old_status = update.old_chat_member.status
    new_status = update.new_chat_member.status

    user_service = UserService(db)
    chat_service = ChatService(db)

    # Handle user blocking/unblocking in private chats
    if update.chat.type == 'private':
        # If user blocked the bot
        if old_status in ['member', 'administrator', 'creator'] and new_status in ['left', 'kicked', 'restricted']:
            await user_service.block_user(update.from_user.id)

        # If user unblocked the bot (optional - can restore messaging ability)
        elif old_status in ['left', 'kicked', 'restricted'] and new_status in ['member', 'administrator', 'creator']:
            # User unblocked the bot, but we'll handle this in /start command
            pass

    # Handle bot being added to/removed from group chats and channels
    elif update.chat.type in ['group', 'supergroup', 'channel']:
        # Bot was added as admin or creator to a chat
        if (old_status in ['left', 'kicked', 'restricted', 'member'] and
            new_status in ['administrator', 'creator'] and
            update.from_user):

            # Save user who added the bot (if not exists)
            user = await user_service.create_or_update_telegram_user(
                TelegramUserData(
                    id=update.from_user.id,
                    is_bot=update.from_user.is_bot,
                    first_name=update.from_user.first_name,
                    last_name=update.from_user.last_name,
                    username=update.from_user.username,
                    language_code=getattr(update.from_user, 'language_code', None),
                    is_premium=getattr(update.from_user, 'is_premium', None),
                    added_to_attachment_menu=getattr(update.from_user, 'added_to_attachment_menu', None),
                    can_join_groups=getattr(update.from_user, 'can_join_groups', None),
                    can_read_all_group_messages=getattr(update.from_user, 'can_read_all_group_messages', None),
                    supports_inline_queries=getattr(update.from_user, 'supports_inline_queries', None)
                )
            )

            # Save chat information
            chat_data = TelegramChatData(
                id=update.chat.id,
                type=update.chat.type,
                title=getattr(update.chat, 'title', None),
                username=getattr(update.chat, 'username', None)
            )

            chat = await chat_service.create_or_update_chat_from_telegram(chat_data, user.id)

            # Save bot permissions
            bot_permissions = extract_bot_permissions(update.new_chat_member)
            if bot_permissions:
                await chat_service.update_bot_permissions(update.chat.id, bot_permissions)

        # Bot permissions were changed (bot remains admin/creator)
        elif (old_status in ['administrator', 'creator'] and
              new_status in ['administrator', 'creator']):
            # Extract and update bot permissions
            bot_permissions = extract_bot_permissions(update.new_chat_member)
            if bot_permissions:
                await chat_service.update_bot_permissions(update.chat.id, bot_permissions)

        # Bot was removed from chat
        elif (old_status in ['administrator', 'creator', 'member'] and
              new_status in ['left', 'kicked', 'restricted']):
            # Deactivate chat when bot is removed
            await chat_service.deactivate_chat(update.chat.id)


@start_router.message(Command("start"))
async def handle_start_command(message: types.Message, db: AsyncSession) -> None:
    """
    Handle /start command

    Saves user data to database and sends welcome message with chat setup instructions
    """
    # Extract user data from Telegram message
    if message.from_user:
        user_data = TelegramUserData(
            id=message.from_user.id,
            is_bot=message.from_user.is_bot,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
            language_code=message.from_user.language_code,
            is_premium=getattr(message.from_user, 'is_premium', None),
            added_to_attachment_menu=getattr(message.from_user, 'added_to_attachment_menu', None),
            can_join_groups=getattr(message.from_user, 'can_join_groups', None),
            can_read_all_group_messages=getattr(message.from_user, 'can_read_all_group_messages', None),
            supports_inline_queries=getattr(message.from_user, 'supports_inline_queries', None)
        )

        # Save or update user data in database
        user_service = UserService(db)
        await user_service.create_or_update_telegram_user(user_data)

    # Send welcome message with main menu keyboard
    keyboard = get_main_menu_keyboard()
    await message.reply(
        text=START_MESSAGE,
        parse_mode="HTML",
        reply_markup=keyboard
    )

