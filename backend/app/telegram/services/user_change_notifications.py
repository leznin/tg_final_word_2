"""
Service for sending notifications about user profile changes to groups
"""

import asyncio
from typing import Optional, List
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.chats import Chat
from app.models.chat_members import ChatMember
from app.models.telegram_users import TelegramUser


class UserChangeNotificationService:
    """Service for handling user change notifications to groups"""

    def __init__(self, db: AsyncSession, bot: Bot):
        self.db = db
        self.bot = bot

    async def notify_user_changes(
        self,
        telegram_user_id: int,
        field_name: str,
        old_value: Optional[str],
        new_value: Optional[str]
    ) -> None:
        """
        Send notification about user profile changes to all groups where:
        - The bot is an administrator
        - The user is a member
        - Notifications are enabled (notify_on_user_changes=True)
        
        Args:
            telegram_user_id: Telegram user ID
            field_name: Name of the changed field ('first_name', 'last_name', 'username')
            old_value: Old value of the field
            new_value: New value of the field
        """
        try:
            print(f"[NOTIFY] Starting notification process for user {telegram_user_id}, field {field_name}")
            
            # Get user info
            user_result = await self.db.execute(
                select(TelegramUser).where(TelegramUser.telegram_user_id == telegram_user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                print(f"[NOTIFY] User {telegram_user_id} not found in database")
                return

            print(f"[NOTIFY] User found: {user.first_name} {user.last_name} (@{user.username})")

            # Find all chats where:
            # 1. The user is an active member
            # 2. Notifications are enabled
            # 3. The chat is active
            query = (
                select(Chat, ChatMember)
                .join(ChatMember, and_(
                    Chat.id == ChatMember.chat_id,
                    ChatMember.telegram_user_id == telegram_user_id,
                    ChatMember.status == 'active'
                ))
                .where(
                    and_(
                        Chat.is_active == True,
                        Chat.notify_on_user_changes == True
                    )
                )
            )
            
            result = await self.db.execute(query)
            chat_members = result.all()
            
            print(f"[NOTIFY] Found {len(chat_members)} chats where user is active member and notifications enabled")
            
            if not chat_members:
                print(f"[NOTIFY] No chats found for notifications")
                return

            # Prepare notification message
            notification_text = await self._format_notification_message(
                user=user,
                field_name=field_name,
                old_value=old_value,
                new_value=new_value
            )
            
            print(f"[NOTIFY] Notification message prepared: {notification_text[:100]}...")

            # Send notifications to all relevant chats
            sent_count = 0
            for chat, _ in chat_members:
                try:
                    print(f"[NOTIFY] Sending to chat {chat.telegram_chat_id} ({chat.title})")
                    await self._send_notification_to_chat(
                        chat_id=chat.telegram_chat_id,
                        text=notification_text
                    )
                    sent_count += 1
                    print(f"[NOTIFY] Successfully sent to chat {chat.telegram_chat_id}")
                except Exception as e:
                    # Log error but continue with other chats
                    print(f"[NOTIFY] Failed to send notification to chat {chat.telegram_chat_id}: {e}")
                    import traceback
                    traceback.print_exc()
            
            print(f"[NOTIFY] Notification process completed. Sent to {sent_count}/{len(chat_members)} chats")

        except Exception as e:
            print(f"[NOTIFY] Error in notify_user_changes: {e}")
            import traceback
            traceback.print_exc()

    async def _format_notification_message(
        self,
        user: TelegramUser,
        field_name: str,
        old_value: Optional[str],
        new_value: Optional[str]
    ) -> str:
        """
        Format notification message about user change
        Shows current value, user link, and history of changes with dates
        
        Args:
            user: TelegramUser object
            field_name: Name of changed field ('first_name', 'last_name', 'username')
            old_value: Old value
            new_value: New value
            
        Returns:
            Formatted notification message in HTML (Russian)
        """
        from sqlalchemy import select, desc
        from app.models.telegram_user_history import TelegramUserHistory
        
        # Translate field names to Russian
        field_translations = {
            'first_name': 'имя',
            'last_name': 'фамилию',
            'username': 'никнейм'
        }
        
        field_ru = field_translations.get(field_name, field_name)
        
        # Format current value with @ for username
        if field_name == 'username':
            current_value = f"@{new_value}" if new_value else "не указан"
        else:
            current_value = new_value if new_value else "не указано"
        
        user_link = f"tg://user?id={user.telegram_user_id}"
        
        # Get history from database
        query = (
            select(TelegramUserHistory)
            .where(
                TelegramUserHistory.telegram_user_id == user.telegram_user_id,
                TelegramUserHistory.field_name == field_name
            )
            .order_by(desc(TelegramUserHistory.changed_at))
            .limit(10)  # Last 10 changes
        )
        
        result = await self.db.execute(query)
        history_entries = result.scalars().all()
        
        # Build history list (excluding the current change which is first in the list)
        history_lines = []
        for entry in history_entries[1:]:  # Skip the most recent (current change)
            if field_name == 'username':
                value_display = f"@{entry.new_value}" if entry.new_value else "не указан"
            else:
                value_display = entry.new_value if entry.new_value else "не указано"
            # Format date as DD.MM.YYYY
            date_str = entry.changed_at.strftime("%d.%m.%Y")
            history_lines.append(f"- {value_display} ({date_str})")
        
        # Build the message
        message_parts = [
            f"♻️ <b>Участник сменил {field_ru}</b>",
            f"✔️ {current_value}",
            f"🔗 {user_link}",
        ]
        
        if history_lines:
            message_parts.append("")
            message_parts.append(f"<b>Прежние значения:</b>")
            message_parts.extend(history_lines[:3])  # Show only last 3 previous values
        
        return "\n".join(message_parts)

    async def _send_notification_to_chat(self, chat_id: int, text: str) -> None:
        """
        Send notification message to a specific chat
        Messages are not deleted automatically
        
        Args:
            chat_id: Telegram chat ID
            text: Message text in HTML format
        """
        try:
            # Send the notification message
            message = await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="HTML"
            )
            
            # Message will remain in chat (no auto-deletion)
            print(f"[NOTIFY] Sent notification message {message.message_id} to chat {chat_id}")
            
        except Exception as e:
            # Re-raise to be handled by caller
            raise

    async def toggle_notifications(self, chat_id: int, enabled: bool) -> bool:
        """
        Enable or disable user change notifications for a chat
        
        Args:
            chat_id: Database chat ID (not telegram_chat_id)
            enabled: True to enable, False to disable
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = await self.db.execute(
                select(Chat).where(Chat.id == chat_id)
            )
            chat = result.scalar_one_or_none()
            
            if not chat:
                return False
            
            chat.notify_on_user_changes = enabled
            await self.db.commit()
            return True
            
        except Exception as e:
            await self.db.rollback()
            print(f"Error toggling notifications for chat {chat_id}: {e}")
            return False

    async def toggle_notifications_by_telegram_id(self, telegram_chat_id: int, enabled: bool) -> bool:
        """
        Enable or disable user change notifications for a chat by Telegram chat ID
        
        Args:
            telegram_chat_id: Telegram chat ID
            enabled: True to enable, False to disable
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = await self.db.execute(
                select(Chat).where(Chat.telegram_chat_id == telegram_chat_id)
            )
            chat = result.scalar_one_or_none()
            
            if not chat:
                return False
            
            chat.notify_on_user_changes = enabled
            await self.db.commit()
            return True
            
        except Exception as e:
            await self.db.rollback()
            print(f"Error toggling notifications for telegram chat {telegram_chat_id}: {e}")
            return False

    async def get_notification_status(self, telegram_chat_id: int) -> Optional[bool]:
        """
        Get current notification status for a chat
        
        Args:
            telegram_chat_id: Telegram chat ID
            
        Returns:
            True if enabled, False if disabled, None if chat not found
        """
        try:
            result = await self.db.execute(
                select(Chat).where(Chat.telegram_chat_id == telegram_chat_id)
            )
            chat = result.scalar_one_or_none()
            
            if not chat:
                return None
            
            return chat.notify_on_user_changes
            
        except Exception as e:
            print(f"Error getting notification status for telegram chat {telegram_chat_id}: {e}")
            return None
