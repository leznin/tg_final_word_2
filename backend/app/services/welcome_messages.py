"""
Welcome message service for handling message variables and sending
"""

import asyncio
import json
from typing import Optional, Dict, Any
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile, BufferedInputFile
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chats import Chat
from app.models.telegram_users import TelegramUser
from app.core.config import settings


class WelcomeMessageService:
    """Service for handling welcome message functionality"""
    
    def __init__(self, db: AsyncSession, bot: Bot):
        self.db = db
        self.bot = bot

    def replace_variables(self, text: str, user: TelegramUser, chat: Chat) -> str:
        """Replace variables in welcome message text with actual values"""
        if not text:
            return ""
            
        variables = {
            '{ID}': str(user.telegram_user_id),
            '{NAME}': user.first_name or '',
            '{SURNAME}': user.last_name or '',
            '{NAMESURNAME}': f"{user.first_name or ''} {user.last_name or ''}".strip(),
            '{LANG}': user.language_code or 'en',
            '{MENTION}': f"<a href='tg://user?id={user.telegram_user_id}'>{user.first_name or 'User'}</a>",
            '{USERNAME}': f"@{user.username}" if user.username else f"ID: {user.telegram_user_id}",
            '{GROUPNAME}': chat.title or 'Chat'
        }
        
        # Replace all variables in the text
        for var, value in variables.items():
            text = text.replace(var, value)
            
        return text

    def create_inline_keyboard(self, buttons_data: Any) -> Optional[InlineKeyboardMarkup]:
        """Create inline keyboard from buttons data"""
        if not buttons_data:
            return None
            
        try:
            # Handle both list and JSON string formats
            if isinstance(buttons_data, str):
                buttons_rows = json.loads(buttons_data)
            else:
                buttons_rows = buttons_data
                
            if not buttons_rows or not isinstance(buttons_rows, list):
                return None
            
            keyboard_rows = []
            for row in buttons_rows:
                if not isinstance(row, list):
                    continue
                    
                button_row = []
                for button_data in row:
                    if not isinstance(button_data, dict):
                        continue
                        
                    text = button_data.get('text', '').strip()
                    if not text:
                        continue
                    
                    # Create button based on type
                    if button_data.get('url'):
                        button = InlineKeyboardButton(text=text, url=button_data['url'])
                    elif button_data.get('callback_data'):
                        button = InlineKeyboardButton(text=text, callback_data=button_data['callback_data'])
                    else:
                        continue  # Skip invalid buttons
                        
                    button_row.append(button)
                
                if button_row:
                    keyboard_rows.append(button_row)
            
            return InlineKeyboardMarkup(inline_keyboard=keyboard_rows) if keyboard_rows else None
            
        except (json.JSONDecodeError, TypeError, AttributeError):
            return None

    async def send_welcome_message(self, chat: Chat, user: TelegramUser) -> Optional[int]:
        """Send welcome message to a user who joined the chat"""
        if not chat.welcome_message_enabled or not chat.welcome_message_text:
            return None
            
        try:
            # Replace variables in message text
            message_text = self.replace_variables(chat.welcome_message_text, user, chat)
            
            # Create inline keyboard if buttons are configured
            reply_markup = self.create_inline_keyboard(chat.welcome_message_buttons)
            
            sent_message = None
            media_sent_successfully = False
            
            # Try to send message with media if configured
            if chat.welcome_message_media_type and chat.welcome_message_media_url:
                try:
                    media_url = chat.welcome_message_media_url.strip()
                    
                    # Skip if URL is empty
                    if not media_url:
                        print(f"Empty media URL for chat {chat.telegram_chat_id}, will send text-only")
                    else:
                        # Convert relative URL to absolute
                        if media_url.startswith('/'):
                            # Check if APP_DOMAIN is properly configured
                            if not settings.APP_DOMAIN or settings.APP_DOMAIN.startswith('http://localhost'):
                                print(f"⚠️  APP_DOMAIN not configured for production, skipping media for chat {chat.telegram_chat_id}")
                                print(f"   Media URL: {media_url}")
                            else:
                                media_url = f"{settings.APP_DOMAIN}{media_url}"
                        
                        # Only try to send media if we have a valid absolute URL
                        if media_url.startswith(('http://', 'https://')):
                            if chat.welcome_message_media_type == 'photo':
                                sent_message = await self.bot.send_photo(
                                    chat_id=chat.telegram_chat_id,
                                    photo=media_url,
                                    caption=message_text,
                                    parse_mode='HTML',
                                    reply_markup=reply_markup
                                )
                                media_sent_successfully = True
                            elif chat.welcome_message_media_type == 'video':
                                sent_message = await self.bot.send_video(
                                    chat_id=chat.telegram_chat_id,
                                    video=media_url,
                                    caption=message_text,
                                    parse_mode='HTML',
                                    reply_markup=reply_markup
                                )
                                media_sent_successfully = True
                        else:
                            print(f"Invalid media URL format for chat {chat.telegram_chat_id}: {media_url}")
                            
                except TelegramBadRequest as e:
                    # Media sending failed, log and fallback to text
                    print(f"⚠️  Failed to send media for chat {chat.telegram_chat_id}: {e}")
                    print(f"   Media URL was: {chat.welcome_message_media_url}")
                    print(f"   Will send text-only message instead")
                except Exception as e:
                    print(f"⚠️  Unexpected error sending media for chat {chat.telegram_chat_id}: {e}")
            
            # Send text-only message if media wasn't sent
            if not media_sent_successfully:
                sent_message = await self.bot.send_message(
                    chat_id=chat.telegram_chat_id,
                    text=message_text,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            
            # Schedule message deletion if lifetime is set
            if sent_message and chat.welcome_message_lifetime_minutes:
                asyncio.create_task(
                    self.schedule_message_deletion(
                        chat.telegram_chat_id,
                        sent_message.message_id,
                        chat.welcome_message_lifetime_minutes * 60  # Convert to seconds
                    )
                )
            
            return sent_message.message_id if sent_message else None
            
        except TelegramBadRequest as e:
            error_msg = f"Failed to send welcome message to chat {chat.telegram_chat_id}: {e}"
            if chat.welcome_message_media_url:
                error_msg += f"\nMedia URL: {chat.welcome_message_media_url}"
                error_msg += f"\nMedia Type: {chat.welcome_message_media_type}"
            print(error_msg)
            return None
        except Exception as e:
            print(f"Unexpected error sending welcome message to chat {chat.telegram_chat_id}: {e}")
            return None

    async def schedule_message_deletion(self, chat_id: int, message_id: int, delay_seconds: int):
        """Schedule message deletion after specified delay"""
        try:
            await asyncio.sleep(delay_seconds)
            await self.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            print(f"Failed to delete welcome message {message_id} in chat {chat_id}: {e}")