"""
Chat management handler for Telegram bot - linking channels to chats
"""

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.telegram.services.chat_linking import ChatLinkingService
from app.telegram.services.moderator_management import ModeratorManagementService
from app.telegram.states import ChatManagementStates
from app.telegram.keyboards.chat_management import (
    get_chats_keyboard,
    get_chat_actions_keyboard,
    get_cancel_keyboard,
    get_back_to_chats_keyboard,
    get_main_menu_keyboard,
    get_confirm_unlink_keyboard,
    get_edit_timeout_options_keyboard,
    get_custom_timeout_keyboard,
    get_moderator_actions_keyboard,
    get_moderators_list_keyboard,
    get_confirm_remove_moderator_keyboard,
    get_ai_content_check_options_keyboard
)
from app.telegram.utils.constants import (
    StartMessages, ChatManagementMessages, ChannelLinkingMessages,
    HelpMessages, ErrorMessages, ButtonTexts, MessageEditingMessages, ModeratorMessages, PaymentMessages
)

# Create router for chat management
chat_management_router = Router()


async def format_subscription_info(chat_id: int, db: AsyncSession) -> str:
    """
    Helper function to format subscription information for display
    Returns empty string if no active subscription
    """
    from app.services.chat_subscriptions import ChatSubscriptionsService
    subscriptions_service = ChatSubscriptionsService(db)
    active_subscription = await subscriptions_service.get_active_subscription_for_chat(chat_id)

    if active_subscription:
        end_date = active_subscription.end_date.strftime("%d.%m.%Y %H:%M")
        subscription_type_text = "месяц" if active_subscription.subscription_type == "month" else "год"
        return f"\n\n💳 <b>Подписка:</b> AI проверка ({subscription_type_text})\n📅 <b>Действительна до:</b> {end_date}"

    return ""


# Removed /chats command handler - now using buttons only

@chat_management_router.callback_query(F.data == "manage_chats")
async def handle_manage_chats(callback: types.CallbackQuery, db: AsyncSession, state: FSMContext) -> None:
    """
    Handle manage chats button from main menu
    """
    linking_service = ChatLinkingService(db)

    # Get user's chats
    chats = await linking_service.get_user_chats_for_management(callback.from_user.id)

    if not chats:
        keyboard = get_main_menu_keyboard()
        await callback.message.edit_text(
            ChatManagementMessages.NO_CHATS,
            reply_markup=keyboard
        )
        return

    # Show chats keyboard
    keyboard = get_chats_keyboard(chats)
    await callback.message.edit_text(
        ChatManagementMessages.CHAT_SELECTION,
        reply_markup=keyboard
    )

    # Set FSM state
    await state.set_state(ChatManagementStates.selecting_chat)


