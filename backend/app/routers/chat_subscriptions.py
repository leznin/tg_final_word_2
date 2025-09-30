"""
Chat subscriptions API router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.services.chat_subscriptions import ChatSubscriptionsService
from app.schemas.chat_subscriptions import ChatSubscriptionResponse, ChatSubscriptionWithChatInfo


router = APIRouter()


@router.get("/", response_model=List[ChatSubscriptionWithChatInfo])
async def get_chat_subscriptions(
    include_expired: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all chat subscriptions with chat information"""
    service = ChatSubscriptionsService(db)
    return await service.get_all_subscriptions_with_chat_info(
        include_expired=include_expired,
        skip=skip,
        limit=limit
    )


@router.get("/chat/{chat_id}", response_model=List[ChatSubscriptionResponse])
async def get_chat_subscriptions_for_chat(
    chat_id: int,
    include_expired: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get all subscriptions for a specific chat"""
    service = ChatSubscriptionsService(db)
    return await service.get_subscriptions_for_chat(chat_id, include_expired=include_expired)


@router.get("/chat/{chat_id}/active")
async def check_chat_subscription_status(
    chat_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Check if chat has active subscription"""
    service = ChatSubscriptionsService(db)
    has_active = await service.has_active_subscription(chat_id)
    return {"has_active_subscription": has_active}


@router.get("/{subscription_id}", response_model=ChatSubscriptionResponse)
async def get_chat_subscription(
    subscription_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get chat subscription by ID"""
    service = ChatSubscriptionsService(db)
    subscription = await service.get_subscription_by_id(subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Chat subscription not found")
    return subscription


@router.delete("/{subscription_id}")
async def deactivate_chat_subscription(
    subscription_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Deactivate chat subscription"""
    service = ChatSubscriptionsService(db)
    success = await service.deactivate_subscription(subscription_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat subscription not found")
    return {"message": "Chat subscription deactivated successfully"}

