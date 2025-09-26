#!/usr/bin/env python3
"""
Script to check database contents
"""

import asyncio
from app.core.database import engine
from sqlalchemy import text

async def check_database():
    """Check database contents"""
    async with engine.begin() as conn:
        # Check users table
        result = await conn.execute(text('SELECT id, telegram_id, username, first_name, last_name FROM users LIMIT 10'))
        print("Users in database:")
        users = result.fetchall()
        if not users:
            print("No users found")
        else:
            for user in users:
                print(f"ID: {user[0]}, Telegram ID: {user[1]}, Username: {user[2]}, First Name: {user[3]}, Last Name: {user[4]}")

        # Check for duplicate usernames
        result = await conn.execute(text('SELECT username, COUNT(*) as count FROM users GROUP BY username HAVING count > 1'))
        print("\nDuplicate usernames:")
        duplicates = result.fetchall()
        if not duplicates:
            print("No duplicate usernames found")
        else:
            for dup in duplicates:
                print(f"Username: {dup[0]}, Count: {dup[1]}")

        # Check table structure using MySQL syntax
        result = await conn.execute(text("DESCRIBE users"))
        print("\nUsers table structure:")
        for row in result:
            print(f"Field: {row[0]}, Type: {row[1]}, Null: {row[2]}, Key: {row[3]}, Default: {row[4]}, Extra: {row[5]}")

if __name__ == "__main__":
    asyncio.run(check_database())
