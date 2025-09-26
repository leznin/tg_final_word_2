# Application configuration
PROJECT_NAME=FastAPI Telegram Admin
VERSION=1.0.0
DESCRIPTION=FastAPI application with Telegram bot and Admin panel

# API settings
API_V1_STR=/api/v1
SECRET_KEY=your-secret-key-change-in-production

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8080","http://localhost:5173"]

# Database
DATABASE_URL=mysql+aiomysql://root:696578As@localhost/final?charset=utf8mb4

# Telegram Bot - GET TOKEN FROM @BotFather
TELEGRAM_BOT_TOKEN=7703818325:AAEKjEswBvhEK1AXzJVJyLAydxRoPMkmeVk
TELEGRAM_WEBHOOK_URL=https://test777.ngrok.app/webhook

# Admin panel
ADMIN_SECRET_KEY=696578As

# JWT
JWT_SECRET_KEY=jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# Redis (optional)
REDIS_URL=redis://localhost:6379
