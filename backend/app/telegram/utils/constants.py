"""
Constants for Telegram bot - centralized message storage
"""

# Chat types supported by the bot
CHAT_TYPES = {
    'group': 'Групповой чат',
    'supergroup': 'Супергруппа',
    'channel': 'Канал'
}


class StartMessages:
    """Messages for bot start and welcome functionality"""

    WELCOME = (
        "🤖 *Добро пожаловать в бот управления чатами!*\n\n"
        "Я помогу вам связывать Telegram каналы с групповыми чатами для автоматической пересылки уведомлений.\n\n"
        "📋 *Как начать работу:*\n"
        "1️⃣ Добавьте бота как администратора в групповые чаты и каналы\n"
        "2️⃣ Нажмите кнопку 'Управление чатами' ниже\n"
        "3️⃣ Выберите групповой чат из списка\n"
        "4️⃣ Перешлите любое сообщение из канала боту\n\n"
        "💡 *Возможности бота:*\n"
        "• 🔗 Связывание каналов с групповыми чатами\n"
        "• 📢 Автоматическая пересылка уведомлений о редактированиях\n"
        "• ⚙️ Управление настройками через удобный интерфейс\n\n"
        "🚀 Выберите действие ниже:"
    )


class ChatManagementMessages:
    """Messages for chat management functionality"""

    NO_CHATS = (
        "📋 У вас пока нет чатов для управления.\n\n"
        "Добавьте бота в групповые чаты или каналы как администратора, "
        "затем нажмите 'Управление чатами' снова."
    )

    NO_CHATS_SHORT = "📋 У вас нет чатов для управления."

    CHAT_SELECTION = (
        "📋 Выберите групповой чат для управления:\n\n"
        "Условное обозначение:\n"
        "• 👥 - групповой чат\n"
        "• 🔗 - чат уже связан с каналом\n\n"
        "💡 Каналы можно выбрать при связывании с чатом"
    )

    CHAT_NOT_FOUND = "❌ Чат не найден. Попробуйте начать заново."

    SELECTED_CHAT_TEMPLATE = "👥 <b>{chat_title}</b>\n\n🔗 Уже связан с каналом: <b>{channel_title}</b>"
    SELECTED_CHAT_NO_CHANNEL = "👥 <b>{chat_title}</b>\n\n🔗 Канал не связан"

    SELECT_ACTION = "\n\nВыберите действие:"

    OPERATION_CANCELLED = "Операция отменена."

    SETTINGS_SAVED_ERROR = "❌ Ошибка при сохранении настроек."


class ChannelLinkingMessages:
    """Messages for channel linking functionality"""

    CHANNEL_LINKING = (
        "🔗 <b>Связывание канала с чатом</b>\n\n"
        "Перешлите любое сообщение из канала, который хотите связать с этим чатом.\n\n"
        "⚠️ <b>Важно:</b> Бот должен быть добавлен в канал как администратор."
    )

    INVALID_FORWARD = (
        "❌ Это не пересылаемое сообщение из канала.\n\n"
        "Перешлите любое сообщение из канала, который хотите связать с чатом."
    )

    LINKING_SUCCESS_TEMPLATE = "✅ Канал '{channel_name}' успешно связан с чатом '{chat_name}'"

    UNLINKING_SUCCESS_TEMPLATE = "✅ Канал '{channel_name}' успешно отвязан от чата '{chat_name}'"

    # Error messages
    USER_NOT_FOUND = "Пользователь не найден в системе"
    CHANNEL_NOT_FOUND = "Канал не найден. Убедитесь, что бот добавлен в канал как администратор"
    NOT_A_CHANNEL = "Это не канал, а групповой чат"
    NO_CHANNEL_ACCESS = "У вас нет доступа к этому каналу"
    CHANNEL_INACTIVE = "Канал неактивен"
    CHAT_NOT_FOUND = "Канал не найден"
    LINKING_FAILED = "Не удалось связать канал с чатом. Проверьте данные"
    USER_NOT_FOUND_SYSTEM = "Пользователь не найден"
    NO_CHAT_ACCESS = "У вас нет доступа к этому чату"
    UNLINKING_FAILED = "Не удалось отвязать канал"


