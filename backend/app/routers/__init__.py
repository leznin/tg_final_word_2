"""
API routers initialization
"""

from fastapi import APIRouter
from app.routers.users import router as users_router
from app.routers.chats import router as chats_router
from app.routers.messages import router as messages_router
from app.routers.chat_members import router as chat_members_router
from app.routers.auth import router as auth_router
from app.routers.dashboard import router as dashboard_router
from app.routers.chat_moderators import router as chat_moderators_router
from app.routers.admin_chats import router as admin_chats_router
from app.routers.chat_info import router as chat_info_router
from app.routers.openrouter import router as openrouter_router
from app.routers.subscription_prices import router as subscription_prices_router
from app.routers.chat_subscriptions import router as chat_subscriptions_router

api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(chats_router, prefix="/chats", tags=["chats"])
api_router.include_router(messages_router, prefix="/messages", tags=["messages"])
api_router.include_router(chat_members_router, prefix="/chat-members", tags=["chat-members"])
api_router.include_router(chat_moderators_router, prefix="/moderators", tags=["moderators"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(admin_chats_router, prefix="/admin-chats", tags=["admin-chats"])
api_router.include_router(chat_info_router, prefix="/chat-info", tags=["chat-info"])
api_router.include_router(openrouter_router, prefix="/openrouter", tags=["openrouter"])
api_router.include_router(subscription_prices_router, prefix="/subscription-prices", tags=["subscription-prices"])
api_router.include_router(chat_subscriptions_router, prefix="/chat-subscriptions", tags=["chat-subscriptions"])
