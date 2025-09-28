import React from 'react';
import { User, Hash, Calendar, Crown } from 'lucide-react';
import { UserWithChats } from '../../types';

interface UserCompactCardProps {
  user: UserWithChats;
  onClick?: () => void;
}

export const UserCompactCard: React.FC<UserCompactCardProps> = ({ user, onClick }) => {
  // Получить инициалы пользователя для аватара
  const getInitials = (firstName?: string, lastName?: string, username?: string) => {
    if (firstName && lastName) {
      return `${firstName[0]}${lastName[0]}`.toUpperCase();
    }
    if (firstName) return firstName[0].toUpperCase();
    if (username) return username[0].toUpperCase();
    return '?';
  };

  const initials = getInitials(user.first_name, user.last_name, user.username);

  return (
    <div
      className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-all duration-200 cursor-pointer hover:border-gray-300"
      onClick={onClick}
    >
      {/* Header с аватаром и основной информацией */}
      <div className="flex items-center space-x-3 mb-3">
        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
          <span className="text-sm font-semibold text-blue-600">{initials}</span>
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="font-semibold text-gray-900 text-sm leading-tight truncate">
            {user.first_name} {user.last_name}
          </h3>
          {user.username && (
            <p className="text-xs text-gray-500 truncate">@{user.username}</p>
          )}
        </div>
        {user.is_admin && (
          <Crown className="h-4 w-4 text-yellow-500 flex-shrink-0" />
        )}
      </div>

      {/* Статистика */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        <div className="bg-gray-50 rounded-md p-2 text-center">
          <div className="text-sm font-semibold text-gray-900">{user.chats.length}</div>
          <div className="text-xs text-gray-500">чатов</div>
        </div>
        <div className="bg-gray-50 rounded-md p-2 text-center">
          <div className="text-sm font-semibold text-gray-900">
            {user.chats.filter(chat => chat.chat_type === 'channel').length +
             user.chats.filter(chat => chat.linked_channel_info).length}
          </div>
          <div className="text-xs text-gray-500">каналов</div>
        </div>
      </div>

      {/* Дата создания */}
      <div className="flex items-center space-x-1 text-xs text-gray-500">
        <Calendar className="h-3 w-3 flex-shrink-0" />
        <span>Создан {new Date(user.created_at).toLocaleDateString('ru-RU')}</span>
      </div>
    </div>
  );
};
