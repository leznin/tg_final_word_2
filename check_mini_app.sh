#!/bin/bash

# Скрипт для проверки работы Telegram Mini App

echo "=================================="
echo "Проверка Telegram Mini App"
echo "=================================="
echo ""

# Проверка портов
echo "1. Проверка запущенных сервисов:"
echo "   Backend (8000):"
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   ✅ Backend работает на порту 8000"
else
    echo "   ❌ Backend НЕ работает на порту 8000"
fi

echo "   Frontend (5173):"
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   ✅ Frontend работает на порту 5173"
else
    echo "   ❌ Frontend НЕ работает на порту 5173"
fi

echo ""
echo "2. Проверка ngrok:"
if pgrep -x "ngrok" > /dev/null 2>&1; then
    echo "   ✅ ngrok запущен"
    # Проверяем через API ngrok
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o '"public_url":"[^"]*' | grep -o 'https://[^"]*' | head -1)
    if [ -n "$NGROK_URL" ]; then
        echo "   ✅ Публичный URL: $NGROK_URL"
    fi
else
    echo "   ❌ ngrok НЕ запущен"
fi

echo ""
echo "3. Проверка доступности Mini App HTML:"
if [ -f "/Users/s3s3s/Desktop/final word 2.8.1/frontend/mini-app.html" ]; then
    echo "   ✅ mini-app.html существует"
    
    # Проверяем наличие Telegram Web App script
    if grep -q "telegram-web-app.js" "/Users/s3s3s/Desktop/final word 2.8.1/frontend/mini-app.html"; then
        echo "   ✅ Telegram Web App SDK подключен"
    else
        echo "   ❌ Telegram Web App SDK НЕ найден"
    fi
else
    echo "   ❌ mini-app.html НЕ найден"
fi

echo ""
echo "4. Проверка API endpoint для верификации:"
BACKEND_URL="http://localhost:8000/api/v1/mini-app/verify-user"
echo "   Проверка: $BACKEND_URL"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BACKEND_URL" \
    -H "Content-Type: application/json" \
    -d '{"init_data":"test"}' 2>/dev/null)

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "400" ] || [ "$HTTP_CODE" = "422" ]; then
    echo "   ✅ Endpoint доступен (HTTP $HTTP_CODE)"
else
    echo "   ⚠️  Endpoint вернул код: $HTTP_CODE"
fi

echo ""
echo "=================================="
echo "📋 Инструкции для тестирования:"
echo "=================================="
echo ""
echo "1. Убедитесь, что все сервисы запущены:"
echo "   - Backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "   - Frontend: cd frontend && npm run dev"
echo "   - ngrok: ngrok http --domain=test777.ngrok.app 5173"
echo ""
echo "2. Откройте в Telegram Bot (@your_bot):"
echo "   /setmenubutton - установите URL Mini App"
echo "   URL: https://test777.ngrok.app/mini-app.html"
echo ""
echo "3. Откройте Mini App через меню бота"
echo ""
echo "4. Проверьте в консоли браузера (Telegram DevTools):"
echo "   - window.Telegram.WebApp должен быть определен"
echo "   - initData должен быть получен"
echo "   - Запрос на /api/v1/mini-app/verify-user должен быть успешным"
echo ""
echo "=================================="
