import React, { useState, useRef } from 'react';
import { X, Plus, Trash2, Image, Video, MessageCircle, Sparkles, Clock, Link2 } from 'lucide-react';
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
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Gradient Header */}
        <div className="relative bg-gradient-to-r from-blue-600 via-blue-500 to-indigo-600 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-white/20 rounded-xl backdrop-blur-sm">
                <MessageCircle className="h-6 w-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">Приветственное сообщение</h2>
                <p className="text-blue-100 text-xs mt-0.5">Настройте автоматическое приветствие для новых участников</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-white/80 hover:text-white hover:bg-white/20 rounded-lg p-2 transition-all"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto">
          <div className="p-6 space-y-5">
            {/* Enable Toggle with Card */}
            <div 
              onClick={() => setEnabled(!enabled)}
              className="flex items-center justify-between p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200 cursor-pointer hover:shadow-md transition-all"
            >
              <div className="flex items-center space-x-3">
                <div className={`w-12 h-6 rounded-full transition-all duration-300 relative ${enabled ? 'bg-green-500' : 'bg-gray-300'}`}>
                  <div className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow-md transition-all duration-300 ${enabled ? 'left-7' : 'left-1'}`}></div>
                </div>
                <div>
                  <label className="text-sm font-semibold text-gray-900 cursor-pointer pointer-events-none">
                    {enabled ? 'Приветствие включено' : 'Приветствие выключено'}
                  </label>
                  <p className="text-xs text-gray-600">{enabled ? 'Новые участники будут получать это сообщение' : 'Нажмите, чтобы включить приветствие'}</p>
                </div>
              </div>
              <input
                type="checkbox"
                id="enabled"
                checked={enabled}
                onChange={(e) => setEnabled(e.target.checked)}
                className="sr-only"
              />
            </div>

            {enabled && (
              <div className="space-y-5 animate-in slide-in-from-top duration-300">
                {/* Message Text Section */}
                <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                  <label className="flex items-center space-x-2 text-sm font-semibold text-gray-900 mb-3">
                    <MessageCircle className="h-4 w-4 text-blue-600" />
                    <span>Текст сообщения</span>
                    <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    ref={textareaRef}
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    rows={4}
                    className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-shadow shadow-sm"
                    placeholder="Привет, {MENTION}! 👋 Добро пожаловать в {GROUPNAME}!"
                  />
                  
                  {/* Variables Chips */}
                  <div className="mt-3 pt-3 border-t border-gray-300">
                    <p className="text-xs font-medium text-gray-700 mb-2">Переменные:</p>
                    <div className="flex flex-wrap gap-1.5">
                      {VARIABLES.map((variable) => (
                        <button
                          key={variable.key}
                          type="button"
                          onClick={() => insertVariable(variable.key)}
                          className="group relative px-2.5 py-1 bg-white border border-blue-200 text-blue-700 text-xs font-medium rounded-md hover:bg-blue-600 hover:text-white hover:border-blue-600 transition-all shadow-sm"
                          title={variable.description}
                        >
                          {variable.key}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Media Section */}
                <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                  <label className="flex items-center space-x-2 text-sm font-semibold text-gray-900 mb-3">
                    <Image className="h-4 w-4 text-purple-600" />
                    <span>Медиа-контент</span>
                  </label>
                  {!mediaUrl ? (
                    <MediaUploader 
                      onFileSelect={handleFileSelect}
                      onClear={handleClearMedia}
                      isUploading={uploadMediaMutation.isPending}
                    />
                  ) : (
                    <div className="flex items-center justify-between p-3 bg-white rounded-lg border-2 border-green-200 shadow-sm">
                      <div className="flex items-center space-x-3">
                        <div className={`p-2 rounded-lg ${mediaType === 'photo' ? 'bg-green-100' : 'bg-blue-100'}`}>
                          {mediaType === 'photo' ? <Image className="h-5 w-5 text-green-600" /> : <Video className="h-5 w-5 text-blue-600" />}
                        </div>
                        <div>
                          <span className="text-sm font-medium text-gray-900">
                            {mediaType === 'photo' ? 'Фото загружено' : 'Видео загружено'}
                          </span>
                          <p className="text-xs text-gray-500">Файл успешно прикреплен</p>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={handleClearMedia}
                        className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  )}
                </div>

                {/* Lifetime Section */}
                <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                  <label className="flex items-center space-x-2 text-sm font-semibold text-gray-900 mb-3">
                    <Clock className="h-4 w-4 text-orange-600" />
                    <span>Автоудаление</span>
                  </label>
                  <div className="flex items-center space-x-3">
                    <input
                      type="number"
                      value={lifetimeMinutes || ''}
                      onChange={(e) => setLifetimeMinutes(e.target.value ? parseInt(e.target.value) : undefined)}
                      min="1"
                      max="10080"
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm"
                      placeholder="Не удалять"
                    />
                    <span className="text-sm text-gray-600 whitespace-nowrap">минут</span>
                  </div>
                  <p className="mt-2 text-xs text-gray-500 flex items-start">
                    <span className="mr-1">💡</span>
                    <span>Сообщение будет автоматически удалено через указанное время (до 7 дней)</span>
                  </p>
                </div>

                {/* Buttons Section */}
                <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                  <div className="flex items-center justify-between mb-3">
                    <label className="flex items-center space-x-2 text-sm font-semibold text-gray-900">
                      <Link2 className="h-4 w-4 text-indigo-600" />
                      <span>Интерактивные кнопки</span>
                    </label>
                    <button
                      type="button"
                      onClick={addButtonRow}
                      className="flex items-center px-3 py-1.5 bg-indigo-600 text-white text-xs font-medium rounded-lg hover:bg-indigo-700 transition-colors shadow-sm"
                    >
                      <Plus className="h-3.5 w-3.5 mr-1" />
                      Добавить ряд
                    </button>
                  </div>

                  {buttons.length > 0 ? (
                    <div className="space-y-2.5">
                      {buttons.map((row, rowIndex) => (
                        <div key={rowIndex} className="bg-white border-2 border-indigo-100 rounded-lg p-3 shadow-sm">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-semibold text-indigo-600 px-2 py-0.5 bg-indigo-50 rounded">Ряд {rowIndex + 1}</span>
                            <div className="flex items-center space-x-2">
                              <button
                                type="button"
                                onClick={() => addButton(rowIndex)}
                                disabled={row.length >= 3}
                                className="text-xs text-indigo-600 hover:text-indigo-700 font-medium disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                              >
                                + Кнопка
                              </button>
                              <button
                                type="button"
                                onClick={() => removeButtonRow(rowIndex)}
                                className="text-xs text-red-600 hover:text-red-700 font-medium transition-colors"
                              >
                                Удалить
                              </button>
                            </div>
                          </div>
                          <div className="space-y-2">
                            {row.map((button, buttonIndex) => (
                              <div key={buttonIndex} className="flex items-center space-x-2">
                                <input
                                  type="text"
                                  value={button.text}
                                  onChange={(e) => updateButton(rowIndex, buttonIndex, 'text', e.target.value)}
                                  placeholder="Текст"
                                  className="flex-1 px-2.5 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                />
                                <input
                                  type="url"
                                  value={button.url}
                                  onChange={(e) => updateButton(rowIndex, buttonIndex, 'url', e.target.value)}
                                  placeholder="https://..."
                                  className="flex-1 px-2.5 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                />
                                <button
                                  type="button"
                                  onClick={() => removeButton(rowIndex, buttonIndex)}
                                  className="p-1.5 text-red-500 hover:bg-red-50 rounded-md transition-colors"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </button>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-6 text-gray-400">
                      <Link2 className="h-8 w-8 mx-auto mb-2 opacity-30" />
                      <p className="text-xs">Нет добавленных кнопок</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </form>

        {/* Footer with gradient */}
        <div className="flex items-center justify-end space-x-3 p-4 border-t border-gray-200 bg-gray-50">
          <button
            type="button"
            onClick={onClose}
            className="px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-200 rounded-lg transition-colors"
          >
            Отмена
          </button>
          <button
            onClick={handleSubmit}
            disabled={updateWelcomeMessage.isPending}
            className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-sm font-semibold rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg"
          >
            {updateWelcomeMessage.isPending ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Сохранение...
              </span>
            ) : 'Сохранить'}
          </button>
        </div>
      </div>
    </div>
  );
};
