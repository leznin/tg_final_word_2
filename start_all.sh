#!/bin/bash

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

clear

echo -e "${BLUE}=========================================="
echo "  Быстрый запуск Telegram Mini App"
echo -e "==========================================${NC}"
echo ""

# Проверка директории
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Ошибка: Запустите скрипт из корневой директории проекта${NC}"
    exit 1
fi

echo -e "${YELLOW}Этот скрипт покажет команды для запуска всех компонентов${NC}"
echo ""
echo "Для работы Mini App нужно запустить 3 компонента в разных терминалах:"
echo ""

echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}ТЕРМИНАЛ 1: Backend (FastAPI)${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo "cd backend"
echo "source venv/bin/activate"
echo "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo -e "${YELLOW}Должен запуститься на http://0.0.0.0:8000${NC}"
echo ""
read -p "Нажмите Enter когда запустите Backend..."
echo ""

echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}ТЕРМИНАЛ 2: Frontend (Vite + React)${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo "cd frontend"
echo "npm run dev"
echo ""
echo -e "${YELLOW}Должен запуститься на http://localhost:5173${NC}"
echo -e "${YELLOW}После обновления vite.config.ts также на http://0.0.0.0:5173${NC}"
echo ""
read -p "Нажмите Enter когда запустите Frontend..."
echo ""

# Проверка портов
echo -e "${BLUE}Проверка запущенных сервисов...${NC}"
echo ""

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend работает на порту 8000${NC}"
else
    echo -e "${RED}❌ Backend НЕ запущен на порту 8000${NC}"
fi

if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend работает на порту 5173${NC}"
else
    echo -e "${RED}❌ Frontend НЕ запущен на порту 5173${NC}"
fi

echo ""

# Проверка доступности
echo -e "${BLUE}Проверка доступности endpoints...${NC}"
echo ""

if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API доступен${NC}"
else
    echo -e "${RED}❌ Backend API НЕ доступен${NC}"
fi

if curl -s http://localhost:5173/ >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend доступен${NC}"
else
    echo -e "${RED}❌ Frontend НЕ доступен${NC}"
fi

echo ""
echo ""

echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}ТЕРМИНАЛ 3: ngrok (HTTPS туннель)${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo -e "${RED}⚠️  ВАЖНО: ngrok на порт 5173, НЕ на 8000!${NC}"
echo ""
echo "ngrok http --domain=test777.ngrok.app 5173"
echo ""
echo -e "${YELLOW}Или используйте скрипт:${NC}"
echo "./start_ngrok.sh"
echo ""
read -p "Нажмите Enter когда запустите ngrok..."
echo ""

# Финальные инструкции
echo ""
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}Настройка Menu Button${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
echo "Выполните в терминале с Backend:"
echo ""
echo "cd backend"
echo "source venv/bin/activate"
echo "python setup_mini_app.py"
echo ""
read -p "Нажмите Enter когда настроите Menu Button..."
echo ""

echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}✅ ВСЁ ГОТОВО!${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo "Как открыть Mini App в Telegram:"
echo ""
echo "1. Откройте Telegram"
echo "2. Найдите вашего бота"
echo "3. Нажмите кнопку Menu (☰) рядом с полем ввода"
echo "4. Выберите 'User Search'"
echo ""
echo -e "${YELLOW}Отладка:${NC}"
echo "• ngrok dashboard: http://127.0.0.1:4040"
echo "• Backend API docs: http://localhost:8000/docs"
echo "• Frontend: http://localhost:5173"
echo "• Mini App: https://test777.ngrok.app/mini-app.html"
echo ""
echo -e "${YELLOW}Если страница не открывается:${NC}"
echo "1. Проверьте ngrok - должен быть на порту 5173!"
echo "2. Проверьте ngrok dashboard (http://127.0.0.1:4040)"
echo "3. Проверьте консоль браузера (F12) в Telegram"
echo "4. Проверьте логи Backend и Frontend"
echo ""
