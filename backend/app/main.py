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
from app.services.chat_subscriptions import ChatSubscriptionsService
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
    """Background task to clean up old messages and expired subscriptions"""
    while True:
        try:
            # Get database session
            async with async_session() as db:
                # Clean up old messages
                message_service = MessageService(db)
                deleted_count = await message_service.delete_old_messages(settings.MESSAGE_RETENTION_HOURS)
                if deleted_count > 0:
                    print(f"Cleaned up {deleted_count} messages older than {settings.MESSAGE_RETENTION_HOURS} hours")

                # Check for expired subscriptions and disable AI content check
                subscriptions_service = ChatSubscriptionsService(db)
                chats_service = await get_chats_service(db)
                expired_subscriptions = await subscriptions_service.get_expiring_subscriptions(days_ahead=0)

                disabled_count = 0
                for subscription in expired_subscriptions:
                    chat = await chats_service.get_chat(subscription.chat_id)
                    if chat and chat.ai_content_check_enabled:
                        print(f"Disabling AI content check for chat {chat.id} due to expired subscription")
                        chat.ai_content_check_enabled = False
                        disabled_count += 1

                if disabled_count > 0:
                    await db.commit()
                    print(f"Disabled AI content check for {disabled_count} chats with expired subscriptions")

        except Exception as e:
            print(f"Error during cleanup tasks: {e}")

        # Wait for next cleanup cycle
        await asyncio.sleep(settings.CLEANUP_INTERVAL_MINUTES * 60)


async def get_chats_service(db):
    """Helper function to get ChatService instance"""
    from app.services.chats import ChatService
    return ChatService(db)


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
        print("❌ Bot not initialized")
        return {"status": "bot not initialized"}

    try:
        # Get webhook data
        webhook_data = await request.json()

        # Process webhook through aiogram bot
        await bot.process_webhook(webhook_data)

        return {"status": "processed"}

    except Exception as e:
        print(f"❌ WEBHOOK ERROR: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/telegram/webhook")
async def telegram_webhook_legacy(request: Request):
    """Handle Telegram webhook (legacy endpoint for backward compatibility)"""
    # Forward to the main webhook handler
    return await telegram_webhook(request)
