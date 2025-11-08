# Инструкция по запуску Telegram Mini App

## Проблема
Telegram Mini App должен работать через HTTPS, поэтому нужен ngrok для туннелирования локального сервера.

## Правильная настройка

### Архитектура:
```
Telegram → ngrok (HTTPS) → Vite Dev Server (5173) → Backend API (8000)
                            └─ Proxy /api → localhost:8000
```

## Шаги запуска

### 1. Запустите Backend (терминал 1)
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Запустите Frontend (терминал 2)
```bash
cd frontend
npm run dev
```

Frontend теперь запустится на `http://0.0.0.0:5173` (доступен из сети)

### 3. Запустите ngrok (терминал 3)
```bash
ngrok http 5173
```

Вы получите URL типа: `https://xxxx-xxxx.ngrok.app`

### 4. Настройте Telegram Bot

Отправьте команду в BotFather или используйте скрипт:

```bash
cd backend
source venv/bin/activate
python setup_webhook.py
```

Или вручную установите Menu Button URL в BotFather:
- `/setmenubutton`
- Выберите вашего бота
- Укажите URL: `https://your-ngrok-url.ngrok.app/mini-app.html`

### 5. Проверьте настройки

В файле `backend/.env` должно быть:
```env
APP_DOMAIN=https://your-ngrok-url.ngrok.app
TELEGRAM_BOT_TOKEN=ваш_токен
```

## Проверка работоспособности

### 1. Откройте в браузере
```
https://your-ngrok-url.ngrok.app/mini-app.html
```

Должна отобразиться ошибка "Telegram Web App не инициализирован" - это нормально, т.к. браузер не является Telegram клиентом.

### 2. Откройте в Telegram
- Найдите своего бота
- Нажмите кнопку Menu (☰) рядом с полем ввода
- Откроется Mini App

### 3. Проверьте логи

**Backend (терминал 1):**
Должны появиться запросы:
```
INFO: POST /api/v1/mini-app/verify-user
INFO: POST /api/v1/mini-app/search-users
```

**Frontend (терминал 2):**
Должны появиться запросы к статическим файлам:
```
GET /mini-app.html
GET /src/main-mini-app.tsx
GET /src/MiniApp.tsx
```

**ngrok (терминал 3 или Web Interface http://127.0.0.1:4040):**
Должны быть запросы от Telegram серверов.

## Отладка

### Проблема: "404 Not Found" для node_modules
**Причина:** Запросы идут напрямую на backend, минуя Vite
**Решение:** Убедитесь, что ngrok перенаправляет на порт 5173, а не 8000

### Проблема: "Telegram Web App не инициализирован"
**Причина:** Открыто не в Telegram клиенте
**Решение:** Откройте через Menu Button в Telegram боте

### Проблема: "User verification failed"
**Причина:** Неверный TELEGRAM_BOT_TOKEN или проблемы с initData
**Решение:** 
1. Проверьте токен в `.env`
2. Проверьте логи backend
3. Убедитесь, что открыто именно через Telegram

### Проблема: CORS ошибки
**Причина:** Неправильная настройка CORS в backend
**Решение:** В `backend/app/main.py` должно быть:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретный домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Альтернативный вариант: Один ngrok на Backend

Если хотите использовать один ngrok только на backend (порт 8000), нужно:

1. Собрать production build фронтенда:
```bash
cd frontend
npm run build
```

2. Настроить backend для раздачи статики (уже настроено в `app/main.py`):
```python
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

3. Скопировать build в backend/static:
```bash
cp -r frontend/dist/* backend/static/
```

4. Запустить ngrok на порт 8000:
```bash
ngrok http 8000
```

Но для разработки рекомендуется первый вариант (ngrok → Vite).

## Текущая конфигурация

**Vite config обновлён:**
- Сервер доступен на `0.0.0.0:5173`
- Прокси `/api` → `localhost:8000`
- Прокси `/static` → `localhost:8000`

**Команда для проверки:**
```bash
# Проверьте, что Vite сервер доступен из сети
curl http://localhost:5173/mini-app.html

# Проверьте, что backend работает
curl http://localhost:8000/api/v1/health

# Проверьте ngrok Web Interface
open http://127.0.0.1:4040
```

## Финальная проверка

После настройки откройте в Telegram:
1. Найдите бота
2. Нажмите Menu (☰)
3. Должна открыться страница User Search
4. Должна пройти автоматическая верификация
5. Можно искать пользователей

✅ Готово!
