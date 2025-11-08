#!/usr/bin/env python3
"""
Скрипт для установки Menu Button для Telegram Mini App
"""

import os
import json
import urllib.request
import urllib.parse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_DOMAIN = os.getenv("APP_DOMAIN")

def make_request(url, method="GET", data=None):
    """Make HTTP request"""
    try:
        headers = {'Content-Type': 'application/json'}
        
        if data:
            data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
        else:
            req = urllib.request.Request(url, headers=headers, method=method)

        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def get_menu_button():
    """Get current menu button"""
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found in .env")
        return None

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMenuButton"
    data = make_request(url)

    if data and data.get("ok"):
        return data.get("result", {})
    return None

def set_menu_button():
    """Set menu button for Mini App"""
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found in .env")
        return False

    if not APP_DOMAIN:
        print("❌ APP_DOMAIN not found in .env")
        return False

    # Формируем URL для Mini App
    mini_app_url = f"{APP_DOMAIN}/mini-app.html"
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setChatMenuButton"
    
    params = {
        "menu_button": {
            "type": "web_app",
            "text": "User Search",
            "web_app": {
                "url": mini_app_url
            }
        }
    }

    data = make_request(url, method="POST", data=params)

    if data and data.get("ok"):
        print("✅ Menu button set successfully!")
        print(f"   Text: User Search")
        print(f"   URL: {mini_app_url}")
        return True
    else:
        print("❌ Failed to set menu button")
        if data:
            print(f"   Error: {data.get('description', 'Unknown error')}")
        return False

def check_bot_info():
    """Get bot information"""
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found in .env")
        return None

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    data = make_request(url)

    if data and data.get("ok"):
        return data.get("result", {})
    return None

def main():
    print("=" * 60)
    print("Настройка Telegram Mini App Menu Button")
    print("=" * 60)
    print()

    # Check configuration
    print("📋 Проверка конфигурации:")
    print(f"   BOT_TOKEN: {'✅ Установлен' if BOT_TOKEN else '❌ Не найден'}")
    print(f"   APP_DOMAIN: {APP_DOMAIN if APP_DOMAIN else '❌ Не найден'}")
    print()

    if not BOT_TOKEN or not APP_DOMAIN:
        print("❌ Необходимо установить BOT_TOKEN и APP_DOMAIN в .env файле")
        return

    # Get bot info
    print("🤖 Информация о боте:")
    bot_info = check_bot_info()
    if bot_info:
        print(f"   Username: @{bot_info.get('username', 'N/A')}")
        print(f"   Name: {bot_info.get('first_name', 'N/A')}")
        print(f"   ID: {bot_info.get('id', 'N/A')}")
    else:
        print("   ❌ Не удалось получить информацию о боте")
        return
    print()

    # Get current menu button
    print("📱 Текущий Menu Button:")
    current_button = get_menu_button()
    if current_button:
        button_type = current_button.get('type', 'default')
        print(f"   Type: {button_type}")
        if button_type == 'web_app':
            print(f"   Text: {current_button.get('text', 'N/A')}")
            print(f"   URL: {current_button.get('web_app', {}).get('url', 'N/A')}")
        else:
            print(f"   (Стандартная кнопка menu)")
    print()

    # Set new menu button
    print("🔧 Установка нового Menu Button...")
    if set_menu_button():
        print()
        print("=" * 60)
        print("✅ Настройка завершена успешно!")
        print("=" * 60)
        print()
        print("📱 Как открыть Mini App:")
        print("   1. Найдите вашего бота в Telegram")
        print(f"      @{bot_info.get('username', 'your_bot')}")
        print("   2. Нажмите кнопку Menu (☰) рядом с полем ввода")
        print("   3. Выберите 'User Search'")
        print()
        print("🔍 Для отладки:")
        print(f"   - ngrok Web Interface: http://127.0.0.1:4040")
        print(f"   - Mini App URL: {APP_DOMAIN}/mini-app.html")
        print(f"   - Backend API: {APP_DOMAIN}/api/v1/docs")
    else:
        print()
        print("❌ Не удалось установить Menu Button")
        print()
        print("Возможные причины:")
        print("   1. Неверный TELEGRAM_BOT_TOKEN")
        print("   2. Неверный формат APP_DOMAIN")
        print("   3. Проблемы с сетью")

if __name__ == "__main__":
    main()
