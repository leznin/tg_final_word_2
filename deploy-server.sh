#!/bin/bash

# Deployment script for finalword.cc server
# Ubuntu 22.04 LTS

set -e

echo "======================================"
echo "Deploying Final Word 2.8.1 to Server"
echo "======================================"

# Variables
SERVER_IP="45.147.196.229"
SERVER_USER="root"
SERVER_PASSWORD="696578As!!!!"
APP_DIR="/root/tg_final_word_2"
DOMAIN="finalword.cc"
TELEGRAM_BOT_TOKEN="8313267177:AAEvU2rLFC48I7CEXy8crbEHi74-Mk4LElo"

# Database credentials
DB_NAME="finalword_db"
DB_USER="finalword_user"
DB_PASS="FinalWord2024!Secure"

# Generate secure keys
SECRET_KEY=$(openssl rand -hex 32)
ADMIN_SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

echo "🔧 Step 1: Stopping old services..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'ENDSSH'
systemctl stop finalword-backend 2>/dev/null || true
systemctl stop finalword-frontend 2>/dev/null || true
systemctl disable finalword-backend 2>/dev/null || true
systemctl disable finalword-frontend 2>/dev/null || true
pkill -f "uvicorn app.main" || true
pkill -f "npm run dev" || true
ENDSSH

echo "✅ Services stopped"

echo ""
echo "🔧 Step 2: Backing up old installation..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'ENDSSH'
if [ -d "/root/tg_final_word_2" ]; then
    BACKUP_DIR="/root/tg_final_word_2_backup_$(date +%Y%m%d_%H%M%S)"
    mv /root/tg_final_word_2 "$BACKUP_DIR"
    echo "Backed up to $BACKUP_DIR"
fi
ENDSSH

echo "✅ Backup complete"

echo ""
echo "🔧 Step 3: Uploading new version..."
cd "/Users/s3s3s/Desktop/final word 2.8.1"

# Create temporary exclude file
cat > /tmp/rsync_exclude.txt << EOF
.git
.gitignore
node_modules
venv
__pycache__
*.pyc
.DS_Store
.env
backend/.env
frontend/node_modules
frontend/dist
*.log
.vscode
deploy-server.sh
EOF

# Upload project files
sshpass -p "$SERVER_PASSWORD" rsync -avz --exclude-from=/tmp/rsync_exclude.txt \
    -e "ssh -o StrictHostKeyChecking=no" \
    ./ $SERVER_USER@$SERVER_IP:/root/tg_final_word_2/

rm /tmp/rsync_exclude.txt

echo "✅ Files uploaded"

echo ""
echo "🔧 Step 4: Installing system dependencies..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'ENDSSH'
export DEBIAN_FRONTEND=noninteractive

# Update system
apt-get update

# Install basic tools
apt-get install -y software-properties-common curl wget git build-essential libssl-dev

# Install Python 3.11 (Ubuntu 22.04 compatible)
apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Install MySQL
apt-get install -y mysql-server mysql-client libmysqlclient-dev

# Install Nginx
apt-get install -y nginx

# Start services
systemctl start mysql
systemctl enable mysql
systemctl enable nginx

echo "✅ System dependencies installed"
ENDSSH

echo "✅ Dependencies installed"

echo ""
echo "🔧 Step 5: Configuring MySQL database..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << ENDSSH
# Drop old database if exists
mysql -e "DROP DATABASE IF EXISTS finalword_db;" 2>/dev/null || true
mysql -e "DROP DATABASE IF EXISTS final;" 2>/dev/null || true
mysql -e "DROP USER IF EXISTS 'finalword_user'@'localhost';" 2>/dev/null || true

# Create new database
mysql -e "CREATE DATABASE $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -e "CREATE USER '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';"
mysql -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"

echo "✅ Database configured: $DB_NAME"
ENDSSH

echo "✅ MySQL configured"

echo ""
echo "🔧 Step 6: Setting up Backend..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << ENDSSH
cd /root/tg_final_word_2/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
# Application configuration
PROJECT_NAME=FastAPI Telegram Admin
VERSION=2.8.1
DESCRIPTION=FastAPI application with Telegram bot and Admin panel

# API settings
API_V1_STR=/api/v1
APP_DOMAIN=https://$DOMAIN
SECRET_KEY=$SECRET_KEY

# CORS
BACKEND_CORS_ORIGINS=["https://$DOMAIN","http://localhost:5173"]

# Database
DATABASE_URL=mysql+aiomysql://$DB_USER:$DB_PASS@localhost/$DB_NAME?charset=utf8mb4

# Telegram Bot
TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
TELEGRAM_WEBHOOK_URL=https://$DOMAIN/webhook

# Admin panel
ADMIN_SECRET_KEY=$ADMIN_SECRET_KEY

# JWT
JWT_SECRET_KEY=$JWT_SECRET_KEY
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Message Cleanup
MESSAGE_RETENTION_HOURS=168
CLEANUP_INTERVAL_MINUTES=60

