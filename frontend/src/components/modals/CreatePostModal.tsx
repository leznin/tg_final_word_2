import React, { useState } from 'react';
import { X, Send, Plus, Settings, ChevronDown, ChevronRight } from 'lucide-react';
import { MediaUploader } from '../ui/MediaUploader';
import { useCreateChatPost, useUploadChatMedia } from '../../hooks/useChatPosts';
import { ChatPostCreate, MediaUpload, InlineKeyboardButton, InlineKeyboardRow } from '../../types';

interface CreatePostModalProps {
  chatId: number;
  onClose: () => void;
  onSuccess?: () => void;
}

export const CreatePostModal: React.FC<CreatePostModalProps> = ({
  chatId,
  onClose,
  onSuccess
}) => {
  const [contentText, setContentText] = useState('');
  const [media, setMedia] = useState<MediaUpload | null>(null);
  const [mediaFile, setMediaFile] = useState<File | null>(null);
  const [sendImmediately, setSendImmediately] = useState(true);
  const [scheduledTime, setScheduledTime] = useState('');
  const [pinMessage, setPinMessage] = useState(false);
  const [pinDuration, setPinDuration] = useState<number | undefined>(undefined);
  const [deleteAfter, setDeleteAfter] = useState<number | undefined>(undefined);
  const [showKeyboard, setShowKeyboard] = useState(false);
  const [keyboardRows, setKeyboardRows] = useState<InlineKeyboardRow[]>([]);

  const createPostMutation = useCreateChatPost();
  const uploadMediaMutation = useUploadChatMedia();

  const handleFileSelect = async (file: File) => {
    setMediaFile(file);

    // Determine media type
    const fileExtension = file.name.toLowerCase().split('.').pop();
    let mediaType: 'photo' | 'video' | 'document' = 'document';

    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(fileExtension || '')) {
      mediaType = 'photo';
    } else if (['mp4', 'avi', 'mov', 'mkv'].includes(fileExtension || '')) {
      mediaType = 'video';
    }

    try {
      const uploadResult = await uploadMediaMutation.mutateAsync(file);
      setMedia({
        type: mediaType,
        url: uploadResult.url,
        filename: file.name
      });
    } catch (error) {
      console.error('Failed to upload media:', error);
      alert('Не удалось загрузить файл');
      setMediaFile(null);
    }
  };

  const handleClearMedia = () => {
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!contentText.trim() && !media) {
      alert('Введите текст или прикрепите медиа');
      return;
    }

    if (!sendImmediately && !scheduledTime) {
      alert('Укажите время отправки');
      return;
    }

    // Convert local datetime to ISO string preserving the local timezone
    // datetime-local input returns time without timezone (e.g., "2025-11-06T08:30")
    // We need to append the local timezone to send the correct time to the server
    let scheduledSendAt: string | undefined = undefined;
    if (!sendImmediately && scheduledTime) {
      // Get timezone offset in minutes and convert to ±HH:MM format
      const date = new Date(scheduledTime);
      const tzOffset = -date.getTimezoneOffset(); // Note: getTimezoneOffset returns negative for positive offsets
      const sign = tzOffset >= 0 ? '+' : '-';
      const hours = String(Math.floor(Math.abs(tzOffset) / 60)).padStart(2, '0');
      const minutes = String(Math.abs(tzOffset) % 60).padStart(2, '0');
      scheduledSendAt = `${scheduledTime}:00${sign}${hours}:${minutes}`;
    }

    // Prepare keyboard markup
    const replyMarkup = keyboardRows.length > 0 && keyboardRows.some(row => row.buttons.length > 0)
      ? { inline_keyboard: keyboardRows.filter(row => row.buttons.length > 0 && row.buttons.some(btn => btn.text.trim())) }
      : undefined;

    const postData: ChatPostCreate = {
      chat_id: chatId,
      content_text: contentText.trim() || undefined,
      media: media || undefined,
      send_immediately: sendImmediately,
      scheduled_send_at: scheduledSendAt,
      pin_message: pinMessage,
      pin_duration_minutes: pinMessage ? pinDuration : undefined,
      delete_after_minutes: deleteAfter,
      reply_markup: replyMarkup
    };

    try {
      await createPostMutation.mutateAsync(postData);
      onSuccess?.();
      onClose();
    } catch (error: any) {
      console.error('Failed to create post:', error);
      alert(error?.response?.data?.detail || 'Не удалось создать пост');
    }
  };

  const isSubmitting = createPostMutation.isPending;
  const isUploading = uploadMediaMutation.isPending;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Создать пост</h2>
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
          {/* Text Content */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Текст сообщения
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

          {/* Media Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Медиа (опционально)
            </label>
            <MediaUploader
              onFileSelect={handleFileSelect}
              onClear={handleClearMedia}
              isUploading={isUploading}
              mediaUrl={media?.url}
              mediaType={media?.type}
              mediaFilename={media?.filename}
            />
          </div>

          {/* Scheduling Section */}
          <div className="border border-gray-200 rounded-lg p-4 space-y-3">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="sendImmediately"
                checked={sendImmediately}
                onChange={(e) => setSendImmediately(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                disabled={isSubmitting}
              />
              <label htmlFor="sendImmediately" className="ml-2 text-sm font-medium text-gray-700">
                Отправить немедленно
              </label>
            </div>

            {!sendImmediately && (
              <div>
                <label className="block text-sm text-gray-600 mb-1">
                  Время отправки *
                </label>
                <input
                  type="datetime-local"
                  value={scheduledTime}
                  onChange={(e) => setScheduledTime(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isSubmitting}
                  required={!sendImmediately}
                />
                <p className="mt-1 text-xs text-gray-500">
                  Укажите дату и время когда пост должен быть отправлен
                </p>
              </div>
            )}
          </div>

          {/* Pin Settings */}
          <div className="border border-gray-200 rounded-lg p-4 space-y-3">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="pinMessage"
                checked={pinMessage}
                onChange={(e) => setPinMessage(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                disabled={isSubmitting}
              />
              <label htmlFor="pinMessage" className="ml-2 text-sm font-medium text-gray-700">
                Закрепить сообщение
              </label>
            </div>

            {pinMessage && (
              <div>
                <label className="block text-sm text-gray-600 mb-1">
                  Открепить через (минут, опционально)
                </label>
                <input
                  type="number"
                  value={pinDuration || ''}
                  onChange={(e) => setPinDuration(e.target.value ? parseInt(e.target.value) : undefined)}
                  placeholder="Оставить закрепленным"
                  min="1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isSubmitting}
                />
                <div className="flex space-x-2 mt-2">
                  <button
                    type="button"
                    onClick={() => setPinDuration(60)}
                    className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                    disabled={isSubmitting}
                  >
                    1 ч
                  </button>
                  <button
                    type="button"
                    onClick={() => setPinDuration(120)}
                    className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                    disabled={isSubmitting}
                  >
                    2 ч
                  </button>
                  <button
                    type="button"
                    onClick={() => setPinDuration(360)}
                    className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                    disabled={isSubmitting}
                  >
                    6 ч
                  </button>
                  <button
                    type="button"
                    onClick={() => setPinDuration(720)}
                    className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                    disabled={isSubmitting}
                  >
                    12 ч
                  </button>
                  <button
                    type="button"
                    onClick={() => setPinDuration(1440)}
                    className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                    disabled={isSubmitting}
                  >
                    24 ч
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Delete Settings */}
          <div className="border border-gray-200 rounded-lg p-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Удалить через (минут, опционально)
            </label>
            <input
              type="number"
              value={deleteAfter || ''}
              onChange={(e) => setDeleteAfter(e.target.value ? parseInt(e.target.value) : undefined)}
              placeholder="Не удалять автоматически"
              min="1"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isSubmitting}
            />
          </div>

          {/* Keyboard Settings */}
          <div className="border border-gray-200 rounded-lg">
            <button
              type="button"
              onClick={() => setShowKeyboard(!showKeyboard)}
              className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center space-x-2">
                <Settings className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">
                  Кнопки {keyboardRows.length > 0 && `(${keyboardRows.length} рядов)`}
                </span>
              </div>
              {showKeyboard ? (
                <ChevronDown className="h-4 w-4 text-gray-500" />
              ) : (
                <ChevronRight className="h-4 w-4 text-gray-500" />
              )}
            </button>

            {showKeyboard && (
              <div className="px-4 pb-4 border-t border-gray-100 space-y-3 pt-3">
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

                    <div className="space-y-2">
                      {row.buttons.map((button, buttonIndex) => (
                        <div key={buttonIndex} className="space-y-2 p-2 border border-gray-200 rounded bg-gray-50">
                          <input
                            type="text"
                            placeholder="Текст кнопки"
                            value={button.text}
                            onChange={(e) => updateButton(rowIndex, buttonIndex, { text: e.target.value })}
                            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            disabled={isSubmitting}
                          />
                          <input
                            type="url"
                            placeholder="URL (опционально)"
                            value={button.url || ''}
                            onChange={(e) => updateButton(rowIndex, buttonIndex, { url: e.target.value || undefined })}
                            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            disabled={isSubmitting}
                          />
                          <input
                            type="text"
                            placeholder="Callback data (опционально)"
                            value={button.callback_data || ''}
                            onChange={(e) => updateButton(rowIndex, buttonIndex, { callback_data: e.target.value || undefined })}
                            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            disabled={isSubmitting}
                          />
                          <button
                            type="button"
                            onClick={() => removeButtonFromRow(rowIndex, buttonIndex)}
                            className="w-full flex items-center justify-center space-x-1 px-2 py-1.5 text-xs bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
                          >
                            <X className="h-3 w-3" />
                            <span>Удалить кнопку</span>
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}

                <button
                  type="button"
                  onClick={addKeyboardRow}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors"
                >
                  <Plus className="h-4 w-4" />
                  <span>Добавить ряд кнопок</span>
                </button>
              </div>
            )}
          </div>

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
              disabled={isSubmitting || isUploading || (!contentText.trim() && !media)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <Send className="h-4 w-4" />
              <span>{isSubmitting ? 'Отправка...' : 'Отправить'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
