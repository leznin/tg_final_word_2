"""
Message update handler for monitoring changes and forwarding to linked channels
"""

from aiogram import Router, types, Bot, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.services.chats import ChatService
from app.services.messages import MessageService
from app.services.chat_members import ChatMemberService
from app.services.openrouter import OpenRouterService
from app.services.chat_subscriptions import ChatSubscriptionsService
from app.telegram.services.chat_linking import ChatLinkingService
from app.telegram.services.moderator_management import ModeratorManagementService
from app.telegram.states import ChatManagementStates
from app.telegram.keyboards.chat_management import get_cancel_keyboard, get_back_to_chats_keyboard
from app.telegram.utils.constants import ChannelLinkingMessages, MessageEditingMessages, ButtonTexts

# Create router for message updates
message_router = Router()


async def send_media_notification_to_channel(bot: Bot, channel_chat_id: int, message: types.Message, notification_text: str) -> None:
    """
    Send media from edited message to linked channel with notification text as caption
    """
    try:
        # Determine media type and send accordingly
        if message.photo:
            # Send photo with notification as caption
            largest_photo = message.photo[-1] if message.photo else None
            if largest_photo:
                await bot.send_photo(
                    chat_id=channel_chat_id,
                    photo=largest_photo.file_id,
                    caption=notification_text,
                    parse_mode="HTML"
                )
        elif message.video:
            # Send video with notification as caption
            await bot.send_video(
                chat_id=channel_chat_id,
                video=message.video.file_id,
                caption=notification_text,
                parse_mode="HTML"
            )
        elif message.document:
            # Send document with notification as caption
            await bot.send_document(
                chat_id=channel_chat_id,
                document=message.document.file_id,
                caption=notification_text,
                parse_mode="HTML"
            )
        elif message.audio:
            # Send audio with notification as caption
            await bot.send_audio(
                chat_id=channel_chat_id,
                audio=message.audio.file_id,
                caption=notification_text,
                parse_mode="HTML"
            )
        elif message.voice:
            # Send voice with notification as caption
            await bot.send_voice(
                chat_id=channel_chat_id,
                voice=message.voice.file_id,
                caption=notification_text,
                parse_mode="HTML"
            )
        elif message.animation:
            # Send animation (GIF) with notification as caption
            await bot.send_animation(
                chat_id=channel_chat_id,
                animation=message.animation.file_id,
                caption=notification_text,
                parse_mode="HTML"
            )
        elif message.sticker:
            # Send sticker with notification as caption (stickers can have text)
            await bot.send_sticker(
                chat_id=channel_chat_id,
                sticker=message.sticker.file_id
            )
            # Send notification text separately since stickers don't support captions
            await bot.send_message(
                chat_id=channel_chat_id,
                text=notification_text,
                parse_mode="HTML"
            )
        elif message.video_note:
            # Send video note (round video) - video notes don't support captions
            await bot.send_video_note(
                chat_id=channel_chat_id,
                video_note=message.video_note.file_id
            )
            # Send notification text separately
            await bot.send_message(
                chat_id=channel_chat_id,
                text=notification_text,
                parse_mode="HTML"
            )
        else:
            # No media, just send text notification
            await bot.send_message(
                chat_id=channel_chat_id,
                text=notification_text,
                parse_mode="HTML"
            )
    except Exception as e:
        print(f"Failed to send media notification to channel {channel_chat_id}: {e}")
        # Fallback: send text notification if media sending fails
        try:
            await bot.send_message(
                chat_id=channel_chat_id,
                text=notification_text,
                parse_mode="HTML"
            )
        except Exception as fallback_error:
            print(f"Fallback notification also failed: {fallback_error}")


