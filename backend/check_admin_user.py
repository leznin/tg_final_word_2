#!/usr/bin/env python3
"""
Script to check if default admin user exists
"""
import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.core.database import engine
from sqlalchemy import text


async def check_admin_user():
    """Check if default admin user exists"""
    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT email, is_active FROM admin_users WHERE email = :email"),
            {"email": "maksimleznin30@gmail.com"}
        )
        user = result.fetchone()
        
        if user:
            print(f"✅ Default admin user found: {user[0]} (active: {user[1]})")
        else:
            print("❌ Default admin user not found")
            # Create it
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            # Bcrypt only accepts up to 72 bytes
            password = "696578As!@#$"[:72]
            hashed_password = pwd_context.hash(password)
            
            await conn.execute(
                text(
                    "INSERT INTO admin_users (email, password_hash, is_active, role) "
                    "VALUES (:email, :password_hash, :is_active, :role)"
                ),
                {
                    "email": "maksimleznin30@gmail.com",
                    "password_hash": hashed_password,
                    "is_active": True,
                    "role": "admin"
                }
            )
            print("✅ Created default admin user: maksimleznin30@gmail.com")


async def main():
    """Main function"""
    try:
        await check_admin_user()
        print("Check completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        await engine.dispose()
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))