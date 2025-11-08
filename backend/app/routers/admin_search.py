"""
Admin router for search statistics
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.admin_auth import require_admin_auth
from app.schemas.mini_app import SearchStatsResponse
from app.services.admin_search_stats import AdminSearchStatsService

router = APIRouter()


@router.get("/search-stats", response_model=SearchStatsResponse)
async def get_search_statistics(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin_auth)
):
    """Get comprehensive search usage statistics (admin/manager only)"""
    service = AdminSearchStatsService(db)
    return await service.get_search_statistics()
