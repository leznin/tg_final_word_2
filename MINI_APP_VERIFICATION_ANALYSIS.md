# Анализ системы верификации Telegram Mini App

## Обзор

Данный документ содержит анализ системы верификации пользователей на странице `/mini-app/user-search` в Telegram Mini App.

## Архитектура системы

### 1. Frontend (React + TypeScript)

#### 1.1 Загрузка Telegram Web App SDK

**Файл:** `frontend/mini-app.html`

```html
<script src="https://telegram.org/js/telegram-web-app.js?59"></script>
```

✅ **Статус:** SDK подключен корректно в HTML файле

#### 1.2 Хук useTelegramWebApp

**Файл:** `frontend/src/hooks/useTelegramWebApp.ts`

**Функциональность:**
- ✅ Инициализирует Telegram Web App (`webApp.ready()`)
- ✅ Разворачивает приложение на полный экран (`webApp.expand()`)
- ✅ Получает `initData` для верификации на backend
- ✅ Извлекает данные пользователя из `webApp.initDataUnsafe.user`
- ✅ Обрабатывает темы (светлая/темная)
- ✅ Предоставляет haptic feedback функции

**Возвращаемые данные:**
```typescript
{
  isReady: boolean,           // Готовность Web App
  user: TelegramUserData,     // Данные пользователя
  initData: string,           // Строка для верификации на backend
  error: string | null,       // Ошибки инициализации
  theme: TelegramThemeData,   // Тема приложения
  // ... методы управления
}
```

#### 1.3 Компонент MiniAppUserSearch

**Файл:** `frontend/src/pages/MiniAppUserSearch.tsx`

**Процесс верификации:**

```typescript
useEffect(() => {
  if (isReady && initData && !isVerified) {
    verifyUser()
  }
}, [isReady, initData, isVerified])
```

**Шаги верификации:**

1. ✅ Ждет инициализации Telegram Web App (`isReady`)
2. ✅ Проверяет наличие `initData`
3. ✅ Отправляет запрос на `/api/v1/mini-app/verify-user`
4. ✅ Сохраняет статус верификации
5. ✅ Показывает соответствующий UI в зависимости от статуса

**Состояния UI:**
- Loading: "Initializing..." - пока Web App загружается
- Error: Если произошла ошибка инициализации
- No User: Если не удалось получить данные пользователя
- Verifying: "Verifying user..." - во время проверки на backend
- Verified: Основной интерфейс поиска пользователей

### 2. Backend (FastAPI + Python)

#### 2.1 API Endpoint

**Файл:** `backend/app/routers/mini_app.py`

```python
@router.post("/verify-user", response_model=TelegramUserVerifyResponse)
async def verify_telegram_user(
    request: TelegramUserVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    service = MiniAppService(db)
    return await service.verify_telegram_user(request)
```

✅ **Endpoint:** `POST /api/v1/mini-app/verify-user`

#### 2.2 Сервис верификации

**Файл:** `backend/app/services/mini_app.py`

**Метод:** `_verify_telegram_init_data(init_data: str)`

**Алгоритм верификации (соответствует официальной документации Telegram):**

1. ✅ Парсинг URL-encoded строки `initData`
2. ✅ Извлечение хеша из параметров
3. ✅ Создание `data_check_string` из отсортированных параметров
4. ✅ Вычисление секретного ключа:
   ```python
   secret_key = HMAC-SHA256('WebAppData', TELEGRAM_BOT_TOKEN)
   ```
5. ✅ Вычисление хеша данных:
   ```python
   calculated_hash = HMAC-SHA256(secret_key, data_check_string)
   ```
6. ✅ Сравнение хешей через `hmac.compare_digest()` (защита от timing attacks)
7. ✅ Извлечение и парсинг данных пользователя из JSON

**Метод:** `verify_telegram_user(request: TelegramUserVerifyRequest)`

**Логика:**

1. ✅ Верифицирует `initData` через HMAC-SHA256
2. ✅ Извлекает данные пользователя
3. ✅ Ищет пользователя в БД по `telegram_id`
4. ✅ Обновляет существующего пользователя или создает нового
5. ✅ Возвращает результат верификации с данными пользователя

## Схема взаимодействия

