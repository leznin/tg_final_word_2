import React from 'react';
import { User, Calendar, MessageSquare, ExternalLink } from 'lucide-react';
import { useModerators } from '../hooks/useModerators';
import { DataTable } from '../components/ui/DataTable';
import { Loading } from '../components/ui/Loading';
import { Moderator } from '../types';

export const Moderators: React.FC = () => {
  const { data, isLoading } = useModerators();

  if (isLoading) return <Loading />;

  const moderators = data?.moderators || [];

  const columns = [
    {
      key: 'moderator_user_id',
      label: 'ID пользователя',
      sortable: true,
      render: (value: number) => (
        <span className="font-mono text-sm text-gray-600">{value}</span>
      ),
    },
    {
      key: 'moderator_name',
      label: 'Имя',
      sortable: true,
      render: (value: string, moderator: Moderator) => (
        <div className="flex items-center space-x-2">
          <User className="h-4 w-4 text-gray-400" />
          <div>
            <div className="font-medium text-gray-900">{value}</div>
            {moderator.moderator_username && (
              <a
                href={`https://t.me/${moderator.moderator_username}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-1 text-sm text-blue-600 hover:underline"
                onClick={(e) => e.stopPropagation()}
              >
                <span>@{moderator.moderator_username}</span>
                <ExternalLink className="h-3 w-3" />
              </a>
            )}
          </div>
        </div>
      ),
    },
    {
      key: 'chat_title',
      label: 'Чат',
      sortable: true,
      render: (value: string) => (
        <div className="flex items-center space-x-2">
          <MessageSquare className="h-4 w-4 text-blue-500" />
          <span className="font-medium">{value}</span>
        </div>
      ),
    },
    {
      key: 'added_by_user_id',
      label: 'Добавил',
      sortable: true,
      render: (value: number) => (
        <span className="font-mono text-sm text-gray-600">ID: {value}</span>
      ),
    },
    {
      key: 'added_date',
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

  // Группировка статистики
  const uniqueChats = new Set(moderators.map(m => m.chat_id)).size;
  const uniqueUsers = new Set(moderators.map(m => m.moderator_user_id)).size;
  const uniqueAdders = new Set(moderators.map(m => m.added_by_user_id)).size;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Управление модераторами</h1>
          <p className="mt-2 text-sm text-gray-600">
            Всего записей: {moderators.length}
          </p>
        </div>
      </div>

      <DataTable
        data={moderators}
        columns={columns}
        searchPlaceholder="Поиск по имени, username или чату..."
      />

      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Статистика модераторов</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{uniqueChats}</div>
            <div className="text-sm text-blue-800">Чатов с модераторами</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{uniqueUsers}</div>
            <div className="text-sm text-green-800">Уникальных модераторов</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">{uniqueAdders}</div>
            <div className="text-sm text-purple-800">Администраторов</div>
          </div>
        </div>
      </div>
    </div>
  );
};