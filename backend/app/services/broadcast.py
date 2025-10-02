"""
Broadcast service for sending messages to Telegram users
"""

import asyncio
import base64
import mimetypes
from datetime import datetime
from typing import List, Tuple, Optional
from io import BytesIO
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile

from app.models.users import User
from app.schemas.broadcast import BroadcastResult, BroadcastStatus, BroadcastMessageRequest
from app.services.openrouter import OpenRouterService
from app.core.config import settings


class BroadcastService:
    """Service class for broadcasting messages to users"""

    def __init__(self, db: AsyncSession, bot=None):
        self.db = db
        self.bot = bot
        self.openrouter_service = OpenRouterService(db)
        self.is_running = False
        self.current_progress = 0
        self.total_users = 0
        self.sent_successfully = 0
        self.blocked_users = 0
        self.failed_sends = 0
        self.started_at = None

    async def get_broadcast_users(self) -> List[User]:
        """Get users eligible for broadcast (have telegram_id and can receive messages)"""
        result = await self.db.execute(
            select(User).where(
                User.telegram_id.isnot(None),
                User.can_send_messages == True,
                User.is_bot == False,
                User.is_active == True
            )
        )
        return result.scalars().all()

    async def send_broadcast_message(self, request: BroadcastMessageRequest) -> BroadcastResult:
        """
        Send broadcast message to all eligible users with rate limiting
        """
        if self.is_running:
            raise ValueError("Broadcast is already running")

        # Reset counters
        self.is_running = True
        self.current_progress = 0
        self.sent_successfully = 0
        self.blocked_users = 0
        self.failed_sends = 0
        self.started_at = datetime.utcnow()

        try:
            # Get eligible users
            users = await self.get_broadcast_users()
            self.total_users = len(users)

            if not users:
                raise ValueError("No users available for broadcast")

            print(f"Starting broadcast to {len(users)} users")

            # Pre-translate message for all unique languages
            all_languages = set(user.language_code for user in users if user.language_code)
            translations = {}

            if all_languages:
                print(f"Translating message to {len(all_languages)} unique languages: {sorted(all_languages)}")

                # Translate message for each unique language once
                for target_lang in all_languages:
                    try:
                        translations[target_lang] = await self.openrouter_service.translate_message(
                            request.message, target_lang
                        )
                    except Exception as e:
                        print(f"Translation failed for language {target_lang}: {e}")
                        # Fall back to original message for this language
                        translations[target_lang] = request.message

                print(f"Translation completed for {len(translations)} languages")
            else:
                print("No language codes found, sending original message to all users")

            # Send messages with rate limiting (28 messages per second)
            batch_size = 28
            delay_between_batches = 1.0  # 1 second

            for i in range(0, len(users), batch_size):
                batch = users[i:i + batch_size]

                # Send batch concurrently with cached translations
                tasks = []
                for user in batch:
                    # Get translated message from cache or use original
                    if user.language_code and user.language_code in translations:
                        user_message = translations[user.language_code]
                    else:
                        user_message = request.message

                    # Create user-specific request with original message preserved
                    user_request = BroadcastMessageRequest(
                        message=user_message,
                        original_message=request.original_message or request.message,
                        media=request.media,
                        reply_markup=request.reply_markup
                    )

                    tasks.append(self._send_to_user(user, user_request))

                # Wait for all tasks in batch to complete
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for result in batch_results:
                    if isinstance(result, Exception):
                        self.failed_sends += 1
                        print(f"Error in batch: {result}")
                    else:
                        success, was_blocked = result
                        if success:
                            self.sent_successfully += 1
                        elif was_blocked:
                            self.blocked_users += 1
                        else:
                            self.failed_sends += 1

                self.current_progress = min(i + batch_size, len(users))

                # Rate limiting delay (skip delay after last batch)
                if i + batch_size < len(users):
                    await asyncio.sleep(delay_between_batches)

            completed_at = datetime.utcnow()
            duration = (completed_at - self.started_at).total_seconds()

            result = BroadcastResult(
                total_users=self.total_users,
                sent_successfully=self.sent_successfully,
                blocked_users=self.blocked_users,
                failed_sends=self.failed_sends,
                duration_seconds=duration,
                started_at=self.started_at,
                completed_at=completed_at
            )

            print(f"Broadcast completed: {self.sent_successfully} sent, {self.blocked_users} blocked, {self.failed_sends} failed")
            return result

        finally:
            self.is_running = False

    async def _send_to_user(self, user: User, request: BroadcastMessageRequest) -> Tuple[bool, bool]:
        """
        Send message to individual user
        Returns: (success, was_blocked)
        """
        try:
            if not self.bot:
                raise ValueError("Bot instance not provided")

            # Prepare keyboard markup if provided
            reply_markup = None
            if request.reply_markup:
                keyboard = []
                for row in request.reply_markup.inline_keyboard:
                    keyboard_row = []
                    for button in row.buttons:
                        keyboard_row.append(
                            InlineKeyboardButton(
                                text=button.text,
                                url=button.url,
                                callback_data=button.callback_data
                            )
                        )
                    keyboard.append(keyboard_row)
                reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

            # Send media or text message
            if request.media:
                media_type = request.media.type.lower()
                media_url = request.media.url
                caption = request.media.caption or request.message

                # Handle different URL types
                if media_url.startswith('data:'):
                    # Extract base64 data from data URL
                    # Parse data URL: data:mimetype;base64,data
                    header, encoded_data = media_url.split(',', 1)
                    mime_type = header.split(':')[1].split(';')[0]

                    # Decode base64
                    try:
                        file_data = base64.b64decode(encoded_data)
                    except Exception as e:
                        raise ValueError(f"Invalid base64 data: {e}")

                    # Create BufferedInputFile for file
                    filename = f"media.{mimetypes.guess_extension(mime_type) or 'bin'}"
                    buffered_file = BufferedInputFile(file_data, filename=filename)

                    if media_type == 'photo':
                        await self.bot.bot.send_photo(
                            chat_id=user.telegram_id,
                            photo=buffered_file,
                            caption=caption,
                            parse_mode="HTML",
                            reply_markup=reply_markup
                        )
                    elif media_type == 'video':
                        await self.bot.bot.send_video(
                            chat_id=user.telegram_id,
                            video=buffered_file,
                            caption=caption,
                            parse_mode="HTML",
                            reply_markup=reply_markup
                        )
                    elif media_type == 'document':
                        await self.bot.bot.send_document(
                            chat_id=user.telegram_id,
                            document=buffered_file,
                            caption=caption,
                            parse_mode="HTML",
                            reply_markup=reply_markup
                        )
                    else:
                        raise ValueError(f"Unsupported media type: {media_type}")
                else:
                    # Use URL directly (for external URLs)
                    if media_type == 'photo':
                        await self.bot.bot.send_photo(
                            chat_id=user.telegram_id,
                            photo=media_url,
                            caption=caption,
                            parse_mode="HTML",
                            reply_markup=reply_markup
                        )
                    elif media_type == 'video':
                        await self.bot.bot.send_video(
                            chat_id=user.telegram_id,
                            video=media_url,
                            caption=caption,
                            parse_mode="HTML",
                            reply_markup=reply_markup
                        )
                    elif media_type == 'document':
                        await self.bot.bot.send_document(
                            chat_id=user.telegram_id,
                            document=media_url,
                            caption=caption,
                            parse_mode="HTML",
                            reply_markup=reply_markup
                        )
                    else:
                        raise ValueError(f"Unsupported media type: {media_type}")
            else:
                # Send text message
                await self.bot.bot.send_message(
                    chat_id=user.telegram_id,
                    text=request.message,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )

            return True, False

        except TelegramForbiddenError as e:
            # User blocked the bot
            print(f"User {user.telegram_id} blocked the bot: {e}")
            user.can_send_messages = False
            user.blocked_at = datetime.utcnow()
            await self.db.commit()
            return False, True

        except TelegramBadRequest as e:
            # Other Telegram API error (invalid user, media URL, etc.)
            print(f"Telegram API error for user {user.telegram_id}: {e}")
            return False, False

        except Exception as e:
            # Other errors
            print(f"Unexpected error sending to user {user.telegram_id}: {e}")
            return False, False

    def get_broadcast_status(self) -> BroadcastStatus:
        """Get current broadcast status"""
        estimated_time_remaining = None
        if self.is_running and self.total_users > 0 and self.current_progress > 0:
            # Rough estimate based on current progress
            progress_ratio = self.current_progress / self.total_users
            if progress_ratio > 0:
                elapsed = (datetime.utcnow() - self.started_at).total_seconds()
                estimated_total = elapsed / progress_ratio
                estimated_time_remaining = estimated_total - elapsed

        return BroadcastStatus(
            is_running=self.is_running,
            current_progress=self.current_progress,
            total_users=self.total_users,
            sent_successfully=self.sent_successfully,
            blocked_users=self.blocked_users,
            failed_sends=self.failed_sends,
            estimated_time_remaining=estimated_time_remaining,
            started_at=self.started_at
        )
