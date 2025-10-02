# FastAPI Telegram Admin Backend

FastAPI application with Telegram bot integration and admin panel.

## Features

- REST API with FastAPI
- Telegram bot integration
- Admin panel with HTML interface
- User management
- Message history
- JWT authentication
- Async database operations with SQLAlchemy and MySQL
- Docker support

## Project Structure

```
backend/
├── app/
│   ├── core/           # Core configuration and database
│   ├── models/         # Database models
│   ├── routers/        # API routes
│   ├── services/       # Business logic
│   ├── schemas/        # Pydantic schemas
│   ├── utils/          # Utilities (auth, etc.)
│   ├── dependencies/   # FastAPI dependencies
│   ├── telegram/       # Telegram bot implementation
│   ├── admin/          # Admin panel routes
│   └── main.py         # Application entry point
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
└── README.md          # This file
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env file with your configuration
```

3. Run database migrations:
```bash
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

4. Start the application:
```bash
uvicorn app.main:app --reload
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Admin Panel: http://localhost:8000/admin

## Environment Variables

- `APP_DOMAIN`: Base domain for public URLs (e.g., https://yourdomain.com)
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from BotFather
- `TELEGRAM_WEBHOOK_URL`: Webhook URL for Telegram bot (optional)
- `DATABASE_URL`: Database connection string (MySQL format: `mysql+aiomysql://user:password@host:port/database`)
- `SECRET_KEY`: Secret key for JWT tokens
- `ADMIN_SECRET_KEY`: Secret key for admin access

## Admin Panel

Access the admin panel at `/admin/` to manage users and view Telegram messages.

## Development

The application uses:
- FastAPI for the web framework
- SQLAlchemy for database ORM with MySQL support
- aiomysql for async MySQL operations
- Pydantic for data validation
- JWT for authentication
- AsyncIO for asynchronous operations
- Docker for containerization
