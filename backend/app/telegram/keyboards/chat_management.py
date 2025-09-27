"""
Keyboards for chat management functionality
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any
from app.models.chats import Chat
from app.models.chat_moderators import ChatModerator
from app.telegram.utils.constants import ButtonTexts


def get_chats_keyboard(chats: List[Chat]) -> InlineKeyboardMarkup:
    """
    Create keyboard with list of user's chats for selection
    """
    keyboard = []

    for chat in chats:
        # Determine chat type icon
        chat_type_icon = {
            'group': '👥',
            'supergroup': '👥',
            'channel': '📢'
        }.get(chat.chat_type, '💬')

        # Create button text with chat info
        button_text = f"{chat_type_icon} {chat.title or ButtonTexts.UNTITLED_CHAT}"
        if chat.username:
            button_text += f" (@{chat.username})"

        # Add linked channel indicator
        if chat.chat_type != 'channel' and hasattr(chat, 'linked_channel') and chat.linked_channel:
            button_text += " 🔗"

        # Create callback data with chat ID
        callback_data = f"select_chat:{chat.id}"

        keyboard.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])

    # Add back button
    keyboard.append([InlineKeyboardButton(text=ButtonTexts.BACK, callback_data="back_to_menu")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_chat_actions_keyboard(chat: Chat, linked_channel: Chat = None) -> InlineKeyboardMarkup:
    """
    Create keyboard with actions for selected chat
    """
    keyboard = []

    # Chat info header
    chat_type_icon = {
        'group': '👥',
        'supergroup': '👥',
        'channel': '📢'
    }.get(chat.chat_type, '💬')

    # Action buttons
    if chat.chat_type == 'channel':
        # For channels - show how many chats are linked
        from app.services.chats import ChatService
        # Note: We'll need to pass db session to count linked chats
        keyboard.append([InlineKeyboardButton(
            text=ButtonTexts.CHANNEL_NOTIFICATIONS,
            callback_data="channel_info"
        )])
    else:
        # For groups/supergroups - show linking options
        if linked_channel:
            keyboard.append([InlineKeyboardButton(
                text=ButtonTexts.UNLINK_CHANNEL_TEMPLATE.format(
                    channel_title=linked_channel.title or ButtonTexts.UNTITLED_CHAT
                ),
                callback_data=f"confirm_unlink_channel:{chat.id}"
            )])
        else:
            keyboard.append([InlineKeyboardButton(
                text=ButtonTexts.LINK_CHANNEL,
                callback_data=f"link_channel:{chat.id}"
            )])

    # Edit timeout settings button (only for group chats)
    if chat.chat_type in ['group', 'supergroup']:
        keyboard.append([InlineKeyboardButton(
            text=ButtonTexts.EDIT_TIMEOUT_SETTINGS,
            callback_data=f"edit_timeout_settings:{chat.id}"
        )])

        # Manage moderators button (only for group chats)
        keyboard.append([InlineKeyboardButton(
            text=ButtonTexts.MANAGE_MODERATORS,
            callback_data=f"manage_moderators:{chat.id}"
        )])

    # Back button
    keyboard.append([InlineKeyboardButton(text=ButtonTexts.BACK, callback_data="back_to_menu")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """
    Simple keyboard with cancel button
    """
    keyboard = [[InlineKeyboardButton(text=ButtonTexts.CANCEL, callback_data="cancel_action")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Main menu keyboard with management options
    """
    keyboard = [
        [InlineKeyboardButton(text=ButtonTexts.MANAGE_CHATS, callback_data="manage_chats")],
        [InlineKeyboardButton(text=ButtonTexts.HELP, callback_data="show_help")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_to_chats_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard with back to chats button
    """
    keyboard = [[InlineKeyboardButton(text=ButtonTexts.BACK_TO_CHATS, callback_data="back_to_chats_after_success")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirm_unlink_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    """
    Keyboard for confirming channel unlinking
    """
    keyboard = [
        [
            InlineKeyboardButton(text=ButtonTexts.CONFIRM_UNLINK, callback_data=f"unlink_channel:{chat_id}")
        ],
        [
            InlineKeyboardButton(text=ButtonTexts.CANCEL_UNLINK, callback_data="cancel_unlink")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_edit_timeout_options_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    """
    Keyboard for selecting message edit timeout options
    """
    keyboard = [
        [InlineKeyboardButton(text=ButtonTexts.DISABLE_EDITING, callback_data=f"set_timeout:disable:{chat_id}")],
        [InlineKeyboardButton(text=ButtonTexts.SET_TIMEOUT_MINUTES.format(minutes=1), callback_data=f"set_timeout:1:{chat_id}")],
        [InlineKeyboardButton(text=ButtonTexts.SET_TIMEOUT_MINUTES.format(minutes=5), callback_data=f"set_timeout:5:{chat_id}")],
        [InlineKeyboardButton(text=ButtonTexts.SET_TIMEOUT_MINUTES.format(minutes=10), callback_data=f"set_timeout:10:{chat_id}")],
        [InlineKeyboardButton(text=ButtonTexts.SET_TIMEOUT_MINUTES.format(minutes=15), callback_data=f"set_timeout:15:{chat_id}")],
        [InlineKeyboardButton(text=ButtonTexts.SET_TIMEOUT_MINUTES.format(minutes=20), callback_data=f"set_timeout:20:{chat_id}")],
        [InlineKeyboardButton(text=ButtonTexts.CUSTOM_TIMEOUT, callback_data=f"set_timeout:custom:{chat_id}")],
        [InlineKeyboardButton(text=ButtonTexts.BACK, callback_data=f"back_to_chat_actions:{chat_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_custom_timeout_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    """
    Keyboard for custom timeout input
    """
    keyboard = [
        [InlineKeyboardButton(text=ButtonTexts.CANCEL_CUSTOM_TIMEOUT, callback_data=f"cancel_custom_timeout:{chat_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_moderator_actions_keyboard(chat_id: int, moderators_count: int = 0) -> InlineKeyboardMarkup:
    """
    Keyboard for moderator management actions
    """
    keyboard = []

    # Show current moderators count
    keyboard.append([InlineKeyboardButton(
        text=ButtonTexts.VIEW_MODERATORS.format(count=moderators_count),
        callback_data=f"view_moderators:{chat_id}"
    )])

    # Add moderator button
    keyboard.append([InlineKeyboardButton(
        text=ButtonTexts.ADD_MODERATOR,
        callback_data=f"add_moderator:{chat_id}"
    )])

    # Remove moderator button (only if there are moderators)
    if moderators_count > 0:
        keyboard.append([InlineKeyboardButton(
            text=ButtonTexts.REMOVE_MODERATOR,
            callback_data=f"remove_moderator:{chat_id}"
        )])

    # Back button
    keyboard.append([InlineKeyboardButton(text=ButtonTexts.BACK, callback_data=f"back_to_chat_actions:{chat_id}")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_moderators_list_keyboard(chat_id: int, moderators: List) -> InlineKeyboardMarkup:
    """
    Keyboard showing list of moderators for removal
    """
    keyboard = []

    for moderator in moderators:
        # Handle both ChatModerator objects and dicts
        if isinstance(moderator, ChatModerator):
            # Format moderator name for ChatModerator object
            first_name = moderator.first_name or ''
            last_name = moderator.last_name or ''
            username = moderator.username
            moderator_user_id = moderator.moderator_user_id
            moderator_id = moderator.id
        else:
            # Handle dict format (fallback)
            first_name = moderator.get('first_name', '')
            last_name = moderator.get('last_name', '')
            username = moderator.get('username')
            moderator_user_id = moderator.get('moderator_user_id')
            moderator_id = moderator.get('id')

        # Format display name
        name_parts = [first_name, last_name]
        display_name = ' '.join(filter(None, name_parts)).strip()

        if username:
            display_name += f" (@{username})"

        if not display_name:
            display_name = f"ID: {moderator_user_id}"

        # Add button to remove this moderator
        keyboard.append([InlineKeyboardButton(
            text=f"❌ {display_name}",
            callback_data=f"confirm_remove_moderator:{chat_id}:{moderator_id}"
        )])

    # Back button
    keyboard.append([InlineKeyboardButton(text=ButtonTexts.BACK, callback_data=f"manage_moderators:{chat_id}")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirm_remove_moderator_keyboard(chat_id: int, moderator_id: int, moderator_name: str) -> InlineKeyboardMarkup:
    """
    Confirmation keyboard for removing a moderator
    """
    keyboard = [
        [InlineKeyboardButton(
            text=ButtonTexts.CONFIRM_REMOVE_MODERATOR.format(name=moderator_name),
            callback_data=f"remove_moderator_confirmed:{chat_id}:{moderator_id}"
        )],
        [InlineKeyboardButton(text=ButtonTexts.CANCEL, callback_data=f"view_moderators:{chat_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