@message_router.edited_message()
async def handle_edited_message(message: types.Message, db: AsyncSession, bot: Bot) -> None:
    """
    Handle edited messages in group chats - compare with DB and delete if changed, then notify channel
    """
    # Only process messages from group chats (not private chats or channels)
    if message.chat.type not in ['group', 'supergroup']:
        return

    chat_service = ChatService(db)
    message_service = MessageService(db)
    chat_member_service = ChatMemberService(db)
    moderator_service = ModeratorManagementService(db)
    openrouter_service = OpenRouterService(db)
    subscriptions_service = ChatSubscriptionsService(db)

    # Get the chat from database
    chat = await chat_service.get_chat_by_telegram_id(message.chat.id)
    if not chat:
        print(f"Chat {message.chat.id} not found in database")
        return

    # Check if chat has a linked channel
    linked_channel = await chat_service.get_linked_channel(chat.id)
    if not linked_channel:
        print(f"Chat {message.chat.id} has no linked channel")
        return

    # Get the message from database
    db_message = await message_service.get_message_by_telegram_id(chat.id, message.message_id)
    if not db_message:
        print(f"Message {message.message_id} from chat {chat.id} not found in database")
        return

    # Check if user is a moderator in this chat
    is_moderator = await moderator_service.moderator_service.is_user_moderator(chat.id, message.from_user.id)

    # Check if editing is allowed and within timeout
    should_delete_and_notify = False

    if is_moderator:
        # Moderators can always edit messages in their chats
        print(f"User {message.from_user.id} is a moderator in chat {chat.id}, allowing edit")
        return
    elif chat.message_edit_timeout_minutes is None:
        # Editing is completely disabled for this chat
        should_delete_and_notify = True
        print(f"Message editing is disabled for chat {chat.id}, will delete and notify")
    else:
        # Check if within allowed edit time
        edit_deadline = db_message.created_at + timedelta(minutes=chat.message_edit_timeout_minutes)
        current_time = datetime.now(db_message.created_at.tzinfo)

        if current_time > edit_deadline:
            # Time expired - delete and notify
            should_delete_and_notify = True
            print(f"Message {message.message_id} from chat {chat.id} edited after timeout ({chat.message_edit_timeout_minutes} minutes), will delete and notify")
        else:
            # Within allowed time - allow editing
            print(f"Message {message.message_id} from chat {chat.id} edited within timeout, allowing edit")

    # Prepare telegram message data for comparison
    telegram_message_data = {
        'message_id': message.message_id,
        'text': message.text,
        'caption': message.caption,
    }

    # Add user info if available
    if message.from_user:
        telegram_message_data['from_user'] = {
            'id': message.from_user.id,
            'is_bot': message.from_user.is_bot,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name,
            'username': message.from_user.username,
            'language_code': message.from_user.language_code,
            'is_premium': message.from_user.is_premium
        }

    # Add media info
    if message.photo:
        largest_photo = message.photo[-1] if message.photo else None
        if largest_photo:
            telegram_message_data['photo'] = [{'file_id': largest_photo.file_id, 'file_unique_id': largest_photo.file_unique_id, 'width': largest_photo.width, 'height': largest_photo.height}]
    if message.video:
        telegram_message_data['video'] = {'file_id': message.video.file_id}
    if message.document:
        telegram_message_data['document'] = {'file_id': message.document.file_id}
    if message.audio:
        telegram_message_data['audio'] = {'file_id': message.audio.file_id}
    if message.voice:
        telegram_message_data['voice'] = {'file_id': message.voice.file_id}
    if message.animation:
        telegram_message_data['animation'] = {'file_id': message.animation.file_id}
    if message.sticker:
        telegram_message_data['sticker'] = {'file_id': message.sticker.file_id}
    if message.video_note:
        telegram_message_data['video_note'] = {'file_id': message.video_note.file_id}

    if not should_delete_and_notify:
        # Skip deletion and notification, go directly to database update
        print(f"Message {message.message_id} from chat {chat.id} has changes, updating database only")

        # Update the message in database with new content
        try:
            await message_service.update_message_from_telegram(chat.id, telegram_message_data)
            print(f"Successfully updated message {message.message_id} in database")
        except Exception as e:
            print(f"Failed to update message {message.message_id} in database: {e}")
        return

    # Compare message with database version
    has_changes = await message_service.compare_message_with_telegram_data(db_message, telegram_message_data)

    if not has_changes:
        print(f"Message {message.message_id} from chat {chat.id} has no changes, skipping")
        return

    print(f"Message {message.message_id} from chat {chat.id} has changes, processing deletion and notification")

    # Check message content for prohibited material using AI (only if enabled and subscription is active)
    message_text = getattr(message, 'text', '') or getattr(message, 'caption', '') or ''
    is_prohibited = False

    # Check if AI content check is enabled and subscription is active
    ai_check_available = False
    if chat.ai_content_check_enabled and message_text.strip():
        # Check if chat has active subscription for AI content check
        has_active_subscription = await subscriptions_service.has_active_subscription(chat.id)
        if has_active_subscription:
            ai_check_available = True
        else:
            print(f"AI content check subscription expired or not found for chat {chat.id}")
            # Automatically disable AI check for this chat if subscription expired
            print(f"Automatically disabling AI content check for chat {chat.id} due to expired subscription")
            chat.ai_content_check_enabled = False
            await db.commit()

    if ai_check_available:
        try:
            is_prohibited = await openrouter_service.check_message_content(message_text)
            if is_prohibited:
                print(f"Message {message.message_id} contains prohibited content according to AI check")
            else:
                print(f"Message {message.message_id} passed AI content check")
        except Exception as e:
            print(f"Error checking message content with AI: {e}")
            # Continue with notification even if AI check fails
    elif chat.ai_content_check_enabled and not ai_check_available:
        print(f"AI content check enabled but no active subscription for chat {chat.id}")
    elif not chat.ai_content_check_enabled:
        print(f"AI content check is disabled for chat {chat.id}")
    else:
        print(f"No text content to check in message {message.message_id}")

    # Delete the message from the group chat
    try:
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )
        print(f"Successfully deleted message {message.message_id} from chat {message.chat.id}")
    except Exception as e:
        print(f"Failed to delete message {message.message_id} from chat {message.chat.id}: {e}")
        # Continue with notification even if deletion failed

    # Send notification to the linked channel
    try:
        # Format the notification message
        edited_info = MessageEditingMessages.MESSAGE_DELETED_HEADER

        # Add prohibited content warning if detected
        if is_prohibited:
            edited_info += MessageEditingMessages.PROHIBITED_CONTENT_WARNING

        # Add chat name at the beginning
        edited_info += MessageEditingMessages.CHAT_INFO_TEMPLATE.format(
            chat_title=message.chat.title or MessageEditingMessages.GROUP_CHAT
        )

        # Add information about the author if available
        if message.from_user:
            user_name = message.from_user.full_name
            user_id = message.from_user.id
            edited_info += MessageEditingMessages.AUTHOR_INFO_TEMPLATE.format(
                user_name=user_name, user_id=user_id
            )

            # Get detailed user information from chat_members table
            chat_member = await chat_member_service.get_chat_member_by_telegram_id(chat.id, user_id)
            if chat_member:
                # Add username if available
                if chat_member.username:
                    edited_info += MessageEditingMessages.USERNAME_TEMPLATE.format(
                        username=chat_member.username
                    )

                # Add full name details
                full_name_parts = []
                if chat_member.first_name:
                    full_name_parts.append(chat_member.first_name)
                if chat_member.last_name:
                    full_name_parts.append(chat_member.last_name)
                if full_name_parts:
                    edited_info += MessageEditingMessages.FULL_NAME_TEMPLATE.format(
                        full_name=" ".join(full_name_parts)
                    )

                # Add language if available
                if chat_member.language_code:
                    edited_info += MessageEditingMessages.LANGUAGE_TEMPLATE.format(
                        language=chat_member.language_code.upper()
                    )

                # Add premium status
                premium_status = "Да" if chat_member.is_premium else "Нет"
                edited_info += MessageEditingMessages.PREMIUM_TEMPLATE.format(
                    premium_status=premium_status
                )

        # Add message ID
        edited_info += MessageEditingMessages.MESSAGE_ID_TEMPLATE.format(
            message_id=message.message_id
        )

        # Add creation time
        created_time = db_message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        edited_info += MessageEditingMessages.CREATION_TIME_TEMPLATE.format(
            created_time=created_time
        )

        # Add edit time
        edit_time = datetime.fromtimestamp(message.edit_date).strftime('%Y-%m-%d %H:%M:%S') if message.edit_date else MessageEditingMessages.TIME_UNKNOWN
        edited_info += MessageEditingMessages.EDIT_TIME_TEMPLATE.format(
            edit_time=edit_time
        )

        # Calculate and add time difference
        if message.edit_date:
            edit_datetime = datetime.fromtimestamp(message.edit_date)
            time_diff = edit_datetime - db_message.created_at
            total_seconds = int(time_diff.total_seconds())

            if total_seconds < 3600:  # less than 1 hour
                minutes = total_seconds // 60
                edited_info += MessageEditingMessages.TIME_DIFF_MINUTES_TEMPLATE.format(
                    minutes=minutes
                )
            else:  # 1 hour or more
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                edited_info += MessageEditingMessages.TIME_DIFF_HOURS_TEMPLATE.format(
                    hours=hours, minutes=minutes
                )

        edited_info += "\n"

        # Add the original message content
        original_text = db_message.text_content or ''
        if original_text:
            edited_info += MessageEditingMessages.ORIGINAL_MESSAGE_HEADER.format(
                original_text=original_text
            )
        else:
            edited_info += MessageEditingMessages.ORIGINAL_MESSAGE_NO_TEXT

        # Add the new message content
        new_text = getattr(message, 'text', '') or getattr(message, 'caption', '') or ''
        if new_text:
            edited_info += MessageEditingMessages.NEW_MESSAGE_HEADER.format(
                new_text=new_text
            )
        else:
            edited_info += MessageEditingMessages.NEW_MESSAGE_NO_TEXT

        # Send notification to linked channel with media if present
        await send_media_notification_to_channel(
            bot=bot,
            channel_chat_id=linked_channel.telegram_chat_id,
            message=message,
            notification_text=edited_info
        )
        print(f"Successfully sent notification about edited message to channel {linked_channel.telegram_chat_id}")

    except Exception as e:
        print(f"Failed to send notification to channel {linked_channel.telegram_chat_id}: {e}")

    # Update the message in database with new content
    try:
        await message_service.update_message_from_telegram(chat.id, telegram_message_data)
        print(f"Successfully updated message {message.message_id} in database")
    except Exception as e:
        print(f"Failed to update message {message.message_id} in database: {e}")

    # Close OpenRouter service
    try:
        await openrouter_service.close()
    except Exception as e:
        print(f"Error closing OpenRouter service: {e}")


