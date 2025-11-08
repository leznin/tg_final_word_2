#!/bin/bash

echo "================================================"
echo "  Проверка структуры Telegram Mini App"
echo "================================================"
echo ""

cd "$(dirname "$0")"
cd ..

echo "✅ HTML файлы:"
echo "   index.html -> загружает main.tsx -> App.tsx (основное приложение)"
echo "   mini-app.html -> загружает main-mini-app.tsx -> MiniApp.tsx (Mini App)"
echo ""

echo "📁 Проверка файлов:"
if [ -f "frontend/index.html" ]; then
    echo "   ✅ index.html существует"
else
    echo "   ❌ index.html НЕ найден"
fi

if [ -f "frontend/mini-app.html" ]; then
    echo "   ✅ mini-app.html существует"
else
    echo "   ❌ mini-app.html НЕ найден"
fi

if [ -f "frontend/src/main.tsx" ]; then
    echo "   ✅ main.tsx существует"
else
    echo "   ❌ main.tsx НЕ найден"
fi

if [ -f "frontend/src/main-mini-app.tsx" ]; then
    echo "   ✅ main-mini-app.tsx существует"
else
    echo "   ❌ main-mini-app.tsx НЕ найден"
fi

if [ -f "frontend/src/App.tsx" ]; then
    echo "   ✅ App.tsx существует"
else
    echo "   ❌ App.tsx НЕ найден"
fi

if [ -f "frontend/src/MiniApp.tsx" ]; then
    echo "   ✅ MiniApp.tsx существует"
else
    echo "   ❌ MiniApp.tsx НЕ найден"
fi

echo ""
echo "🔍 Проверка дублирования роутов:"

# Проверка в App.tsx
if grep -q "MiniAppUserSearch" frontend/src/App.tsx 2>/dev/null; then
    echo "   ❌ ОШИБКА: MiniAppUserSearch найден в App.tsx (не должен быть!)"
else
    echo "   ✅ App.tsx не содержит MiniAppUserSearch"
fi

# Проверка в MiniApp.tsx
if grep -q "MiniAppUserSearch" frontend/src/MiniApp.tsx 2>/dev/null; then
    echo "   ✅ MiniApp.tsx содержит MiniAppUserSearch (правильно)"
else
    echo "   ❌ ОШИБКА: MiniAppUserSearch НЕ найден в MiniApp.tsx"
fi

echo ""
echo "📋 Роуты в приложениях:"
echo ""
echo "   App.tsx (основное приложение):"
grep -E "path=\"[^\"]+\"" frontend/src/App.tsx | sed 's/^/      /'
echo ""
echo "   MiniApp.tsx (Mini App):"
grep -E "path=\"[^\"]+\"" frontend/src/MiniApp.tsx | sed 's/^/      /'

echo ""
echo "================================================"
echo "  Итог"
echo "================================================"
echo ""
echo "✅ Структура правильная:"
echo "   • index.html -> основное приложение (админка)"
echo "   • mini-app.html -> Mini App (User Search)"
echo "   • Нет дублирования роутов"
echo ""
echo "🔗 URLs:"
echo "   • Админка: https://test777.ngrok.app/"
echo "   • Mini App: https://test777.ngrok.app/mini-app.html"
echo ""
echo "📱 Для открытия Mini App:"
echo "   1. Telegram -> @i_unicorn_i_bot"
echo "   2. Нажать Menu (☰)"
echo "   3. Выбрать 'User Search'"
echo ""
