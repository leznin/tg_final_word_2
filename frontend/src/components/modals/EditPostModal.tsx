import React, { useState, useEffect } from 'react';
import { X, Save, Pin, Trash2, Clock, Settings, Plus, ChevronDown, ChevronRight } from 'lucide-react';
import { useUpdateChatPost } from '../../hooks/useChatPosts';
import { ChatPost, ChatPostUpdate, InlineKeyboardButton, InlineKeyboardRow } from '../../types';
import { getMediaUrl } from '../../utils/media';

interface EditPostModalProps {
  post: ChatPost;
  onClose: () => void;
  onSuccess?: () => void;
}

export const EditPostModal: React.FC<EditPostModalProps> = ({
  post,
  onClose,
  onSuccess
}) => {
  const [contentText, setContentText] = useState(post.content_text || '');
  const [scheduledTime, setScheduledTime] = useState('');
  const [pinMessage, setPinMessage] = useState(post.is_pinned);
  const [pinDuration, setPinDuration] = useState<number | undefined>(post.pin_duration_minutes || undefined);
  const [deleteAfter, setDeleteAfter] = useState<number | undefined>(post.delete_after_minutes || undefined);
  const [showKeyboard, setShowKeyboard] = useState(false);
  const [keyboardRows, setKeyboardRows] = useState<InlineKeyboardRow[]>([]);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  
  const updatePostMutation = useUpdateChatPost();

  useEffect(() => {
    setContentText(post.content_text || '');
    setPinMessage(post.is_pinned);
    setPinDuration(post.pin_duration_minutes || undefined);
    setDeleteAfter(post.delete_after_minutes || undefined);
    
    // Initialize scheduled time for unsent posts
    if (!post.is_sent && post.scheduled_send_at) {
      // Convert UTC time to local datetime-local format
      const date = new Date(post.scheduled_send_at);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      setScheduledTime(`${year}-${month}-${day}T${hours}:${minutes}`);
    }
    
    // Initialize keyboard if exists
    if (post.reply_markup) {
      try {
        const markup = typeof post.reply_markup === 'string' 
          ? JSON.parse(post.reply_markup) 
          : post.reply_markup;
        
        if (markup.inline_keyboard) {
          setKeyboardRows(markup.inline_keyboard);
          setShowKeyboard(true);
        }
      } catch (e) {
        console.error('Failed to parse reply_markup:', e);
      }
    }
  }, [post]);

  // Keyboard handling functions
  const addKeyboardRow = () => {
    setKeyboardRows([...keyboardRows, { buttons: [] }]);
  };

  const removeKeyboardRow = (rowIndex: number) => {
    setKeyboardRows(keyboardRows.filter((_, index) => index !== rowIndex));
  };

  const addButtonToRow = (rowIndex: number) => {
    const newRows = [...keyboardRows];
    if (newRows[rowIndex].buttons.length < 3) {
      newRows[rowIndex].buttons.push({ text: '', url: undefined, callback_data: undefined });
      setKeyboardRows(newRows);
    }
  };

  const updateButton = (rowIndex: number, buttonIndex: number, updates: Partial<InlineKeyboardButton>) => {
    const newRows = [...keyboardRows];
    newRows[rowIndex].buttons[buttonIndex] = { ...newRows[rowIndex].buttons[buttonIndex], ...updates };
    setKeyboardRows(newRows);
  };

  const removeButtonFromRow = (rowIndex: number, buttonIndex: number) => {
    const newRows = [...keyboardRows];
    newRows[rowIndex].buttons = newRows[rowIndex].buttons.filter((_, index) => index !== buttonIndex);
    setKeyboardRows(newRows);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!contentText.trim() && !post.media_type) {
      alert('Введите текст сообщения');
      return;
    }

    // For unsent posts with scheduled time
    let scheduledSendAt: string | undefined = undefined;
    if (!post.is_sent && scheduledTime) {
      // Convert local datetime to ISO string with timezone
      const date = new Date(scheduledTime);
      const tzOffset = -date.getTimezoneOffset();
      const sign = tzOffset >= 0 ? '+' : '-';
      const hours = String(Math.floor(Math.abs(tzOffset) / 60)).padStart(2, '0');
      const minutes = String(Math.abs(tzOffset) % 60).padStart(2, '0');
      scheduledSendAt = `${scheduledTime}:00${sign}${hours}:${minutes}`;
    }

    // Prepare keyboard markup
    const replyMarkup = keyboardRows.length > 0 && keyboardRows.some(row => row.buttons.length > 0)
      ? { inline_keyboard: keyboardRows.filter(row => row.buttons.length > 0 && row.buttons.some(btn => btn.text.trim())) }
      : undefined;

    const postData: ChatPostUpdate = {
      content_text: contentText.trim() || undefined,
      scheduled_send_at: scheduledSendAt,
      pin_message: pinMessage,
      pin_duration_minutes: pinMessage ? pinDuration : undefined,
      delete_after_minutes: deleteAfter,
      reply_markup: replyMarkup
    };

    try {
      await updatePostMutation.mutateAsync({ postId: post.id, postData });
      onSuccess?.();
      onClose();
    } catch (error: any) {
      console.error('Failed to update post:', error);
      alert(error?.response?.data?.detail || 'Не удалось обновить пост');
    }
  };

  const isSubmitting = updatePostMutation.isPending;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Редактировать пост</h2>
            <p className="text-sm text-gray-500 mt-1">
              {post.is_sent ? 'Отправленный пост' : 'Запланированный пост'}
            </p>
          </div>
          <button
            onClick={onClose}
            disabled={isSubmitting}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Info Messages */}
          {post.media_type && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-sm text-blue-700">
                ℹ️ Медиа нельзя изменить в Telegram. Можно редактировать только текст и настройки.
              </p>
            </div>
          )}
          
          {!post.is_sent && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <p className="text-sm text-yellow-700">
                ⏰ Этот пост ещё не отправлен. Вы можете изменить время отправки.
              </p>
            </div>
          )}

          {/* Text Content */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {post.media_type ? 'Подпись к медиа' : 'Текст сообщения'}
            </label>
            <textarea
              value={contentText}
              onChange={(e) => setContentText(e.target.value)}
              placeholder="Введите текст поста..."
              className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              disabled={isSubmitting}
            />
            <p className="mt-1 text-xs text-gray-500">
              {contentText.length} / 4096 символов
            </p>
          </div>

          {/* Current Media Preview */}
          {post.media_type && (
            <div className="border border-gray-200 rounded-lg p-4">
              <p className="text-sm font-medium text-gray-700 mb-2">Текущее медиа:</p>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">
                  Тип: <span className="font-medium">{post.media_type}</span>
                </span>
                {post.media_filename && (
                  <span className="text-sm text-gray-600">
                    • {post.media_filename}
                  </span>
                )}
              </div>
              {post.media_type === 'photo' && post.media_url && (
                <div className="mt-3">
                  <img 
                    src={getMediaUrl(post.media_url)} 
                    alt="Current media" 
                    className="max-h-48 rounded-lg object-contain"
                  />
                </div>
              )}
            </div>
          )}

          {/* Scheduled Time (only for unsent posts) */}
          {!post.is_sent && (
            <div className="border border-gray-200 rounded-lg p-4 space-y-3">
              <div className="flex items-center space-x-2">
                <Clock className="h-5 w-5 text-gray-600" />
                <label className="block text-sm font-medium text-gray-700">
                  Время отправки
                </label>
              </div>
              <input
                type="datetime-local"
                value={scheduledTime}
                onChange={(e) => setScheduledTime(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={isSubmitting}
              />
              <p className="text-xs text-gray-500">
                Текущее: {post.scheduled_send_at ? new Date(post.scheduled_send_at).toLocaleString('ru-RU') : 'Не установлено'}
              </p>
            </div>
          )}

          {/* Advanced Settings Toggle */}
          <button
            type="button"
            onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
            className="flex items-center space-x-2 text-gray-700 hover:text-gray-900 transition-colors"
          >
            {showAdvancedSettings ? (
              <ChevronDown className="h-5 w-5" />
            ) : (
              <ChevronRight className="h-5 w-5" />
            )}
            <Settings className="h-5 w-5" />
            <span className="font-medium">Дополнительные настройки</span>
          </button>

          {showAdvancedSettings && (
            <div className="space-y-4 pl-4 border-l-2 border-gray-200">
              {/* Pin Settings */}
              <div className="border border-gray-200 rounded-lg p-4 space-y-3">
                <div className="flex items-center space-x-2">
                  <Pin className="h-5 w-5 text-gray-600" />
                  <label className="block text-sm font-medium text-gray-700">
                    Закрепление
                  </label>
                </div>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={pinMessage}
                    onChange={(e) => {
                      setPinMessage(e.target.checked);
                      if (!e.target.checked) {
                        setPinDuration(undefined);
                      }
                    }}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    disabled={isSubmitting}
                  />
                  <span className="text-sm text-gray-700">
                    {post.is_sent ? 'Закрепить сообщение' : 'Закрепить при отправке'}
                  </span>
                </label>
                
                {pinMessage && (
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Длительность закрепления (минут, 0 = бессрочно)
                    </label>
                    <input
                      type="number"
                      min="0"
                      value={pinDuration || ''}
                      onChange={(e) => setPinDuration(e.target.value ? parseInt(e.target.value) : undefined)}
                      placeholder="0 = бессрочно"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      disabled={isSubmitting}
                    />
                  </div>
                )}
              </div>

              {/* Delete After Settings */}
              <div className="border border-gray-200 rounded-lg p-4 space-y-3">
                <div className="flex items-center space-x-2">
                  <Trash2 className="h-5 w-5 text-gray-600" />
                  <label className="block text-sm font-medium text-gray-700">
                    Автоудаление
                  </label>
                </div>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">
                    Удалить через (минут, 0 = отключить)
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={deleteAfter || ''}
                    onChange={(e) => setDeleteAfter(e.target.value ? parseInt(e.target.value) : undefined)}
                    placeholder="0 = отключить"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    disabled={isSubmitting}
                  />
                  {post.is_sent && deleteAfter && deleteAfter > 0 && (
                    <p className="mt-1 text-xs text-gray-500">
                      Сообщение будет удалено через {deleteAfter} минут от текущего момента
                    </p>
                  )}
                </div>
              </div>

              {/* Keyboard Settings */}
              <div className="border border-gray-200 rounded-lg p-4 space-y-3">
                <button
                  type="button"
                  onClick={() => setShowKeyboard(!showKeyboard)}
                  className="flex items-center justify-between w-full"
                >
                  <div className="flex items-center space-x-2">
                    {showKeyboard ? (
                      <ChevronDown className="h-5 w-5 text-gray-600" />
                    ) : (
                      <ChevronRight className="h-5 w-5 text-gray-600" />
                    )}
                    <span className="text-sm font-medium text-gray-700">
                      Inline клавиатура {keyboardRows.length > 0 && `(${keyboardRows.length} рядов)`}
                    </span>
                  </div>
                </button>

                {showKeyboard && (
                  <div className="space-y-3 pt-2">
                    {keyboardRows.map((row, rowIndex) => (
                      <div key={rowIndex} className="border border-gray-200 rounded-lg p-3 space-y-2 bg-gray-50">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium text-gray-600">Ряд {rowIndex + 1}</span>
                          <div className="flex items-center space-x-2">
                            <button
                              type="button"
                              onClick={() => addButtonToRow(rowIndex)}
                              disabled={row.buttons.length >= 3 || isSubmitting}
                              className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              + Кнопка
                            </button>
                            <button
                              type="button"
                              onClick={() => removeKeyboardRow(rowIndex)}
                              disabled={isSubmitting}
                              className="text-xs px-2 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200"
                            >
                              ✕
                            </button>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 gap-2">
                          {row.buttons.map((button, buttonIndex) => (
                            <div key={buttonIndex} className="space-y-1 p-2 border border-gray-200 rounded bg-white">
                              <input
                                type="text"
                                placeholder="Текст кнопки"
                                value={button.text}
                                onChange={(e) => updateButton(rowIndex, buttonIndex, { text: e.target.value })}
                                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                                disabled={isSubmitting}
                              />
                              <input
                                type="url"
                                placeholder="URL"
                                value={button.url || ''}
                                onChange={(e) => updateButton(rowIndex, buttonIndex, { url: e.target.value || undefined, callback_data: undefined })}
                                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                                disabled={isSubmitting}
                              />
                              <button
                                type="button"
                                onClick={() => removeButtonFromRow(rowIndex, buttonIndex)}
                                disabled={isSubmitting}
                                className="w-full text-xs px-2 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200"
                              >
                                Удалить кнопку
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}

                    <button
                      type="button"
                      onClick={addKeyboardRow}
                      disabled={isSubmitting}
                      className="w-full flex items-center justify-center space-x-2 px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors disabled:opacity-50"
                    >
                      <Plus className="h-4 w-4" />
                      <span className="text-sm">Добавить ряд кнопок</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !contentText.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <Save className="h-4 w-4" />
              <span>{isSubmitting ? 'Сохранение...' : 'Сохранить'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
