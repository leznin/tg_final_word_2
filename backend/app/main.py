"""
FastAPI application main file with OOP structure for Telegram and Admin panel
"""

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db, get_db, async_session
from app.routers import api_router
from app.admin.routes import admin_router
from app.telegram.bot import TelegramBot
from app.services.messages import MessageService
from fastapi import Request


# Global telegram bot instance
telegram_bot_instance = None

# Global cleanup task reference
cleanup_task = None


def set_telegram_bot(bot_instance):
    """Set telegram bot instance"""
    global telegram_bot_instance
    telegram_bot_instance = bot_instance


def get_telegram_bot():
    """Get telegram bot instance"""
    return telegram_bot_instance


async def cleanup_old_messages():
    """Background task to clean up old messages"""
    while True:
        try:
            # Get database session
            async with async_session() as db:
                message_service = MessageService(db)
                deleted_count = await message_service.delete_old_messages(settings.MESSAGE_RETENTION_HOURS)
                if deleted_count > 0:
                    print(f"Cleaned up {deleted_count} messages older than {settings.MESSAGE_RETENTION_HOURS} hours")
        except Exception as e:
            print(f"Error during message cleanup: {e}")

        # Wait for next cleanup cycle
        await asyncio.sleep(settings.CLEANUP_INTERVAL_MINUTES * 60)


async def start_cleanup_task():
    """Start the background cleanup task"""
    global cleanup_task
    cleanup_task = asyncio.create_task(cleanup_old_messages())
    print(f"Started message cleanup task (every {settings.CLEANUP_INTERVAL_MINUTES} minutes)")


async def stop_cleanup_task():
    """Stop the background cleanup task"""
    global cleanup_task
    if cleanup_task:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
        print("Stopped message cleanup task")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await init_db()
    bot_instance = TelegramBot()
    await bot_instance.start()

    # Set bot instance for webhook router
    set_telegram_bot(bot_instance)

    # Start background cleanup task
    await start_cleanup_task()

    yield
    # Shutdown
    await stop_cleanup_task()
    await bot_instance.stop()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix="/admin")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to FastAPI Telegram Admin API",
        "version": settings.VERSION,
        "docs": "/docs",
        "admin": "/admin"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook"""
    bot = get_telegram_bot()
    if bot is None:
        return {"status": "bot not initialized"}

    try:
        # Get webhook data
        webhook_data = await request.json()

        # Process webhook through aiogram bot
        await bot.process_webhook(webhook_data)

        return {"status": "processed"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/telegram/webhook")
async def telegram_webhook_legacy(request: Request):
    """Handle Telegram webhook (legacy endpoint for backward compatibility)"""
    # Forward to the main webhook handler
    return await telegram_webhook(request)