class MessageEditingMessages:
    """Messages for message editing notifications"""

    MESSAGE_DELETED_HEADER = "🚫 <b>Сообщение удалено из чата</b>\n\n"

    CHAT_INFO_TEMPLATE = "💬 <b>Чат:</b> {chat_title}\n"
    AUTHOR_INFO_TEMPLATE = "👤 <b>Автор:</b> {user_name} (ID: {user_id})\n"
    MESSAGE_ID_TEMPLATE = "🆔 <b>ID сообщения:</b> {message_id}\n"
    CREATION_TIME_TEMPLATE = "📅 <b>Время написания:</b> {created_time}\n"
    EDIT_TIME_TEMPLATE = "📝 <b>Время редактирования:</b> {edit_time}\n"
    TIME_DIFF_MINUTES_TEMPLATE = "⏱️ <b>Время после написания:</b> {minutes} мин\n"
    TIME_DIFF_HOURS_TEMPLATE = "⏱️ <b>Время после написания:</b> {hours} ч {minutes} мин\n"

    ORIGINAL_MESSAGE_HEADER = "<b>Изначальное сообщение:</b>\n{original_text}\n\n"
    ORIGINAL_MESSAGE_NO_TEXT = "<i>Изначальное сообщение без текста (возможно, содержит медиа)</i>\n\n"

    NEW_MESSAGE_HEADER = "<b>Новое сообщение:</b>\n{new_text}"
    NEW_MESSAGE_NO_TEXT = "<i>Новое сообщение без текста (возможно, содержит медиа)</i>"

    TIME_UNKNOWN = 'неизвестно'


class ErrorMessages:
    """General error messages"""

    CHAT_NOT_FOUND = "❌ Чат не найден. Попробуйте начать заново."
    CHAT_NOT_SELECTED = "❌ Ошибка: чат не выбран."
    ACTION_CANCELLED = "❌ Действие отменено."
    SELECTED_CHAT_ERROR = "❌ Ошибка: не найден выбранный чат. Попробуйте начать заново."
    CHANNEL_ALREADY_UNLINKED = "❌ Канал уже отвязан или не найден."
    INVALID_TIMEOUT_VALUE = "❌ Ошибка: некорректное значение времени."
    TIMEOUT_TOO_SMALL = (
        "❌ Время должно быть не менее 1 минуты.\n\n"
        "Введите количество минут (от 1 до 1440):"
    )
    TIMEOUT_TOO_LARGE = (
        "❌ Время не может превышать 1440 минут (24 часа).\n\n"
        "Введите количество минут (от 1 до 1440):"
    )
    NOT_A_NUMBER = (
        "❌ Пожалуйста, введите число.\n\n"
        "Введите количество минут (от 1 до 1440):"
    )


class ButtonTexts:
    """Text constants for keyboard buttons"""

    # Main menu
    MANAGE_CHATS = "📋 Управление чатами"
    HELP = "ℹ️ Помощь"

    # Navigation
    BACK = "⬅️ Назад"
    BACK_TO_MENU = "⬅️ Назад"
    BACK_TO_CHATS = "⬅️ Назад к чатам"

    # Actions
    CANCEL = "❌ Отмена"
    CANCEL_ACTION = "❌ Отмена"
    CANCEL_UNLINK = "❌ Отмена"
    CONFIRM_UNLINK = "✅ Да, отвязать канал"

    # Chat actions
    LINK_CHANNEL = "🔗 Связать канал"
    UNLINK_CHANNEL_TEMPLATE = "🔗 Отвязать канал: {channel_title}"
    EDIT_TIMEOUT_SETTINGS = "⚙️ Настройки редактирования"

    # Channel info
    CHANNEL_NOTIFICATIONS = "🔗 Используется для уведомлений"

    # Timeout options
    DISABLE_EDITING = "🚫 Запретить редактирование"
    SET_TIMEOUT_MINUTES = "{minutes} минут"
    CUSTOM_TIMEOUT = "⏰ Ввести вручную"
    CANCEL_CUSTOM_TIMEOUT = "❌ Отмена"

    # Chat naming
    UNTITLED_CHAT = "Без названия"
    GROUP_CHAT = "Групповой чат"


