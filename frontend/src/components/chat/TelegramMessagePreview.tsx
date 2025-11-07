import React from 'react';
import { Clock } from 'lucide-react';
import { WelcomeMessageButton } from '../../types';

interface TelegramMessagePreviewProps {
  text?: string;
  mediaType?: 'photo' | 'video' | null;
  mediaUrl?: string;
  buttons?: WelcomeMessageButton[][];
  lifetimeMinutes?: number;
}

export const TelegramMessagePreview: React.FC<TelegramMessagePreviewProps> = ({
  text,
  mediaType,
  mediaUrl,
  buttons,
  lifetimeMinutes
}) => {
  // Функция для форматирования текста с Markdown-разметкой Telegram
  const formatTelegramText = (text: string) => {
    // Поддержка базовых форматов Telegram
    let formatted = text;
    
    // **жирный** или __жирный__
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/__(.+?)__/g, '<strong>$1</strong>');
    
    // *курсив* или _курсив_
    formatted = formatted.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');
    formatted = formatted.replace(/(?<!_)_(?!_)(.+?)(?<!_)_(?!_)/g, '<em>$1</em>');
    
    // ~зачёркнутый~
    formatted = formatted.replace(/~(.+?)~/g, '<del>$1</del>');
    
    // `моноширинный` и ```код```
    formatted = formatted.replace(/```(.+?)```/gs, '<pre>$1</pre>');
    formatted = formatted.replace(/`(.+?)`/g, '<code>$1</code>');
    
    // ||спойлер||
    formatted = formatted.replace(/\|\|(.+?)\|\|/g, '<span class="spoiler">$1</span>');
    
    // [ссылка](url)
    formatted = formatted.replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    
    return formatted;
  };

  return (
    <div className="max-w-md mx-auto">
      {/* Telegram message bubble */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
        {/* Header - имитация шапки чата */}
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-4 py-3 flex items-center space-x-3">
          <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center text-white font-bold">
            👋
          </div>
          <div className="flex-1">
            <div className="text-white font-semibold text-sm">Бот</div>
            <div className="text-white/80 text-xs">онлайн</div>
          </div>
        </div>

        {/* Message content area */}
        <div className="bg-[#0f1419] p-4">
          {/* Message bubble */}
          <div className="flex justify-start">
            <div className="max-w-[85%]">
              {/* Combined media and text bubble */}
              <div className="bg-white rounded-2xl rounded-tl-sm shadow-sm overflow-hidden">
                {/* Lifetime warning at the top if present */}
                {lifetimeMinutes && (
                  <div className="flex items-center space-x-1 text-xs text-gray-500 px-4 pt-3 pb-2 border-b border-gray-200">
                    <Clock className="h-3 w-3" />
                    <span>Удалится через {lifetimeMinutes} мин</span>
                  </div>
                )}

                {/* Media preview inside bubble */}
                {mediaType && mediaUrl && (
                  <div className="overflow-hidden">
                    {mediaType === 'photo' ? (
                      <img 
                        src={mediaUrl} 
                        alt="Welcome media" 
                        className="w-full h-auto max-h-64 object-cover"
                        onError={(e) => {
                          e.currentTarget.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23ddd" width="400" height="300"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3E📷 Фото%3C/text%3E%3C/svg%3E';
                        }}
                      />
                    ) : (
                      <div className="relative">
                        <video 
                          src={mediaUrl} 
                          className="w-full h-auto max-h-64 object-cover"
                          controls
                        />
                        <div className="absolute top-2 right-2 bg-black/50 px-2 py-1 rounded text-white text-xs">
                          🎥 Видео
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Text content inside bubble */}
                {text && (
                  <div className={`px-4 ${lifetimeMinutes ? 'pt-3' : 'pt-3'} pb-3`}>
                    <div 
                      className="text-[15px] text-gray-900 leading-relaxed whitespace-pre-wrap break-words"
                      dangerouslySetInnerHTML={{ __html: formatTelegramText(text) }}
                      style={{
                        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
                      }}
                    />
                    <div className="flex items-center justify-end mt-1 space-x-1">
                      <span className="text-[11px] text-gray-400">
                        {new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                )}

                {/* If no text but has media, still show time */}
                {!text && mediaType && mediaUrl && (
                  <div className="px-4 pb-3 pt-2">
                    <div className="flex items-center justify-end space-x-1">
                      <span className="text-[11px] text-gray-400">
                        {new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                )}
              </div>

              {/* Inline keyboard buttons */}
              {buttons && buttons.length > 0 && (
                <div className="mt-1 space-y-1">
                  {buttons.map((row, rowIndex) => (
                    <div key={rowIndex} className="flex gap-1">
                      {row.map((button, btnIndex) => (
                        <button
                          key={btnIndex}
                          className="flex-1 bg-white hover:bg-gray-50 text-blue-600 font-medium py-2.5 px-3 rounded-lg text-sm transition-colors shadow-sm border border-gray-200 active:bg-gray-100"
                          style={{
                            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
                          }}
                          onClick={(e) => {
                            e.preventDefault();
                            if (button.url) {
                              // Показываем, что это ссылка
                              alert(`Откроется ссылка: ${button.url}`);
                            }
                          }}
                        >
                          <span className="truncate block">
                            {button.text}
                            {button.url && ' 🔗'}
                          </span>
                        </button>
                      ))}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Info badge */}
      <div className="mt-3 text-center">
        <span className="inline-flex items-center px-3 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
          📱 Предпросмотр сообщения в стиле Telegram
        </span>
      </div>

      {/* Styling for special elements */}
      <style>{`
        .spoiler {
          background: #999;
          color: transparent;
          border-radius: 2px;
          transition: all 0.2s;
          cursor: pointer;
        }
        .spoiler:hover {
          background: transparent;
          color: inherit;
        }
        code {
          background: #f0f0f0;
          padding: 2px 4px;
          border-radius: 3px;
          font-family: 'Courier New', monospace;
          font-size: 0.9em;
        }
        pre {
          background: #f0f0f0;
          padding: 8px;
          border-radius: 4px;
          overflow-x: auto;
          font-family: 'Courier New', monospace;
          font-size: 0.9em;
        }
        a {
          color: #2481cc;
          text-decoration: none;
        }
        a:hover {
          text-decoration: underline;
        }
        del {
          text-decoration: line-through;
          opacity: 0.6;
        }
      `}</style>
    </div>
  );
};