@chat_management_router.callback_query(F.data == "show_help")
async def handle_show_help(callback: types.CallbackQuery) -> None:
    """
    Handle help button from main menu
    """
    keyboard = get_main_menu_keyboard()
    await callback.message.edit_text(
        StartMessages.WELCOME,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@chat_management_router.callback_query(ChatManagementStates.selecting_chat, F.data.startswith("select_chat:"))
async def handle_chat_selection(
    callback: types.CallbackQuery,
    state: FSMContext,
    db: AsyncSession
) -> None:
    """
    Handle chat selection from keyboard - immediately start channel linking process
    """
    # Extract chat ID from callback data
    chat_id = int(callback.data.split(":")[1])

    linking_service = ChatLinkingService(db)

    # Get chat details
    chat = await linking_service.chat_service.get_chat(chat_id)
    if not chat:
        await callback.message.edit_text(
            "ChatManagementMessages.CHAT_NOT_FOUND"
        )
        await state.clear()
        return

    # Check if chat already has a linked channel
    linked_channel = await linking_service.chat_service.get_linked_channel(chat.id)
    if linked_channel:
        # If already linked, show info and option to unlink or continue
        keyboard = get_chat_actions_keyboard(chat, linked_channel)

        response_text = ChatManagementMessages.SELECTED_CHAT_TEMPLATE.format(
            chat_title=chat.title or ButtonTexts.UNTITLED_CHAT,
            channel_title=linked_channel.title or ButtonTexts.UNTITLED_CHAT
        )
        if linked_channel.username:
            response_text += f" (@{linked_channel.username})"

        # Add subscription information if active
        response_text += await format_subscription_info(chat.id, db)

        response_text += ChatManagementMessages.SELECT_ACTION

        await callback.message.edit_text(
            response_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await state.update_data(selected_chat_id=chat.id)
        return

    # If not linked, immediately start channel linking process
    await callback.message.edit_text(
        ChannelLinkingMessages.CHANNEL_LINKING,
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )

    # Store selected chat ID and switch to waiting state
    await state.update_data(selected_chat_id=chat.id)
    await state.set_state(ChatManagementStates.waiting_for_channel_forward)


# Removed - channel linking now happens directly in handle_chat_selection

@chat_management_router.callback_query(F.data.startswith("confirm_unlink_channel:"))
async def handle_confirm_unlink_channel(
    callback: types.CallbackQuery,
    db: AsyncSession,
    state: FSMContext
) -> None:
    """
    Handle confirmation request for unlinking channel from chat
    """
    # Extract chat ID from callback data
    chat_id = int(callback.data.split(":")[1])

    linking_service = ChatLinkingService(db)

    # Get chat details
    chat = await linking_service.chat_service.get_chat(chat_id)
    if not chat:
        await callback.message.edit_text(
            "ChatManagementMessages.CHAT_NOT_FOUND"
        )
        await state.clear()
        return

    # Get linked channel info
    linked_channel = await linking_service.chat_service.get_linked_channel(chat.id)
    if not linked_channel:
        await callback.message.edit_text(
            ErrorMessages.CHANNEL_ALREADY_UNLINKED,
            reply_markup=get_back_to_chats_keyboard()
        )
        return

    # Show confirmation dialog
    confirm_text = HelpMessages.UNLINK_CONFIRMATION_TEMPLATE.format(
        chat_title=chat.title or ButtonTexts.UNTITLED_CHAT,
        channel_title=linked_channel.title or ButtonTexts.UNTITLED_CHAT
    )
    if linked_channel.username:
        confirm_text += f" (@{linked_channel.username})"

    keyboard = get_confirm_unlink_keyboard(chat.id)
    await callback.message.edit_text(
        confirm_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

    # Set state for confirmation
    await state.set_state(ChatManagementStates.confirming_unlink)
    await state.update_data(selected_chat_id=chat.id)


@chat_management_router.callback_query(ChatManagementStates.confirming_unlink, F.data.startswith("unlink_channel:"))
async def handle_unlink_channel(
    callback: types.CallbackQuery,
    db: AsyncSession,
    state: FSMContext
) -> None:
    """
    Handle unlinking channel from chat after confirmation
    """
    # Extract chat ID from callback data
    chat_id = int(callback.data.split(":")[1])

    linking_service = ChatLinkingService(db)

    # Try to unlink
    success, message = await linking_service.unlink_channel_from_chat(
        chat_id, callback.from_user.id
    )

    if success:
        await callback.message.edit_text(
            message,
            reply_markup=get_back_to_chats_keyboard()
        )
    else:
        await callback.message.edit_text(f"❌ Ошибка: {message}")

    # Clear state after operation
    await state.clear()


@chat_management_router.callback_query(ChatManagementStates.confirming_unlink, F.data == "cancel_unlink")
async def handle_cancel_unlink(
    callback: types.CallbackQuery,
    db: AsyncSession,
    state: FSMContext
) -> None:
    """
    Handle cancellation of channel unlinking
    """
    # Get state data to return to chat actions
    state_data = await state.get_data()
    chat_id = state_data.get('selected_chat_id')

    if chat_id:
        linking_service = ChatLinkingService(db)

        # Get chat and linked channel info to show actions again
        chat = await linking_service.chat_service.get_chat(chat_id)
        linked_channel = await linking_service.chat_service.get_linked_channel(chat_id)

        if chat and linked_channel:
            keyboard = get_chat_actions_keyboard(chat, linked_channel)
            response_text = f"👥 <b>{chat.title or ButtonTexts.UNTITLED_CHAT}</b>\n\n"
            response_text += f"🔗 Уже связан с каналом: <b>{linked_channel.title or ButtonTexts.UNTITLED_CHAT}</b>"
            if linked_channel.username:
                response_text += f" (@{linked_channel.username})"

            # Add subscription information if active
            response_text += await format_subscription_info(chat.id, db)

            response_text += "\n\n" + ChatManagementMessages.SELECT_ACTION

            await callback.message.edit_text(
                response_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            # If something went wrong, go back to chats
            await callback.message.edit_text(
                ChatManagementMessages.OPERATION_CANCELLED,
                reply_markup=get_back_to_chats_keyboard()
            )
    else:
        # If no chat ID, go back to menu
        keyboard = get_main_menu_keyboard()
        await callback.message.edit_text(
            StartMessages.WELCOME,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    # Clear state
    await state.clear()


@chat_management_router.callback_query(F.data == "back_to_menu")
async def handle_back_to_menu(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """
    Handle back to main menu from chat selection
    """
    # Answer the callback first
    await callback.answer()

    await state.clear()
    keyboard = get_main_menu_keyboard()
    try:
        await callback.message.edit_text(
            StartMessages.WELCOME,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception as e:
        # If edit fails, send a new message
        await callback.message.answer(
            StartMessages.WELCOME,
            parse_mode="HTML",
            reply_markup=keyboard
        )


@chat_management_router.callback_query(F.data.in_(["cancel_chat_selection", "cancel_action"]))
async def handle_cancel(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """
    Handle cancellation of chat management
    """
    await callback.answer()
    await state.clear()
    keyboard = get_main_menu_keyboard()
    await callback.message.edit_text(
        StartMessages.WELCOME,
        parse_mode="HTML",
        reply_markup=keyboard
    )


@chat_management_router.callback_query(F.data == "channel_info")
async def handle_channel_info(
    callback: types.CallbackQuery
) -> None:
    """
    Handle channel info display
    """
    await callback.message.edit_text(
        HelpMessages.CHANNEL_INFO,
        parse_mode="HTML"
    )


@chat_management_router.callback_query(F.data == "back_to_chats_after_success")
async def handle_back_to_chats_after_success(
    callback: types.CallbackQuery,
    db: AsyncSession,
    state: FSMContext
) -> None:
    """
    Handle back to chats after successful channel linking
    """
    linking_service = ChatLinkingService(db)

    # Get user's chats
    chats = await linking_service.get_user_chats_for_management(callback.from_user.id)

    if not chats:
        keyboard = get_main_menu_keyboard()
        await callback.message.edit_text(
            ChatManagementMessages.NO_CHATS_SHORT,
            reply_markup=keyboard
        )
        await state.clear()
        return

    # Show chats keyboard
    keyboard = get_chats_keyboard(chats)
    await callback.message.edit_text(
        ChatManagementMessages.CHAT_SELECTION,
        reply_markup=keyboard
    )

    # Set FSM state
    await state.set_state(ChatManagementStates.selecting_chat)


@chat_management_router.callback_query(F.data.startswith("edit_timeout_settings:"))
async def handle_edit_timeout_settings(
    callback: types.CallbackQuery,
    db: AsyncSession,
    state: FSMContext
) -> None:
    """
    Handle edit timeout settings button - show timeout options
    """
    # Extract chat ID from callback data
    chat_id = int(callback.data.split(":")[1])

    linking_service = ChatLinkingService(db)

    # Get chat details
    chat = await linking_service.chat_service.get_chat(chat_id)
    if not chat:
        await callback.message.edit_text(
            "ChatManagementMessages.CHAT_NOT_FOUND"
        )
        await state.clear()
        return

    # Show current setting in the message
    current_setting = HelpMessages.TIMEOUT_DISABLED if chat.message_edit_timeout_minutes is None else f"{chat.message_edit_timeout_minutes} минут"

    response_text = HelpMessages.EDIT_TIMEOUT_SETTINGS_TEMPLATE.format(
        chat_title=chat.title or ButtonTexts.UNTITLED_CHAT,
        current_setting=current_setting
    )

    keyboard = get_edit_timeout_options_keyboard(chat.id)
    await callback.message.edit_text(
        response_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

    # Set state for timeout selection
    await state.set_state(ChatManagementStates.setting_edit_timeout)
    await state.update_data(selected_chat_id=chat.id)


@chat_management_router.callback_query(ChatManagementStates.setting_edit_timeout, F.data.startswith("set_timeout:"))
async def handle_timeout_option_selection(
    callback: types.CallbackQuery,
    db: AsyncSession,
    state: FSMContext
) -> None:
    """
    Handle timeout option selection
    """
    # Extract option and chat ID from callback data
    parts = callback.data.split(":")
    option = parts[1]
    chat_id = int(parts[2])

    linking_service = ChatLinkingService(db)

    # Get chat details
    chat = await linking_service.chat_service.get_chat(chat_id)
    if not chat:
        await callback.message.edit_text(
            "ChatManagementMessages.CHAT_NOT_FOUND"
        )
        await state.clear()
        return

    if option == "disable":
        # Disable editing
        timeout_minutes = None
        success_message = HelpMessages.EDITING_DISABLED_SUCCESS

    elif option == "custom":
        # Custom timeout - ask for input
        await callback.message.edit_text(
            HelpMessages.CUSTOM_TIMEOUT_INPUT,
            reply_markup=get_custom_timeout_keyboard(chat.id),
            parse_mode="HTML"
        )
        await state.set_state(ChatManagementStates.waiting_for_custom_timeout)
        return

    else:
        # Preset timeout
        try:
            timeout_minutes = int(option)
            success_message = HelpMessages.TIMEOUT_SET_SUCCESS_TEMPLATE.format(minutes=timeout_minutes)
        except ValueError:
            await callback.message.edit_text(ErrorMessages.INVALID_TIMEOUT_VALUE)
            return

    # Update chat settings
    from app.schemas.chats import ChatUpdate
    update_data = ChatUpdate(message_edit_timeout_minutes=timeout_minutes)
    updated_chat = await linking_service.chat_service.update_chat(chat_id, update_data)

    if updated_chat:
        # Return to chat actions
        linked_channel = await linking_service.chat_service.get_linked_channel(chat.id)
        keyboard = get_chat_actions_keyboard(chat, linked_channel)
        response_text = f"👥 <b>{chat.title or 'ButtonTexts.UNTITLED_CHAT'}</b>\n\n"
        response_text += f"🔗 Уже связан с каналом: <b>{linked_channel.title or ButtonTexts.UNTITLED_CHAT}</b>" if linked_channel else ChatManagementMessages.SELECTED_CHAT_NO_CHANNEL
        if linked_channel and linked_channel.username:
            response_text += f" (@{linked_channel.username})"

        # Add subscription information if active
        if linked_channel:  # Only check subscription if there's a linked channel
            response_text += await format_subscription_info(chat.id, db)

        response_text += f"\n\n{success_message}\n\n" + ChatManagementMessages.SELECT_ACTION

        await callback.message.edit_text(
            response_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(ChatManagementMessages.SETTINGS_SAVED_ERROR)

    await state.clear()


@chat_management_router.callback_query(ChatManagementStates.setting_edit_timeout, F.data.startswith("back_to_chat_actions:"))
async def handle_back_to_chat_actions(
    callback: types.CallbackQuery,
    db: AsyncSession,
    state: FSMContext
) -> None:
    """
    Handle back to chat actions from timeout settings
    """
    chat_id = int(callback.data.split(":")[1])

    linking_service = ChatLinkingService(db)

    # Get chat and linked channel info to show actions again
    chat = await linking_service.chat_service.get_chat(chat_id)
    linked_channel = await linking_service.chat_service.get_linked_channel(chat_id)

    if chat:
        keyboard = get_chat_actions_keyboard(chat, linked_channel)
        response_text = f"👥 <b>{chat.title or 'ButtonTexts.UNTITLED_CHAT'}</b>\n\n"
        response_text += f"🔗 Уже связан с каналом: <b>{linked_channel.title or ButtonTexts.UNTITLED_CHAT}</b>" if linked_channel else ChatManagementMessages.SELECTED_CHAT_NO_CHANNEL
        if linked_channel and linked_channel.username:
            response_text += f" (@{linked_channel.username})"

        # Add subscription information if active
        if linked_channel:  # Only check subscription if there's a linked channel
            response_text += await format_subscription_info(chat.id, db)

        response_text += "\n\n" + ChatManagementMessages.SELECT_ACTION

        await callback.message.edit_text(
            response_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            "❌ Чат не найден.",
            reply_markup=get_back_to_chats_keyboard()
        )

    await state.clear()


@chat_management_router.message(ChatManagementStates.waiting_for_custom_timeout)
async def handle_custom_timeout_input(
    message: types.Message,
    state: FSMContext,
    db: AsyncSession
) -> None:
    """
    Handle custom timeout input
    """
    state_data = await state.get_data()
    chat_id = state_data.get('selected_chat_id')

    if not chat_id:
        await message.reply(ErrorMessages.CHAT_NOT_SELECTED)
        await state.clear()
        return

    try:
        timeout_minutes = int(message.text.strip())

        # Validate timeout (1-1440 minutes = 24 hours)
        if timeout_minutes < 1:
            await message.reply(
                ErrorMessages.TIMEOUT_TOO_SMALL,
                reply_markup=get_custom_timeout_keyboard(chat_id)
            )
            return

        if timeout_minutes > 1440:
            await message.reply(
                ErrorMessages.TIMEOUT_TOO_LARGE,
                reply_markup=get_custom_timeout_keyboard(chat_id)
            )
            return

    except ValueError:
        await message.reply(
            ErrorMessages.NOT_A_NUMBER,
            reply_markup=get_custom_timeout_keyboard(chat_id)
        )
        return

    # Update chat settings
    from app.telegram.services.chat_linking import ChatLinkingService
    from app.schemas.chats import ChatUpdate

    linking_service = ChatLinkingService(db)
    update_data = ChatUpdate(message_edit_timeout_minutes=timeout_minutes)
    updated_chat = await linking_service.chat_service.update_chat(chat_id, update_data)

    if updated_chat:
        # Get chat info for response
        chat = await linking_service.chat_service.get_chat(chat_id)
        linked_channel = await linking_service.chat_service.get_linked_channel(chat_id)

        success_message = HelpMessages.TIMEOUT_SET_SUCCESS_TEMPLATE.format(minutes=timeout_minutes)

        if chat:
            keyboard = get_chat_actions_keyboard(chat, linked_channel)
            response_text = ChatManagementMessages.SELECTED_CHAT_TEMPLATE.format(
                chat_title=chat.title or ButtonTexts.UNTITLED_CHAT,
                channel_title=linked_channel.title or ButtonTexts.UNTITLED_CHAT
            ) if linked_channel else ChatManagementMessages.SELECTED_CHAT_NO_CHANNEL.format(
                chat_title=chat.title or ButtonTexts.UNTITLED_CHAT
            )
            if linked_channel and linked_channel.username:
                response_text += f" (@{linked_channel.username})"

            # Add subscription information if active
            if linked_channel:  # Only check subscription if there's a linked channel
                response_text += await format_subscription_info(chat.id, db)

            response_text += f"\n\n{success_message}" + ChatManagementMessages.SELECT_ACTION

            await message.reply(
                response_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            await message.reply(success_message)
    else:
        await message.reply(ChatManagementMessages.SETTINGS_SAVED_ERROR)

    await state.clear()


@chat_management_router.callback_query(F.data.startswith("cancel_custom_timeout:"))
async def handle_cancel_custom_timeout(
    callback: types.CallbackQuery,
    db: AsyncSession,
    state: FSMContext
) -> None:
    """
    Handle cancellation of custom timeout input
    """
    chat_id = int(callback.data.split(":")[1])

    linking_service = ChatLinkingService(db)

    # Get chat and return to timeout settings
    chat = await linking_service.chat_service.get_chat(chat_id)
    if chat:
        current_setting = HelpMessages.TIMEOUT_DISABLED if chat.message_edit_timeout_minutes is None else f"{chat.message_edit_timeout_minutes} минут"

        response_text = HelpMessages.EDIT_TIMEOUT_SETTINGS_TEMPLATE.format(
            chat_title=chat.title or ButtonTexts.UNTITLED_CHAT,
            current_setting=current_setting
        )

        keyboard = get_edit_timeout_options_keyboard(chat.id)
        await callback.message.edit_text(
            response_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

        await state.set_state(ChatManagementStates.setting_edit_timeout)
        await state.update_data(selected_chat_id=chat.id)
    else:
        await callback.message.edit_text(
            "❌ Чат не найден.",
            reply_markup=get_back_to_chats_keyboard()
        )
        await state.clear()


@chat_management_router.callback_query(F.data.startswith("manage_moderators:"))
async def handle_manage_moderators(
    callback: types.CallbackQuery,
    db: AsyncSession,
    state: FSMContext
) -> None:
    """
    Handle manage moderators button - show moderator actions
    """
    try:
        # Extract chat ID from callback data
        chat_id = int(callback.data.split(":")[1])

        moderator_service = ModeratorManagementService(db)

        # Get moderators count for this chat
        moderators, error_msg = await moderator_service.get_chat_moderators_for_display(
            chat_id, int(callback.from_user.id)
        )

        if error_msg:
            await callback.answer()
            await callback.message.edit_text(
                f"❌ Ошибка: {error_msg}",
                reply_markup=get_back_to_chats_keyboard()
            )
            return

        moderators_count = len(moderators)

        # Show moderator actions keyboard
        keyboard = get_moderator_actions_keyboard(chat_id, moderators_count)
        await callback.answer()
        await callback.message.edit_text(
            ModeratorMessages.MODERATOR_MANAGEMENT,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

        # Update state data (keep existing state)
        await state.update_data(selected_chat_id=chat_id)
    except Exception as e:
        await callback.answer()
        await callback.message.edit_text(
            f"❌ Произошла ошибка: {str(e)}",
            reply_markup=get_back_to_chats_keyboard()
        )


@chat_management_router.callback_query(F.data.startswith("add_moderator:"))
async def handle_add_moderator(
    callback: types.CallbackQuery,
    db: AsyncSession,
    state: FSMContext
) -> None:
    """
    Handle add moderator button - start forwarded message waiting
    """
    try:
        # Extract chat ID from callback data
        chat_id = int(callback.data.split(":")[1])

        await callback.answer()
        await callback.message.edit_text(
            ModeratorMessages.ADD_MODERATOR_INSTRUCTIONS,
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )

        # Store selected chat ID and switch to waiting state
        await state.update_data(selected_chat_id=chat_id)
        await state.set_state(ChatManagementStates.waiting_for_moderator_forward)
    except Exception as e:
        await callback.answer()
        await callback.message.edit_text(
            f"❌ Произошла ошибка: {str(e)}",
            reply_markup=get_back_to_chats_keyboard()
        )


@chat_management_router.callback_query(F.data.startswith("view_moderators:"))
async def handle_view_moderators(
    callback: types.CallbackQuery,
    db: AsyncSession,
    state: FSMContext
) -> None:
    """
    Handle view moderators button - show list of moderators
    """
    try:
        # Extract chat ID from callback data
        chat_id = int(callback.data.split(":")[1])

        moderator_service = ModeratorManagementService(db)

        # Get moderators for this chat
        moderators, error_msg = await moderator_service.get_chat_moderators_for_display(
            chat_id, int(callback.from_user.id)
        )

        if error_msg:
            await callback.answer()
            await callback.message.edit_text(
                f"❌ Ошибка: {error_msg}",
                reply_markup=get_back_to_chats_keyboard()
            )
            return

        if not moderators:
            await callback.answer()
            await callback.message.edit_text(
                ModeratorMessages.NO_MODERATORS,
                reply_markup=get_moderator_actions_keyboard(chat_id, 0)
            )
            return

        # Format moderators list
        moderators_list = ""
        for i, moderator in enumerate(moderators, 1):
            name = moderator_service._format_moderator_name(moderator)
            moderators_list += f"{i}. {name}\n"

        response_text = ModeratorMessages.MODERATORS_LIST_TEMPLATE.format(
            count=len(moderators),
            moderators_list=moderators_list.strip()
        )

        # Show moderators list keyboard for removal
        keyboard = get_moderators_list_keyboard(chat_id, moderators)
        await callback.answer()
        await callback.message.edit_text(
            response_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.answer()
        await callback.message.edit_text(
            f"❌ Произошла ошибка: {str(e)}",
            reply_markup=get_back_to_chats_keyboard()
        )




@chat_management_router.callback_query(F.data.startswith("confirm_remove_moderator:"))
async def handle_confirm_remove_moderator(
    callback: types.CallbackQuery,
    db: AsyncSession,
    state: FSMContext
) -> None:
    """
    Handle confirmation request for removing a moderator
    """
    try:
        # Extract chat ID and moderator ID from callback data
        parts = callback.data.split(":")
        chat_id = int(parts[1])
        moderator_id = int(parts[2])

        moderator_service = ModeratorManagementService(db)

        # Get moderator info
        moderator = await moderator_service.moderator_service.get_moderator(moderator_id)
        if not moderator:
            await callback.answer()
            await callback.message.edit_text(
                "❌ Модератор не найден.",
                reply_markup=get_back_to_chats_keyboard()
            )
            return

        moderator_name = moderator_service._format_moderator_name(moderator)

        # Show confirmation dialog
        confirm_text = ModeratorMessages.CONFIRM_REMOVE_MODERATOR_TEMPLATE.format(
            moderator_name=moderator_name
        )

        keyboard = get_confirm_remove_moderator_keyboard(chat_id, moderator_id, moderator_name)
        await callback.answer()
        await callback.message.edit_text(
            confirm_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

        # Set state for confirmation
        await state.set_state(ChatManagementStates.confirming_unlink)  # Reusing existing state
        await state.update_data(selected_chat_id=chat_id, selected_moderator_id=moderator_id)
    except Exception as e:
        await callback.answer()
        await callback.message.edit_text(
            f"❌ Произошла ошибка: {str(e)}",
            reply_markup=get_back_to_chats_keyboard()
        )


@chat_management_router.callback_query(F.data.startswith("remove_moderator_confirmed:"))
async def handle_remove_moderator_confirmed(
    callback: types.CallbackQuery,
    db: AsyncSession,
    state: FSMContext
) -> None:
    """
    Handle confirmed moderator removal
    """
    try:
        # Extract chat ID and moderator ID from callback data
        parts = callback.data.split(":")
        chat_id = int(parts[1])
        moderator_id = int(parts[2])

        moderator_service = ModeratorManagementService(db)

        # Get moderator info before removal
        moderator = await moderator_service.moderator_service.get_moderator(moderator_id)
        if not moderator:
            await callback.answer()
            await callback.message.edit_text(
                "❌ Модератор не найден.",
                reply_markup=get_back_to_chats_keyboard()
            )
            return

        # Remove moderator
        success, message = await moderator_service.remove_moderator(
            chat_id, moderator.moderator_user_id, int(callback.from_user.id)
        )

        await callback.answer()
        if success:
            await callback.message.edit_text(
                message,
                reply_markup=get_back_to_chats_keyboard()
            )
        else:
            await callback.message.edit_text(
                f"❌ Ошибка: {message}",
                reply_markup=get_back_to_chats_keyboard()
            )

        # Clear state after operation
        await state.clear()
    except Exception as e:
        await callback.answer()
        await callback.message.edit_text(
            f"❌ Произошла ошибка: {str(e)}",
            reply_markup=get_back_to_chats_keyboard()
        )


@chat_management_router.callback_query(F.data.startswith("ai_content_check_settings:"))
async def handle_ai_content_check_settings(
    callback: types.CallbackQuery,
    db: AsyncSession,
    state: FSMContext
) -> None:
    """
    Handle AI content check settings button - show current status and options
    """
    # Extract chat ID from callback data
    chat_id = int(callback.data.split(":")[1])

    linking_service = ChatLinkingService(db)

    # Get chat details
    chat = await linking_service.chat_service.get_chat(chat_id)
    if not chat:
        await callback.message.edit_text(
            ChatManagementMessages.CHAT_NOT_FOUND
        )
        await state.clear()
        return

    # Check subscription status
    from app.services.chat_subscriptions import ChatSubscriptionsService
    subscriptions_service = ChatSubscriptionsService(db)
    active_subscription = await subscriptions_service.get_active_subscription_for_chat(chat.id)

    if active_subscription:
        # Has active subscription - show current setting
        current_setting = HelpMessages.AI_CHECK_ENABLED if chat.ai_content_check_enabled else HelpMessages.AI_CHECK_DISABLED
        response_text = HelpMessages.AI_CONTENT_CHECK_SETTINGS_TEMPLATE.format(
            chat_title=chat.title or ButtonTexts.UNTITLED_CHAT,
            current_setting=current_setting
        )
        keyboard = get_ai_content_check_options_keyboard(chat.id, chat.ai_content_check_enabled)
    else:
        # No active subscription - show payment options
        from app.services.subscription_prices import SubscriptionPricesService
        prices_service = SubscriptionPricesService(db)
        month_price = await prices_service.get_price_by_type('month')
        year_price = await prices_service.get_price_by_type('year')

        prices_info = {}
        if month_price:
            prices_info['month'] = month_price.price_stars
        if year_price:
            prices_info['year'] = year_price.price_stars

        if prices_info:
            from app.telegram.keyboards.payment_keyboard import payment_options_keyboard
            keyboard = payment_options_keyboard(chat.id, prices_info)
            response_text = PaymentMessages.AI_CHECK_DISABLED_NO_SUBSCRIPTION
        else:
            # No prices configured
            response_text = "❌ AI проверка контента недоступна.\n\nЦены подписок не настроены администратором."
            keyboard = get_back_to_chat_actions_keyboard(chat.id)
    await callback.message.edit_text(
        response_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

    # Set state for AI check setting selection
    await state.set_state(ChatManagementStates.setting_edit_timeout)  # Reusing existing state
    await state.update_data(selected_chat_id=chat.id)


@chat_management_router.callback_query(F.data.startswith("set_ai_check:"))
async def handle_ai_check_option_selection(
    callback: types.CallbackQuery,
    db: AsyncSession,
    state: FSMContext
) -> None:
    """
    Handle AI check option selection (enable/disable)
    """
    # Extract option and chat ID from callback data
    parts = callback.data.split(":")
    option = parts[1]
    chat_id = int(parts[2])

    linking_service = ChatLinkingService(db)

    # Get chat details
    chat = await linking_service.chat_service.get_chat(chat_id)
    if not chat:
        await callback.message.edit_text(
            ChatManagementMessages.CHAT_NOT_FOUND
        )
        await state.clear()
        return

    # Determine new setting
    if option == "enable":
        # Check if subscription is active before enabling
        from app.services.chat_subscriptions import ChatSubscriptionsService
        subscriptions_service = ChatSubscriptionsService(db)
        has_active_subscription = await subscriptions_service.has_active_subscription(chat_id)

        if not has_active_subscription:
            # No active subscription - show payment required message
            from app.services.subscription_prices import SubscriptionPricesService
            prices_service = SubscriptionPricesService(db)
            month_price = await prices_service.get_price_by_type('month')
            year_price = await prices_service.get_price_by_type('year')

            prices_info = {}
            if month_price:
                prices_info['month'] = month_price.price_stars
            if year_price:
                prices_info['year'] = year_price.price_stars

            if prices_info:
                from app.telegram.keyboards.payment_keyboard import payment_options_keyboard
                keyboard = payment_options_keyboard(chat_id, prices_info)
                await callback.message.edit_text(
                    PaymentMessages.AI_CHECK_DISABLED_NO_SUBSCRIPTION,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            else:
                await callback.message.edit_text(
                    "❌ AI проверка контента недоступна.\n\nЦены подписок не настроены администратором."
                )
            return

        new_setting = True
        success_message = HelpMessages.AI_CHECK_ENABLED_SUCCESS
    elif option == "disable":
        new_setting = False
        success_message = HelpMessages.AI_CHECK_DISABLED_SUCCESS
    else:
        await callback.message.edit_text("❌ Неверная опция")
        return

    # Update chat settings
    from app.schemas.chats import ChatUpdate
    update_data = ChatUpdate(ai_content_check_enabled=new_setting)
    updated_chat = await linking_service.chat_service.update_chat(chat_id, update_data)

    if updated_chat:
        # Return to chat actions
        linked_channel = await linking_service.chat_service.get_linked_channel(chat.id)
        keyboard = get_chat_actions_keyboard(chat, linked_channel)
        response_text = ChatManagementMessages.SELECTED_CHAT_TEMPLATE.format(
            chat_title=chat.title or ButtonTexts.UNTITLED_CHAT,
            channel_title=linked_channel.title or ButtonTexts.UNTITLED_CHAT
        ) if linked_channel else ChatManagementMessages.SELECTED_CHAT_NO_CHANNEL.format(
            chat_title=chat.title or ButtonTexts.UNTITLED_CHAT
        )
        if linked_channel and linked_channel.username:
            response_text += f" (@{linked_channel.username})"

        # Add subscription information if active
        if linked_channel:  # Only check subscription if there's a linked channel
            response_text += await format_subscription_info(chat.id, db)

        response_text += f"\n\n{success_message}\n\n" + ChatManagementMessages.SELECT_ACTION

        await callback.message.edit_text(
            response_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(ChatManagementMessages.SETTINGS_SAVED_ERROR)

    await state.clear()
