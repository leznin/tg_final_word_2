#!/usr/bin/env python3
"""
Create user_verification_schedule table manually
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine
from sqlalchemy import text


async def create_verification_schedule_table():
    """Create user_verification_schedule table"""
    try:
        async with engine.connect() as conn:
            # Check if table already exists
            result = await conn.execute(text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = DATABASE() AND table_name = 'user_verification_schedule'
            """))

            if result.fetchone():
                print("✅ user_verification_schedule table already exists")
                return

            # Create the table
            await conn.execute(text("""
                CREATE TABLE user_verification_schedule (
                    id INT NOT NULL AUTO_INCREMENT,
                    enabled BOOLEAN NOT NULL DEFAULT FALSE,
                    schedule_time TIME NOT NULL,
                    interval_hours INT NOT NULL DEFAULT 24,
                    auto_update BOOLEAN NOT NULL DEFAULT TRUE,
                    chat_id INT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    last_run_at DATETIME NULL,
                    next_run_at DATETIME NULL,
                    PRIMARY KEY (id),
                    INDEX ix_user_verification_schedule_id (id),
                    FOREIGN KEY (chat_id) REFERENCES chats(id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))

            await conn.commit()
            print("✅ Successfully created user_verification_schedule table")

    except Exception as e:
        print(f"❌ Error creating table: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(create_verification_schedule_table())