# Environment
ENVIRONMENT=production
EOF

echo "✅ Backend environment configured"
ENDSSH

echo "✅ Backend configured"

echo ""
echo "🔧 Step 7: Creating SSL certificates..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'ENDSSH'
mkdir -p /etc/nginx/ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/finalword.key \
    -out /etc/nginx/ssl/finalword.crt \
    -subj "/C=NL/ST=Netherlands/L=Amsterdam/O=FinalWord/CN=finalword.cc"

chmod 600 /etc/nginx/ssl/finalword.key
chmod 644 /etc/nginx/ssl/finalword.crt

echo "✅ SSL certificates created"
ENDSSH

echo "✅ SSL certificates created"

echo ""
echo "🔧 Step 8: Configuring Nginx..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'ENDSSH'
# Remove default config
rm -f /etc/nginx/sites-enabled/default

# Create nginx config
cat > /etc/nginx/sites-available/finalword.cc << 'EOF'
# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name finalword.cc www.finalword.cc;
    
    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name finalword.cc www.finalword.cc;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/finalword.crt;
    ssl_certificate_key /etc/nginx/ssl/finalword.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Max upload size
    client_max_body_size 50M;

    # Frontend (static files)
    root /root/tg_final_word_2/frontend/dist;
    index index.html;

    # Frontend routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Admin panel
    location /admin {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Telegram webhook
    location /webhook {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    # API docs
    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /redoc {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files from backend
    location /static/ {
        alias /root/tg_final_word_2/backend/static/;
    }

    # Logging
    access_log /var/log/nginx/finalword_access.log;
    error_log /var/log/nginx/finalword_error.log;
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/finalword.cc /etc/nginx/sites-enabled/

# Test configuration
nginx -t

echo "✅ Nginx configured"
ENDSSH

echo "✅ Nginx configured"

echo ""
echo "🔧 Step 9: Setting up Frontend..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'ENDSSH'
cd /root/tg_final_word_2/frontend

# Install dependencies
npm install

# Build for production
npm run build

echo "✅ Frontend built"
ENDSSH

echo "✅ Frontend built"

echo ""
echo "🔧 Step 10: Creating systemd services..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'ENDSSH'
# Backend service
cat > /etc/systemd/system/finalword-backend.service << 'EOF'
[Unit]
Description=FinalWord Backend Service
After=network.target mysql.service
Wants=mysql.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/tg_final_word_2/backend
Environment="PATH=/root/tg_final_word_2/backend/venv/bin"
ExecStart=/root/tg_final_word_2/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

echo "✅ Systemd services created"
ENDSSH

echo "✅ Systemd services created"

echo ""
echo "🔧 Step 11: Initializing database..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'ENDSSH'
cd /root/tg_final_word_2/backend
source venv/bin/activate

# Run migrations
alembic upgrade head

echo "✅ Database initialized"
ENDSSH

echo "✅ Database initialized"

echo ""
echo "🔧 Step 12: Starting services..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'ENDSSH'
# Start and enable services
systemctl start finalword-backend
systemctl enable finalword-backend

# Restart nginx
systemctl restart nginx

# Check status
sleep 3
systemctl status finalword-backend --no-pager | head -20

echo "✅ Services started"
ENDSSH

echo "✅ Services started"

echo ""
echo "🔧 Step 13: Setting up Telegram webhook..."
sleep 5
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << ENDSSH
cd /root/tg_final_word_2/backend
source venv/bin/activate

# Set webhook
python3 -c "
import requests
import sys

bot_token = '$TELEGRAM_BOT_TOKEN'
webhook_url = 'https://finalword.cc/webhook'

response = requests.post(
    f'https://api.telegram.org/bot{bot_token}/setWebhook',
    json={'url': webhook_url}
)

print(f'Webhook response: {response.json()}')

if response.json().get('ok'):
    print('✅ Webhook set successfully')
    sys.exit(0)
else:
    print('❌ Failed to set webhook')
    sys.exit(1)
"
ENDSSH

echo "✅ Webhook configured"

echo ""
echo "======================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "======================================"
echo ""
echo "📝 Server Information:"
echo "  Domain: https://finalword.cc"
echo "  Backend API: https://finalword.cc/api/v1"
echo "  Admin Panel: https://finalword.cc/admin"
echo "  API Docs: https://finalword.cc/docs"
echo ""
echo "🔐 Database:"
echo "  Name: $DB_NAME"
echo "  User: $DB_USER"
echo "  Pass: $DB_PASS"
echo ""
echo "🤖 Telegram:"
echo "  Webhook: https://finalword.cc/webhook"
echo ""
echo "📊 Check services:"
echo "  ssh root@$SERVER_IP"
echo "  systemctl status finalword-backend"
echo "  systemctl status nginx"
echo ""
echo "📋 View logs:"
echo "  journalctl -u finalword-backend -f"
echo "  tail -f /var/log/nginx/finalword_error.log"
echo ""
