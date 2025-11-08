"""
Chat moderators API router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.chat_moderators import (
    ChatModeratorResponse,
    ChatModeratorCreate,
    ChatModeratorUpdate,
    ChatModeratorWithUserResponse,
    ModeratorListResponse
)
from app.services.chat_moderators import ChatModeratorService

router = APIRouter()


@router.get("/", response_model=ModeratorListResponse)
async def get_all_moderators(
    db: AsyncSession = Depends(get_db)
):
    """Get all moderators with chat information"""
    moderator_service = ChatModeratorService(db)
    moderators = await moderator_service.get_all_moderators_with_chat_info()
    return {"moderators": moderators}


@router.get("/chat/{chat_id}")
async def get_chat_moderators(
    chat_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all moderators for a specific chat"""
    from app.services.chats import ChatService
    from sqlalchemy import select, func
    from app.models.users import User

    moderator_service = ChatModeratorService(db)
    chat_service = ChatService(db)

    # Determine chat by ID type
    try:
        chat_id_int = int(chat_id)
        if chat_id.startswith("-") or chat_id_int < 0:
            chat = await chat_service.get_chat_by_telegram_id(chat_id_int)
            if chat:
                actual_chat_id = chat.id
            else:
                raise HTTPException(status_code=404, detail="Chat not found")
        else:
            actual_chat_id = chat_id_int
            chat = await chat_service.get_chat(actual_chat_id)
    except ValueError:
        if chat_id.startswith("-"):
            try:
                telegram_chat_id = int(chat_id)
                chat = await chat_service.get_chat_by_telegram_id(telegram_chat_id)
                if chat:
                    actual_chat_id = chat.id
                else:
                    raise HTTPException(status_code=404, detail="Chat not found")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid chat ID format")
        else:
            raise HTTPException(status_code=400, detail="Invalid chat ID format")

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Get all moderators and filter by chat_id
    all_moderators = await moderator_service.get_all_moderators_with_chat_info()

    # Filter moderators for this specific chat
    moderators = [mod for mod in all_moderators if mod['chat_id'] == actual_chat_id]

    return moderators


