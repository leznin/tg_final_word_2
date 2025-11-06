"""
Quick script to apply the reply_markup migration
"""
import asyncio
import sys
from sqlalchemy import text
from app.core.database import async_session

async def apply_migration():
    """Apply the reply_markup migration directly"""
    async with async_session() as session:
        try:
            # Add the reply_markup column
            await session.execute(text(
                "ALTER TABLE chat_posts ADD COLUMN reply_markup JSON NULL"
            ))
            await session.commit()
            print("✅ Successfully added reply_markup column to chat_posts table")
            
            # Update alembic version
            await session.execute(text(
                "UPDATE alembic_version SET version_num = 'c1feaeec13d2'"
            ))
            await session.commit()
            print("✅ Updated alembic version to c1feaeec13d2")
            
        except Exception as e:
            await session.rollback()
            if "Duplicate column name" in str(e):
                print("⚠️  Column already exists, updating alembic version only")
                await session.execute(text(
                    "UPDATE alembic_version SET version_num = 'c1feaeec13d2'"
                ))
                await session.commit()
                print("✅ Updated alembic version to c1feaeec13d2")
            else:
                print(f"❌ Error: {e}")
                sys.exit(1)

if __name__ == "__main__":
    asyncio.run(apply_migration())
