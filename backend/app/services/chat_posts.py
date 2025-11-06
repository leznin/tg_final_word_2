"""
Chat Posts Service
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional, Tuple
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

from app.models.chat_posts import ChatPost
from app.models.chats import Chat
from app.schemas.chat_posts import ChatPostCreate, ChatPostUpdate, ChatPostResponse
from aiogram import Bot
from aiogram.types import InputFile, FSInputFile, URLInputFile, BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
import aiohttp
import mimetypes


class ChatPostService:
    """Service for managing chat posts"""

    def __init__(self, db: AsyncSession, bot: Bot = None):
        self.db = db
        self.bot = bot

    async def get_chat_by_id(self, chat_id: int) -> Optional[Chat]:
        """Get chat by internal ID"""
        result = await self.db.execute(
            select(Chat).where(Chat.id == chat_id)
        )
        return result.scalar_one_or_none()

    async def create_post(self, post_data: ChatPostCreate, created_by_user_id: int) -> ChatPost:
        """Create a post (send immediately or schedule for later)"""
        
        # Get chat info
        chat = await self.get_chat_by_id(post_data.chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        # Determine if we should send immediately or schedule
        send_now = post_data.send_immediately and not post_data.scheduled_send_at
        
        if send_now:
            # Send immediately to Telegram
            return await self._send_post_now(post_data, chat, created_by_user_id)
        else:
            # Schedule for later
            return await self._schedule_post(post_data, chat, created_by_user_id)

    async def _schedule_post(self, post_data: ChatPostCreate, chat: Chat, created_by_user_id: int) -> ChatPost:
        """Schedule a post for later sending"""
        
        scheduled_time = post_data.scheduled_send_at
        if not scheduled_time:
            # If no time specified, schedule for 1 hour from now as default
            scheduled_time = datetime.now(timezone.utc) + timedelta(hours=1)
        else:
            # Convert to UTC if timezone-aware, or assume UTC if naive
            if scheduled_time.tzinfo is None:
                # If naive datetime, assume it's UTC and make it timezone-aware
                scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
            else:
                # Convert to UTC to ensure consistent storage
                scheduled_time = scheduled_time.astimezone(timezone.utc)
        
        # Validate scheduled time is in the future (compare in UTC)
        current_time = datetime.now(timezone.utc)
        if scheduled_time <= current_time:
            raise HTTPException(status_code=400, detail="Scheduled time must be in the future")
        
        # Validate button URLs if reply_markup is provided
        if post_data.reply_markup:
            for row in post_data.reply_markup.inline_keyboard:
                for button in row.buttons:
                    if button.url:
                        url_lower = button.url.lower()
                        if 'localhost' in url_lower or '127.0.0.1' in url_lower:
                            raise HTTPException(
                                status_code=400, 
                                detail=f"Invalid button URL '{button.url}': Telegram does not accept localhost URLs. Please use a public URL (e.g., ngrok tunnel or production domain)."
                            )
        
        # Calculate scheduled times for pin/delete if needed
        scheduled_unpin_at = None
        scheduled_delete_at = None
        
        if post_data.pin_duration_minutes and post_data.pin_message:
            # Calculate unpin time from scheduled send time
            scheduled_unpin_at = scheduled_time + timedelta(minutes=post_data.pin_duration_minutes)
        
        if post_data.delete_after_minutes:
            # Calculate delete time from scheduled send time
            scheduled_delete_at = scheduled_time + timedelta(minutes=post_data.delete_after_minutes)
        
        # Convert reply_markup to dict for JSON storage
        reply_markup_dict = None
        if post_data.reply_markup:
            reply_markup_dict = post_data.reply_markup.model_dump()
        
        # Create database record (not sent yet)
        db_post = ChatPost(
            chat_id=post_data.chat_id,
            telegram_message_id=None,  # Will be set when sent
            scheduled_send_at=scheduled_time,
            is_sent=False,
            sent_at=None,
            content_text=post_data.content_text,
            media_type=post_data.media.type if post_data.media else None,
            media_file_id=None,  # Will be set when sent
            media_url=post_data.media.url if post_data.media else None,
            media_filename=post_data.media.filename if post_data.media else None,
            is_pinned=False,  # Will be set when sent
            pin_duration_minutes=post_data.pin_duration_minutes if post_data.pin_message else None,
            scheduled_unpin_at=scheduled_unpin_at,
            delete_after_minutes=post_data.delete_after_minutes,
            scheduled_delete_at=scheduled_delete_at,
            reply_markup=reply_markup_dict,
            created_by_user_id=created_by_user_id,
            is_deleted=False
        )
        
        self.db.add(db_post)
        await self.db.commit()
        await self.db.refresh(db_post)
        
        return db_post

    async def _send_post_now(self, post_data: ChatPostCreate, chat: Chat, created_by_user_id: int) -> ChatPost:
        """Send a post to Telegram immediately"""
        if not self.bot:
            raise HTTPException(status_code=500, detail="Telegram bot not available")

        telegram_chat_id = chat.telegram_chat_id

        try:
            # Prepare keyboard markup if provided
            reply_markup = None
            if post_data.reply_markup:
                keyboard = []
                for row in post_data.reply_markup.inline_keyboard:
                    keyboard_row = []
                    for button in row.buttons:
                        # Skip invalid buttons
                        if not button.url and not button.callback_data:
                            print(f"Warning: Skipping button '{button.text}' - inline keyboard buttons must have url or callback_data")
                            continue
                        if button.url and button.callback_data:
                            print(f"Warning: Skipping button '{button.text}' - inline keyboard buttons cannot have both url and callback_data")
                            continue
                        
                        # Validate button URL - Telegram doesn't accept localhost URLs
                        if button.url:
                            url_lower = button.url.lower()
                            if 'localhost' in url_lower or '127.0.0.1' in url_lower:
                                raise HTTPException(
                                    status_code=400, 
                                    detail=f"Invalid button URL '{button.url}': Telegram does not accept localhost URLs. Please use a public URL (e.g., ngrok tunnel or production domain)."
                                )

                        # Create button with only defined parameters
                        button_kwargs = {"text": button.text}
                        if button.url:
                            button_kwargs["url"] = button.url
                        if button.callback_data:
                            button_kwargs["callback_data"] = button.callback_data
                        keyboard_row.append(InlineKeyboardButton(**button_kwargs))

                    # Only add non-empty rows
                    if keyboard_row:
                        keyboard.append(keyboard_row)

                # Only create markup if keyboard is not empty
                if keyboard:
                    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

            # Send message to Telegram
            telegram_message = None
            media_type = None
            media_file_id = None
            media_url = None
            media_filename = None

            if post_data.media:
                media_type = post_data.media.type
                media_url = post_data.media.url
                media_filename = post_data.media.filename

                # Prepare media input
                # If file_id is provided, use it (forwarding existing message)
                # Otherwise, use FSInputFile for local files uploaded to server
                media_input = None
                
                if post_data.media.file_id:
                    media_input = post_data.media.file_id
                elif post_data.media.url:
                    # Convert relative URL to absolute file path for local files
                    from pathlib import Path
                    if post_data.media.url.startswith('/static/'):
                        relative_path = post_data.media.url.lstrip('/').replace('static/', '', 1)
                        file_path = Path('static') / relative_path
                        
                        if file_path.exists():
                            media_input = FSInputFile(str(file_path))
                        else:
                            raise HTTPException(status_code=404, detail=f"Media file not found: {post_data.media.url}")
                    else:
                        # External URL - use as is
                        media_input = post_data.media.url

                # Send message with media
                if media_type == 'photo':
                    telegram_message = await self.bot.send_photo(
                        chat_id=telegram_chat_id,
                        photo=media_input,
                        caption=post_data.content_text or "",
                        reply_markup=reply_markup
                    )
                    media_file_id = telegram_message.photo[-1].file_id if telegram_message.photo else None

                elif media_type == 'video':
                    telegram_message = await self.bot.send_video(
                        chat_id=telegram_chat_id,
                        video=media_input,
                        caption=post_data.content_text or "",
                        reply_markup=reply_markup
                    )
                    media_file_id = telegram_message.video.file_id if telegram_message.video else None

                elif media_type == 'document':
                    if isinstance(media_input, FSInputFile):
                        telegram_message = await self.bot.send_document(
                            chat_id=telegram_chat_id,
                            document=FSInputFile(media_input.path, filename=post_data.media.filename or "document"),
                            caption=post_data.content_text or "",
                            reply_markup=reply_markup
                        )
                    else:
                        telegram_message = await self.bot.send_document(
                            chat_id=telegram_chat_id,
                            document=media_input,
                            caption=post_data.content_text or "",
                            filename=post_data.media.filename or "document",
                            reply_markup=reply_markup
                        )
                    media_file_id = telegram_message.document.file_id if telegram_message.document else None
            else:
                # Send text-only message
                if not post_data.content_text:
                    raise HTTPException(status_code=400, detail="Message must have either text or media")
                
                telegram_message = await self.bot.send_message(
                    chat_id=telegram_chat_id,
                    text=post_data.content_text,
                    reply_markup=reply_markup
                )

            if not telegram_message:
                raise HTTPException(status_code=500, detail="Failed to send message to Telegram")

            # Calculate scheduled times
            scheduled_unpin_at = None
            scheduled_delete_at = None

            if post_data.pin_duration_minutes:
                scheduled_unpin_at = datetime.now(timezone.utc) + timedelta(minutes=post_data.pin_duration_minutes)

            if post_data.delete_after_minutes:
                scheduled_delete_at = datetime.now(timezone.utc) + timedelta(minutes=post_data.delete_after_minutes)

            # Create database record
            db_post = ChatPost(
                chat_id=post_data.chat_id,
                telegram_message_id=telegram_message.message_id,
                scheduled_send_at=None,  # Was sent immediately
                is_sent=True,
                sent_at=datetime.now(timezone.utc),
                content_text=post_data.content_text,
                media_type=media_type,
                media_file_id=media_file_id,
                media_url=media_url,
                media_filename=media_filename,
                is_pinned=post_data.pin_message,
                pin_duration_minutes=post_data.pin_duration_minutes,
                scheduled_unpin_at=scheduled_unpin_at,
                delete_after_minutes=post_data.delete_after_minutes,
                scheduled_delete_at=scheduled_delete_at,
                created_by_user_id=created_by_user_id,
                is_deleted=False
            )

            self.db.add(db_post)
            await self.db.commit()
            await self.db.refresh(db_post)

            # Pin message if requested
            if post_data.pin_message:
                try:
                    await self.bot.pin_chat_message(
                        chat_id=telegram_chat_id,
                        message_id=telegram_message.message_id,
                        disable_notification=True
                    )
                except Exception as e:
                    print(f"Failed to pin message: {e}")
                    # Don't fail the whole operation if pinning fails
                    db_post.is_pinned = False
                    await self.db.commit()

            return db_post

        except TelegramForbiddenError:
            raise HTTPException(status_code=403, detail="Bot doesn't have permission to send messages in this chat")
        except TelegramBadRequest as e:
            raise HTTPException(status_code=400, detail=f"Telegram error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create post: {str(e)}")

    async def update_post(self, post_id: int, post_data: ChatPostUpdate) -> ChatPost:
        """Update an existing post (edit message text, scheduling, pinning, keyboard in Telegram)"""
        if not self.bot:
            raise HTTPException(status_code=500, detail="Telegram bot not available")

        # Get post
        result = await self.db.execute(
            select(ChatPost).where(ChatPost.id == post_id, ChatPost.is_deleted == False)
        )
        db_post = result.scalar_one_or_none()

        if not db_post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Get chat info
        chat = await self.get_chat_by_id(db_post.chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        try:
            telegram_chat_id = chat.telegram_chat_id
            
            # Update scheduled send time (only for unsent posts)
            if post_data.scheduled_send_at is not None and not db_post.is_sent:
                scheduled_time = post_data.scheduled_send_at
                
                # Convert to UTC if needed
                if scheduled_time.tzinfo is None:
                    scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
                else:
                    scheduled_time = scheduled_time.astimezone(timezone.utc)
                
                # Validate scheduled time is in the future
                current_time = datetime.now(timezone.utc)
                if scheduled_time <= current_time:
                    raise HTTPException(status_code=400, detail="Scheduled time must be in the future")
                
                db_post.scheduled_send_at = scheduled_time
                
                # Recalculate scheduled_unpin_at and scheduled_delete_at based on new send time
                if db_post.pin_duration_minutes:
                    db_post.scheduled_unpin_at = scheduled_time + timedelta(minutes=db_post.pin_duration_minutes)
                if db_post.delete_after_minutes:
                    db_post.scheduled_delete_at = scheduled_time + timedelta(minutes=db_post.delete_after_minutes)
            
            # For sent posts, update content and/or keyboard in Telegram
            if db_post.is_sent and db_post.telegram_message_id:
                # Prepare keyboard markup if provided
                reply_markup = None
                if post_data.reply_markup is not None:
                    keyboard = []
                    for row in post_data.reply_markup.inline_keyboard:
                        keyboard_row = []
                        for button in row.buttons:
                            # Skip invalid buttons
                            if not button.url and not button.callback_data:
                                continue
                            if button.url and button.callback_data:
                                continue
                            
                            # Validate button URL
                            if button.url:
                                url_lower = button.url.lower()
                                if 'localhost' in url_lower or '127.0.0.1' in url_lower:
                                    raise HTTPException(
                                        status_code=400,
                                        detail=f"Invalid button URL '{button.url}': Telegram does not accept localhost URLs."
                                    )
                            
                            # Create button
                            button_kwargs = {"text": button.text}
                            if button.url:
                                button_kwargs["url"] = button.url
                            if button.callback_data:
                                button_kwargs["callback_data"] = button.callback_data
                            keyboard_row.append(InlineKeyboardButton(**button_kwargs))
                        
                        if keyboard_row:
                            keyboard.append(keyboard_row)
                    
                    if keyboard:
                        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
                
                # Edit message text/caption and/or keyboard
                if post_data.content_text is not None or reply_markup is not None:
                    text_to_use = post_data.content_text if post_data.content_text is not None else db_post.content_text
                    
                    if db_post.media_type:
                        # For messages with media, edit caption
                        await self.bot.edit_message_caption(
                            chat_id=telegram_chat_id,
                            message_id=db_post.telegram_message_id,
                            caption=text_to_use,
                            reply_markup=reply_markup
                        )
                    else:
                        # For text-only messages, edit text
                        await self.bot.edit_message_text(
                            chat_id=telegram_chat_id,
                            message_id=db_post.telegram_message_id,
                            text=text_to_use,
                            reply_markup=reply_markup
                        )
                
                # Update text in database
                if post_data.content_text is not None:
                    db_post.content_text = post_data.content_text
                
                # Update keyboard in database
                if post_data.reply_markup is not None:
                    db_post.reply_markup = post_data.reply_markup.model_dump()
                
                # Handle pinning for sent posts
                if post_data.pin_message is not None:
                    if post_data.pin_message and not db_post.is_pinned:
                        # Pin the message
                        try:
                            await self.bot.pin_chat_message(
                                chat_id=telegram_chat_id,
                                message_id=db_post.telegram_message_id,
                                disable_notification=True
                            )
                            db_post.is_pinned = True
                            
                            # Calculate unpin time if duration specified
                            if post_data.pin_duration_minutes:
                                db_post.pin_duration_minutes = post_data.pin_duration_minutes
                                db_post.scheduled_unpin_at = datetime.now(timezone.utc) + timedelta(minutes=post_data.pin_duration_minutes)
                            else:
                                db_post.pin_duration_minutes = None
                                db_post.scheduled_unpin_at = None
                        except Exception as e:
                            print(f"Failed to pin message: {e}")
                            raise HTTPException(status_code=400, detail=f"Failed to pin message: {str(e)}")
                    
                    elif not post_data.pin_message and db_post.is_pinned:
                        # Unpin the message
                        try:
                            await self.bot.unpin_chat_message(
                                chat_id=telegram_chat_id,
                                message_id=db_post.telegram_message_id
                            )
                            db_post.is_pinned = False
                            db_post.pin_duration_minutes = None
                            db_post.scheduled_unpin_at = None
                        except Exception as e:
                            print(f"Failed to unpin message: {e}")
                            raise HTTPException(status_code=400, detail=f"Failed to unpin message: {str(e)}")
                
                # Update delete schedule for sent posts
                if post_data.delete_after_minutes is not None:
                    if post_data.delete_after_minutes > 0:
                        db_post.delete_after_minutes = post_data.delete_after_minutes
                        # Calculate delete time from now
                        db_post.scheduled_delete_at = datetime.now(timezone.utc) + timedelta(minutes=post_data.delete_after_minutes)
                    else:
                        # Clear delete schedule
                        db_post.delete_after_minutes = None
                        db_post.scheduled_delete_at = None
            
            # For unsent posts, update all fields in database only
            else:
                if post_data.content_text is not None:
                    db_post.content_text = post_data.content_text
                
                if post_data.reply_markup is not None:
                    db_post.reply_markup = post_data.reply_markup.model_dump()
                
                if post_data.pin_message is not None:
                    db_post.pin_duration_minutes = post_data.pin_duration_minutes if post_data.pin_message else None
                    # Unpin time will be calculated when post is sent
                    if db_post.scheduled_send_at and post_data.pin_message and post_data.pin_duration_minutes:
                        db_post.scheduled_unpin_at = db_post.scheduled_send_at + timedelta(minutes=post_data.pin_duration_minutes)
                    else:
                        db_post.scheduled_unpin_at = None
                
                if post_data.delete_after_minutes is not None:
                    if post_data.delete_after_minutes > 0:
                        db_post.delete_after_minutes = post_data.delete_after_minutes
                        # Delete time will be calculated when post is sent
                        if db_post.scheduled_send_at:
                            db_post.scheduled_delete_at = db_post.scheduled_send_at + timedelta(minutes=post_data.delete_after_minutes)
                    else:
                        db_post.delete_after_minutes = None
                        db_post.scheduled_delete_at = None

            db_post.updated_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(db_post)

            return db_post

        except TelegramBadRequest as e:
            raise HTTPException(status_code=400, detail=f"Telegram error: {str(e)}")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update post: {str(e)}")

    async def delete_post(self, post_id: int) -> bool:
        """Delete a post (mark as deleted and delete from Telegram)"""
        if not self.bot:
            raise HTTPException(status_code=500, detail="Telegram bot not available")

        # Get post
        result = await self.db.execute(
            select(ChatPost).where(ChatPost.id == post_id, ChatPost.is_deleted == False)
        )
        db_post = result.scalar_one_or_none()

        if not db_post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Get chat info
        chat = await self.get_chat_by_id(db_post.chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        try:
            # Only try to delete from Telegram if the message was actually sent
            if db_post.telegram_message_id is not None:
                await self.bot.delete_message(
                    chat_id=chat.telegram_chat_id,
                    message_id=db_post.telegram_message_id
                )

            # Mark as deleted in database
            db_post.is_deleted = True
            db_post.updated_at = datetime.now(timezone.utc)
            await self.db.commit()

            return True

        except TelegramBadRequest as e:
            # Message might already be deleted in Telegram
            print(f"Telegram error when deleting: {e}")
            db_post.is_deleted = True
            await self.db.commit()
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete post: {str(e)}")

    async def pin_post(self, post_id: int, pin_duration_minutes: Optional[int] = None) -> ChatPost:
        """Pin a post in the chat"""
        if not self.bot:
            raise HTTPException(status_code=500, detail="Telegram bot not available")

        # Get post
        result = await self.db.execute(
            select(ChatPost).where(ChatPost.id == post_id, ChatPost.is_deleted == False)
        )
        db_post = result.scalar_one_or_none()

        if not db_post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Get chat info
        chat = await self.get_chat_by_id(db_post.chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        try:
            # Pin message in Telegram
            await self.bot.pin_chat_message(
                chat_id=chat.telegram_chat_id,
                message_id=db_post.telegram_message_id,
                disable_notification=True
            )

            # Update database
            db_post.is_pinned = True
            db_post.pin_duration_minutes = pin_duration_minutes
            
            if pin_duration_minutes:
                db_post.scheduled_unpin_at = datetime.now(timezone.utc) + timedelta(minutes=pin_duration_minutes)
            else:
                db_post.scheduled_unpin_at = None

            db_post.updated_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(db_post)

            return db_post

        except TelegramBadRequest as e:
            raise HTTPException(status_code=400, detail=f"Telegram error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to pin post: {str(e)}")

    async def unpin_post(self, post_id: int) -> ChatPost:
        """Unpin a post from the chat"""
        if not self.bot:
            raise HTTPException(status_code=500, detail="Telegram bot not available")

        # Get post
        result = await self.db.execute(
            select(ChatPost).where(ChatPost.id == post_id, ChatPost.is_deleted == False)
        )
        db_post = result.scalar_one_or_none()

        if not db_post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Get chat info
        chat = await self.get_chat_by_id(db_post.chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        try:
            # Unpin message in Telegram
            await self.bot.unpin_chat_message(
                chat_id=chat.telegram_chat_id,
                message_id=db_post.telegram_message_id
            )

            # Update database
            db_post.is_pinned = False
            db_post.scheduled_unpin_at = None
            db_post.updated_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(db_post)

            return db_post

        except TelegramBadRequest as e:
            # Message might not be pinned
            print(f"Telegram error when unpinning: {e}")
            db_post.is_pinned = False
            db_post.scheduled_unpin_at = None
            await self.db.commit()
            await self.db.refresh(db_post)
            return db_post
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to unpin post: {str(e)}")

    async def get_chat_posts(
        self, 
        chat_id: int, 
        page: int = 1, 
        page_size: int = 20,
        include_deleted: bool = False
    ) -> Tuple[List[ChatPost], int]:
        """Get posts for a chat with pagination"""
        offset = (page - 1) * page_size

        # Build query
        query = select(ChatPost).where(ChatPost.chat_id == chat_id)
        
        if not include_deleted:
            query = query.where(ChatPost.is_deleted == False)

        query = query.order_by(ChatPost.created_at.desc())

        # Get total count
        count_query = select(func.count(ChatPost.id)).where(ChatPost.chat_id == chat_id)
        if not include_deleted:
            count_query = count_query.where(ChatPost.is_deleted == False)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = query.offset(offset).limit(page_size)
        result = await self.db.execute(query)
        posts = result.scalars().all()

        return list(posts), total

    async def get_post_by_id(self, post_id: int) -> Optional[ChatPost]:
        """Get a single post by ID"""
        result = await self.db.execute(
            select(ChatPost).where(ChatPost.id == post_id)
        )
        return result.scalar_one_or_none()

    async def process_scheduled_actions(self):
        """Process scheduled unpin, delete, and send actions"""
        if not self.bot:
            return

        now = datetime.now(timezone.utc)
        # Debug logging enabled:
        print(f"[ChatPosts] Checking scheduled actions at {now}")
        
        # Debug: Check all unsent posts
        debug_query = select(ChatPost).where(
            and_(
                ChatPost.is_sent == False,
                ChatPost.is_deleted == False
            )
        )
        debug_result = await self.db.execute(debug_query)
        all_unsent = debug_result.scalars().all()
        if all_unsent:
            print(f"[ChatPosts] Total unsent posts in DB: {len(all_unsent)}")
            for post in all_unsent:
                print(f"[ChatPosts] Unsent post {post.id}: scheduled_send_at={post.scheduled_send_at}, is_sent={post.is_sent}, is_deleted={post.is_deleted}")

        # Process scheduled sends
        # First, get all unsent scheduled posts
        send_query = select(ChatPost).where(
            and_(
                ChatPost.is_sent == False,
                ChatPost.scheduled_send_at.isnot(None),
                ChatPost.is_deleted == False
            )
        )
        send_result = await self.db.execute(send_query)
        all_scheduled = send_result.scalars().all()
        
        # Filter posts that should be sent (handling timezone-naive datetimes)
        posts_to_send = []
        for post in all_scheduled:
            scheduled_time = post.scheduled_send_at
            # Make timezone-aware if needed
            if scheduled_time.tzinfo is None:
                scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
            
            if scheduled_time <= now:
                posts_to_send.append(post)
        
        if posts_to_send:
            print(f"[ChatPosts] Found {len(posts_to_send)} scheduled post(s) to send")
            for post in posts_to_send:
                scheduled_time = post.scheduled_send_at
                if scheduled_time.tzinfo is None:
                    scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
                print(f"[ChatPosts] Post {post.id}: scheduled for {scheduled_time}, is_sent={post.is_sent}, is_deleted={post.is_deleted}")
        else:
            print(f"[ChatPosts] No scheduled posts found to send")

        for post in posts_to_send:
            try:
                await self._send_scheduled_post(post)
                print(f"Sent scheduled post {post.id}")
            except Exception as e:
                print(f"Error sending scheduled post {post.id}: {e}")
                # Mark the post as failed to prevent retry loops
                post.is_deleted = True  # Mark as deleted so it won't be retried
                await self.db.commit()
                print(f"Failed to send scheduled post {post.id}: {e}")

        # Process scheduled unpins
        unpin_query = select(ChatPost).where(
            and_(
                ChatPost.is_pinned == True,
                ChatPost.scheduled_unpin_at <= now,
                ChatPost.scheduled_unpin_at.isnot(None),
                ChatPost.is_deleted == False
            )
        )
        unpin_result = await self.db.execute(unpin_query)
        posts_to_unpin = unpin_result.scalars().all()

        if posts_to_unpin:
            print(f"Found {len(posts_to_unpin)} post(s) to unpin")

        for post in posts_to_unpin:
            try:
                print(f"Unpinning post {post.id} (scheduled for {post.scheduled_unpin_at}, now is {now})")
                await self.unpin_post(post.id)
                print(f"Auto-unpinned post {post.id}")
            except Exception as e:
                print(f"Failed to auto-unpin post {post.id}: {e}")

        # Process scheduled deletes
        delete_query = select(ChatPost).where(
            and_(
                ChatPost.scheduled_delete_at <= now,
                ChatPost.scheduled_delete_at.isnot(None),
                ChatPost.is_deleted == False
            )
        )
        delete_result = await self.db.execute(delete_query)
        posts_to_delete = delete_result.scalars().all()

        for post in posts_to_delete:
            try:
                await self.delete_post(post.id)
                print(f"Auto-deleted post {post.id}")
            except Exception as e:
                print(f"Failed to auto-delete post {post.id}: {e}")

    async def _send_scheduled_post(self, post: ChatPost):
        """Send a previously scheduled post to Telegram"""
        if not self.bot:
            raise HTTPException(status_code=500, detail="Telegram bot not available")

        # Get chat info
        chat = await self.get_chat_by_id(post.chat_id)
        if not chat:
            print(f"Chat {post.chat_id} not found for scheduled post {post.id}")
            return

        telegram_chat_id = chat.telegram_chat_id

        try:
            # Prepare keyboard markup if stored
            reply_markup = None
            if post.reply_markup:
                keyboard = []
                for row in post.reply_markup.get('inline_keyboard', []):
                    keyboard_row = []
                    for button in row.get('buttons', []):
                        # Skip invalid buttons
                        if not button.get('url') and not button.get('callback_data'):
                            continue
                        if button.get('url') and button.get('callback_data'):
                            continue
                        
                        # Validate button URL - Telegram doesn't accept localhost URLs
                        if button.get('url'):
                            url_lower = button['url'].lower()
                            if 'localhost' in url_lower or '127.0.0.1' in url_lower:
                                raise ValueError(
                                    f"Invalid button URL '{button['url']}': Telegram does not accept localhost URLs. Please use a public URL."
                                )

                        # Create button with only defined parameters
                        button_kwargs = {"text": button.get('text', '')}
                        if button.get('url'):
                            button_kwargs["url"] = button['url']
                        if button.get('callback_data'):
                            button_kwargs["callback_data"] = button['callback_data']
                        keyboard_row.append(InlineKeyboardButton(**button_kwargs))

                    # Only add non-empty rows
                    if keyboard_row:
                        keyboard.append(keyboard_row)

                # Only create markup if keyboard is not empty
                if keyboard:
                    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

            # Send message to Telegram
            telegram_message = None
            media_file_id = None

            if post.media_type and post.media_url:
                # For scheduled posts, media is stored locally on server
                # Convert relative URL to absolute file path
                import os
                from pathlib import Path
                
                # Remove leading slash and 'static/' from URL
                relative_path = post.media_url.lstrip('/').replace('static/', '', 1)
                file_path = Path('static') / relative_path
                
                if not file_path.exists():
                    print(f"Media file not found: {file_path}")
                    raise HTTPException(status_code=404, detail=f"Media file not found: {post.media_url}")
                
                # Send message with media from local file
                if post.media_type == 'photo':
                    telegram_message = await self.bot.send_photo(
                        chat_id=telegram_chat_id,
                        photo=FSInputFile(str(file_path)),
                        caption=post.content_text or "",
                        reply_markup=reply_markup
                    )
                    media_file_id = telegram_message.photo[-1].file_id if telegram_message.photo else None

                elif post.media_type == 'video':
                    telegram_message = await self.bot.send_video(
                        chat_id=telegram_chat_id,
                        video=FSInputFile(str(file_path)),
                        caption=post.content_text or "",
                        reply_markup=reply_markup
                    )
                    media_file_id = telegram_message.video.file_id if telegram_message.video else None

                elif post.media_type == 'document':
                    telegram_message = await self.bot.send_document(
                        chat_id=telegram_chat_id,
                        document=FSInputFile(str(file_path), filename=post.media_filename or "document"),
                        caption=post.content_text or "",
                        reply_markup=reply_markup
                    )
                    media_file_id = telegram_message.document.file_id if telegram_message.document else None
            else:
                # Send text-only message
                if not post.content_text:
                    print(f"Post {post.id} has no content to send")
                    return
                
                telegram_message = await self.bot.send_message(
                    chat_id=telegram_chat_id,
                    text=post.content_text,
                    reply_markup=reply_markup
                )

            if not telegram_message:
                print(f"Failed to send scheduled post {post.id}")
                return

            # Update post as sent
            post.telegram_message_id = telegram_message.message_id
            post.is_sent = True
            post.sent_at = datetime.now(timezone.utc)
            post.media_file_id = media_file_id

            # Pin message if requested
            if post.pin_duration_minutes is not None or post.scheduled_unpin_at:
                try:
                    await self.bot.pin_chat_message(
                        chat_id=telegram_chat_id,
                        message_id=telegram_message.message_id,
                        disable_notification=True
                    )
                    post.is_pinned = True
                    
                    # Recalculate unpin time from actual send time if pin_duration_minutes is set
                    if post.pin_duration_minutes is not None:
                        post.scheduled_unpin_at = datetime.now(timezone.utc) + timedelta(minutes=post.pin_duration_minutes)
                        
                except Exception as e:
                    print(f"Failed to pin scheduled post {post.id}: {e}")

            await self.db.commit()

        except Exception as e:
            print(f"Error sending scheduled post {post.id}: {e}")
            raise
