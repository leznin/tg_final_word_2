"""
Database initialization and connection management
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import inspect
from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


# Create async engine with optimized connection pool for high concurrency
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # SQL logging disabled for production
    future=True,
    # Connection pool settings for high concurrency (bot in many chats)
    pool_size=20,  # Maximum number of connections in the pool
    max_overflow=30,  # Maximum number of connections that can be created beyond pool_size
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Import all models to register them with Base.metadata
# This import must happen after engine creation to avoid circular imports
from app.models.users import User
from app.models.chats import Chat
from app.models.chat_members import ChatMember
from app.models.messages import Message
from app.models.auth_attempts import AuthAttempt
from app.models.chat_moderators import ChatModerator
from app.models.openrouter import OpenRouterSettings
from app.models.subscription_prices import SubscriptionPrice
from app.models.chat_subscriptions import ChatSubscription

# Import TelegramUser after Base is created to avoid circular import
from app.models.telegram_users import TelegramUser

# Create async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Initialize database - check and create missing tables"""
    async with engine.begin() as conn:
        # Get all table names from metadata
        all_tables = list(Base.metadata.tables.keys())

        # Check which tables already exist
        def check_existing_tables(sync_conn):
            inspector = inspect(sync_conn)
            existing_tables = inspector.get_table_names()
            return existing_tables

        existing_tables = await conn.run_sync(check_existing_tables)

        # Find missing tables
        missing_tables = [table for table in all_tables if table not in existing_tables]

        if missing_tables:
            # Create only missing tables
            for table_name in missing_tables:
                table = Base.metadata.tables[table_name]
                await conn.run_sync(table.create, conn)


async def get_db() -> AsyncSession:
    """Dependency for getting database session"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
