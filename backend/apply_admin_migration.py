#!/usr/bin/env python3
"""
Script to apply the admin_users migration
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.core.database import engine, Base
from app.models.admin_users import AdminUser
from passlib.context import CryptContext
from sqlalchemy import text


async def create_admin_users_table():
    """Create admin_users table and insert default admin"""
    async with engine.begin() as conn:
        # Check if table already exists
        result = await conn.execute(text("SHOW TABLES LIKE 'admin_users'"))
        if result.fetchone():
            print("Table admin_users already exists")
            return
        
        # Create the table
        await conn.run_sync(AdminUser.__table__.create)
        print("Created admin_users table")
        
        # Hash the password
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash("696578As!@#$")
        
        # Insert default admin user
        await conn.execute(
            text(
                "INSERT INTO admin_users (email, password_hash, is_active) "
                "VALUES (:email, :password_hash, :is_active)"
            ),
            {
                "email": "Maksimleznin30@gmail.com",
                "password_hash": hashed_password,
                "is_active": True
            }
        )
        print(f"Created default admin user: Maksimleznin30@gmail.com")


async def main():
    """Main function"""
    try:
        await create_admin_users_table()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        await engine.dispose()
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))