#!/bin/bash

# Скрипт для запуска ngrok на правильный порт (5173 - frontend)

echo "=========================================="
echo "  Запуск ngrok для Telegram Mini App"
echo "=========================================="
echo ""
echo "⚠️  ВАЖНО: ngrok должен перенаправлять на порт 5173 (frontend)"
echo "           НЕ на порт 8000 (backend)!"
echo ""
echo "Причина: Vite dev server на порту 5173 проксирует"
echo "         запросы /api на backend (8000)"
echo ""
echo "Схема: Telegram → ngrok → Vite(5173) → Backend(8000)"
echo ""
echo "=========================================="
echo ""

# Проверяем, запущен ли frontend
if ! lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "❌ ОШИБКА: Frontend не запущен на порту 5173!"
    echo ""
    echo "Запустите frontend:"
    echo "  cd frontend"
    echo "  npm run dev"
    echo ""
    exit 1
fi

echo "✅ Frontend запущен на порту 5173"
echo ""

# Проверяем, запущен ли backend
if ! lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  ПРЕДУПРЕЖДЕНИЕ: Backend не запущен на порту 8000!"
    echo ""
    echo "Запустите backend:"
    echo "  cd backend"
    echo "  source venv/bin/activate"
    echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
fi

echo "✅ Backend запущен на порту 8000"
echo ""

# Убиваем существующие процессы ngrok
if pgrep -x "ngrok" >/dev/null; then
    echo "🔄 Останавливаем существующий ngrok..."
    pkill -x ngrok
    sleep 2
fi

echo "🚀 Запуск ngrok на порт 5173..."
echo ""
echo "Доменное имя: test777.ngrok.app"
echo "Порт: 5173 (Frontend)"
echo ""

# Запуск ngrok
ngrok http --domain=test777.ngrok.app 5173
