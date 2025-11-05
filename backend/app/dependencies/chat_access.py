"""
Chat access dependency for checking manager permissions
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.admin_auth import get_current_admin_user
from app.services.manager_chat_access import ManagerChatAccessService
from app.models.admin_users import UserRole


async def check_chat_access(
    chat_id: int,
    user_info: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if user has access to the specified chat.
    Admins have access to all chats, managers only to assigned chats.
    """
    # Admins have access to everything
    if user_info.get("role") == UserRole.ADMIN.value:
        return user_info
    
    # Managers need explicit access
    if user_info.get("role") == UserRole.MANAGER.value:
        access_service = ManagerChatAccessService(db)
        has_access = await access_service.has_chat_access(user_info["user_id"], chat_id)
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this chat"
            )
        
        return user_info
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid user role"
    )
