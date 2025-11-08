#!/bin/bash

# Скрипт для запуска ngrok на правильный порт (8000 - backend)

echo "=========================================="
echo "  Запуск ngrok для Telegram Mini App"
echo "=========================================="
echo ""
echo "⚠️  ВАЖНО: ngrok должен перенаправлять на порт 8000 (backend)"
echo "           Backend раздаёт статические файлы из frontend/dist"
echo ""
echo "Схема: Telegram → ngrok → Backend(8000) → static files + API"
echo ""
echo "=========================================="
echo ""

# Проверяем, запущен ли backend
if ! lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "❌ ОШИБКА: Backend не запущен на порту 8000!"
    echo ""
    echo "Запустите backend:"
    echo "  cd backend"
    echo "  source venv/bin/activate"
    echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    exit 1
fi

echo "✅ Backend запущен на порту 8000"
echo ""

# Проверяем, собран ли frontend
if [ ! -d "../frontend/dist" ] && [ ! -d "frontend/dist" ]; then
    echo "⚠️  ПРЕДУПРЕЖДЕНИЕ: Frontend не собран!"
    echo ""
    echo "Соберите frontend:"
    echo "  cd frontend"
    echo "  npm run build"
    echo ""
fi

if [ -d "../frontend/dist" ] || [ -d "frontend/dist" ]; then
    echo "✅ Frontend собран (dist/ существует)"
    echo ""
fi

# Убиваем существующие процессы ngrok
if pgrep -x "ngrok" >/dev/null; then
    echo "🔄 Останавливаем существующий ngrok..."
    pkill -x ngrok
    sleep 2
fi

echo "🚀 Запуск ngrok на порт 8000..."
echo ""
echo "Доменное имя: test777.ngrok.app"
echo "Порт: 8000 (Backend + Static Files)"
echo ""

# Запуск ngrok
ngrok http --domain=test777.ngrok.app 8000
