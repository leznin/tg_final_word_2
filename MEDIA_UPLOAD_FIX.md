# Исправление отправки медиа в отложенных постах

## Проблема

При создании отложенного поста с картинкой/видео/документом возникала ошибка 400 Bad Request.

**Причина:** При отложенной отправке медиа-файлы загружались на сервер (путь вида `/static/chat_posts/uuid.jpg`), но при отправке в Telegram использовался относительный URL, который Telegram API не мог обработать.

## Решение

### Что было изменено:

**Файл:** `backend/app/services/chat_posts.py`

#### 1. Функция `_send_post_now()` (немедленная отправка)

**До:**
```python
if post_data.media.url:
    telegram_message = await self.bot.send_photo(
        chat_id=telegram_chat_id,
        photo=post_data.media.url,  # ❌ Передавался URL напрямую
        caption=post_data.content_text or ""
    )
```

**После:**
```python
# Конвертируем локальный путь в FSInputFile
if post_data.media.url.startswith('/static/'):
    relative_path = post_data.media.url.lstrip('/').replace('static/', '', 1)
    file_path = Path('static') / relative_path
    if file_path.exists():
        media_input = FSInputFile(str(file_path))  # ✅ Отправляем файл напрямую
```

#### 2. Функция `_send_scheduled_post()` (отложенная отправка)

**До:**
```python
telegram_message = await self.bot.send_photo(
    chat_id=telegram_chat_id,
    photo=post.media_url,  # ❌ /static/chat_posts/file.jpg
    caption=post.content_text or ""
)
```

**После:**
```python
# Конвертируем URL в абсолютный путь к файлу
relative_path = post.media_url.lstrip('/').replace('static/', '', 1)
file_path = Path('static') / relative_path

if not file_path.exists():
    raise HTTPException(status_code=404, detail=f"Media file not found")

telegram_message = await self.bot.send_photo(
    chat_id=telegram_chat_id,
    photo=FSInputFile(str(file_path)),  # ✅ Отправляем из файла
    caption=post.content_text or ""
)
```

## Как работает теперь:

### Процесс отправки с медиа:

1. **Загрузка на сервер** (endpoint `/api/v1/chat-posts/upload-media`):
   - Файл загружается через FormData
   - Сохраняется в `static/chat_posts/` с уникальным именем
   - Возвращается URL: `/static/chat_posts/uuid-filename.jpg`

2. **Создание поста** (endpoint `/api/v1/chat-posts/`):
   - В базу данных сохраняется:
     - `media_type`: 'photo', 'video', 'document'
     - `media_url`: '/static/chat_posts/uuid-filename.jpg'
     - `media_filename`: оригинальное имя файла

3. **Отправка в Telegram**:
   - **Немедленная:** 
     - URL конвертируется в путь: `static/chat_posts/uuid-filename.jpg`
     - Создается `FSInputFile(path)`
     - Файл отправляется в Telegram через API
   
   - **Отложенная:** 
     - Фоновая задача находит посты готовые к отправке
     - URL из БД конвертируется в путь к файлу
     - Создается `FSInputFile(path)`
     - Файл отправляется в Telegram через API

4. **После отправки:**
   - Telegram возвращает `file_id`
   - `file_id` сохраняется в БД как `media_file_id`
   - В будущем можно использовать `file_id` для пересылки

## Поддерживаемые типы медиа:

- **Фото:** `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- **Видео:** `.mp4`, `.avi`, `.mov`, `.mkv`
- **Документы:** все остальные типы файлов

## Ограничения:

- Максимальный размер файла: **50 MB** (настраивается в `chat_posts.py`)
- Файлы хранятся в `backend/static/chat_posts/`

## Тестирование:

### Тест 1: Немедленная отправка с фото
1. Откройте страницу чата `/chats/{id}`
2. Создайте новый пост
3. Прикрепите фото
4. ✅ Отметьте "Отправить немедленно"
5. Нажмите "Отправить"
6. **Ожидаемый результат:** Фото отправляется в Telegram чат

### Тест 2: Отложенная отправка с фото
1. Создайте новый пост
2. Прикрепите фото
3. ❌ Снимите "Отправить немедленно"
4. Установите время отправки через 2 минуты
5. Нажмите "Отправить"
6. **Ожидаемый результат:** 
   - Пост создан в БД
   - Через 2 минуты фото автоматически отправляется в чат
   - В логах: `Sent scheduled post {id}`

## Проверка в логах:

```bash
# Backend должен показывать:
[ChatPosts] Checking scheduled actions at 2025-11-06 07:50:00...
Sent scheduled post 5
```

## Проверка в БД:

```sql
SELECT 
    id, 
    chat_id, 
    is_sent,
    media_type,
    media_url,
    media_file_id,
    scheduled_send_at,
    sent_at
FROM chat_posts 
WHERE media_url IS NOT NULL
ORDER BY created_at DESC;
```

После отправки:
- `is_sent` = 1
- `media_file_id` = заполнен (Telegram file_id)
- `sent_at` = время отправки

## Устранение неполадок:

### Ошибка "Media file not found"
- Проверьте, что файл существует: `ls -la static/chat_posts/`
- Проверьте путь в БД: должен быть `/static/chat_posts/...`

### Файл не отправляется
- Проверьте права доступа к файлу: `chmod 644 static/chat_posts/*`
- Проверьте, что директория существует: `mkdir -p static/chat_posts`

### Ошибка при загрузке файла
- Проверьте размер файла (макс. 50MB)
- Проверьте свободное место на диске

## ✅ Статус

**Проблема полностью исправлена!**

Теперь отложенные посты с медиа работают корректно.