@router.post("/", response_model=ChatModeratorResponse)
async def create_moderator(
    moderator_data: ChatModeratorCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat moderator"""
    moderator_service = ChatModeratorService(db)

    # Check if user can manage moderators for this chat
    can_manage = await moderator_service.can_user_manage_moderators(
        moderator_data.chat_id,
        moderator_data.added_by_user_id
    )
    if not can_manage:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to manage moderators for this chat"
        )

    moderator = await moderator_service.create_moderator(moderator_data)
    return moderator


@router.put("/{moderator_id}", response_model=ChatModeratorResponse)
async def update_moderator(
    moderator_id: int,
    moderator_data: ChatModeratorUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a chat moderator"""
    moderator_service = ChatModeratorService(db)

    # Get current moderator to check permissions
    current_moderator = await moderator_service.get_moderator(moderator_id)
    if not current_moderator:
        raise HTTPException(status_code=404, detail="Moderator not found")

    # Check if user can manage moderators for this chat
    # Note: We would need to pass the user_id from authentication
    # For now, we'll assume the permission check happens at the service level

    updated_moderator = await moderator_service.update_moderator(moderator_id, moderator_data)
    if not updated_moderator:
        raise HTTPException(status_code=404, detail="Moderator not found")

    return updated_moderator


@router.delete("/{moderator_id}")
async def delete_moderator(
    moderator_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a chat moderator"""
    moderator_service = ChatModeratorService(db)

    # Get current moderator to check permissions
    current_moderator = await moderator_service.get_moderator(moderator_id)
    if not current_moderator:
        raise HTTPException(status_code=404, detail="Moderator not found")

    # Check if user can manage moderators for this chat
    # Note: We would need to pass the user_id from authentication

    success = await moderator_service.remove_moderator(moderator_id)
    if not success:
        raise HTTPException(status_code=404, detail="Moderator not found")

    return {"message": "Moderator removed successfully"}


@router.delete("/chat/{chat_id}/user/{moderator_user_id}")
async def remove_moderator_by_user(
    chat_id: int,
    moderator_user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Remove moderator by chat and user ID"""
    moderator_service = ChatModeratorService(db)

    # Check if user can manage moderators for this chat
    # Note: We would need to pass the user_id from authentication

    success = await moderator_service.remove_moderator_by_user(chat_id, moderator_user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Moderator not found")

    return {"message": "Moderator removed successfully"}


@router.get("/user/{moderator_user_id}/chats", response_model=List[ChatModeratorResponse])
async def get_user_moderator_chats(
    moderator_user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all chats where user is a moderator"""
    moderator_service = ChatModeratorService(db)
    moderators = await moderator_service.get_user_moderator_chats(moderator_user_id)
    return moderators


@router.get("/chat/{chat_id}/user/{moderator_user_id}/check")
async def check_user_is_moderator(
    chat_id: int,
    moderator_user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Check if user is a moderator in the chat"""
    moderator_service = ChatModeratorService(db)
    is_moderator = await moderator_service.is_user_moderator(chat_id, moderator_user_id)
    return {"is_moderator": is_moderator}


@router.get("/chat/{chat_id}/telegram-admins")
async def get_telegram_chat_admins(
    chat_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get administrators from Telegram for a specific chat"""
    from app.services.chats import ChatService
    import app.main
    
    chat_service = ChatService(db)
    
    # Determine chat by ID type
    try:
        chat_id_int = int(chat_id)
        if chat_id.startswith("-") or chat_id_int < 0:
            chat = await chat_service.get_chat_by_telegram_id(chat_id_int)
            if not chat:
                raise HTTPException(status_code=404, detail="Chat not found")
            telegram_chat_id = chat_id_int
        else:
            chat = await chat_service.get_chat(chat_id_int)
            if not chat:
                raise HTTPException(status_code=404, detail="Chat not found")
            telegram_chat_id = chat.telegram_chat_id
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid chat ID format")
    
    # Get bot instance
    bot_instance = app.main.telegram_bot_instance
    if not bot_instance or not bot_instance.bot:
        raise HTTPException(status_code=503, detail="Bot is not available")
    
    # Get administrators from Telegram
    try:
        administrators = await bot_instance.bot.get_chat_administrators(telegram_chat_id)
        
        admin_list = []
        for admin in administrators:
            # Skip bot accounts
            if admin.user.is_bot:
                continue
                
            admin_data = {
                'user_id': admin.user.id,
                'first_name': getattr(admin.user, 'first_name', None),
                'last_name': getattr(admin.user, 'last_name', None),
                'username': getattr(admin.user, 'username', None),
                'status': admin.status,
                'custom_title': getattr(admin, 'custom_title', None),
            }
            admin_list.append(admin_data)
        
        return {"admins": admin_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get administrators: {str(e)}")


@router.post("/chat/{chat_id}/add-from-telegram")
async def add_moderator_from_telegram(
    chat_id: str,
    request: dict,
    db: AsyncSession = Depends(get_db)
):
    """Add a moderator from Telegram admin"""
    from app.services.chats import ChatService
    from app.dependencies.admin_auth import get_current_admin_user
    
    moderator_service = ChatModeratorService(db)
    chat_service = ChatService(db)
    
    # Get admin user from request
    admin_user_id = request.get('added_by_user_id')
    moderator_user_id = request.get('moderator_user_id')
    first_name = request.get('first_name')
    last_name = request.get('last_name')
    username = request.get('username')
    
    if not admin_user_id or not moderator_user_id:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # Determine chat by ID type
    try:
        chat_id_int = int(chat_id)
        if chat_id.startswith("-") or chat_id_int < 0:
            chat = await chat_service.get_chat_by_telegram_id(chat_id_int)
            if not chat:
                raise HTTPException(status_code=404, detail="Chat not found")
            actual_chat_id = chat.id
        else:
            actual_chat_id = chat_id_int
            chat = await chat_service.get_chat(actual_chat_id)
            if not chat:
                raise HTTPException(status_code=404, detail="Chat not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid chat ID format")
    
    # Create moderator
    moderator_data = ChatModeratorCreate(
        chat_id=actual_chat_id,
        moderator_user_id=moderator_user_id,
        first_name=first_name,
        last_name=last_name,
        username=username,
        added_by_user_id=admin_user_id
    )
    
    moderator = await moderator_service.create_moderator(moderator_data)
    return moderator

