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


@router.get("/chat/{chat_id}")
async def get_chat_members(
    chat_id: str,
    skip: int = 0,
    limit: int = 30,
    search: str = "",
    db: AsyncSession = Depends(get_db)
):
    """Get all members of a specific chat with their group memberships"""
    from app.services.chats import ChatService
    from app.models.chats import Chat
    from app.models.chat_members import ChatMember
    from sqlalchemy import select, func, or_, and_

    member_service = ChatMemberService(db)
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

    # Get total count for pagination
    total_query = select(func.count(ChatMember.id)).where(ChatMember.chat_id == actual_chat_id)

    # Add search conditions if search parameter is provided
    if search:
        search_filter = or_(
            ChatMember.first_name.ilike(f"%{search}%"),
            ChatMember.last_name.ilike(f"%{search}%"),
            ChatMember.username.ilike(f"%{search}%"),
            func.cast(ChatMember.telegram_user_id, func.String).ilike(f"%{search}%")
        )
        total_query = total_query.where(search_filter)

    total_result = await db.execute(total_query)
    total = total_result.scalar()

    # Get chat members with pagination and search
    members = await member_service.get_chat_members_with_search(actual_chat_id, skip, limit, search)

    # Get group memberships for each member
    members_data = []
    for member in members:
        # Find other groups this user is in
        user_groups_result = await db.execute(
            select(
                Chat.title,
                Chat.telegram_chat_id,
                Chat.chat_type
            )
            .select_from(ChatMember)
            .join(Chat, ChatMember.chat_id == Chat.id)
            .where(ChatMember.telegram_user_id == member.telegram_user_id)
            .where(Chat.is_active == True)
            .where(Chat.chat_type.in_(['group', 'supergroup']))
            .where(Chat.id != actual_chat_id)  # Exclude current chat
            .limit(10)  # Limit to prevent too much data
        )

        user_groups = []
        for row in user_groups_result:
            user_groups.append({
                'title': row.title or f'Chat {row.telegram_chat_id}',
                'telegram_chat_id': row.telegram_chat_id,
                'chat_type': row.chat_type
            })

        # Get user data from the joined telegram_user
        user = member.telegram_user
        member_data = {
            'id': member.id,
            'chat_id': member.chat_id,
            'telegram_user_id': member.telegram_user_id,
            'is_bot': user.is_bot if user else False,
            'first_name': user.first_name if user else None,
            'last_name': user.last_name if user else None,
            'username': user.username if user else None,
            'language_code': user.language_code if user else None,
            'is_premium': user.is_premium if user else None,
            'added_to_attachment_menu': user.added_to_attachment_menu if user else None,
            'can_join_groups': user.can_join_groups if user else None,
            'can_read_all_group_messages': user.can_read_all_group_messages if user else None,
            'supports_inline_queries': user.supports_inline_queries if user else None,
            'can_connect_to_business': user.can_connect_to_business if user else None,
            'has_main_web_app': user.has_main_web_app if user else None,
            'joined_at': member.joined_at.isoformat() if member.joined_at else None,
            'created_at': member.created_at.isoformat() if member.created_at else None,
            'updated_at': member.updated_at.isoformat() if member.updated_at else None,
            'user_groups': user_groups
        }
        members_data.append(member_data)

    return {
        "members": members_data,
        "total": total
    }


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
