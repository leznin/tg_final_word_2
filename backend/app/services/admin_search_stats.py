"""
Admin service for search statistics
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import List
from app.models.user_search_logs import UserSearchLog
from app.models.users import User
from app.schemas.mini_app import SearchStatsEntry, SearchStatsResponse


class AdminSearchStatsService:
    """Service for admin search statistics"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_search_statistics(self) -> SearchStatsResponse:
        """Get comprehensive search statistics"""
        
        # Get total searches all time
        total_all_time_query = select(func.count()).select_from(UserSearchLog)
        total_all_time_result = await self.db.execute(total_all_time_query)
        total_searches_all_time = total_all_time_result.scalar() or 0

        # Get total searches today
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        total_today_query = select(func.count()).select_from(UserSearchLog).where(
            UserSearchLog.searched_at >= twenty_four_hours_ago
        )
        total_today_result = await self.db.execute(total_today_query)
        total_searches_today = total_today_result.scalar() or 0

        # Get per-user statistics
        # Subquery for today's searches count per user
        today_searches_subquery = (
            select(
                UserSearchLog.user_id,
                func.count().label('searches_today')
            )
            .where(UserSearchLog.searched_at >= twenty_four_hours_ago)
            .group_by(UserSearchLog.user_id)
            .subquery()
        )

        # Main query: get users with their search stats
        stats_query = (
            select(
                User.id,
                User.telegram_id,
                User.username,
                User.first_name,
                User.last_name,
                func.count(UserSearchLog.id).label('total_searches'),
                func.max(UserSearchLog.searched_at).label('last_search_at'),
                func.coalesce(today_searches_subquery.c.searches_today, 0).label('searches_today')
            )
            .join(UserSearchLog, User.id == UserSearchLog.user_id)
            .outerjoin(today_searches_subquery, User.id == today_searches_subquery.c.user_id)
            .group_by(
                User.id,
                User.telegram_id,
                User.username,
                User.first_name,
                User.last_name,
                today_searches_subquery.c.searches_today
            )
            .order_by(func.count(UserSearchLog.id).desc())
        )

        result = await self.db.execute(stats_query)
        rows = result.all()

        # Convert to schema
        stats: List[SearchStatsEntry] = []
        for row in rows:
            stats.append(SearchStatsEntry(
                user_id=row.id,
                telegram_user_id=row.telegram_id,
                username=row.username,
                first_name=row.first_name,
                last_name=row.last_name,
                total_searches=row.total_searches,
                last_search_at=row.last_search_at,
                searches_today=row.searches_today
            ))

        return SearchStatsResponse(
            total_users=len(stats),
            total_searches_all_time=total_searches_all_time,
            total_searches_today=total_searches_today,
            stats=stats
        )
