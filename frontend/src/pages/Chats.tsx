import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, Calendar, Settings, Hash, Radio, User, Users } from 'lucide-react';
import { useChats } from '../hooks/useChats';
import { DataTable } from '../components/ui/DataTable';
import { Loading } from '../components/ui/Loading';
import { Chat } from '../types';

export const Chats: React.FC = () => {
  const navigate = useNavigate();
  const { data, isLoading } = useChats();

  if (isLoading) return <Loading />;

  const chats = data?.chats || [];

  const columns = [
    {
      key: 'telegram_chat_id',
      label: 'ID чата',
      sortable: true,
      render: (value: number) => (
        <div className="flex items-center space-x-2">
          <Hash className="h-4 w-4 text-gray-400" />
          <span className="font-mono text-sm">{value}</span>
        </div>
      ),
    },
    {
      key: 'title',
      label: 'Название',
      sortable: true,
      render: (value: string, chat: Chat) => (
        <div className="flex items-center space-x-2">
          <MessageSquare className="h-4 w-4 text-blue-500" />
          <span
            className="font-medium text-blue-600 cursor-pointer hover:underline"
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/chats/${chat.telegram_chat_id}`);
            }}
          >
            {value || 'Без названия'}
          </span>
        </div>
      ),
    },
    {
      key: 'chat_type',
      label: 'Тип',
      sortable: true,
      render: (value: string) => {
        const typeLabels = {
          group: 'Группа',
          supergroup: 'Супергруппа',
          channel: 'Канал'
        };
        const colors = {
          group: 'bg-blue-100 text-blue-800',
          supergroup: 'bg-green-100 text-green-800',
          channel: 'bg-purple-100 text-purple-800'
        };
        return (
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[value as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
            {typeLabels[value as keyof typeof typeLabels] || value}
          </span>
        );
      },
    },
    {
      key: 'linked_channel_info',
      label: 'Привязанный канал',
      sortable: false,
      render: (value: any, chat: Chat) => {
        if (!chat.linked_channel_info) {
          return <span className="text-gray-400 text-sm">Не привязан</span>;
        }

        const channel = chat.linked_channel_info;
        return (
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <Radio className="h-4 w-4 text-purple-500" />
              <span className="text-sm font-medium text-purple-600">
                {channel.title || channel.username || `Канал ${channel.telegram_chat_id}`}
              </span>
            </div>
            <div className="text-xs text-gray-500 pl-6">
              ID: {channel.telegram_chat_id}
            </div>
          </div>
        );
      },
    },
    {
      key: 'linked_channel_info',
      label: 'Администратор канала',
      sortable: false,
      render: (value: any, chat: Chat) => {
        if (!chat.linked_channel_info) {
          return <span className="text-gray-400 text-sm">-</span>;
        }

        const channel = chat.linked_channel_info;
        return (
          <div className="flex items-center space-x-2">
            <User className="h-4 w-4 text-blue-500" />
            <div className="text-sm">
              <div className="font-medium">{channel.admin_name || 'Неизвестен'}</div>
              {channel.admin_username && (
                <div className="text-gray-500">@{channel.admin_username}</div>
              )}
            </div>
          </div>
        );
      },
    },
    {
      key: 'chat_moderators',
      label: 'Модераторы чата',
      sortable: false,
      render: (value: any, chat: Chat) => {
        if (!chat.chat_moderators || !chat.chat_moderators.length) {
          return (
            <div className="flex items-center space-x-2">
              <Users className="h-4 w-4 text-gray-400" />
              <span className="text-gray-400 text-sm">Нет модераторов</span>
            </div>
          );
        }

        const moderators = chat.chat_moderators;
        return (
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <Users className="h-4 w-4 text-green-500" />
              <span className="text-sm font-medium text-green-600">
                {moderators.length} модератор{moderators.length > 1 ? 'ов' : ''}
              </span>
            </div>
            <div className="max-w-xs">
              {moderators.slice(0, 2).map((mod, index) => (
                <div key={mod.id} className="text-xs text-gray-600 truncate">
                  {mod.first_name || mod.username || `Модератор ${mod.moderator_user_id}`}
                  {index < moderators.length - 1 && index < 1 && ', '}
                </div>
              ))}
              {moderators.length > 2 && (
                <div className="text-xs text-gray-500">
                  и ещё {moderators.length - 2}...
                </div>
              )}
            </div>
          </div>
        );
      },
    },
    {
      key: 'delete_messages_enabled',
      label: 'Удаление',
      sortable: true,
      render: (value: boolean) => (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          value ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
        }`}>
          {value ? 'Включено' : 'Отключено'}
        </span>
      ),
    },
    {
      key: 'message_edit_timeout_minutes',
      label: 'Время редактирования',
      sortable: true,
      render: (value: number) => (
        <span className="text-sm">{value || 0} мин</span>
      ),
    },
    {
      key: 'added_at',
      label: 'Дата добавления',
      sortable: true,
      render: (value: string) => (
        <div className="flex items-center space-x-1">
          <Calendar className="h-4 w-4 text-gray-400" />
          <span className="text-sm text-gray-600">
            {new Date(value).toLocaleDateString('ru-RU')}
          </span>
        </div>
      ),
    },
  ];

  const handleRowClick = (chat: Chat) => {
    navigate(`/chats/${chat.telegram_chat_id}`);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Управление чатами</h1>
          <p className="mt-2 text-sm text-gray-600">
            Всего чатов: {chats.length}
          </p>
        </div>
      </div>

      <DataTable
        data={chats}
        columns={columns}
        searchPlaceholder="Поиск по названию или ID чата..."
        onRowClick={handleRowClick}
      />

      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Статистика по чатам</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {chats.length}
            </div>
            <div className="text-sm text-blue-800">Всего чатов</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {chats.filter(c => c.chat_type === 'group').length}
            </div>
            <div className="text-sm text-green-800">Групп</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {chats.filter(c => c.chat_type === 'supergroup').length}
            </div>
            <div className="text-sm text-purple-800">Супергрупп</div>
          </div>
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">
              {chats.filter(c => c.linked_channel_info).length}
            </div>
            <div className="text-sm text-orange-800">С привязанными каналами</div>
          </div>
        </div>
      </div>
    </div>
  );
};