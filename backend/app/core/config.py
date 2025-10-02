"""
Application configuration with environment variables
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings"""

    # Project info
    PROJECT_NAME: str = "FastAPI Telegram Admin"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "FastAPI application with Telegram bot and Admin panel"

    # API settings
    API_V1_STR: str = "/api/v1"
    APP_DOMAIN: str = "http://localhost:8000"  # Base domain for public URLs
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React frontend
        "http://localhost:8080",  # Vue frontend
        "http://localhost:5173",  # Vite frontend
    ]

    # Database
    DATABASE_URL: str = "mysql+aiomysql://user:password@localhost:3306/fin_app"

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""

    # Admin panel
    ADMIN_SECRET_KEY: str = "admin-secret-key"

    # Redis (optional)
    REDIS_URL: str = "redis://localhost:6379"

    # JWT
    JWT_SECRET_KEY: str = "jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 30

    # Message cleanup settings
    MESSAGE_RETENTION_HOURS: int = 168  # Keep messages for 7 days (168 hours)
    CLEANUP_INTERVAL_MINUTES: int = 60  # Run cleanup every hour

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
