"""
FastAPI application main file with OOP structure for Telegram and Admin panel
"""

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db, get_db, async_session
from app.routers import api_router
from app.telegram.bot import TelegramBot
from app.services.messages import MessageService
from app.services.chat_subscriptions import ChatSubscriptionsService
from app.middleware.security import SecurityMiddleware
from fastapi import Request


# Global telegram bot instance
telegram_bot_instance = None

# Global cleanup task reference
cleanup_task = None

# Global verification task reference
verification_task = None

# Global chat posts task reference
chat_posts_task = None


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


async def scheduled_user_verification():
    """Background task to run scheduled user verifications"""
    while True:
        try:
            # Get database session
            async with async_session() as db:
                from app.services.user_verification_schedule import VerificationScheduleService
                from app.services.user_verification import UserVerificationService
                import app.routers.user_verification as verification_router
                
                schedule_service = VerificationScheduleService(db)
                
                # Get schedules that should run now
                schedules_to_run = await schedule_service.get_schedules_to_run()
                
                if not schedules_to_run:
                    continue
                    
                print(f"Found {len(schedules_to_run)} verification schedule(s) to run")
                
                # Get telegram bot
                telegram_bot = get_telegram_bot()
                if not telegram_bot or not telegram_bot.is_running:
                    print("Telegram bot is not available for scheduled verification")
                    continue
                
                # Run each schedule
                for schedule in schedules_to_run:
                    try:
                        print(f"Running verification schedule {schedule.id}")
                        
                        # Use global verification service instance for progress tracking
                        # This allows the /status endpoint to show real-time progress
                        if verification_router._verification_service_instance is None or \
                           not verification_router._verification_service_instance.is_running:
                            verification_router._verification_service_instance = UserVerificationService(telegram_bot.bot, db)
                        
                        verification_service = verification_router._verification_service_instance
                        
                        # Run verification
                        result = await verification_service.verify_all_active_users(
                            chat_id=schedule.chat_id,
                            auto_update=schedule.auto_update,
                            delay_between_requests=0.5
                        )
                        
                        print(f"Verification schedule {schedule.id} completed: "
                              f"{result.total_checked} checked, "
                              f"{result.total_updated} updated, "
                              f"{result.total_errors} errors")
                        
                        # Update last run timestamp
                        from datetime import datetime
                        await schedule_service.update_last_run(
                            schedule.id,
                            datetime.now()  # Use local time instead of UTC
                        )
                        
                    except Exception as e:
                        print(f"Error running verification schedule {schedule.id}: {e}")
                        
        except Exception as e:
            print(f"Error in scheduled verification task: {e}")
        
        # Wait 60 seconds before next check
        await asyncio.sleep(60)


async def process_chat_posts_scheduled_actions():
    """Background task to process scheduled chat post actions (unpin/delete)"""
    while True:
        try:
            # Get database session
            async with async_session() as db:
                from app.services.chat_posts import ChatPostService
                
                # Get telegram bot
                telegram_bot = get_telegram_bot()
                if not telegram_bot or not telegram_bot.is_running:
                    print("Telegram bot is not available for chat posts processing")
                    await asyncio.sleep(60)
                    continue
                
                # Create service and process scheduled actions
                chat_post_service = ChatPostService(db, telegram_bot.bot)
                await chat_post_service.process_scheduled_actions()
                
        except Exception as e:
            print(f"Error in chat posts scheduled actions task: {e}")
        
        # Wait 60 seconds before next check
        await asyncio.sleep(60)


async def start_verification_task():
    """Start the background verification task"""
    global verification_task
    verification_task = asyncio.create_task(scheduled_user_verification())
    print("Started scheduled user verification task")


async def stop_verification_task():
    """Stop the background verification task"""
    global verification_task
    if verification_task:
        verification_task.cancel()
        try:
            await verification_task
        except asyncio.CancelledError:
            pass
        print("Stopped scheduled user verification task")


async def start_chat_posts_task():
    """Start the background chat posts processing task"""
    global chat_posts_task
    chat_posts_task = asyncio.create_task(process_chat_posts_scheduled_actions())
    print("Started chat posts scheduled actions task")


async def stop_chat_posts_task():
    """Stop the background chat posts processing task"""
    global chat_posts_task
    if chat_posts_task:
        chat_posts_task.cancel()
        try:
            await chat_posts_task
        except asyncio.CancelledError:
            pass
        print("Stopped chat posts scheduled actions task")


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
    
    # Start background verification task
    await start_verification_task()
    
    # Start background chat posts task
    await start_chat_posts_task()

    yield
    # Shutdown
    await stop_cleanup_task()
    await stop_verification_task()
    await stop_chat_posts_task()
    await bot_instance.stop()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    # Disable docs in production for security
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware
app.add_middleware(SecurityMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount frontend files for mini app
from fastapi.responses import FileResponse
import os

# Mount frontend assets and html files
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    # Mount assets folder
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="frontend-assets")
    # Mount dist for direct access to .html files
    app.mount("/dist", StaticFiles(directory=frontend_dist, html=True), name="frontend-dist")

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/mini-app")
async def mini_app():
    """Serve mini app HTML file"""
    frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
    mini_app_path = os.path.join(frontend_dist, "mini-app.html")

    if os.path.exists(mini_app_path):
        return FileResponse(mini_app_path, media_type="text/html")
    else:
        return {"error": "Mini app not found"}


@app.get("/mini-app.html")
async def mini_app_html():
    """Serve mini app HTML file directly"""
    frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
    mini_app_path = os.path.join(frontend_dist, "mini-app.html")

    if os.path.exists(mini_app_path):
        return FileResponse(mini_app_path, media_type="text/html")
    else:
        return {"error": "Mini app not found"}


@app.get("/mini-app/user-search")
async def mini_app_user_search():
    """Serve mini app HTML file for user search route"""
    frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
    mini_app_path = os.path.join(frontend_dist, "mini-app.html")

    if os.path.exists(mini_app_path):
        return FileResponse(mini_app_path, media_type="text/html")
    else:
        return {"error": "Mini app not found"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to FastAPI Telegram Admin API",
        "version": settings.VERSION,
        "docs": "/docs"
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


# Admin panel routes - serve index.html for admin panel routes
@app.get("/login")
async def serve_admin_login():
    """Serve admin panel for /login"""
    frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
    index_path = os.path.join(frontend_dist, "index.html")
    
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    else:
        return {"error": "Admin panel not found"}


@app.get("/dashboard{full_path:path}")
async def serve_admin_dashboard(full_path: str):
    """Serve admin panel for /dashboard/*"""
    frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
    index_path = os.path.join(frontend_dist, "index.html")
    
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    else:
        return {"error": "Admin panel not found"}
