#!/usr/bin/env python3
"""
Script to apply manual database migrations
"""
import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.core.database import engine
from sqlalchemy import text


async def apply_migrations():
    """Apply manual migrations"""
    async with engine.begin() as conn:
        try:
            # Check if role column exists
            result = await conn.execute(
                text("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'admin_users' AND COLUMN_NAME = 'role'
                """)
            )
            if result.fetchone():
                print("✅ Role column already exists in admin_users table")
            else:
                # Add role column
                await conn.execute(
                    text("ALTER TABLE admin_users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'admin'")
                )
                print("✅ Added role column to admin_users table")
            
            # Check if manager_chat_access table exists
            result = await conn.execute(
                text("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = 'manager_chat_access'
                """)
            )
            if result.fetchone():
                print("✅ manager_chat_access table already exists")
            else:
                # Create manager_chat_access table
                await conn.execute(
                    text("""
                        CREATE TABLE manager_chat_access (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            admin_user_id INT NOT NULL,
                            chat_id INT NOT NULL,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                            FOREIGN KEY (admin_user_id) REFERENCES admin_users(id) ON DELETE CASCADE,
                            FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
                            UNIQUE KEY uix_manager_chat (admin_user_id, chat_id),
                            INDEX ix_manager_chat_access_admin_user_id (admin_user_id),
                            INDEX ix_manager_chat_access_chat_id (chat_id)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    """)
                )
                print("✅ Created manager_chat_access table")
            
            print("\n✅ All migrations applied successfully!")
            
        except Exception as e:
            print(f"❌ Error applying migrations: {e}")
            return 1
    
    return 0


async def main():
    """Main function"""
    try:
        result = await apply_migrations()
        return result
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        await engine.dispose()


if __name__ == "__main__":
    exit(asyncio.run(main()))
