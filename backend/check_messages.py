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

        # Check chats table - all chats
        result = await conn.execute(text('SELECT id, telegram_chat_id, chat_type, title, linked_channel_id, is_active FROM chats ORDER BY id'))
        print("\nAll chats in database:")
        chats = result.fetchall()
        if not chats:
            print("No chats found")
        else:
            for chat in chats:
                print(f"ID: {chat[0]}, Telegram ID: {chat[1]}, Type: {chat[2]}, Title: {chat[3]}, Linked Channel: {chat[4]}, Active: {chat[5]}")

        # Check specific chat ID
        specific_chat_id = -1003062613079
        result = await conn.execute(text(f'SELECT id, telegram_chat_id, chat_type, title, linked_channel_id, is_active FROM chats WHERE telegram_chat_id = {specific_chat_id}'))
        specific_chat = result.fetchone()
        print(f"\nSpecific chat with Telegram ID {specific_chat_id}:")
        if specific_chat:
            print(f"ID: {specific_chat[0]}, Telegram ID: {specific_chat[1]}, Type: {specific_chat[2]}, Title: {specific_chat[3]}, Linked Channel: {specific_chat[4]}, Active: {specific_chat[5]}")
        else:
            print("Chat not found in database")

        # Check active groups/supergroups only (what the API returns)
        result = await conn.execute(text("SELECT id, telegram_chat_id, chat_type, title, linked_channel_id, is_active FROM chats WHERE is_active = 1 AND chat_type IN ('group', 'supergroup') ORDER BY id"))
        print("\nActive groups/supergroups (what API returns):")
        active_groups = result.fetchall()
        if not active_groups:
            print("No active groups/supergroups found")
        else:
            for chat in active_groups:
                print(f"ID: {chat[0]}, Telegram ID: {chat[1]}, Type: {chat[2]}, Title: {chat[3]}, Linked Channel: {chat[4]}, Active: {chat[5]}")

if __name__ == "__main__":
    asyncio.run(check_messages())
