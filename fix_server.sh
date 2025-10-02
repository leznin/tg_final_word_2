#!/bin/bash

# Fix script for finalword.cc server
set -e

echo "🚀 STARTING SERVER FIX SCRIPT"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    error "This script must be run as root"
    exit 1
fi

# Function to backup file
backup_file() {
    local file=$1
    if [[ -f "$file" ]]; then
        cp "$file" "${file}.backup.$(date +%Y%m%d_%H%M%S)"
        log "Backed up $file"
    fi
}

# 1. Check system status
log "Checking system status..."
success "System check completed"

# 2. Check Docker containers
log "Checking Docker containers..."
if command -v docker &> /dev/null; then
    docker ps -a
    if docker ps | grep -q "fin-app"; then
        success "Docker container 'fin-app' is running"
    else
        warning "Docker container 'fin-app' not found or not running"
        log "Checking for any running containers..."
        docker ps
    fi
else
    error "Docker not installed"
fi

# 3. Check nginx configuration
log "Checking nginx configuration..."
if command -v nginx &> /dev/null; then
    if nginx -t 2>/dev/null; then
        success "Nginx configuration is valid"
    else
        error "Nginx configuration has errors"
        nginx -t
    fi

    # Check nginx sites
    if [[ -f "/etc/nginx/sites-available/default" ]]; then
        log "Current nginx default site config:"
        cat /etc/nginx/sites-available/default | head -50
    fi
else
    error "Nginx not installed"
fi

# 4. Fix nginx configuration for API proxy
log "Fixing nginx configuration..."

NGINX_CONFIG="/etc/nginx/sites-available/default"
backup_file "$NGINX_CONFIG"

# Create new nginx config
cat > "$NGINX_CONFIG" << 'EOF'
server {
    listen 80;
    server_name finalword.cc www.finalword.cc;

    # Frontend (React app)
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Handle client-side routing
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS headers
        add_header 'Access-Control-Allow-Origin' 'https://finalword.cc' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;

        # Handle preflight requests
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' 'https://finalword.cc' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain charset=UTF-8';
            add_header 'Content-Length' 0;
            return 204;
        }
    }

    # Webhook endpoint
    location /webhook {
        proxy_pass http://localhost:8000/webhook;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Admin panel
    location /admin/ {
        proxy_pass http://localhost:8000/admin/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        proxy_pass http://localhost:8000/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

success "Updated nginx configuration"

# Test nginx config
if nginx -t; then
    success "Nginx configuration test passed"
    systemctl reload nginx
    success "Nginx reloaded"
else
    error "Nginx configuration test failed"
    exit 1
fi

# 5. Check and fix Docker setup
log "Checking Docker setup..."

# Check if docker-compose file exists
if [[ -f "/root/docker-compose.yml" ]]; then
    log "Found docker-compose.yml"
    cat /root/docker-compose.yml
else
    warning "docker-compose.yml not found in /root"
    # Look for it in other common locations
    find /home -name "docker-compose.yml" 2>/dev/null || true
fi

# Check if app directory exists
if [[ -d "/root/app" ]]; then
    log "Found /root/app directory"
    ls -la /root/app
else
    warning "/root/app directory not found"
fi

# Try to start/restart Docker containers
log "Attempting to start Docker containers..."
if [[ -f "/root/docker-compose.yml" ]]; then
    cd /root
    docker-compose down || true
    docker-compose up -d
    sleep 5
    docker-compose ps
else
    warning "No docker-compose.yml found, trying to run container directly"
    # Try to run the container directly if image exists
    if docker images | grep -q "fin-app"; then
        docker run -d -p 8000:8000 --name fin-app fin-app
    fi
fi

# 6. Check backend API
log "Checking backend API..."
sleep 10

API_ENDPOINTS=(
    "http://localhost:8000/health"
    "http://localhost:8000/api/v1/chats/"
    "http://localhost:8000/api/v1/dashboard/"
    "http://localhost:8000/api/v1/openrouter/settings"
)

for endpoint in "${API_ENDPOINTS[@]}"; do
    log "Testing $endpoint..."
    if curl -s --max-time 10 "$endpoint" > /dev/null; then
        success "$endpoint is accessible"
    else
        error "$endpoint is not accessible"
    fi
done

# 7. Check database connection
log "Checking database connection..."
if command -v mysql &> /dev/null; then
    # Try to connect to database
    if mysql -h localhost -u root -p'696578As!!!!' -e "SHOW DATABASES;" 2>/dev/null | grep -q "final"; then
        success "Database connection successful"
        mysql -h localhost -u root -p'696578As!!!!' -e "USE final; SHOW TABLES;" 2>/dev/null
    else
        error "Database connection failed"
    fi
else
    warning "MySQL client not found"
fi

# 8. Check frontend
log "Checking frontend..."
if [[ -d "/root/frontend" ]]; then
    log "Found frontend directory"
    cd /root/frontend
    if [[ -f "package.json" ]]; then
        log "Installing frontend dependencies..."
        npm install || warning "npm install failed"
        log "Building frontend..."
        npm run build || warning "npm run build failed"
    fi
else
    warning "Frontend directory not found"
fi

# 9. Start frontend if not running
log "Checking frontend process..."
if ! pgrep -f "node.*3000" > /dev/null; then
    if [[ -d "/root/frontend" ]]; then
        cd /root/frontend
        log "Starting frontend..."
        npm run dev -- --host 0.0.0.0 --port 3000 &
        sleep 5
        if pgrep -f "node.*3000" > /dev/null; then
            success "Frontend started on port 3000"
        else
            error "Failed to start frontend"
        fi
    fi
else
    success "Frontend already running"
fi

# 10. Final test
log "Running final API tests..."
sleep 5

PUBLIC_ENDPOINTS=(
    "https://finalword.cc/api/v1/chats/"
    "https://finalword.cc/api/v1/dashboard/"
    "https://finalword.cc/api/v1/openrouter/settings"
)

for endpoint in "${PUBLIC_ENDPOINTS[@]}"; do
    log "Testing public endpoint $endpoint..."
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" --max-time 10 "$endpoint" 2>/dev/null || echo "ERROR")
    http_code=$(echo "$response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')

    if [[ "$http_code" == "200" ]]; then
        success "$endpoint returns 200 OK"
    elif [[ "$http_code" == "404" ]]; then
        error "$endpoint returns 404 Not Found"
    else
        warning "$endpoint returns HTTP $http_code"
    fi
done

# 11. Show final status
log "Final system status:"
echo ""
echo "Running processes:"
ps aux | grep -E "(nginx|docker|node|uvicorn|python)" | grep -v grep || true

echo ""
echo "Listening ports:"
netstat -tlnp 2>/dev/null | grep -E ":(80|443|3000|8000)" || true

echo ""
echo "Docker containers:"
docker ps 2>/dev/null || echo "Docker not available"

success "Server fix script completed!"
echo ""
echo "Please test your application at https://finalword.cc"
echo "If issues persist, check the logs above for error messages."