class HelpMessages:
    """Help and information messages"""

    HELP_TEXT = (
        "🤖 <b>Помощь по использованию бота</b>\n\n"
        "Этот бот позволяет связывать Telegram каналы с групповыми чатами для автоматической пересылки уведомлений.\n\n"
        "📋 <b>Как пользоваться:</b>\n"
        "1️⃣ Добавьте бота как администратора в групповые чаты и каналы\n"
        "2️⃣ Нажмите 'Управление чатами'\n"
        "3️⃣ Выберите групповой чат из списка\n"
        "4️⃣ Перешлите любое сообщение из канала боту\n\n"
        "💡 <b>Важно:</b>\n"
        "• При выборе чата сразу начинается процесс связывания\n"
        "• Если чат уже связан с каналом, появятся дополнительные опции\n"
        "• Каналы выбираются путем пересылки сообщений\n"
        "• Бот должен быть администратором в канале\n\n"
        "❓ При возникновении проблем обращайтесь к администратору."
    )

    CHANNEL_INFO = (
        "📢 <b>Информация о канале</b>\n\n"
        "Этот канал используется для отправки уведомлений в связанные чаты.\n\n"
        "Чтобы изменить настройки, перейдите в чат, связанный с этим каналом."
    )

    CUSTOM_TIMEOUT_INPUT = (
        "⏰ <b>Ввод времени редактирования</b>\n\n"
        "Введите количество минут (от 1 до 1440):\n\n"
        "<i>Пример: 30</i>"
    )

    UNLINK_CONFIRMATION_TEMPLATE = (
        "⚠️ <b>Подтверждение отвязки канала</b>\n\n"
        "👥 <b>Чат:</b> {chat_title}\n"
        "📢 <b>Канал:</b> {channel_title}\n\n"
        "Вы действительно хотите отвязать этот канал от чата?\n\n"
        "<i>После отвязки уведомления из канала перестанут приходить в чат.</i>"
    )

    EDIT_TIMEOUT_SETTINGS_TEMPLATE = (
        "⚙️ <b>Настройки редактирования сообщений</b>\n\n"
        "👥 <b>Чат:</b> {chat_title}\n"
        "⏰ <b>Текущее ограничение:</b> {current_setting}\n\n"
        "Выберите время, в течение которого разрешено редактировать сообщения:"
    )

    TIMEOUT_DISABLED = "запрещено"
    TIMEOUT_SET_SUCCESS_TEMPLATE = "✅ Время редактирования установлено: {minutes} минут"
    EDITING_DISABLED_SUCCESS = "🚫 Редактирование сообщений запрещено"


# Backward compatibility - keep old constant names for existing imports
START_MESSAGE = StartMessages.WELCOME
NO_CHATS_MESSAGE = ChatManagementMessages.NO_CHATS
CHAT_SELECTION_MESSAGE = ChatManagementMessages.CHAT_SELECTION
CHANNEL_LINKING_MESSAGE = ChannelLinkingMessages.CHANNEL_LINKING
INVALID_FORWARD_MESSAGE = ChannelLinkingMessages.INVALID_FORWARD
LINKING_SUCCESS_TEMPLATE = ChannelLinkingMessages.LINKING_SUCCESS_TEMPLATE
UNLINKING_SUCCESS_TEMPLATE = ChannelLinkingMessages.UNLINKING_SUCCESS_TEMPLATE
CANCELLED_MESSAGE = ErrorMessages.ACTION_CANCELLED