@message_router.message(ChatManagementStates.waiting_for_channel_forward)
async def handle_channel_forward_for_linking(
    message: types.Message,
    state: FSMContext,
    db: AsyncSession
) -> None:
    """
    Handle forwarded messages from channels when user is in linking state
    """
    linking_service = ChatLinkingService(db)

    # Extract channel ID from forwarded message
    channel_telegram_id = await linking_service.extract_channel_from_forwarded_message(message)

    if not channel_telegram_id:
        # Message is not forwarded from a channel
        await message.reply(
            ChannelLinkingMessages.INVALID_FORWARD,
            reply_markup=get_cancel_keyboard()
        )
        return

    # Get chat ID from FSM state
    state_data = await state.get_data()
    chat_id = state_data.get('selected_chat_id')

    if not chat_id:
        from app.telegram.utils.constants import ErrorMessages
        await message.reply(
            ErrorMessages.SELECTED_CHAT_ERROR,
            reply_markup=get_cancel_keyboard()
        )
        await state.clear()
        return

    # Try to link channel to chat
    success, response_message = await linking_service.link_channel_to_chat(
        chat_id, channel_telegram_id, message.from_user.id
    )

    if success:
        await message.reply(
            response_message,
            reply_markup=get_back_to_chats_keyboard()
        )
    else:
        await message.reply(
            f"❌ Ошибка связывания: {response_message}\n\n"
            "Попробуйте переслать другое сообщение из канала.",
            reply_markup=get_cancel_keyboard()
        )
        return

    # Clear FSM state
    await state.clear()


