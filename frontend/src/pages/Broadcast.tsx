import React, { useState, useEffect } from 'react';
import { Send, Users, CheckCircle, XCircle, Clock, AlertTriangle, Upload, Plus, X, Image, Video, File, ChevronDown, ChevronRight, Settings, MessageSquare } from 'lucide-react';
import { useBroadcast, useBroadcastUsersCount, useBroadcastStatus, useMediaUpload } from '../hooks/useBroadcast';
import { Loading } from '../components/ui/Loading';
import { InlineKeyboardButton, InlineKeyboardRow, MediaFile } from '../types';

export const Broadcast: React.FC = () => {
  const [message, setMessage] = useState('');
  const [showResults, setShowResults] = useState(false);

  // Collapsible sections
  const [showMedia, setShowMedia] = useState(false);
  const [showKeyboard, setShowKeyboard] = useState(false);

  // Media state
  const [media, setMedia] = useState<MediaFile | null>(null);
  const [mediaFile, setMediaFile] = useState<File | null>(null);

  // Keyboard state
  const [keyboardRows, setKeyboardRows] = useState<InlineKeyboardRow[]>([]);

  const { data: usersCount, isLoading: usersCountLoading } = useBroadcastUsersCount();
  const { data: status, isLoading: statusLoading } = useBroadcastStatus();
  const { sendBroadcast, isSending, error, result } = useBroadcast();
  const { uploadMedia, isUploading } = useMediaUpload();

  useEffect(() => {
    if (result) {
      setShowResults(true);
    }
  }, [result]);

  useEffect(() => {
    if (status && !status.is_running && showResults) {
      // Broadcast completed, keep showing results
    }
  }, [status, showResults]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!message.trim()) {
      alert('Пожалуйста, введите сообщение');
      return;
    }

    if (message.length > 4096) {
      alert('Сообщение слишком длинное (максимум 4096 символов)');
      return;
    }

    // Validate media
    if (media && !media.url) {
      alert('Пожалуйста, укажите URL для медиафайла');
      return;
    }

    // Validate keyboard buttons
    for (const row of keyboardRows) {
      for (const button of row.buttons) {
        if (!button.text.trim()) {
          alert('Все кнопки должны иметь текст');
          return;
        }
        if (button.url && button.callback_data) {
          alert('Кнопка не может иметь одновременно URL и callback_data');
          return;
        }
        if (!button.url && !button.callback_data) {
          alert('Кнопка должна иметь либо URL, либо callback_data');
          return;
        }
      }
    }

    const requestData: any = {
      message: message.trim(),
      original_message: message.trim(),
    };

    // Add media if present
    if (media && media.url) {
      requestData.media = media;
    }

    // Add keyboard if present
    if (keyboardRows.length > 0) {
      requestData.reply_markup = {
        inline_keyboard: keyboardRows.filter(row => row.buttons.length > 0)
      };
    }

    try {
      await sendBroadcast(requestData);
    } catch (err) {
      console.error('Broadcast failed:', err);
    }
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const formatTimeRemaining = (seconds?: number) => {
    if (!seconds) return 'Расчет...';
    return formatDuration(seconds);
  };

  // Media handling functions
  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setMediaFile(file);

      // Determine media type from file extension
      const fileExtension = file.name.toLowerCase().split('.').pop();
      let mediaType: 'photo' | 'video' | 'document' = 'document';

      if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(fileExtension || '')) {
        mediaType = 'photo';
      } else if (['mp4', 'avi', 'mov', 'mkv'].includes(fileExtension || '')) {
        mediaType = 'video';
      }

      try {
        // Upload file to server
        const uploadResult = await uploadMedia(file);

        setMedia({
          type: mediaType,
          url: uploadResult.url,
          filename: file.name,
          caption: ''
        });
      } catch (error) {
        console.error('Failed to upload media file:', error);
        alert('Failed to upload media file. Please try again.');
        // Reset file input
        event.target.value = '';
      }
    }
  };

  const handleMediaUrlChange = (url: string) => {
    if (media) {
      setMedia({ ...media, url });
    }
  };

  const handleMediaCaptionChange = (caption: string) => {
    if (media) {
      setMedia({ ...media, caption });
    }
  };

  const clearMedia = () => {
    setMedia(null);
    setMediaFile(null);
  };

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

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <MessageSquare className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Рассылка сообщений</h1>
            <p className="text-sm text-gray-600">Отправка сообщений пользователям</p>
          </div>
        </div>

        {/* User count badge */}
        <div className="flex items-center space-x-2 bg-blue-50 px-3 py-2 rounded-lg">
          <Users className="h-4 w-4 text-blue-500" />
          {usersCountLoading ? (
            <Loading />
          ) : (
            <span className="text-sm font-medium text-blue-700">
              {usersCount?.count || 0} получателей
            </span>
          )}
        </div>
      </div>

      {/* Status indicators */}
      <div className="flex items-center space-x-2">
        {status?.is_running && (
          <div className="flex items-center space-x-2 bg-yellow-50 px-3 py-2 rounded-lg border border-yellow-200">
            <Clock className="h-4 w-4 text-yellow-500" />
            <span className="text-sm text-yellow-700">
              Рассылка: {status.current_progress}/{status.total_users} • {formatTimeRemaining(status.estimated_time_remaining)}
            </span>
          </div>
        )}

        {error && (
          <div className="flex items-center space-x-2 bg-red-50 px-3 py-2 rounded-lg border border-red-200">
            <XCircle className="h-4 w-4 text-red-500" />
            <span className="text-sm text-red-700">Ошибка отправки</span>
          </div>
        )}
      </div>

      {/* Main form */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Message input */}
          <div className="space-y-2">
            <label htmlFor="message" className="block text-sm font-medium text-gray-700">
              Сообщение
            </label>
            <textarea
              id="message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Введите сообщение для рассылки..."
              className="w-full h-24 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none text-sm"
              disabled={isSending}
              maxLength={4096}
            />
            <div className="flex justify-between items-center text-xs text-gray-500">
              <span>HTML форматирование поддерживается</span>
              <span>{message.length}/4096</span>
            </div>
          </div>

          {/* Collapsible Media section */}
          <div className="border border-gray-200 rounded-lg">
            <button
              type="button"
              onClick={() => setShowMedia(!showMedia)}
              className="w-full flex items-center justify-between p-3 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center space-x-2">
                <Upload className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">
                  Медиа {media && '(прикреплено)'}
                </span>
              </div>
              {showMedia ? (
                <ChevronDown className="h-4 w-4 text-gray-500" />
              ) : (
                <ChevronRight className="h-4 w-4 text-gray-500" />
              )}
            </button>

            {showMedia && (
              <div className="px-3 pb-3 border-t border-gray-100">
                {!media ? (
                  <div className="space-y-3 pt-3">
                    <input
                      type="file"
                      accept="image/*,video/*,.pdf,.doc,.docx"
                      onChange={handleFileSelect}
                      className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                      disabled={isSending}
                    />
                    <div className="relative">
                      <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t border-gray-300"></div>
                      </div>
                      <div className="relative flex justify-center text-sm">
                        <span className="px-2 bg-white text-gray-500">или</span>
                      </div>
                    </div>
                    <input
                      type="url"
                      placeholder="URL медиафайла"
                      onChange={(e) => {
                        const url = e.target.value;
                        if (url) {
                          setMedia({
                            type: 'photo',
                            url,
                            caption: ''
                          });
                        }
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                      disabled={isSending}
                    />
                  </div>
                ) : (
                  <div className="pt-3 space-y-3">
                    <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-2">
                        {media.type === 'photo' && <Image className="h-4 w-4 text-blue-500" />}
                        {media.type === 'video' && <Video className="h-4 w-4 text-red-500" />}
                        {media.type === 'document' && <File className="h-4 w-4 text-green-500" />}
                        <span className="text-sm font-medium">{media.filename || 'Медиафайл'}</span>
                      </div>
                      <button
                        type="button"
                        onClick={clearMedia}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      <div className="space-y-1">
                        <label className="block text-xs font-medium text-gray-700">Тип</label>
                        <select
                          value={media.type}
                          onChange={(e) => setMedia({ ...media, type: e.target.value as 'photo' | 'video' | 'document' })}
                          className="w-full px-2 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                        >
                          <option value="photo">Фото</option>
                          <option value="video">Видео</option>
                          <option value="document">Документ</option>
                        </select>
                      </div>

                      <div className="md:col-span-2 space-y-1">
                        <label className="block text-xs font-medium text-gray-700">Подпись</label>
                        <input
                          type="text"
                          value={media.caption}
                          onChange={(e) => handleMediaCaptionChange(e.target.value)}
                          placeholder="Описание медиафайла"
                          className="w-full px-2 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                          disabled={isSending}
                        />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Collapsible Keyboard section */}
          <div className="border border-gray-200 rounded-lg">
            <button
              type="button"
              onClick={() => setShowKeyboard(!showKeyboard)}
              className="w-full flex items-center justify-between p-3 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center space-x-2">
                <Settings className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">
                  Клавиатура {keyboardRows.length > 0 && `(${keyboardRows.length} рядов)`}
                </span>
              </div>
              {showKeyboard ? (
                <ChevronDown className="h-4 w-4 text-gray-500" />
              ) : (
                <ChevronRight className="h-4 w-4 text-gray-500" />
              )}
            </button>

            {showKeyboard && (
              <div className="px-3 pb-3 border-t border-gray-100 space-y-3 pt-3">
                {keyboardRows.map((row, rowIndex) => (
                  <div key={rowIndex} className="border border-gray-200 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Ряд {rowIndex + 1}</span>
                      <div className="flex space-x-1">
                        <button
                          type="button"
                          onClick={() => addButtonToRow(rowIndex)}
                          disabled={row.buttons.length >= 3}
                          className="flex items-center space-x-1 px-2 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200 disabled:opacity-50"
                        >
                          <Plus className="h-3 w-3" />
                        </button>
                        <button
                          type="button"
                          onClick={() => removeKeyboardRow(rowIndex)}
                          className="flex items-center space-x-1 px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                      {row.buttons.map((button, buttonIndex) => (
                        <div key={buttonIndex} className="space-y-1 p-2 border border-gray-200 rounded">
                          <input
                            type="text"
                            placeholder="Текст кнопки"
                            value={button.text}
                            onChange={(e) => updateButton(rowIndex, buttonIndex, { text: e.target.value })}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                            disabled={isSending}
                          />
                          <input
                            type="url"
                            placeholder="URL"
                            value={button.url || ''}
                            onChange={(e) => updateButton(rowIndex, buttonIndex, { url: e.target.value || undefined })}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                            disabled={isSending}
                          />
                          <input
                            type="text"
                            placeholder="Callback data"
                            value={button.callback_data || ''}
                            onChange={(e) => updateButton(rowIndex, buttonIndex, { callback_data: e.target.value || undefined })}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                            disabled={isSending}
                          />
                          <button
                            type="button"
                            onClick={() => removeButtonFromRow(rowIndex, buttonIndex)}
                            className="w-full flex items-center justify-center space-x-1 px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}

                <button
                  type="button"
                  onClick={addKeyboardRow}
                  className="flex items-center space-x-2 px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 text-sm"
                >
                  <Plus className="h-4 w-4" />
                  <span>Добавить ряд</span>
                </button>
              </div>
            )}
          </div>

          {/* Send button */}
          <button
            type="submit"
            disabled={isSending || !message.trim() || message.length > 4096}
            className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isSending ? (
              <>
                <Loading />
                <span>Отправка...</span>
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                <span>Отправить рассылку</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Results summary - compact version */}
      {showResults && result && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Результаты рассылки</h3>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <div>
                <p className="text-lg font-bold text-green-600">{result.sent_successfully}</p>
                <p className="text-xs text-gray-600">Успешно</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <XCircle className="h-5 w-5 text-red-500" />
              <div>
                <p className="text-lg font-bold text-red-600">{result.blocked_users}</p>
                <p className="text-xs text-gray-600">Заблокировано</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-orange-500" />
              <div>
                <p className="text-lg font-bold text-orange-600">{result.failed_sends}</p>
                <p className="text-xs text-gray-600">Ошибки</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Clock className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-lg font-bold text-blue-600">{formatDuration(result.duration_seconds)}</p>
                <p className="text-xs text-gray-600">Время</p>
              </div>
            </div>
          </div>

          <div className="text-xs text-gray-500 space-y-1">
            <p>Всего: {result.total_users} пользователей</p>
            <p>{new Date(result.started_at).toLocaleString()} - {new Date(result.completed_at).toLocaleString()}</p>
          </div>
        </div>
      )}
    </div>
  );
};
