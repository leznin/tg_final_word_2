"""
Chat members API router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.chat_members import ChatMemberResponse
from app.services.chat_members import ChatMemberService

router = APIRouter()


@router.get("/chat/{chat_id}", response_model=List[ChatMemberResponse])
async def get_chat_members(
    chat_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all members of a specific chat"""
    member_service = ChatMemberService(db)
    members = await member_service.get_chat_members(chat_id, skip, limit)
    return members


@router.get("/chat/{chat_id}/count")
async def get_chat_member_count(
    chat_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get member count for a specific chat"""
    member_service = ChatMemberService(db)
    count = await member_service.get_member_count(chat_id)
    return {"chat_id": chat_id, "member_count": count}


@router.get("/{member_id}", response_model=ChatMemberResponse)
async def get_chat_member(
    member_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get chat member by ID"""
    member_service = ChatMemberService(db)
    member = await member_service.get_chat_member(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Chat member not found")
    return member


@router.get("/chat/{chat_id}/user/{telegram_user_id}", response_model=ChatMemberResponse)
async def get_chat_member_by_telegram_id(
    chat_id: int,
    telegram_user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get chat member by chat_id and telegram_user_id"""
    member_service = ChatMemberService(db)
    member = await member_service.get_chat_member_by_telegram_id(chat_id, telegram_user_id)
    if not member:
        raise HTTPException(status_code=404, detail="Chat member not found")
    return member