@message_router.message(ChatManagementStates.waiting_for_moderator_forward)
async def handle_moderator_forward_for_adding(
    message: types.Message,
    state: FSMContext,
    db: AsyncSession
) -> None:
    """
    Handle forwarded messages from users when user is in moderator adding state
    """
    moderator_service = ModeratorManagementService(db)

    # Extract user data from forwarded message
    user_data = await moderator_service.extract_user_from_forwarded_message(message)

    if not user_data:
        # Message is not forwarded from a user
        await message.reply(
            "❌ Это не пересылаемое сообщение от пользователя.\n\n"
            "Перешлите сообщение от пользователя, которого хотите назначить модератором.",
            reply_markup=get_cancel_keyboard()
        )
        return

    # Get chat ID from FSM state
    state_data = await state.get_data()
    chat_id = state_data.get('selected_chat_id')

    if not chat_id:
        from app.telegram.utils.constants import ErrorMessages
        await message.reply(
            ErrorMessages.SELECTED_CHAT_ERROR,
            reply_markup=get_cancel_keyboard()
        )
        await state.clear()
        return

    # Try to add moderator
    success, response_message = await moderator_service.add_moderator_from_forwarded_message(
        chat_id, message.from_user.id, user_data
    )

    if success:
        await message.reply(
            response_message,
            reply_markup=get_back_to_chats_keyboard()
        )
    else:
        await message.reply(
            f"❌ Ошибка: {response_message}\n\n"
            "Попробуйте переслать другое сообщение от пользователя.",
            reply_markup=get_cancel_keyboard()
        )
        return

    # Clear FSM state
    await state.clear()


