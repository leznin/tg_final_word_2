"""
Manager chat access API router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.manager_chat_access import (
    ManagerChatAccessCreate,
    ManagerChatAccessBulkCreate,
    ManagerChatAccessResponse,
    ManagerChatsResponse,
    ManagerChatInfo
)
from app.services.manager_chat_access import ManagerChatAccessService
from app.dependencies.admin_auth import require_admin_role

router = APIRouter()


@router.post("/", response_model=ManagerChatAccessResponse)
async def assign_chat_to_manager(
    access_data: ManagerChatAccessCreate,
    _: dict = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    """Assign a chat to a manager (admin only)"""
    access_service = ManagerChatAccessService(db)
    try:
        access = await access_service.assign_chat_to_manager(access_data)
        return access
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/bulk", response_model=List[ManagerChatAccessResponse])
async def assign_chats_to_manager(
    access_data: ManagerChatAccessBulkCreate,
    _: dict = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    """Assign multiple chats to a manager (admin only)"""
    access_service = ManagerChatAccessService(db)
    accesses = await access_service.assign_chats_to_manager(access_data)
    return accesses


@router.get("/{manager_id}/chats", response_model=List[ManagerChatInfo])
async def get_manager_chats(
    manager_id: int,
    _: dict = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    """Get all chats assigned to a manager (admin only)"""
    access_service = ManagerChatAccessService(db)
    chats = await access_service.get_manager_chats(manager_id)
    return chats


@router.delete("/{manager_id}/chats/{chat_id}")
async def remove_chat_access(
    manager_id: int,
    chat_id: int,
    _: dict = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    """Remove manager's access to a specific chat (admin only)"""
    access_service = ManagerChatAccessService(db)
    success = await access_service.remove_chat_access(manager_id, chat_id)
    if not success:
        raise HTTPException(status_code=404, detail="Access not found")
    
    return {"message": "Access removed successfully"}


@router.get("/chat/{chat_id}/managers")
async def get_chat_managers(
    chat_id: int,
    _: dict = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    """Get all managers who have access to a chat (admin only)"""
    access_service = ManagerChatAccessService(db)
    manager_ids = await access_service.get_chat_managers(chat_id)
    return {"chat_id": chat_id, "manager_ids": manager_ids}
