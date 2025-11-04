"""
Admin authentication dependency for protecting API endpoints
"""

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.routers.auth import get_current_admin


async def require_admin_auth(request: Request):
    """
    Dependency to require admin authentication for API endpoints
    """
    is_admin = await get_current_admin(request)
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required"
        )
    return True


async def get_current_admin_or_403(request: Request):
    """
    Get current admin or raise 403 Forbidden
    """
    is_admin = await get_current_admin(request)
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return True