```
┌─────────────────────────────────────────────────────────────────┐
│                     Telegram Mini App                            │
│                                                                   │
│  1. Пользователь открывает Mini App в Telegram                   │
│  2. Telegram инициализирует window.Telegram.WebApp               │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              useTelegramWebApp Hook (Frontend)                   │
│                                                                   │
│  1. webApp.ready() - инициализация                               │
│  2. webApp.expand() - полноэкранный режим                        │
│  3. Получение initData (подписанная строка)                      │
│  4. Получение user данных из initDataUnsafe                      │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│            MiniAppUserSearch Component                           │
│                                                                   │
│  1. useEffect следит за isReady и initData                       │
│  2. Вызывает verifyUser() при инициализации                      │
│  3. Отправляет POST /api/v1/mini-app/verify-user                 │
│     Body: { init_data: "auth_date=...&hash=...&user=..." }      │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                               │
│                                                                   │
│  Endpoint: POST /mini-app/verify-user                            │
│  Router: app/routers/mini_app.py                                 │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│           MiniAppService.verify_telegram_user()                  │
│                                                                   │
│  1. _verify_telegram_init_data(init_data)                        │
│     - Парсинг параметров                                         │
│     - Проверка HMAC-SHA256 подписи                               │
│     - Извлечение user данных                                     │
│                                                                   │
│  2. Поиск пользователя в БД по telegram_id                       │
│                                                                   │
│  3. Создание/обновление пользователя                             │
│                                                                   │
│  4. Возврат результата:                                          │
│     {                                                            │
│       "verified": true,                                          │
│       "telegram_user_id": 123456789,                             │
│       "message": "User verified successfully",                   │
│       "user_data": {...}                                         │
│     }                                                            │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                Frontend: Обработка ответа                        │
│                                                                   │
│  if (response.verified) {                                        │
│    setIsVerified(true)                                           │
│    hapticFeedback.notification('success')                        │
│    // Показываем интерфейс поиска                                │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

## Безопасность

### ✅ Реализованные меры безопасности

1. **HMAC-SHA256 подпись**
   - Telegram подписывает `initData` с использованием секретного ключа бота
   - Backend проверяет подпись, используя тот же алгоритм
   - Невозможно подделать без знания `TELEGRAM_BOT_TOKEN`

2. **Защита от timing attacks**
   - Используется `hmac.compare_digest()` для безопасного сравнения хешей

3. **Валидация данных**
   - Проверка наличия обязательных полей
   - Парсинг JSON в try-catch блоке
   - Проверка типов данных

4. **Обработка ошибок**
   - Все ошибки логируются
   - Пользователю возвращаются безопасные сообщения
   - Не раскрывается внутренняя структура системы

### ⚠️ Рекомендации по улучшению

1. **Проверка временных меток**
   - Добавить проверку `auth_date` для предотвращения replay attacks
   - Отклонять запросы старше определенного времени (например, 24 часа)

2. **Rate limiting**
   - Ограничить количество запросов на верификацию с одного IP
   - Защита от брутфорса

3. **Логирование**
   - Улучшить логирование попыток верификации
   - Отслеживать неудачные попытки

## Тестирование

### Созданный тест-скрипт

**Файл:** `backend/test_mini_app_verification.py`

**Функциональность:**

1. ✅ Проверка всех компонентов системы
2. ✅ Генерация валидных `initData` для тестирования
3. ✅ Тестирование успешной верификации
4. ✅ Тестирование обработки невалидных данных
5. ✅ Проверка создания/обновления пользователей в БД

**Запуск:**
```bash
cd backend
source venv/bin/activate
python test_mini_app_verification.py
```

## Проверочный чеклист

### Frontend
- ✅ Telegram Web App SDK подключен в HTML
- ✅ `useTelegramWebApp` инициализирует Web App
- ✅ Получает `initData` для верификации
- ✅ Получает данные пользователя
- ✅ Компонент верифицирует пользователя при загрузке
- ✅ Обрабатывает различные состояния (loading, error, verified)
- ✅ Показывает соответствующий UI для каждого состояния

### Backend
- ✅ Endpoint `/mini-app/verify-user` существует
- ✅ Реализован алгоритм проверки HMAC-SHA256
- ✅ Парсинг и валидация `initData`
- ✅ Извлечение данных пользователя из JSON
- ✅ Создание/обновление пользователей в БД
- ✅ Возврат структурированного ответа
- ✅ Обработка ошибок

### Безопасность
- ✅ Проверка подписи через HMAC-SHA256
- ✅ Использование `hmac.compare_digest()`
- ✅ Валидация входных данных
- ✅ Обработка исключений
- ⚠️ Проверка временных меток (рекомендуется добавить)
- ⚠️ Rate limiting (рекомендуется добавить)

## Вывод

**✅ Система верификации работает корректно:**

1. При открытии `/mini-app/user-search` в Telegram Mini App:
   - Загружается Telegram Web App SDK
   - Инициализируется `window.Telegram.WebApp`
   - Получаются данные пользователя и `initData`

2. Автоматически запускается процесс верификации:
   - `initData` отправляется на backend
   - Backend проверяет HMAC-SHA256 подпись
   - Пользователь создается/обновляется в БД
   - Frontend получает подтверждение верификации

3. После успешной верификации:
   - Пользователь может искать других пользователей
   - Доступны все функции Mini App

4. Безопасность:
   - Невозможно подделать данные без знания `TELEGRAM_BOT_TOKEN`
   - Все критичные операции защищены
   - Ошибки обрабатываются корректно

## Дополнительная информация

### Ссылки на код

- Frontend Hook: `frontend/src/hooks/useTelegramWebApp.ts`
- Frontend Component: `frontend/src/pages/MiniAppUserSearch.tsx`
- Backend Router: `backend/app/routers/mini_app.py`
- Backend Service: `backend/app/services/mini_app.py`
- Backend Schemas: `backend/app/schemas/mini_app.py`

### Официальная документация Telegram

- [Telegram Web Apps](https://core.telegram.org/bots/webapps)
- [Validating data received via the Web App](https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app)
