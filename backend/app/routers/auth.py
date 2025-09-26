"""
Authentication router for admin panel with fingerprint blocking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Form
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.services.auth_attempts import AuthAttemptsService

router = APIRouter()

# Simple in-memory session store (in production, use Redis or database)
_sessions = set()

security = HTTPBearer(auto_error=False)


async def get_current_admin(request: Request):
    """Get current admin session"""
    # Check if admin session exists
    admin_token = request.cookies.get("admin_session")
    if admin_token and admin_token in _sessions:
        return True
    return False


@router.post("/login")
async def login(
    response: Response,
    request: Request,
    fingerprint: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Admin login with password verification and fingerprint blocking"""
    auth_service = AuthAttemptsService(db)

    # Get client info
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # Check if fingerprint is blocked
    is_blocked, block_reason = await auth_service.is_fingerprint_blocked(fingerprint)
    if is_blocked:
        # Record blocked attempt
        await auth_service.record_attempt(
            fingerprint=fingerprint,
            ip_address=client_ip,
            user_agent=user_agent,
            success=False,
            blocked=True,
            block_reason=block_reason
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Access blocked: {block_reason}"
        )

    # Check password
    if password == settings.ADMIN_SECRET_KEY:
        # Create simple session token
        import uuid
        session_token = str(uuid.uuid4())

        # Store session (in production, use Redis/database)
        _sessions.add(session_token)

        # Record successful attempt
        await auth_service.record_attempt(
            fingerprint=fingerprint,
            ip_address=client_ip,
            user_agent=user_agent,
            success=True,
            blocked=False
        )

        # Set session cookie
        response.set_cookie(
            key="admin_session",
            value=session_token,
            httponly=True,
            max_age=30 * 60,  # 30 minutes
            samesite="lax"
        )

        return {"success": True, "message": "Login successful"}

    # Invalid password - record failed attempt
    await auth_service.record_attempt(
        fingerprint=fingerprint,
        ip_address=client_ip,
        user_agent=user_agent,
        success=False,
        blocked=False
    )

    # Invalid password
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid password"
    )


@router.get("/check")
async def check_auth(request: Request):
    """Check if admin is authenticated"""
    is_admin = await get_current_admin(request)
    return {"authenticated": is_admin}


@router.post("/logout")
async def logout(request: Request, response: Response):
    """Admin logout"""
    admin_token = request.cookies.get("admin_session")
    if admin_token and admin_token in _sessions:
        _sessions.remove(admin_token)

    # Clear session cookie
    response.delete_cookie("admin_session")

    return {"success": True, "message": "Logged out successfully"}