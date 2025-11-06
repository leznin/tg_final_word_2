# Прогресс-бар для автоматической проверки по расписанию

## Что было изменено

### 1. Backend изменения

#### `backend/app/main.py`
Обновлена функция `scheduled_user_verification()`:
- Теперь использует глобальный экземпляр `_verification_service_instance` из `app.routers.user_verification`
- Это позволяет API эндпоинту `/status` отслеживать прогресс автоматических проверок
- Прогресс доступен в реальном времени через тот же API, что и для ручных проверок

### 2. Frontend изменения

#### `frontend/src/pages/UserVerification.tsx`

**Добавлен новый useEffect:**
```typescript
// Poll for verification status when on schedule tab
useEffect(() => {
  let statusCheckInterval: NodeJS.Timeout | null = null;
  
  if (activeTab === 'schedule') {
    // Check status every 2 seconds when on schedule tab
    statusCheckInterval = setInterval(async () => {
      const response = await fetch('/api/v1/admin/user-verification/status');
      const data = await response.json();
      
      if (data.is_running) {
        setVerificationProgress(data);
        if (!pollingInterval && !verifyBulkLoading) {
          setVerifyBulkLoading(true);
        }
      } else {
        if (verificationProgress?.is_running) {
          loadSchedules();
          setVerifyBulkLoading(false);
        }
        setVerificationProgress(null);
      }
    }, 2000);
  }
  
  return () => {
    if (statusCheckInterval) {
      clearInterval(statusCheckInterval);
    }
  };
}, [activeTab, verificationProgress?.is_running]);
```

**Добавлен прогресс-бар на вкладке "Расписания проверок":**
- Показывается автоматически когда запускается проверка по расписанию
- Отображает:
  - Процент выполнения
  - Количество проверенных/обновленных пользователей
  - Количество ошибок и изменений
  - Прогресс-бар с оценкой времени

## Как это работает

### Автоматический запуск по расписанию

1. **Фоновая задача** каждые 60 секунд проверяет, есть ли расписания для запуска
2. Когда находит расписание для запуска:
   - Использует **глобальный** экземпляр `UserVerificationService`
   - Этот же экземпляр отслеживается через `/api/v1/admin/user-verification/status`
3. Frontend автоматически обнаруживает запущенную проверку и показывает прогресс-бар

### Отображение прогресса

1. Когда пользователь находится на вкладке "Расписания проверок"
2. Frontend каждые 2 секунды проверяет `/api/v1/admin/user-verification/status`
3. Если проверка запущена (`is_running: true`):
   - Показывается прогресс-бар вверху страницы
   - Обновляется в реальном времени
4. Когда проверка завершается:
   - Прогресс-бар исчезает
   - Список расписаний обновляется (показывает новое время last_run_at)

## Тестирование

### 1. Диагностика расписаний
```bash
cd backend
source venv/bin/activate
python check_verification_schedule.py
```

Покажет:
- Все созданные расписания
- Их статус (включено/выключено)
- Время последнего и следующего запуска
- Какие расписания должны запуститься прямо сейчас

### 2. Тест с прогресс-баром
```bash
cd backend
source venv/bin/activate
python test_schedule_progress.py
```

**Требования:**
- Backend сервер должен быть запущен (`uvicorn app.main:app --reload`)
- Telegram бот должен работать
- Должно быть хотя бы одно включенное расписание

Скрипт:
1. Найдет первое включенное расписание
2. Запустит проверку вручную
3. Покажет прогресс-бар в консоли
4. Обновит время last_run_at

### 3. Проверка в веб-интерфейсе

1. Запустите backend и frontend
2. Откройте веб-интерфейс
3. Перейдите на "Проверка пользователей" → "Расписания проверок"
4. Запустите тестовый скрипт ИЛИ дождитесь автоматического запуска
5. **Вы должны увидеть:**
   - Синяя панель вверху с заголовком "Выполняется проверка по расписанию"
   - Прогресс-бар с процентом выполнения
   - Статистику: проверено, обновлено, ошибок, изменений
   - Оценку оставшегося времени

## Проверка логов

### Backend логи
Когда расписание запускается, вы увидите:
```
Found 1 verification schedule(s) to run
Running verification schedule 1
Verification schedule 1 completed: 50 checked, 5 updated, 0 errors
```

### API статус
Проверить текущий статус можно через API:
```bash
curl http://localhost:8000/api/v1/admin/user-verification/status
```

Ответ во время выполнения:
```json
{
  "is_running": true,
  "current_progress": 25,
  "total_users": 100,
  "checked_users": 25,
  "updated_users": 3,
  "users_with_changes": 5,
  "users_with_errors": 0,
  "progress_percentage": 25.0,
  "estimated_time_remaining": 37.5,
  "started_at": "2025-11-06T17:30:00"
}
```

## Troubleshooting

### Прогресс-бар не появляется

1. **Проверьте, что backend запущен:**
   ```bash
   curl http://localhost:8000/api/v1/admin/user-verification/status
   ```

2. **Проверьте логи backend:**
   - Должно быть сообщение "Started scheduled user verification task"
   - При запуске: "Found X verification schedule(s) to run"

3. **Проверьте вкладку:**
   - Прогресс-бар показывается только на вкладке "Расписания проверок"
   - При переключении на другую вкладку опрос останавливается

4. **Проверьте консоль браузера:**
   - Откройте DevTools (F12) → Console
   - Не должно быть ошибок при вызове `/api/v1/admin/user-verification/status`

### Расписание не запускается

1. **Проверьте статус:**
   ```bash
   python check_verification_schedule.py
   ```

2. **Убедитесь что:**
   - Расписание включено (`enabled: true`)
   - `next_run_at` в прошлом или настоящем
   - Backend запущен
   - Telegram бот работает

3. **Проверьте логи backend:**
   - Каждую минуту должна быть проверка расписаний
   - Если есть расписания для запуска, будет сообщение

## Преимущества реализации

✅ **Единообразие:** Тот же прогресс-бар для ручных и автоматических проверок
✅ **Реальное время:** Прогресс обновляется каждые 2 секунды
✅ **Автообнаружение:** Frontend автоматически обнаруживает запущенную проверку
✅ **Не мешает:** Опрос активен только когда открыта вкладка "Расписания"
✅ **Информативность:** Показывает детальную статистику выполнения
