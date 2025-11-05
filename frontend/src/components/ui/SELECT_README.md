# Компонент Select

Красивый и функциональный компонент выпадающего списка с поддержкой иконок, вариантов оформления и валидации.

## Возможности

- 🎨 **4 варианта оформления**: default, primary, success, danger
- 🎯 **Поддержка иконок**: добавьте иконку слева
- ✅ **Валидация**: встроенная поддержка ошибок и подсказок
- 🔍 **Красивая стрелка**: анимированная иконка ChevronDown
- 📱 **Адаптивный**: отлично работает на всех устройствах
- ⚡ **Плавные анимации**: transitions для всех состояний
- ♿ **Доступность**: полная поддержка accessibility

## Использование

### Базовый пример

```tsx
import { Select } from '../components/ui/Select';
import { MessageSquare } from 'lucide-react';

<Select
  label="Выберите чат"
  value={chatId}
  onChange={(e) => setChatId(e.target.value)}
>
  <option value="">Выберите...</option>
  <option value="1">Чат 1</option>
  <option value="2">Чат 2</option>
</Select>
```

### С иконкой

```tsx
<Select
  label="Тип чата"
  value={type}
  onChange={(e) => setType(e.target.value)}
  icon={<MessageSquare className="w-5 h-5" />}
>
  <option value="all">Все типы</option>
  <option value="group">Группа</option>
  <option value="supergroup">Супергруппа</option>
</Select>
```

### С вариантами оформления

```tsx
// Primary (синий)
<Select
  label="Основной выбор"
  variant="primary"
  value={value}
  onChange={handleChange}
>
  {/* options */}
</Select>

// Success (зеленый)
<Select
  label="Успешная операция"
  variant="success"
  value={value}
  onChange={handleChange}
>
  {/* options */}
</Select>

// Danger (красный)
<Select
  label="Критический выбор"
  variant="danger"
  value={value}
  onChange={handleChange}
>
  {/* options */}
</Select>
```

### С валидацией

```tsx
<Select
  label="Email"
  value={email}
  onChange={handleChange}
  error={errors.email}
  helperText="Выберите адрес для отправки"
>
  {/* options */}
</Select>
```

## Props

| Prop | Тип | По умолчанию | Описание |
|------|-----|--------------|----------|
| `label` | `string` | - | Метка поля |
| `error` | `string` | - | Текст ошибки (красный) |
| `helperText` | `string` | - | Вспомогательный текст (серый) |
| `icon` | `ReactNode` | - | Иконка слева |
| `variant` | `'default' \| 'primary' \| 'success' \| 'danger'` | `'default'` | Вариант оформления |
| `className` | `string` | `''` | Дополнительные CSS классы |
| `...props` | `SelectHTMLAttributes` | - | Все стандартные props для select |

## Примеры из проекта

### UserVerification.tsx
```tsx
<Select
  label="Чат"
  value={singleChatId}
  onChange={(e) => setSingleChatId(e.target.value)}
  icon={<MessageSquare className="w-5 h-5" />}
  variant="primary"
>
  <option value="">Выберите чат...</option>
  {chats.map(chat => (
    <option key={chat.id} value={chat.id}>
      {chat.title}
    </option>
  ))}
</Select>
```

### ChatFilters.tsx
```tsx
<Select
  label="Тип чата"
  value={filters.chatType}
  onChange={(e) => updateFilter('chatType', e.target.value)}
  icon={<MessageSquare className="w-5 h-5" />}
>
  <option value="all">Все типы</option>
  <option value="group">Группа</option>
  <option value="supergroup">Супергруппа</option>
  <option value="channel">Канал</option>
</Select>
```

## Стили и анимации

- **Hover эффект**: изменение цвета border
- **Focus состояние**: кольцо и изменение цвета границы
- **Disabled состояние**: серый фон и курсор not-allowed
- **Тень**: subtle shadow для глубины
- **Transitions**: плавные переходы (200ms)

## Преимущества

1. **Консистентность**: единый стиль во всем приложении
2. **Простота использования**: как обычный select, но красивее
3. **Гибкость**: легко кастомизировать через props
4. **Производительность**: минимальный оверхед
5. **Типизация**: полная поддержка TypeScript
