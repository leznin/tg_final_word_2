import React from 'react';
import { MessageSquare, Hash, Radio, Users, Clock, Shield } from 'lucide-react';
import { Chat } from '../../types';

interface ChatCompactCardProps {
  chat: Chat;
  onClick?: () => void;
}

export const ChatCompactCard: React.FC<ChatCompactCardProps> = ({ chat, onClick }) => {
  const getChatTypeInfo = (type: string) => {
    switch (type) {
      case 'group':
        return { label: 'Группа', color: 'bg-blue-100 text-blue-800', icon: MessageSquare };
      case 'supergroup':
        return { label: 'Супергруппа', color: 'bg-green-100 text-green-800', icon: MessageSquare };
      case 'channel':
        return { label: 'Канал', color: 'bg-purple-100 text-purple-800', icon: Radio };
      default:
        return { label: type, color: 'bg-gray-100 text-gray-800', icon: MessageSquare };
    }
  };

  const typeInfo = getChatTypeInfo(chat.chat_type);
  const TypeIcon = typeInfo.icon;

  return (
    <div
      className="bg-white rounded-lg shadow-sm border border-gray-200 p-3 hover:shadow-md transition-all duration-200 cursor-pointer hover:border-gray-300"
      onClick={onClick}
    >
      {/* Header с типом и названием */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center space-x-2 min-w-0 flex-1">
          <div className={`p-1 rounded-md flex-shrink-0 ${typeInfo.color.replace('text-', 'bg-').replace('-800', '-100')}`}>
            <TypeIcon className={`h-3 w-3 ${typeInfo.color}`} />
          </div>
          <div className="min-w-0 flex-1">
            <h4 className="font-medium text-gray-900 text-sm leading-tight truncate">
              {chat.title || 'Без названия'}
            </h4>
            <div className="flex items-center space-x-1 mt-1">
              <Hash className="h-3 w-3 text-gray-400 flex-shrink-0" />
              <span className="text-xs font-mono text-gray-600 truncate">{chat.telegram_chat_id}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Привязанный канал */}
      {chat.linked_channel_info && (
        <div className="mb-2 p-2 bg-purple-50 rounded-md border border-purple-200">
          <div className="flex items-center space-x-1.5 mb-1">
            <Radio className="h-3 w-3 text-purple-600 flex-shrink-0" />
            <span className="text-xs font-medium text-purple-900 truncate">
              {chat.linked_channel_info.title || chat.linked_channel_info.username || `Канал ${chat.linked_channel_info.telegram_chat_id}`}
            </span>
          </div>
          <div className="text-xs text-purple-700 truncate">
            Админ: {chat.linked_channel_info.admin_name || 'Неизвестен'}
          </div>
        </div>
      )}

      {/* Модераторы и настройки */}
      <div className="grid grid-cols-2 gap-1 text-xs">
        <div className="flex items-center space-x-1">
          <Users className="h-3 w-3 text-gray-400 flex-shrink-0" />
          <span className="text-gray-600 truncate">
            {chat.chat_moderators?.length || 0} мод.
          </span>
        </div>

        {chat.message_edit_timeout_minutes && chat.message_edit_timeout_minutes > 0 && (
          <div className="flex items-center space-x-1">
            <Clock className="h-3 w-3 text-gray-400 flex-shrink-0" />
            <span className="text-gray-600 truncate">
              {chat.message_edit_timeout_minutes} мин
            </span>
          </div>
        )}

        <div className="flex items-center space-x-1">
          <Shield className="h-3 w-3 text-gray-400 flex-shrink-0" />
          <span className={`truncate ${chat.delete_messages_enabled ? 'text-red-600' : 'text-gray-600'}`}>
            {chat.delete_messages_enabled ? 'Удал.' : 'Без уд.'}
          </span>
        </div>
      </div>
    </div>
  );
};
