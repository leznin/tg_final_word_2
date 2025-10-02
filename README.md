# FastAPI Telegram Admin Project

Full-stack application with FastAPI backend, Telegram bot integration, and admin panel.

**Current Status:** ✅ Application is configured and ready to run with MySQL database support.

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
- Telegram bot integration with aiogram
- Admin panel with HTML interface
- User management system
- Message history tracking with cleanup
- JWT authentication with python-jose
- Async MySQL database operations with SQLAlchemy
- Docker containerization
- Pydantic v2 with email validation
- CORS support
- Automatic database migrations with Alembic

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

### Prerequisites

- Python 3.13+
- MySQL database (or any SQLAlchemy-compatible database)
- Virtual environment tools

### Backend Setup

1. **Clone and navigate to the project:**
```bash
cd /Users/s3s3s/Desktop/Не\ удалять/fin\ 6/backend
```

2. **Create and activate virtual environment:**
```bash
# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration (see Configuration section below)
nano .env  # or use your preferred editor
```

5. **Set up MySQL database:**
   - Create a MySQL database
   - Update `DATABASE_URL` in `.env` file:
   ```
   DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/database_name
   ```

6. **Initialize database (tables will be created automatically on first run):**
```bash
# The application will create tables automatically when started
```

7. **Start the backend server:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Start with auto-reload for development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Verify Installation

After starting the server, verify it's working:

```bash
# Check API documentation
curl http://localhost:8000/docs

# Should return HTML content (HTTP 200)
```

### Stopping the Server

```bash
# Press Ctrl+C in the terminal where uvicorn is running
# Or from another terminal:
pkill -f uvicorn
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

Create a `.env` file in the backend directory with the following variables:

```env
# Database Configuration (REQUIRED)
DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/database_name

# Security (REQUIRED)
SECRET_KEY=your-super-secret-key-change-this-in-production
ADMIN_SECRET_KEY=admin-secret-key-change-this-too

# Domain Configuration (REQUIRED for file uploads)
APP_DOMAIN=https://yourdomain.com

# Telegram Bot (OPTIONAL - for bot functionality)
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_WEBHOOK_URL=https://yourdomain.com/webhook

# CORS (OPTIONAL)
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Redis (OPTIONAL)
REDIS_URL=redis://localhost:6379

# Message Cleanup (OPTIONAL)
MESSAGE_RETENTION_HOURS=50
CLEANUP_INTERVAL_MINUTES=60
```

### Database Setup

1. **Install MySQL** (if not already installed)
2. **Create database:**
   ```sql
   CREATE DATABASE fin_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. **Create user:**
   ```sql
   CREATE USER 'fin_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON fin_app.* TO 'fin_user'@'localhost';
   FLUSH PRIVILEGES;
   ```
4. **Update DATABASE_URL** in `.env`:
   ```
   DATABASE_URL=mysql+aiomysql://fin_user:your_password@localhost:3306/fin_app
   ```

### Troubleshooting

#### Common Issues

**1. Port already in use:**
```bash
# Kill existing processes
pkill -f uvicorn

# Or use different port
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**2. Virtual environment not activated:**
```bash
# Always activate venv before running commands
source venv/bin/activate
which python  # Should show venv path
```

**3. Database connection error:**
```bash
# Check MySQL service
brew services list | grep mysql

# Test connection
python -c "import aiomysql; print('MySQL driver works')"
```

**4. Module import errors:**
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt
```

#### Health Check

```bash
# Check if application is running
curl -s http://localhost:8000/docs | head -1

# Check database connection
curl http://localhost:8000/api/v1/dashboard/stats

# View application logs
tail -f /tmp/fastapi.log  # if logging is configured
```

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

## Dependencies

### Core Dependencies
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM with async support
- **aiomysql** - Async MySQL driver
- **Pydantic v2** - Data validation and serialization
- **aiogram** - Telegram Bot API framework
- **python-jose** - JWT token handling
- **passlib** - Password hashing
- **alembic** - Database migrations

### Development Dependencies
- **pytest** - Testing framework
- **pytest-asyncio** - Async testing support
- **httpx** - HTTP client for testing

## Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Use type hints
5. Follow PEP 8 style guidelines

## Support

If you encounter any issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Verify your environment setup
3. Check database connectivity
4. Ensure virtual environment is activated

## License

This project is open source and available under the MIT License.
