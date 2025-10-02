"""
Broadcast router for sending messages to Telegram users
"""

import base64
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Union

from app.core.database import get_db
from app.services.broadcast import BroadcastService
from app.schemas.broadcast import BroadcastMessageRequest, BroadcastResult, BroadcastStatus

router = APIRouter()

# Global broadcast service instance for status tracking
_broadcast_service = None


def get_broadcast_service(db: AsyncSession = Depends(get_db)):
    """Get broadcast service instance"""
    global _broadcast_service

    # Access bot instance directly to avoid circular imports
    import app.main
    bot = app.main.telegram_bot_instance
    if not bot:
        raise HTTPException(status_code=500, detail="Telegram bot not initialized")

    if _broadcast_service is None or _broadcast_service.db != db:
        _broadcast_service = BroadcastService(db, bot)

    return _broadcast_service


@router.post("/send", response_model=BroadcastResult)
async def send_broadcast(
    request: BroadcastMessageRequest,
    service: BroadcastService = Depends(get_broadcast_service)
) -> BroadcastResult:
    """
    Send broadcast message to all eligible users
    """
    try:
        # Validate message length (Telegram limit is 4096 characters)
        if len(request.message) > 4096:
            raise HTTPException(status_code=400, detail="Message too long (max 4096 characters)")

        if len(request.message.strip()) == 0:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        # Validate media URL if provided
        if request.media and request.media.url:
            if not request.media.url.startswith(('http://', 'https://', 'data:')):
                raise HTTPException(status_code=400, detail="Media URL must be a valid HTTP/HTTPS URL or data URL")

        # Check if broadcast is already running
        if service.is_running:
            raise HTTPException(status_code=409, detail="Broadcast is already running")

        # Send broadcast
        result = await service.send_broadcast_message(request)

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Broadcast failed: {str(e)}")


@router.get("/status", response_model=BroadcastStatus)
async def get_broadcast_status(
    service: BroadcastService = Depends(get_broadcast_service)
) -> BroadcastStatus:
    """
    Get current broadcast status
    """
    return service.get_broadcast_status()


@router.post("/upload-media")
async def upload_media_file(
    file: UploadFile = File(...)
) -> Dict[str, Union[str, int]]:
    """
    Upload media file and return URL for use in broadcasts
    """
    try:
        import os
        from pathlib import Path

        # Validate file size (max 10MB)
        content = await file.read()
        file_size = len(content)

        if file_size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=413, detail="File too large (max 10MB)")

        # Validate file type
        allowed_types = [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'video/mp4', 'video/avi', 'video/mov', 'video/mkv',
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]

        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

        # Create uploads directory if it doesn't exist
        uploads_dir = Path("static/uploads")
        uploads_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        import uuid
        file_extension = Path(file.filename or "file").suffix or ""
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = uploads_dir / unique_filename

        # Save file
        with open(file_path, "wb") as f:
            f.write(content)

        # Create public URL (using ngrok for development)
        # In production, replace with your actual domain
        public_url = f"https://test777.ngrok.app/static/uploads/{unique_filename}"

        return {
            "url": public_url,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file_size
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@router.get("/users/count")
async def get_broadcast_users_count(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get count of users eligible for broadcast
    """
    try:
        service = BroadcastService(db)
        users = await service.get_broadcast_users()
        return {
            "count": len(users),
            "description": "Users with active Telegram accounts who can receive messages"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get users count: {str(e)}")
