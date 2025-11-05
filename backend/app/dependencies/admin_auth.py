"""
Admin authentication dependency for protecting API endpoints
"""

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.routers.auth import get_current_admin
from app.models.admin_users import UserRole


async def require_admin_auth(request: Request):
    """
    Dependency to require admin or manager authentication for API endpoints
    """
    user_info = await get_current_admin(request)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required"
        )
    return user_info


async def require_admin_role(request: Request):
    """
    Dependency to require admin role (not manager)
    """
    user_info = await get_current_admin(request)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required"
        )
    
    if user_info.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    return user_info


async def get_current_admin_user(request: Request):
    """
    Get current authenticated admin/manager user info
    """
    user_info = await get_current_admin(request)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user_info


async def get_current_admin_or_403(request: Request):
    """
    Get current admin or raise 403 Forbidden
    """
    user_info = await get_current_admin(request)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user_info