import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, MessageSquare, Users, Radio, Settings, Calendar, Hash, User, Link, Unlink, Plus, Trash2 } from 'lucide-react';
import { useChatDetail, useAvailableChannels, useLinkChannel, useUnlinkChannel, useChatModerators, useRemoveModerator } from '../hooks/useChats';
import { Loading } from '../components/ui/Loading';

export const ChatDetail: React.FC = () => {
  const { chatId } = useParams<{ chatId: string }>();
  const navigate = useNavigate();
  const { data, isLoading } = useChatDetail(chatId!);
  const [showChannelSelector, setShowChannelSelector] = useState(false);

  // Hooks for channel linking
  const { data: availableChannels } = useAvailableChannels(data?.chat.admin_user_id || 0);
  const linkChannelMutation = useLinkChannel();
  const unlinkChannelMutation = useUnlinkChannel();

  // Hooks for moderators
  const { data: moderatorsData, isLoading: moderatorsLoading } = useChatModerators(chatId!);
  const removeModeratorMutation = useRemoveModerator();

  if (isLoading) return <Loading />;
  if (!data) return <div>Чат не найден</div>;

  const { chat, moderators, channels } = data;

  const handleLinkChannel = async (channelId: number) => {
    try {
      await linkChannelMutation.mutateAsync({ chatId: chat.id, channelId });
      setShowChannelSelector(false);
    } catch (error) {
      console.error('Failed to link channel:', error);
    }
  };

  const handleUnlinkChannel = async () => {
    try {
      await unlinkChannelMutation.mutateAsync(chat.id);
    } catch (error) {
      console.error('Failed to unlink channel:', error);
    }
  };

  const handleRemoveModerator = async (moderatorId: number) => {
    if (window.confirm('Вы уверены, что хотите удалить этого модератора?')) {
      try {
        await removeModeratorMutation.mutateAsync(moderatorId);
      } catch (error) {
        console.error('Failed to remove moderator:', error);
        alert('Не удалось удалить модератора');
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/chats')}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{chat.chat_title}</h1>
          <p className="text-sm text-gray-600">ID чата: {chat.chat_id}</p>
        </div>
      </div>

      {/* Информация о чате */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <MessageSquare className="h-5 w-5 mr-2 text-blue-500" />
          Информация о чате
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <label className="text-sm font-medium text-gray-500">Тип чата</label>
            <p className="mt-1 text-sm text-gray-900">{chat.chat_type}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">ID администратора</label>
            <p className="mt-1 text-sm text-gray-900 font-mono">{chat.admin_user_id}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Статус</label>
            <p className="mt-1">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                chat.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {chat.is_active ? 'Активен' : 'Неактивен'}
              </span>
            </p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Удаление сообщений</label>
            <p className="mt-1">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                chat.delete_messages_enabled ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {chat.delete_messages_enabled ? 'Включено' : 'Отключено'}
              </span>
            </p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Время редактирования</label>
            <p className="mt-1 text-sm text-gray-900">{chat.max_edit_time_minutes} минут</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Дата добавления</label>
            <p className="mt-1 text-sm text-gray-900 flex items-center">
              <Calendar className="h-4 w-4 mr-1 text-gray-400" />
              {new Date(chat.added_date).toLocaleDateString('ru-RU')}
            </p>
          </div>
        </div>
      </div>

      {/* Модераторы */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <Users className="h-5 w-5 mr-2 text-purple-500" />
          Модераторы ({moderatorsData?.length || moderators.length})
        </h2>
        {(moderatorsData || moderators).length > 0 ? (
          <div className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Пользователь
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Добавил
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Дата добавления
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Действия
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {(moderatorsData || moderators).map((moderator) => (
                  <tr key={moderator.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        <User className="h-4 w-4 text-gray-400" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {moderator.moderator_name || `${moderator.first_name || ''} ${moderator.last_name || ''}`.trim() || `Пользователь ${moderator.moderator_user_id}`}
                          </div>
                          <div className="text-sm text-gray-500 font-mono">
                            ID: {moderator.moderator_user_id}
                          </div>
                          {(moderator.moderator_username || moderator.username) && (
                            <a
                              href={`https://t.me/${moderator.moderator_username || moderator.username}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm text-blue-600 hover:underline"
                            >
                              @{moderator.moderator_username || moderator.username}
                            </a>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono">
                      ID: {moderator.added_by_user_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(moderator.added_date || moderator.created_at).toLocaleDateString('ru-RU')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => handleRemoveModerator(moderator.id)}
                        disabled={removeModeratorMutation.isPending}
                        className="text-red-600 hover:text-red-900 disabled:opacity-50"
                        title="Удалить модератора"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8">
            <Users className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">Модераторы не назначены</p>
            <p className="text-sm text-gray-400">
              Назначьте модераторов через Telegram бота для управления правами редактирования сообщений в этом чате.
            </p>
          </div>
        )}
      </div>

      {/* Привязанный канал */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <Link className="h-5 w-5 mr-2 text-blue-500" />
          Привязанный канал для пересылки
        </h2>

        {chat.linked_channel ? (
          <div className="border border-gray-200 rounded-lg p-4 bg-blue-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Radio className="h-5 w-5 text-blue-500" />
                <div>
                  <div className="font-medium text-gray-900">
                    {chat.linked_channel.title || `Канал ${chat.linked_channel.telegram_chat_id}`}
                  </div>
                  <div className="text-sm text-gray-500 font-mono">
                    ID: {chat.linked_channel.telegram_chat_id}
                  </div>
                  {chat.linked_channel.username && (
                    <a
                      href={`https://t.me/${chat.linked_channel.username}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:underline"
                    >
                      @{chat.linked_channel.username}
                    </a>
                  )}
                </div>
              </div>
              <button
                onClick={handleUnlinkChannel}
                disabled={unlinkChannelMutation.isPending}
                className="px-3 py-1 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md transition-colors disabled:opacity-50"
              >
                <Unlink className="h-4 w-4 inline mr-1" />
                Отвязать
              </button>
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <Radio className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">Канал для пересылки не привязан</p>
            <button
              onClick={() => setShowChannelSelector(!showChannelSelector)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="h-4 w-4 inline mr-2" />
              Привязать канал
            </button>
          </div>
        )}

        {showChannelSelector && availableChannels && availableChannels.length > 0 && (
          <div className="mt-4 border-t pt-4">
            <h3 className="text-lg font-medium text-gray-900 mb-3">Выберите канал для привязки:</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {availableChannels.map((channel) => (
                <div
                  key={channel.id}
                  className="border border-gray-200 rounded-lg p-3 hover:border-blue-300 hover:bg-blue-50 cursor-pointer transition-colors"
                  onClick={() => handleLinkChannel(channel.id)}
                >
                  <div className="flex items-center space-x-2">
                    <Radio className="h-4 w-4 text-green-500" />
                    <div>
                      <div className="font-medium text-gray-900">
                        {channel.chat_title || `Канал ${channel.chat_id}`}
                      </div>
                      <div className="text-sm text-gray-500 font-mono">
                        ID: {channel.chat_id}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-3">
              <button
                onClick={() => setShowChannelSelector(false)}
                className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
              >
                Отмена
              </button>
            </div>
          </div>
        )}

        {showChannelSelector && (!availableChannels || availableChannels.length === 0) && (
          <div className="mt-4 border-t pt-4">
            <p className="text-gray-500 text-center py-4">
              У вас нет доступных каналов. Добавьте бота как администратора в канал, чтобы привязать его.
            </p>
          </div>
        )}
      </div>

      {/* Каналы */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <Radio className="h-5 w-5 mr-2 text-green-500" />
          Привязанные каналы ({channels.length})
        </h2>
        {channels.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {channels.map((channel) => (
              <div key={channel.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Hash className="h-4 w-4 text-gray-400" />
                  <span className="font-mono text-sm">{channel.channel_id}</span>
                </div>
                <div className="text-xs text-gray-500">
                  Админ: {channel.admin_user_id}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Создан: {new Date(channel.created_date).toLocaleDateString('ru-RU')}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">Каналы не привязаны</p>
        )}
      </div>
    </div>
  );
};