@message_router.message()
async def handle_new_message(message: types.Message, db: AsyncSession) -> None:
    """
    Handle new messages - save to database and log chat members
    """
    # Only process messages from group chats (not private chats or channels)
    if message.chat.type not in ['group', 'supergroup']:
        return

    from app.services.chats import ChatService
    from app.services.chat_members import ChatMemberService
    from app.services.messages import MessageService
    from app.schemas.chat_members import TelegramUserData
    from app.schemas.messages import TelegramMessageData

    chat_service = ChatService(db)
    member_service = ChatMemberService(db)
    message_service = MessageService(db)

    # Get the chat from database
    chat = await chat_service.get_chat_by_telegram_id(message.chat.id)
    if not chat:
        return

    # Log chat member if user sent the message
    if message.from_user:
        try:
            telegram_user_data = TelegramUserData(
                id=message.from_user.id,
                is_bot=message.from_user.is_bot,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                username=message.from_user.username,
                language_code=message.from_user.language_code,
                is_premium=message.from_user.is_premium,
                added_to_attachment_menu=message.from_user.added_to_attachment_menu,
                can_join_groups=message.from_user.can_join_groups,
                can_read_all_group_messages=message.from_user.can_read_all_group_messages,
                supports_inline_queries=message.from_user.supports_inline_queries,
                can_connect_to_business=message.from_user.can_connect_to_business,
                has_main_web_app=message.from_user.has_main_web_app
            )

            # Create or update member in database
            await member_service.create_or_update_member_from_telegram(chat.id, telegram_user_data)

        except Exception as e:
            print(f"Error logging chat member {message.from_user.id}: {e}")

    # Save message to database
    try:
        # Prepare message data for service
        message_dict = {
            'message_id': message.message_id,
            'date': message.date,
            'text': message.text,
            'caption': message.caption,
        }

        # Add user info if available
        if message.from_user:
            message_dict['from_user'] = {
                'id': message.from_user.id,
                'is_bot': message.from_user.is_bot,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name,
                'username': message.from_user.username,
                'language_code': message.from_user.language_code,
                'is_premium': message.from_user.is_premium
            }

        # Add media info
        if message.photo:
            # Take the largest photo (last in array)
            largest_photo = message.photo[-1] if message.photo else None
            if largest_photo:
                message_dict['photo'] = [{'file_id': largest_photo.file_id, 'file_unique_id': largest_photo.file_unique_id, 'width': largest_photo.width, 'height': largest_photo.height}]
        if message.video:
            message_dict['video'] = {'file_id': message.video.file_id}
        if message.document:
            message_dict['document'] = {'file_id': message.document.file_id}
        if message.audio:
            message_dict['audio'] = {'file_id': message.audio.file_id}
        if message.voice:
            message_dict['voice'] = {'file_id': message.voice.file_id}
        if message.animation:
            message_dict['animation'] = {'file_id': message.animation.file_id}
        if message.sticker:
            message_dict['sticker'] = {'file_id': message.sticker.file_id}
        if message.video_note:
            message_dict['video_note'] = {'file_id': message.video_note.file_id}

        # Save message
        await message_service.create_message_from_telegram(chat.id, message_dict)

    except Exception as e:
        print(f"Error saving message {message.message_id}: {e}")
