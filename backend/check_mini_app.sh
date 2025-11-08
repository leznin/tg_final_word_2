#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================================================"
echo "  Проверка конфигурации Telegram Mini App"
echo "======================================================================"
echo ""

# Переход в директорию backend
cd "$(dirname "$0")"

# Проверка .env файла
echo "📋 Проверка .env файла..."
if [ -f ".env" ]; then
    echo -e "   ${GREEN}✅${NC} Файл .env найден"
    
    # Проверка переменных
    if grep -q "TELEGRAM_BOT_TOKEN=" .env; then
        echo -e "   ${GREEN}✅${NC} TELEGRAM_BOT_TOKEN установлен"
    else
        echo -e "   ${RED}❌${NC} TELEGRAM_BOT_TOKEN не найден"
    fi
    
    if grep -q "APP_DOMAIN=" .env; then
        APP_DOMAIN=$(grep "APP_DOMAIN=" .env | cut -d '=' -f2)
        echo -e "   ${GREEN}✅${NC} APP_DOMAIN: $APP_DOMAIN"
    else
        echo -e "   ${RED}❌${NC} APP_DOMAIN не найден"
    fi
else
    echo -e "   ${RED}❌${NC} Файл .env не найден"
    exit 1
fi
echo ""

# Проверка виртуального окружения
echo "🐍 Проверка Python окружения..."
if [ -d "venv" ]; then
    echo -e "   ${GREEN}✅${NC} Виртуальное окружение найдено"
else
    echo -e "   ${YELLOW}⚠️${NC}  Виртуальное окружение не найдено"
fi
echo ""

# Проверка процессов
echo "🔄 Проверка запущенных процессов..."

# Проверка Backend
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "   ${GREEN}✅${NC} Backend работает на порту 8000"
else
    echo -e "   ${RED}❌${NC} Backend НЕ запущен на порту 8000"
fi

# Проверка Frontend
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "   ${GREEN}✅${NC} Frontend работает на порту 5173"
else
    echo -e "   ${RED}❌${NC} Frontend НЕ запущен на порту 5173"
fi

# Проверка ngrok
if pgrep -x "ngrok" >/dev/null; then
    echo -e "   ${GREEN}✅${NC} ngrok запущен"
    echo ""
    echo "   📊 ngrok Web Interface: http://127.0.0.1:4040"
else
    echo -e "   ${RED}❌${NC} ngrok НЕ запущен"
fi
echo ""

# Проверка доступности localhost endpoints
echo "🌐 Проверка доступности endpoints..."

# Backend health
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo -e "   ${GREEN}✅${NC} Backend health endpoint доступен"
else
    echo -e "   ${RED}❌${NC} Backend health endpoint НЕ доступен"
fi

# Frontend
if curl -s http://localhost:5173/ >/dev/null 2>&1; then
    echo -e "   ${GREEN}✅${NC} Frontend доступен"
else
    echo -e "   ${RED}❌${NC} Frontend НЕ доступен"
fi
echo ""

# Проверка файлов Mini App
echo "📁 Проверка файлов Mini App..."
cd ..
if [ -f "frontend/mini-app.html" ]; then
    echo -e "   ${GREEN}✅${NC} mini-app.html найден"
    
    # Проверка наличия Telegram Web App script
    if grep -q "telegram-web-app.js" frontend/mini-app.html; then
        echo -e "   ${GREEN}✅${NC} Telegram Web App SDK подключен"
    else
        echo -e "   ${RED}❌${NC} Telegram Web App SDK не найден в HTML"
    fi
else
    echo -e "   ${RED}❌${NC} mini-app.html не найден"
fi

if [ -f "frontend/src/pages/MiniAppUserSearch.tsx" ]; then
    echo -e "   ${GREEN}✅${NC} MiniAppUserSearch компонент найден"
else
    echo -e "   ${RED}❌${NC} MiniAppUserSearch компонент не найден"
fi

if [ -f "frontend/src/hooks/useTelegramWebApp.ts" ]; then
    echo -e "   ${GREEN}✅${NC} useTelegramWebApp хук найден"
else
    echo -e "   ${RED}❌${NC} useTelegramWebApp хук не найден"
fi
echo ""

# Итоговая информация
echo "======================================================================"
echo "  Итоговая информация"
echo "======================================================================"
echo ""
echo "📝 Следующие шаги:"
echo ""
echo "   1. Убедитесь, что все компоненты запущены:"
echo "      • Backend: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "      • Frontend: npm run dev"
echo "      • ngrok: ngrok http 5173"
echo ""
echo "   2. Настройте Menu Button:"
echo "      cd backend"
echo "      source venv/bin/activate"
echo "      python setup_mini_app.py"
echo ""
echo "   3. Откройте в Telegram:"
echo "      • Найдите вашего бота"
echo "      • Нажмите кнопку Menu (☰)"
echo "      • Выберите 'User Search'"
echo ""
echo "   4. Проверьте работу:"
echo "      • Должна пройти автоматическая верификация"
echo "      • Должен открыться интерфейс поиска пользователей"
echo ""
echo "🔍 Отладка:"
echo "   • ngrok dashboard: http://127.0.0.1:4040"
echo "   • Backend API docs: http://localhost:8000/docs"
echo "   • Frontend: http://localhost:5173"
echo ""
