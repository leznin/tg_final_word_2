import React from 'react';
import { MessageSquare, Hash, Radio, Users, Clock, User, Calendar, Shield, ShieldCheck } from 'lucide-react';
import { Chat } from '../../types';

interface ChatCardProps {
  chat: Chat;
  onClick?: () => void;
}

export const ChatCard: React.FC<ChatCardProps> = ({ chat, onClick }) => {
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

  const getBotPermissionsStatus = () => {
    if (!chat.last_info_update) return { label: 'Не проверено', color: 'text-gray-400' };
    if (!chat.bot_permissions) return { label: 'Нет прав', color: 'text-red-600' };

    const hasAdminRights = chat.bot_permissions.can_delete_messages ||
                          chat.bot_permissions.can_restrict_members ||
                          chat.bot_permissions.can_promote_members;
    return {
      label: hasAdminRights ? 'Администратор' : 'Ограниченные',
      color: hasAdminRights ? 'text-green-600' : 'text-yellow-600'
    };
  };

  const botPermissions = getBotPermissionsStatus();

  return (
    <div
      className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-all duration-200 cursor-pointer hover:border-gray-300 min-h-[280px] flex flex-col"
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3 flex-shrink-0">
        <div className="flex items-center space-x-3 min-w-0 flex-1">
          <div className={`p-1.5 rounded-lg flex-shrink-0 ${typeInfo.color.replace('text-', 'bg-').replace('-800', '-100')}`}>
            <TypeIcon className={`h-4 w-4 ${typeInfo.color}`} />
          </div>
          <div className="min-w-0 flex-1">
            <h3 className="font-semibold text-gray-900 text-base leading-tight overflow-hidden" style={{
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical' as const,
              lineHeight: '1.25rem',
              maxHeight: '2.5rem'
            }}>
              {chat.title || 'Без названия'}
            </h3>
            <div className="flex items-center space-x-2 mt-1">
              <Hash className="h-3 w-3 text-gray-400 flex-shrink-0" />
              <span className="text-xs font-mono text-gray-600 truncate">{chat.telegram_chat_id}</span>
              <span className={`inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium ${typeInfo.color} flex-shrink-0`}>
                {typeInfo.label}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Linked Channel Info */}
      {chat.linked_channel_info && (
        <div className="mb-3 p-2.5 bg-purple-50 rounded-lg border border-purple-200 flex-shrink-0">
          <div className="flex items-center space-x-2 mb-1.5">
            <Radio className="h-3.5 w-3.5 text-purple-600 flex-shrink-0" />
            <span className="text-xs font-medium text-purple-900">Привязанный канал</span>
          </div>
          <div className="text-xs text-purple-800 font-medium truncate mb-1">
            {chat.linked_channel_info.title || chat.linked_channel_info.username || `Канал ${chat.linked_channel_info.telegram_chat_id}`}
          </div>
          <div className="flex items-center space-x-1.5">
            <User className="h-3 w-3 text-purple-600 flex-shrink-0" />
            <span className="text-xs text-purple-800 truncate">
              {chat.linked_channel_info.admin_name || 'Неизвестен'}
              {chat.linked_channel_info.admin_username && (
                <span className="text-purple-600 ml-1">@{chat.linked_channel_info.admin_username}</span>
              )}
            </span>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="space-y-2 flex-1 min-h-0">
        {/* Moderators */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1.5 min-w-0 flex-1">
            <Users className="h-3.5 w-3.5 text-gray-400 flex-shrink-0" />
            <span className="text-xs text-gray-600 truncate">
              {chat.chat_moderators?.length || 0} модератор{chat.chat_moderators?.length !== 1 ? 'ов' : ''}
            </span>
          </div>
        </div>

        {/* Delete Messages Status */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1.5 min-w-0 flex-1">
            <Shield className="h-3.5 w-3.5 text-gray-400 flex-shrink-0" />
            <span className="text-xs text-gray-600 truncate">Удаление</span>
          </div>
          <span className={`text-xs font-medium flex-shrink-0 ${chat.delete_messages_enabled ? 'text-red-600' : 'text-gray-600'}`}>
            {chat.delete_messages_enabled ? 'Вкл' : 'Откл'}
          </span>
        </div>

        {/* Edit Timeout */}
        {chat.message_edit_timeout_minutes && chat.message_edit_timeout_minutes > 0 && (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-1.5 min-w-0 flex-1">
              <Clock className="h-3.5 w-3.5 text-gray-400 flex-shrink-0" />
              <span className="text-xs text-gray-600 truncate">Редактирование</span>
            </div>
            <span className="text-xs font-medium text-gray-900 flex-shrink-0">
              {chat.message_edit_timeout_minutes} мин
            </span>
          </div>
        )}

        {/* Member Count */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1.5 min-w-0 flex-1">
            <User className="h-3.5 w-3.5 text-gray-400 flex-shrink-0" />
            <span className="text-xs text-gray-600 truncate">Участников</span>
          </div>
          <span className="text-xs font-medium text-gray-900 flex-shrink-0 truncate">
            {chat.chat_type === 'channel' ? 'Канал' :
             chat.member_count ? chat.member_count.toLocaleString() :
             chat.last_info_update ? 'Неизвестно' : 'Не получено'}
          </span>
        </div>

        {/* Bot Permissions */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1.5 min-w-0 flex-1">
            <ShieldCheck className="h-3.5 w-3.5 text-gray-400 flex-shrink-0" />
            <span className="text-xs text-gray-600 truncate">Права бота</span>
          </div>
          <span className={`text-xs font-medium flex-shrink-0 truncate ${botPermissions.color}`}>
            {botPermissions.label}
          </span>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-gray-100 pt-2 mt-3 flex-shrink-0">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center space-x-1 min-w-0 flex-1">
            <Calendar className="h-3 w-3 flex-shrink-0" />
            <span className="truncate">Добавлен {new Date(chat.added_at).toLocaleDateString('ru-RU')}</span>
          </div>
          {chat.last_info_update && (
            <span className="flex-shrink-0 ml-2">Обновлено {new Date(chat.last_info_update).toLocaleDateString('ru-RU')}</span>
          )}
        </div>
      </div>
    </div>
  );
};
