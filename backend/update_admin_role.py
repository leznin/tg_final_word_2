#!/usr/bin/env python3
"""
Update existing admin user role
"""
import asyncio
import sys
from pathlib import Path

backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.core.database import engine
from sqlalchemy import text


async def update_admin_role():
    """Update admin user role"""
    async with engine.begin() as conn:
        await conn.execute(
            text("UPDATE admin_users SET role = 'admin' WHERE email = :email"),
            {"email": "maksimleznin30@gmail.com"}
        )
        print("✅ Updated admin user role to 'admin'")


async def main():
    try:
        await update_admin_role()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
