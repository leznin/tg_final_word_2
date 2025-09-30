"""
Subscription prices API router for admin panel
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.services.subscription_prices import SubscriptionPricesService
from app.schemas.subscription_prices import SubscriptionPriceCreate, SubscriptionPriceUpdate, SubscriptionPriceResponse


router = APIRouter()


@router.get("/", response_model=List[SubscriptionPriceResponse])
async def get_subscription_prices(
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get all subscription prices"""
    service = SubscriptionPricesService(db)
    return await service.get_all_prices(include_inactive=include_inactive)


@router.get("/{price_id}", response_model=SubscriptionPriceResponse)
async def get_subscription_price(
    price_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get subscription price by ID"""
    service = SubscriptionPricesService(db)
    price = await service.get_price_by_id(price_id)
    if not price:
        raise HTTPException(status_code=404, detail="Subscription price not found")
    return price


@router.post("/", response_model=SubscriptionPriceResponse)
async def create_subscription_price(
    price_data: SubscriptionPriceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new subscription price"""
    service = SubscriptionPricesService(db)
    return await service.create_price(price_data)


@router.put("/{price_id}", response_model=SubscriptionPriceResponse)
async def update_subscription_price(
    price_id: int,
    price_data: SubscriptionPriceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update subscription price"""
    service = SubscriptionPricesService(db)
    updated_price = await service.update_price(price_id, price_data)
    if not updated_price:
        raise HTTPException(status_code=404, detail="Subscription price not found")
    return updated_price


@router.delete("/{price_id}")
async def deactivate_subscription_price(
    price_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Deactivate subscription price"""
    service = SubscriptionPricesService(db)
    success = await service.deactivate_price(price_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subscription price not found")
    return {"message": "Subscription price deactivated successfully"}


@router.post("/cleanup-duplicates")
async def cleanup_duplicate_prices(
    db: AsyncSession = Depends(get_db)
):
    """Clean up duplicate active subscription prices, keeping only the most recent for each type"""
    service = SubscriptionPricesService(db)
    deactivated_count = await service.cleanup_duplicate_prices()
    return {
        "message": f"Cleaned up {deactivated_count} duplicate subscription prices",
        "deactivated_count": deactivated_count
    }

