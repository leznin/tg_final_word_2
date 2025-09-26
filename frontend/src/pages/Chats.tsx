import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, Calendar, Settings, Hash, Radio } from 'lucide-react';
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
      key: 'chat_id',
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
      key: 'chat_title',
      label: 'Название',
      sortable: true,
      render: (value: string, chat: Chat) => (
        <div className="flex items-center space-x-2">
          <MessageSquare className="h-4 w-4 text-blue-500" />
          <span 
            className="font-medium text-blue-600 cursor-pointer hover:underline"
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/chats/${chat.chat_id}`);
            }}
          >
            {value}
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
      key: 'admin_user_id',
      label: 'Админ ID',
      sortable: true,
      render: (value: number) => (
        <span className="font-mono text-sm text-gray-600">{value}</span>
      ),
    },
    {
      key: 'channel_count',
      label: 'Каналы',
      sortable: true,
      render: (value: number) => (
        <div className="flex items-center space-x-1">
          <Radio className="h-4 w-4 text-green-500" />
          <span className={value > 0 ? 'text-green-600 font-medium' : 'text-gray-400'}>{value}</span>
        </div>
      ),
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
      key: 'max_edit_time_minutes',
      label: 'Время редактирования',
      sortable: true,
      render: (value: number) => (
        <span className="text-sm">{value} мин</span>
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

  const handleRowClick = (chat: Chat) => {
    navigate(`/chats/${chat.chat_id}`);
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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {chats.filter(c => c.chat_type === 'group').length}
            </div>
            <div className="text-sm text-blue-800">Групп</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {chats.filter(c => c.chat_type === 'supergroup').length}
            </div>
            <div className="text-sm text-green-800">Супергрупп</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {chats.filter(c => c.channel_count > 0).length}
            </div>
            <div className="text-sm text-purple-800">С каналами</div>
          </div>
        </div>
      </div>
    </div>
  );
};