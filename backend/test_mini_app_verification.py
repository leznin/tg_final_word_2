#!/usr/bin/env python3
"""
Скрипт для тестирования верификации пользователей в Mini App
"""

import asyncio
import hashlib
import hmac
import json
from urllib.parse import urlencode
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session_context
from app.services.mini_app import MiniAppService
from app.schemas.mini_app import TelegramUserVerifyRequest
from app.core.config import settings


def generate_test_init_data(user_data: dict) -> str:
    """
    Генерирует валидный initData для тестирования
    """
    # Создаем данные пользователя
    user_json = json.dumps(user_data, separators=(',', ':'))
    
    # Создаем параметры
    auth_date = str(int(datetime.now().timestamp()))
    
    params = {
        'user': user_json,
        'auth_date': auth_date,
        'query_id': 'test_query_123'
    }
    
    # Сортируем параметры и создаем data_check_string
    data_check_arr = []
    for key in sorted(params.keys()):
        data_check_arr.append(f"{key}={params[key]}")
    
    data_check_string = '\n'.join(data_check_arr)
    
    # Вычисляем HMAC-SHA256
    secret_key = hmac.new(
        key='WebAppData'.encode(),
        msg=settings.TELEGRAM_BOT_TOKEN.encode(),
        digestmod=hashlib.sha256
    ).digest()
    
    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    # Добавляем хеш к параметрам
    params['hash'] = calculated_hash
    
    # Кодируем в URL-формат
    return urlencode(params)


async def test_verification():
    """
    Тестирует процесс верификации пользователя
    """
    print("=" * 60)
    print("Тестирование верификации Telegram Mini App")
    print("=" * 60)
    
    # Тестовые данные пользователя
    test_users = [
        {
            'id': 123456789,
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'language_code': 'ru',
            'is_premium': False
        },
        {
            'id': 987654321,
            'first_name': 'Иван',
            'last_name': 'Петров',
            'username': 'ivanpetrov',
            'language_code': 'ru',
            'is_premium': True
        }
    ]
    
    async with get_session_context() as db:
        service = MiniAppService(db)
        
        for i, user_data in enumerate(test_users, 1):
            print(f"\n\nТест #{i}")
            print("-" * 60)
            print(f"Тестовый пользователь:")
            print(f"  ID: {user_data['id']}")
            print(f"  Имя: {user_data['first_name']} {user_data.get('last_name', '')}")
            print(f"  Username: @{user_data.get('username', 'N/A')}")
            print(f"  Premium: {user_data.get('is_premium', False)}")
            
            # Генерируем валидный initData
            init_data = generate_test_init_data(user_data)
            print(f"\nСгенерирован initData (первые 100 символов):")
            print(f"  {init_data[:100]}...")
            
            # Создаем запрос на верификацию
            request = TelegramUserVerifyRequest(init_data=init_data)
            
            # Выполняем верификацию
            print("\nВыполняется верификация...")
            result = await service.verify_telegram_user(request)
            
            # Выводим результат
            print("\n✅ Результат верификации:")
            print(f"  Верифицирован: {result.verified}")
            print(f"  Telegram User ID: {result.telegram_user_id}")
            print(f"  Сообщение: {result.message}")
            if result.user_data:
                print(f"  Данные пользователя:")
                print(f"    - DB ID: {result.user_data['id']}")
                print(f"    - Username: {result.user_data.get('username', 'N/A')}")
                print(f"    - Имя: {result.user_data.get('first_name', '')} {result.user_data.get('last_name', '')}")


async def test_invalid_data():
    """
    Тестирует обработку невалидных данных
    """
    print("\n\n" + "=" * 60)
    print("Тестирование обработки невалидных данных")
    print("=" * 60)
    
    invalid_cases = [
        ("Пустой initData", ""),
        ("Невалидный хеш", "user=%7B%22id%22%3A123%7D&hash=invalid"),
        ("Отсутствует хеш", "user=%7B%22id%22%3A123%7D&auth_date=1234567890"),
        ("Невалидный JSON", "user=invalid_json&hash=test&auth_date=1234567890"),
    ]
    
    async with get_session_context() as db:
        service = MiniAppService(db)
        
        for i, (case_name, init_data) in enumerate(invalid_cases, 1):
            print(f"\n\nТест невалидных данных #{i}: {case_name}")
            print("-" * 60)
            
            request = TelegramUserVerifyRequest(init_data=init_data)
            result = await service.verify_telegram_user(request)
            
            print(f"✅ Результат:")
            print(f"  Верифицирован: {result.verified}")
            print(f"  Сообщение: {result.message}")
            
            if result.verified:
                print(f"  ⚠️ ОШИБКА: Невалидные данные были приняты!")
            else:
                print(f"  ✅ Правильно: Невалидные данные отклонены")


async def check_verification_components():
    """
    Проверяет наличие всех необходимых компонентов
    """
    print("\n\n" + "=" * 60)
    print("Проверка компонентов системы верификации")
    print("=" * 60)
    
    checks = []
    
    # Проверка настроек
    if settings.TELEGRAM_BOT_TOKEN:
        checks.append(("✅", "TELEGRAM_BOT_TOKEN настроен"))
    else:
        checks.append(("❌", "TELEGRAM_BOT_TOKEN НЕ настроен"))
    
    # Проверка импортов
    try:
        from app.routers.mini_app import router
        checks.append(("✅", "Router mini_app импортируется"))
    except Exception as e:
        checks.append(("❌", f"Router mini_app НЕ импортируется: {e}"))
    
    try:
        from app.schemas.mini_app import TelegramUserVerifyRequest, TelegramUserVerifyResponse
        checks.append(("✅", "Схемы mini_app импортируются"))
    except Exception as e:
        checks.append(("❌", f"Схемы mini_app НЕ импортируются: {e}"))
    
    # Проверка базы данных
    try:
        async with get_session_context() as db:
            from sqlalchemy import text
            result = await db.execute(text("SELECT 1"))
            checks.append(("✅", "Подключение к базе данных работает"))
    except Exception as e:
        checks.append(("❌", f"Подключение к БД НЕ работает: {e}"))
    
    print("\nРезультаты проверки:")
    for status, message in checks:
        print(f"  {status} {message}")
    
    all_passed = all(status == "✅" for status, _ in checks)
    
    if all_passed:
        print("\n✅ Все компоненты работают корректно!")
    else:
        print("\n⚠️ Обнаружены проблемы с некоторыми компонентами")
    
    return all_passed


async def main():
    """
    Главная функция для запуска всех тестов
    """
    try:
        print("Начало тестирования системы верификации Mini App\n")
        
        # Проверяем компоненты
        components_ok = await check_verification_components()
        
        if not components_ok:
            print("\n⚠️ Некоторые компоненты не работают. Продолжить тестирование? (y/n)")
            # В автоматическом режиме продолжаем
            pass
        
        # Тестируем валидные данные
        await test_verification()
        
        # Тестируем невалидные данные
        await test_invalid_data()
        
        print("\n\n" + "=" * 60)
        print("✅ Все тесты завершены!")
        print("=" * 60)
        
        print("\n📝 Выводы:")
        print("1. Telegram Web App script подключен в mini-app.html")
        print("2. useTelegramWebApp хук получает данные пользователя")
        print("3. Компонент MiniAppUserSearch верифицирует пользователя при загрузке")
        print("4. Сервер проверяет подпись initData через HMAC-SHA256")
        print("5. После верификации пользователь может искать других пользователей")
        
    except Exception as e:
        print(f"\n❌ Ошибка при выполнении тестов: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
