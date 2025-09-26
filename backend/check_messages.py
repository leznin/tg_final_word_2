#!/usr/bin/env python3
"""
Script to check messages in database
"""

import asyncio
from app.core.database import engine
from sqlalchemy import text

async def check_messages():
    """Check messages contents"""
    async with engine.begin() as conn:
        # Check messages table
        result = await conn.execute(text('SELECT id, chat_id, telegram_message_id, telegram_user_id, message_type, text_content, media_file_id, created_at FROM messages LIMIT 20'))
        print("Messages in database:")
        messages = result.fetchall()
        if not messages:
            print("No messages found")
        else:
            for msg in messages:
                print(f"ID: {msg[0]}, Chat: {msg[1]}, Telegram Msg ID: {msg[2]}, User: {msg[3]}, Type: {msg[4]}, Text: {msg[5][:50] if msg[5] else None}, Media: {msg[6]}, Created: {msg[7]}")

        # Check chats table
        result = await conn.execute(text('SELECT id, telegram_chat_id, chat_type, title, linked_channel_id FROM chats LIMIT 10'))
        print("\nChats in database:")
        chats = result.fetchall()
        if not chats:
            print("No chats found")
        else:
            for chat in chats:
                print(f"ID: {chat[0]}, Telegram ID: {chat[1]}, Type: {chat[2]}, Title: {chat[3]}, Linked Channel: {chat[4]}")

if __name__ == "__main__":
    asyncio.run(check_messages())
