#!/usr/bin/env python3
"""
Apply database migrations manually
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine
from sqlalchemy import text


async def apply_migration():
    """Apply the account_creation_date migration manually"""
    try:
        async with engine.connect() as conn:
            # Check if column already exists
            result = await conn.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'chat_members' AND column_name = 'account_creation_date'
            """))

            if result.fetchone():
                print("account_creation_date column already exists")
                return

            # Add the column
            await conn.execute(text("""
                ALTER TABLE chat_members ADD COLUMN account_creation_date DATETIME
            """))

            await conn.commit()
            print("Successfully added account_creation_date column")

    except Exception as e:
        print(f"Error applying migration: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(apply_migration())
