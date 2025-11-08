"""
Admin router for search statistics
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.admin_auth import require_admin_auth
from app.schemas.mini_app import SearchStatsResponse, SearchBoostPriceResponse, SearchBoostPriceUpdate
from app.services.admin_search_stats import AdminSearchStatsService
from app.services.search_boost import SearchBoostService

router = APIRouter()


@router.get("/search-stats", response_model=SearchStatsResponse)
async def get_search_statistics(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin_auth)
):
    """Get comprehensive search usage statistics (admin/manager only)"""
    service = AdminSearchStatsService(db)
    return await service.get_search_statistics()


@router.get("/search-boost/price", response_model=SearchBoostPriceResponse)
async def get_search_boost_price_admin(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin_auth)
):
    """Get current search boost price (admin only)"""
    from fastapi import HTTPException
    service = SearchBoostService(db)
    price = await service.get_price_response()
    
    if not price:
        raise HTTPException(status_code=404, detail="Search boost price not configured")
    
    return price


@router.put("/search-boost/price", response_model=SearchBoostPriceResponse)
async def update_search_boost_price(
    price_update: SearchBoostPriceUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin_auth)
):
    """Update search boost price (admin only)"""
    service = SearchBoostService(db)
    updated_price = await service.update_price(price_update)
    
    return SearchBoostPriceResponse(
        id=updated_price.id,
        boost_amount=updated_price.boost_amount,
        price_stars=updated_price.price_stars,
        currency=updated_price.currency,
        is_active=updated_price.is_active,
        created_at=updated_price.created_at,
        updated_at=updated_price.updated_at
    )
