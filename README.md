# FastAPI Telegram Admin Project

Full-stack application with FastAPI backend, Telegram bot integration, and admin panel.

## Project Structure

```
fin 3/
├── backend/           # FastAPI backend
│   ├── app/          # Application code
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
└── frontend/         # Frontend application
    └── README.md
```

## Features

### Backend (FastAPI)
- REST API with FastAPI framework
- Telegram bot integration
- Admin panel with HTML interface
- User management system
- Message history tracking
- JWT authentication
- Async database operations
- Docker containerization

### Telegram Bot
- Message handling
- User registration
- Integration with backend services
- Webhook support

### Admin Panel
- User management
- Telegram message monitoring
- Statistics dashboard
- Settings configuration

## Quick Start

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize database:
```bash
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

5. Start the backend server:
```bash
uvicorn app.main:app --reload
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Follow the setup instructions in `frontend/README.md`

## API Documentation

Once the backend is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Admin Panel: http://localhost:8000/admin

## Configuration

### Required Environment Variables

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
- `DATABASE_URL`: Database connection string (SQLite, PostgreSQL, MySQL)
- `SECRET_KEY`: Secret key for JWT token encryption
- `ADMIN_SECRET_KEY`: Secret key for admin panel access

### Optional Configuration

- `TELEGRAM_WEBHOOK_URL`: Webhook URL for Telegram bot
- `BACKEND_CORS_ORIGINS`: Allowed origins for CORS
- `REDIS_URL`: Redis connection for caching

## Development

### Backend Development

The backend follows a modular architecture:

- **Core**: Configuration, database setup
- **Models**: Database models with SQLAlchemy
- **Schemas**: Pydantic schemas for validation
- **Services**: Business logic layer
- **Routers**: API endpoints
- **Utils**: Authentication, helpers
- **Dependencies**: FastAPI dependencies
- **Telegram**: Bot implementation
- **Admin**: Admin panel routes

### Frontend Development

The frontend is designed to work with any modern framework and should integrate with the REST API endpoints.

## Deployment

### Docker Deployment

1. Build and run with Docker:
```bash
docker build -t fastapi-telegram-admin backend/
docker run -p 8000:8000 fastapi-telegram-admin
```

### Production Deployment

For production deployment, consider:
- Using a production WSGI server (Gunicorn with Uvicorn workers)
- Setting up a reverse proxy (Nginx)
- Using a production database (PostgreSQL, MySQL)
- Setting up Redis for caching
- Configuring proper environment variables
- Setting up SSL certificates

## Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Use type hints
5. Follow PEP 8 style guidelines

## License

This project is open source and available under the MIT License.
