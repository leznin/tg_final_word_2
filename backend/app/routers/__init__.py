"""
API routers initialization
"""

from fastapi import APIRouter
from app.routers.users import router as users_router
from app.routers.chats import router as chats_router
from app.routers.messages import router as messages_router
from app.routers.chat_members import router as chat_members_router

api_router = APIRouter()

# Include all routers
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(chats_router, prefix="/chats", tags=["chats"])
api_router.include_router(messages_router, prefix="/messages", tags=["messages"])
api_router.include_router(chat_members_router, prefix="/chat-members", tags=["chat-members"])
