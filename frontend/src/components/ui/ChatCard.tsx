import React, { useState } from 'react';
import { MessageSquare, Hash, Radio, Users, Clock, User, Calendar, Shield, ShieldCheck, Star, AlertTriangle, EyeOff, ChevronDown, ChevronUp } from 'lucide-react';
import { Chat } from '../../types';

interface ChatCardProps {
  chat: Chat;
  onClick?: () => void;
}

export const ChatCard: React.FC<ChatCardProps> = ({ chat, onClick }) => {
  const [isExpanded, setIsExpanded] = useState(false);

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
      className={`bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-all duration-200 cursor-pointer hover:border-gray-300 flex flex-col relative ${
        !chat.is_active ? 'opacity-60' : ''
      }`}
      onClick={onClick}
    >
      {/* Inactive overlay indicator */}
      {!chat.is_active && (
        <div className="absolute top-2 right-2 z-10">
          <div className="flex items-center space-x-1 bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs font-medium">
            <EyeOff className="h-3 w-3" />
            <span>Неактивен</span>
          </div>
        </div>
      )}

      {/* Compact Header - always visible */}
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

      {/* Compact Info - always visible */}
      <div className="space-y-2 mb-3 flex-shrink-0">
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

        {/* Subscription indicator - compact */}
        {chat.active_subscription && (
          <div className="flex items-center space-x-1.5">
            <Star className="h-3.5 w-3.5 text-green-600 flex-shrink-0" />
            <span className="text-xs text-green-800 truncate">
              Подписка до {new Date(chat.active_subscription.end_date).toLocaleDateString('ru-RU')}
            </span>
          </div>
        )}

        {/* Linked channel indicator - compact */}
        {chat.linked_channel_info && (
          <div className="flex items-center space-x-1.5">
            <Radio className="h-3.5 w-3.5 text-purple-600 flex-shrink-0" />
            <span className="text-xs text-purple-800 truncate">
              Привязан канал
            </span>
          </div>
        )}
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <>
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

          {/* Subscription Info */}
          {chat.active_subscription && (
            <div className="p-2.5 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200 flex-shrink-0">
              <div className="flex items-center space-x-2 mb-1.5">
                <Star className="h-3.5 w-3.5 text-green-600 flex-shrink-0" />
                <span className="text-xs font-medium text-green-900">Подписка</span>
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-green-800">Тип:</span>
                  <span className="text-xs font-medium text-green-900 capitalize">
                    {chat.active_subscription.subscription_type === 'month' ? 'Месяц' : 'Год'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-green-800">Стоимость:</span>
                  <span className="text-xs font-medium text-green-900 flex items-center">
                    {chat.active_subscription.price_stars} <Star className="h-3 w-3 ml-1 text-yellow-500" />
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-green-800">Истекает:</span>
                  <span className={`text-xs font-medium ${new Date(chat.active_subscription.end_date) < new Date() ? 'text-red-600' : 'text-green-900'}`}>
                    {new Date(chat.active_subscription.end_date).toLocaleDateString('ru-RU')}
                    {new Date(chat.active_subscription.end_date) < new Date() && (
                      <AlertTriangle className="h-3 w-3 ml-1 inline text-red-600" />
                    )}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Detailed Content */}
          <div className="space-y-2 mb-3 flex-1 min-h-0">
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
        </>
      )}

      {/* Expand/Collapse Button */}
      <div className="border-t border-gray-100 pt-2 mt-3 flex-shrink-0">
        <button
          onClick={(e) => {
            e.stopPropagation();
            setIsExpanded(!isExpanded);
          }}
          className="w-full flex items-center justify-center space-x-2 py-2 text-xs text-gray-600 hover:text-gray-900 transition-colors duration-200"
        >
          {isExpanded ? (
            <>
              <ChevronUp className="h-3 w-3" />
              <span>Свернуть</span>
            </>
          ) : (
            <>
              <ChevronDown className="h-3 w-3" />
              <span>Показать больше</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
