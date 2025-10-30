# Telegram Mini App - Поиск пользователей

## Описание

Telegram Mini App для поиска пользователей в системе администрирования Telegram бота. Приложение интегрируется с Telegram Web App API для аутентификации пользователей и предоставляет интерфейс поиска по имени пользователя или username.

## Функциональность

- ✅ Верификация пользователей через Telegram Web App API
- ✅ Поиск пользователей по имени или username
- ✅ Отображение результатов поиска с информацией о пользователях
- ✅ Адаптивный интерфейс для мобильных устройств
- ✅ Haptic feedback для взаимодействия

## API Endpoints

### POST `/api/mini-app/verify-user`
Верификация пользователя на основе данных от Telegram.

**Request Body:**
```json
{
  "init_data": "query_id=AAHdF6IQAAAAAN0XohDhrOrc&user=%7B%22id%22%3A279058397%2C%22first_name%22%3A%22Vladimir%22%2C%22last_name%22%3A%22Gramovich%22%2C%22username%22%3A%22VladimirGramovich%22%2C%22language_code%22%3A%22ru%22%2C%22is_premium%22%3Atrue%7D&auth_date=1662771648&hash=c501b71e775f74ce10e377dea85a7ea24ecd640b223ea86dfe453e0eaed633c61"
}
```

**Проверка подлинности:**
- `init_data` содержит подписанные данные от Telegram Web App
- Backend проверяет HMAC-SHA256 хеш для верификации подлинности данных
- Если хеш не совпадает, запрос отклоняется

**Response:**
```json
{
  "verified": true,
  "telegram_user_id": 123456789,
  "message": "User verified and updated successfully",
  "user_data": {
    "id": 1,
    "username": "ivanov",
    "first_name": "Иван",
    "last_name": "Иванов"
  }
}
```

### POST `/api/mini-app/search-users`
Поиск пользователей по имени или username.

**Request Body:**
```json
{
  "query": "ivan",
  "limit": 20,
  "offset": 0
}
```

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "telegram_id": 123456789,
      "username": "ivanov",
      "first_name": "Иван",
      "last_name": "Иванов",
      "language_code": "ru",
      "is_premium": false,
      "is_bot": false,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

## Структура файлов

### Backend
- `backend/app/schemas/mini_app.py` - Pydantic схемы
- `backend/app/services/mini_app.py` - Бизнес логика
- `backend/app/routers/mini_app.py` - API роутер

### Frontend
- `frontend/mini-app.html` - HTML файл для mini app
- `frontend/src/main-mini-app.tsx` - Entry point для mini app
- `frontend/src/MiniApp.tsx` - Главный компонент mini app
- `frontend/src/pages/MiniAppUserSearch.tsx` - Страница поиска пользователей
- `frontend/src/hooks/useTelegramWebApp.ts` - Хук для работы с Telegram Web App
- `frontend/src/hooks/useUserSearch.ts` - Хук для поиска пользователей
- `frontend/src/types/mini-app.ts` - TypeScript типы

## Настройка в Telegram

1. **В BotFather:**
   - Создайте или настройте существующего бота
   - Выберите "Bot Settings" → "Menu Button"
   - Установите URL для mini app: `https://yourdomain.com/mini-app/user-search`

2. **Альтернативный способ:**
   - Используйте inline клавиатуру или команды для открытия mini app
   - В коде бота отправляйте ссылку: `https://yourdomain.com/mini-app/user-search`

3. **Настройка вебхука:**
   - Убедитесь, что ваш домен доступен по HTTPS
   - Настройте вебхук через BotFather или API: `https://yourdomain.com/webhook`

## Разработка и тестирование

### Запуск backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Запуск frontend
```bash
cd frontend
npm run dev
```

### Сборка для продакшена
```bash
cd frontend
npm run build
```

### Тестирование mini app

**В браузере (для разработки):**
- Откройте: `http://localhost:5173/mini-app/user-search`

**Через backend (production):**
- URL: `https://yourdomain.com/mini-app/user-search`
- Backend автоматически отдаст HTML файл mini app

**В Telegram:**
- Используйте BotFather для настройки menu button
- Или отправьте ссылку через бота: `https://yourdomain.com/mini-app/user-search`

**Отладка:**
- Проверьте логи backend на наличие ошибок
- Убедитесь, что frontend/dist содержит mini-app.html
- Проверьте, что все assets доступны по пути /assets/

## Безопасность

### Верификация пользователей
- **HMAC-SHA256 проверка**: Все данные от Telegram Web App проверяются с использованием криптографического хеша
- **Bot Token**: Для проверки используется секретный bot token из конфигурации
- **Истечение срока**: initData имеет ограниченное время жизни (обычно 24 часа)

### Защита от подделки
- **Хеш-сравнение**: Безопасное сравнение хешей с использованием `hmac.compare_digest()`
- **URL декодирование**: Правильная обработка URL-encoded данных
- **Валидация структуры**: Проверка наличия обязательных полей (hash, user data)

### Дополнительные меры безопасности
- Верификация пользователей происходит только через Telegram Web App API
- Все запросы к API требуют валидных данных от Telegram
- Поиск ограничен минимальной длиной запроса (2 символа)
- API endpoints защищены от чрезмерного использования

## Мобильная оптимизация

- Используется `viewport-fit=cover` для правильного отображения на iPhone X+
- Интерфейс адаптирован для сенсорного ввода
- Haptic feedback для лучшего пользовательского опыта
- Telegram Web App автоматически расширяется на весь экран
