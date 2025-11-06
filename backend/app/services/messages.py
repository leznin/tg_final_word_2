"""
Messages service with business logic
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, and_
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.messages import Message
from app.schemas.messages import MessageCreate, MessageUpdate


class MessageService:
    """Service class for message operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_message(self, message_data: MessageCreate) -> Message:
        """Create a new message"""
        db_message = Message(**message_data.model_dump())
        self.db.add(db_message)
        await self.db.commit()
        # Don't refresh to avoid triggering lazy-loaded relationships
        # await self.db.refresh(db_message)
        return db_message

    async def get_message(self, message_id: int) -> Optional[Message]:
        """Get message by ID"""
        result = await self.db.execute(select(Message).where(Message.id == message_id))
        return result.scalar_one_or_none()

    async def get_message_by_telegram_id(self, chat_id: int, telegram_message_id: int) -> Optional[Message]:
        """Get message by chat_id and telegram_message_id"""
        result = await self.db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .where(Message.telegram_message_id == telegram_message_id)
        )
        return result.scalar_one_or_none()

    async def get_chat_messages(self, chat_id: int, skip: int = 0, limit: int = 100) -> List[Message]:
        """Get messages from a specific chat"""
        result = await self.db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent_messages(self, chat_id: int, hours: int = 24) -> List[Message]:
        """Get messages from chat within specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        result = await self.db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .where(Message.created_at >= cutoff_time)
            .order_by(Message.created_at.desc())
        )
        return result.scalars().all()

    async def update_message(self, message_id: int, message_data: MessageUpdate) -> Optional[Message]:
        """Update message"""
        db_message = await self.get_message(message_id)
        if not db_message:
            return None

        for field, value in message_data.model_dump(exclude_unset=True).items():
            setattr(db_message, field, value)

        await self.db.commit()
        await self.db.refresh(db_message)
        return db_message

    async def delete_old_messages(self, hours: int = 50) -> int:
        """Delete messages older than specified hours. Returns count of deleted messages."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        result = await self.db.execute(
            delete(Message)
            .where(Message.created_at < cutoff_time)
        )
        await self.db.commit()
        return result.rowcount

    async def get_message_count(self, chat_id: int) -> int:
        """Get count of messages in a chat"""
        result = await self.db.execute(
            select(func.count(Message.id))
            .where(Message.chat_id == chat_id)
        )
        return result.scalar()

    async def get_total_message_count(self) -> int:
        """Get total count of all messages"""
        result = await self.db.execute(select(func.count(Message.id)))
        return result.scalar()

    async def create_message_from_telegram(self, chat_id: int, telegram_message_data: dict) -> Optional[Message]:
        """Create message from Telegram message data"""
        try:
            message_type = 'text'
            text_content = None
            media_file_id = None
            media_type = None
            telegram_user_id = None

            # Extract user ID
            if 'from_user' in telegram_message_data and telegram_message_data['from_user']:
                telegram_user_id = telegram_message_data['from_user'].get('id')

            # Determine message type and extract content
            # First check for media types
            if telegram_message_data.get('photo'):
                message_type = 'photo'
                media_type = 'photo'
                # Get the highest quality photo
                if isinstance(telegram_message_data['photo'], list) and telegram_message_data['photo']:
                    media_file_id = telegram_message_data['photo'][-1].get('file_id')
                text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('video'):
                message_type = 'video'
                media_type = 'video'
                media_file_id = telegram_message_data['video'].get('file_id')
                text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('document'):
                message_type = 'document'
                media_type = 'document'
                media_file_id = telegram_message_data['document'].get('file_id')
                text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('audio'):
                message_type = 'audio'
                media_type = 'audio'
                media_file_id = telegram_message_data['audio'].get('file_id')
                text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('voice'):
                message_type = 'voice'
                media_type = 'voice'
                media_file_id = telegram_message_data['voice'].get('file_id')
                text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('animation'):
                message_type = 'animation'
                media_type = 'animation'
                media_file_id = telegram_message_data['animation'].get('file_id')
                text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('sticker'):
                message_type = 'sticker'
                media_type = 'sticker'
                media_file_id = telegram_message_data['sticker'].get('file_id')
                text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('video_note'):
                message_type = 'video_note'
                media_type = 'video_note'
                media_file_id = telegram_message_data['video_note'].get('file_id')
                text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('text'):
                message_type = 'text'
                text_content = telegram_message_data['text']
            else:
                # Message without text or media
                message_type = 'service'

            message_data = MessageCreate(
                chat_id=chat_id,
                telegram_message_id=telegram_message_data['message_id'],
                telegram_user_id=telegram_user_id,
                message_type=message_type,
                text_content=text_content,
                media_file_id=media_file_id,
                media_type=media_type
            )

            return await self.create_message(message_data)

        except Exception as e:
            print(f"Error creating message from telegram data: {e}")
            return None

    async def compare_message_with_telegram_data(self, db_message: Message, telegram_message_data: dict) -> bool:
        """
        Compare message in database with telegram message data
        Returns True if messages are different, False if they are the same
        """
        try:
            # Extract content from telegram message data
            new_text_content = None
            new_media_file_id = None
            new_media_type = None

            # Determine message type and extract content
            if telegram_message_data.get('photo'):
                new_media_type = 'photo'
                if isinstance(telegram_message_data['photo'], list) and telegram_message_data['photo']:
                    new_media_file_id = telegram_message_data['photo'][-1].get('file_id')
                new_text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('video'):
                new_media_type = 'video'
                new_media_file_id = telegram_message_data['video'].get('file_id')
                new_text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('document'):
                new_media_type = 'document'
                new_media_file_id = telegram_message_data['document'].get('file_id')
                new_text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('audio'):
                new_media_type = 'audio'
                new_media_file_id = telegram_message_data['audio'].get('file_id')
                new_text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('voice'):
                new_media_type = 'voice'
                new_media_file_id = telegram_message_data['voice'].get('file_id')
                new_text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('animation'):
                new_media_type = 'animation'
                new_media_file_id = telegram_message_data['animation'].get('file_id')
                new_text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('sticker'):
                new_media_type = 'sticker'
                new_media_file_id = telegram_message_data['sticker'].get('file_id')
                new_text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('video_note'):
                new_media_type = 'video_note'
                new_media_file_id = telegram_message_data['video_note'].get('file_id')
                new_text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('text'):
                new_text_content = telegram_message_data['text']

            # Compare text content (handle None values)
            text_changed = (db_message.text_content or "") != (new_text_content or "")

            # Compare media
            media_changed = (db_message.media_file_id or "") != (new_media_file_id or "")
            media_type_changed = (db_message.media_type or "") != (new_media_type or "")

            return text_changed or media_changed or media_type_changed

        except Exception as e:
            print(f"Error comparing message: {e}")
            return True  # Assume changed if comparison fails

    async def update_message_from_telegram(self, chat_id: int, telegram_message_data: dict) -> Optional[Message]:
        """
        Update message from Telegram message data
        """
        try:
            telegram_message_id = telegram_message_data.get('message_id')
            if not telegram_message_id:
                return None

            # Get existing message
            db_message = await self.get_message_by_telegram_id(chat_id, telegram_message_id)
            if not db_message:
                return None

            # Extract updated content
            message_type = 'text'
            text_content = None
            media_file_id = None
            media_type = None
            telegram_user_id = None

            # Extract user ID
            if 'from_user' in telegram_message_data and telegram_message_data['from_user']:
                telegram_user_id = telegram_message_data['from_user'].get('id')

            # Determine message type and extract content (same logic as create_message_from_telegram)
            if telegram_message_data.get('photo'):
                message_type = 'photo'
                media_type = 'photo'
                if isinstance(telegram_message_data['photo'], list) and telegram_message_data['photo']:
                    media_file_id = telegram_message_data['photo'][-1].get('file_id')
                text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('video'):
                message_type = 'video'
                media_type = 'video'
                media_file_id = telegram_message_data['video'].get('file_id')
                text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('document'):
                message_type = 'document'
                media_type = 'document'
                media_file_id = telegram_message_data['document'].get('file_id')
                text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('audio'):
                message_type = 'audio'
                media_type = 'audio'
                media_file_id = telegram_message_data['audio'].get('file_id')
                text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('voice'):
                message_type = 'voice'
                media_type = 'voice'
                media_file_id = telegram_message_data['voice'].get('file_id')
                text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('animation'):
                message_type = 'animation'
                media_type = 'animation'
                media_file_id = telegram_message_data['animation'].get('file_id')
                text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('sticker'):
                message_type = 'sticker'
                media_type = 'sticker'
                media_file_id = telegram_message_data['sticker'].get('file_id')
                text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('video_note'):
                message_type = 'video_note'
                media_type = 'video_note'
                media_file_id = telegram_message_data['video_note'].get('file_id')
                text_content = telegram_message_data.get('caption')
            elif telegram_message_data.get('text'):
                message_type = 'text'
                text_content = telegram_message_data['text']
            else:
                message_type = 'service'

            # Update message fields
            db_message.message_type = message_type
            db_message.text_content = text_content
            db_message.media_file_id = media_file_id
            db_message.media_type = media_type
            if telegram_user_id:
                db_message.telegram_user_id = telegram_user_id

            await self.db.commit()
            await self.db.refresh(db_message)
            return db_message

        except Exception as e:
            print(f"Error updating message from telegram data: {e}")
            return None
