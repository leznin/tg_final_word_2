import React, { useState, useRef } from 'react';
import { X, Plus, Trash2, Image, Video, MessageCircle } from 'lucide-react';
import { MediaUploader } from '../ui/MediaUploader';
import { useUpdateWelcomeMessage } from '../../hooks/useChats';
import { useUploadChatMedia } from '../../hooks/useChatPosts';
import { Chat, WelcomeMessageSettings, WelcomeMessageButton } from '../../types';

interface WelcomeMessageModalProps {
  chat: Chat;
  onClose: () => void;
}

const VARIABLES = [
  { key: '{ID}', description: 'Идентификатор пользователя' },
  { key: '{NAME}', description: 'Имя' },
  { key: '{SURNAME}', description: 'Фамилия' },
  { key: '{NAMESURNAME}', description: 'Имя и фамилия' },
  { key: '{LANG}', description: 'Язык пользователя' },
  { key: '{MENTION}', description: 'Ссылка на профиль' },
  { key: '{USERNAME}', description: 'Имя пользователя' },
  { key: '{GROUPNAME}', description: 'Имя группы' },
];

export const WelcomeMessageModal: React.FC<WelcomeMessageModalProps> = ({ chat, onClose }) => {
  const [enabled, setEnabled] = useState(chat.welcome_message_enabled || false);
  const [text, setText] = useState(chat.welcome_message_text || '');
  const [mediaType, setMediaType] = useState<'photo' | 'video' | null>(chat.welcome_message_media_type as any || null);
  const [mediaUrl, setMediaUrl] = useState(chat.welcome_message_media_url || '');
  const [lifetimeMinutes, setLifetimeMinutes] = useState<number | undefined>(chat.welcome_message_lifetime_minutes || undefined);
  const [buttons, setButtons] = useState<WelcomeMessageButton[][]>(
    chat.welcome_message_buttons ? JSON.parse(JSON.stringify(chat.welcome_message_buttons)) : []
  );
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const updateWelcomeMessage = useUpdateWelcomeMessage();
  const uploadMediaMutation = useUploadChatMedia();

  const handleFileSelect = async (file: File) => {
    // Determine media type
    const fileExtension = file.name.toLowerCase().split('.').pop();
    let type: 'photo' | 'video' = 'photo';

    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(fileExtension || '')) {
      type = 'photo';
    } else if (['mp4', 'avi', 'mov', 'mkv'].includes(fileExtension || '')) {
      type = 'video';
    }

    try {
      const uploadResult = await uploadMediaMutation.mutateAsync(file);
      setMediaType(type);
      setMediaUrl(uploadResult.url);
    } catch (error) {
      console.error('Failed to upload media:', error);
      alert('Не удалось загрузить файл');
    }
  };

  const handleClearMedia = () => {
    setMediaType(null);
    setMediaUrl('');
  };

  const addButtonRow = () => {
    setButtons([...buttons, []]);
  };

  const removeButtonRow = (rowIndex: number) => {
    setButtons(buttons.filter((_, index) => index !== rowIndex));
  };

  const addButton = (rowIndex: number) => {
    const newButtons = [...buttons];
    if (newButtons[rowIndex].length < 3) {
      newButtons[rowIndex].push({ text: '', url: '' });
      setButtons(newButtons);
    }
  };

  const updateButton = (rowIndex: number, buttonIndex: number, field: 'text' | 'url', value: string) => {
    const newButtons = [...buttons];
    newButtons[rowIndex][buttonIndex][field] = value;
    setButtons(newButtons);
  };

  const removeButton = (rowIndex: number, buttonIndex: number) => {
    const newButtons = [...buttons];
    newButtons[rowIndex] = newButtons[rowIndex].filter((_, index) => index !== buttonIndex);
    if (newButtons[rowIndex].length === 0) {
      newButtons.splice(rowIndex, 1);
    }
    setButtons(newButtons);
  };

  const insertVariable = (variable: string) => {
    const textarea = textareaRef.current;
    if (!textarea) {
      // Fallback if ref is not available
      setText(text + variable);
      return;
    }

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const currentText = text;

    // Replace selected text or insert at cursor position
    const newText = currentText.substring(0, start) + variable + currentText.substring(end);
    setText(newText);

    // Set cursor position after the inserted variable
    setTimeout(() => {
      textarea.focus();
      const newCursorPosition = start + variable.length;
      textarea.setSelectionRange(newCursorPosition, newCursorPosition);
    }, 0);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (enabled && !text.trim()) {
      alert('Введите текст приветственного сообщения');
      return;
    }

    // Filter out buttons without text
    const filteredButtons = buttons
      .map(row => row.filter(btn => btn.text.trim()))
      .filter(row => row.length > 0);

    const settings: WelcomeMessageSettings = {
      enabled,
      text: text.trim() || undefined,
      media_type: mediaType,
      media_url: mediaUrl || undefined,
      lifetime_minutes: lifetimeMinutes,
      buttons: filteredButtons.length > 0 ? filteredButtons : undefined,
    };

    try {
      await updateWelcomeMessage.mutateAsync({
        chatId: chat.telegram_chat_id,
        settings,
      });
      onClose();
    } catch (error: any) {
      console.error('Failed to update welcome message:', error);
      alert(error.response?.data?.detail || 'Не удалось обновить приветственное сообщение');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <MessageCircle className="h-6 w-6 text-blue-600" />
            <h2 className="text-xl font-bold text-gray-900">Приветственное сообщение</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Enable Toggle */}
          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              id="enabled"
              checked={enabled}
              onChange={(e) => setEnabled(e.target.checked)}
              className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="enabled" className="text-sm font-medium text-gray-900">
              Включить приветственное сообщение
            </label>
          </div>

          {enabled && (
            <>
              {/* Message Text */}
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Текст сообщения *
                </label>
                <textarea
                  ref={textareaRef}
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Введите текст приветственного сообщения..."
                />
                
                {/* Variables */}
                <div className="mt-2">
                  <p className="text-xs text-gray-600 mb-2">Доступные переменные:</p>
                  <div className="flex flex-wrap gap-2">
                    {VARIABLES.map((variable) => (
                      <button
                        key={variable.key}
                        type="button"
                        onClick={() => insertVariable(variable.key)}
                        className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded hover:bg-blue-100 transition-colors"
                        title={variable.description}
                      >
                        {variable.key}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Media Upload */}
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Медиа (фото или видео)
                </label>
                {!mediaUrl ? (
                  <MediaUploader 
                    onFileSelect={handleFileSelect}
                    onClear={handleClearMedia}
                    isUploading={uploadMediaMutation.isPending}
                  />
                ) : (
                  <div className="relative">
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
                      <div className="flex items-center space-x-2">
                        {mediaType === 'photo' && <Image className="h-5 w-5 text-green-600" />}
                        {mediaType === 'video' && <Video className="h-5 w-5 text-blue-600" />}
                        <span className="text-sm text-gray-700">
                          {mediaType === 'photo' ? 'Фото загружено' : 'Видео загружено'}
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={handleClearMedia}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Lifetime */}
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Время жизни сообщения (минут)
                </label>
                <input
                  type="number"
                  value={lifetimeMinutes || ''}
                  onChange={(e) => setLifetimeMinutes(e.target.value ? parseInt(e.target.value) : undefined)}
                  min="1"
                  max="10080"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Оставьте пустым для постоянного сообщения"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Сообщение будет автоматически удалено через указанное время (максимум 7 дней)
                </p>
              </div>

              {/* Buttons */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-gray-900">
                    Кнопки
                  </label>
                  <button
                    type="button"
                    onClick={addButtonRow}
                    className="flex items-center px-3 py-1 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    Добавить ряд
                  </button>
                </div>

                {buttons.length > 0 && (
                  <div className="space-y-3">
                    {buttons.map((row, rowIndex) => (
                      <div key={rowIndex} className="border border-gray-200 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-medium text-gray-600">Ряд {rowIndex + 1}</span>
                          <div className="flex space-x-2">
                            <button
                              type="button"
                              onClick={() => addButton(rowIndex)}
                              disabled={row.length >= 3}
                              className="text-xs text-blue-600 hover:text-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              + Кнопка
                            </button>
                            <button
                              type="button"
                              onClick={() => removeButtonRow(rowIndex)}
                              className="text-xs text-red-600 hover:text-red-700"
                            >
                              Удалить ряд
                            </button>
                          </div>
                        </div>
                        <div className="space-y-2">
                          {row.map((button, buttonIndex) => (
                            <div key={buttonIndex} className="flex space-x-2">
                              <input
                                type="text"
                                value={button.text}
                                onChange={(e) => updateButton(rowIndex, buttonIndex, 'text', e.target.value)}
                                placeholder="Текст кнопки"
                                className="flex-1 px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              />
                              <input
                                type="url"
                                value={button.url}
                                onChange={(e) => updateButton(rowIndex, buttonIndex, 'url', e.target.value)}
                                placeholder="https://..."
                                className="flex-1 px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              />
                              <button
                                type="button"
                                onClick={() => removeButton(rowIndex, buttonIndex)}
                                className="text-red-500 hover:text-red-700"
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </form>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
          >
            Отмена
          </button>
          <button
            onClick={handleSubmit}
            disabled={updateWelcomeMessage.isPending}
            className="px-6 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {updateWelcomeMessage.isPending ? 'Сохранение...' : 'Сохранить'}
          </button>
        </div>
      </div>
    </div>
  );
};
