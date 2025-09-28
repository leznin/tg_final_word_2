import React from 'react';
import { useNavigate } from 'react-router-dom';
import { UserCompactCard } from './UserCompactCard';
import { ChatCompactCard } from './ChatCompactCard';
import { UserWithChats } from '../../types';

interface UserChatsGroupProps {
  user: UserWithChats;
}

export const UserChatsGroup: React.FC<UserChatsGroupProps> = ({ user }) => {
  const navigate = useNavigate();

  const handleUserClick = () => {
    // Можно добавить навигацию к детальной странице пользователя
    // navigate(`/users/${user.id}`);
  };

  const handleChatClick = (chatId: number) => {
    navigate(`/chats/${chatId}`);
  };

  return (
    <div className="bg-gray-50 rounded-xl p-4 mb-6">
      {/* Заголовок группы */}
      <div className="mb-4">
        <div className="flex items-center space-x-2 mb-1">
          <h2 className="text-lg font-semibold text-gray-900">
            {user.first_name} {user.last_name}
            {user.username && <span className="text-gray-500 text-sm ml-2">(@{user.username})</span>}
          </h2>
          {user.is_admin && (
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
              Администратор
            </span>
          )}
        </div>
        <div className="flex items-center space-x-4 text-sm text-gray-600">
          <span>{user.chats.length} чат{user.chats.length !== 1 ? 'ов' : ''}</span>
          <span>{user.chats.filter(chat => chat.chat_type === 'channel').length} канал{user.chats.filter(chat => chat.chat_type === 'channel').length !== 1 ? 'ов' : ''}</span>
          <span>{user.chats.filter(chat => chat.linked_channel_info).length} привяз{user.chats.filter(chat => chat.linked_channel_info).length !== 1 ? 'ок' : 'ка'}</span>
          <span className="text-gray-400">•</span>
          <span>Создан {new Date(user.created_at).toLocaleDateString('ru-RU')}</span>
        </div>
      </div>

      {/* Сетка с чатами */}
      {user.chats.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {user.chats.map((chat) => (
            <ChatCompactCard
              key={chat.id}
              chat={chat}
              onClick={() => handleChatClick(chat.telegram_chat_id)}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <div className="text-sm">У пользователя нет чатов</div>
        </div>
      )}
    </div>
  );
};
