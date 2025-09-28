"""
OpenRouter API router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.schemas.openrouter import (
    OpenRouterCreate, OpenRouterUpdate, OpenRouterResponse,
    OpenRouterModelsResponse, OpenRouterBalanceResponse
)
from app.services.openrouter import OpenRouterService

router = APIRouter()


@router.get("/test")
async def test_openrouter():
    """Test route for OpenRouter"""
    return {"status": "ok", "message": "OpenRouter router is working", "timestamp": datetime.utcnow().isoformat()}


@router.get("/settings")
async def get_openrouter_settings(db: AsyncSession = Depends(get_db)):
    """Get OpenRouter settings"""
    service = OpenRouterService(db)
    try:
        settings = await service.get_settings()
        if not settings:
            raise HTTPException(status_code=404, detail="OpenRouter settings not found")
        await service.close()

        # Convert to dict and handle datetime serialization
        settings_dict = {
            "id": settings.id,
            "api_key": settings.api_key,
            "selected_model": settings.selected_model,
            "balance": settings.balance,
            "prompt": settings.prompt,
            "is_active": settings.is_active,
            "created_at": settings.created_at.isoformat() if settings.created_at else None,
            "updated_at": settings.updated_at.isoformat() if settings.updated_at else None,
        }
        return settings_dict
    except HTTPException:
        await service.close()
        raise
    except Exception as e:
        await service.close()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/settings", response_model=OpenRouterResponse)
async def save_openrouter_settings(
    settings_data: OpenRouterCreate,
    db: AsyncSession = Depends(get_db)
):
    """Save OpenRouter settings"""
    service = OpenRouterService(db)
    try:
        # Validate API key before saving
        is_valid = await service.validate_api_key(settings_data.api_key)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid OpenRouter API key")

        settings = await service.save_settings(settings_data)
        await service.close()
        return settings
    except HTTPException:
        await service.close()
        raise
    except Exception as e:
        await service.close()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/settings", response_model=OpenRouterResponse)
async def update_openrouter_settings(
    settings_data: OpenRouterUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update OpenRouter settings"""
    service = OpenRouterService(db)
    try:
        if settings_data.api_key:
            # Validate API key if provided
            is_valid = await service.validate_api_key(settings_data.api_key)
            if not is_valid:
                raise HTTPException(status_code=400, detail="Invalid OpenRouter API key")

        settings = await service.update_settings(settings_data)
        if not settings:
            raise HTTPException(status_code=404, detail="OpenRouter settings not found")
        await service.close()
        return settings
    except HTTPException:
        await service.close()
        raise
    except Exception as e:
        await service.close()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=OpenRouterModelsResponse)
async def get_openrouter_models(db: AsyncSession = Depends(get_db)):
    """Get available OpenRouter models"""
    service = OpenRouterService(db)
    try:
        models = await service.get_models()
        await service.close()
        return OpenRouterModelsResponse(models=models)
    except ValueError as e:
        await service.close()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await service.close()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/balance", response_model=OpenRouterBalanceResponse)
async def get_openrouter_balance(db: AsyncSession = Depends(get_db)):
    """Get OpenRouter account balance"""
    service = OpenRouterService(db)
    try:
        balance = await service.get_balance()
        await service.close()
        return OpenRouterBalanceResponse(
            balance=balance,
            last_updated=datetime.utcnow().isoformat()
        )
    except ValueError as e:
        await service.close()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await service.close()
        raise HTTPException(status_code=500, detail=str(e))
