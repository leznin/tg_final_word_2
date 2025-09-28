import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Users, Radio, Settings, Calendar, User, Link, Unlink, Plus, Trash2, Clock } from 'lucide-react';
import { useChatDetail, useAvailableChannels, useLinkChannel, useUnlinkChannel, useChatModerators, useRemoveModerator, useChatMembers } from '../hooks/useChats';
import { Loading } from '../components/ui/Loading';
import { StatsCard } from '../components/ui/StatsCard';

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
  const { data: moderatorsData } = useChatModerators(chatId!);
  const removeModeratorMutation = useRemoveModerator();

  // Hooks for chat members
  const { data: membersData, isLoading: membersLoading } = useChatMembers(chatId!);

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

  const statsCards = [
    {
      title: 'Модераторы',
      value: moderatorsData?.length || moderators.length,
      icon: Users,
      gradient: 'bg-gradient-to-r from-purple-500 to-purple-600'
    },
    {
      title: 'Участники',
      value: membersData?.length || 0,
      icon: User,
      gradient: 'bg-gradient-to-r from-green-500 to-green-600'
    },
    {
      title: 'Привязанные каналы',
      value: channels.length,
      icon: Radio,
      gradient: 'bg-gradient-to-r from-blue-500 to-blue-600'
    },
    {
      title: 'Время редактирования',
      value: chat.max_edit_time_minutes,
      icon: Clock,
      gradient: 'bg-gradient-to-r from-orange-500 to-orange-600'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Компактный заголовок */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/chats')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{chat.chat_title}</h1>
              <div className="flex items-center space-x-4 mt-1">
                <span className="text-sm text-gray-600 font-mono">ID: {chat.chat_id}</span>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  chat.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {chat.is_active ? 'Активен' : 'Неактивен'}
                </span>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  chat.delete_messages_enabled ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  Удаление: {chat.delete_messages_enabled ? 'Вкл' : 'Откл'}
                </span>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <Calendar className="h-4 w-4" />
            <span>Добавлен {new Date(chat.added_date).toLocaleDateString('ru-RU')}</span>
          </div>
        </div>

        {/* Метрики в виде карточек */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {statsCards.map((stat, index) => (
            <StatsCard key={index} {...stat} />
          ))}
        </div>
      </div>

      {/* Двухколоночный layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Левая колонка - Модераторы */}
        <div className="space-y-6">
          {/* Модераторы */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <Users className="h-5 w-5 mr-2 text-purple-500" />
              Модераторы ({moderatorsData?.length || moderators.length})
            </h2>
            {(moderatorsData || moderators).length > 0 ? (
              <div className="grid grid-cols-1 gap-3">
                {(moderatorsData || moderators).map((moderator) => (
                  <div key={moderator.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3 flex-1 min-w-0">
                        <div className="flex-shrink-0">
                          <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                            <User className="w-4 h-4 text-purple-600" />
                          </div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <h3 className="text-sm font-medium text-gray-900 truncate">
                              {'moderator_name' in moderator ? moderator.moderator_name : `${moderator.first_name || ''} ${moderator.last_name || ''}`.trim() || `Пользователь ${moderator.moderator_user_id}`}
                            </h3>
                          </div>
                          <div className="text-xs text-gray-500 mb-2">
                            ID: {moderator.moderator_user_id}
                            {('moderator_username' in moderator ? moderator.moderator_username : moderator.username) && (
                              <span className="ml-2">
                                <a
                                  href={`https://t.me/${'moderator_username' in moderator ? moderator.moderator_username : moderator.username}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-blue-600 hover:underline"
                                >
                                  @{'moderator_username' in moderator ? moderator.moderator_username : moderator.username}
                                </a>
                              </span>
                            )}
                          </div>
                          <div className="text-xs text-gray-400">
                            Добавлен: {'added_date' in moderator ? new Date(moderator.added_date).toLocaleDateString('ru-RU') : 'created_at' in moderator ? new Date(moderator.created_at).toLocaleDateString('ru-RU') : 'Неизвестно'}
                            {'added_by_user_id' in moderator && moderator.added_by_user_id && (
                              <span className="ml-2 font-mono">Админ: {moderator.added_by_user_id}</span>
                            )}
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => handleRemoveModerator(moderator.id)}
                        disabled={removeModeratorMutation.isPending}
                        className="text-red-600 hover:text-red-900 disabled:opacity-50 p-1 rounded hover:bg-red-50 transition-colors"
                        title="Удалить модератора"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6">
                <Users className="h-10 w-10 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500 mb-2">Модераторы не назначены</p>
                <p className="text-xs text-gray-400">
                  Назначьте модераторов через Telegram бота
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
                      <div className="font-medium text-gray-900 text-sm">
                        {chat.linked_channel.title || `Канал ${chat.linked_channel.telegram_chat_id}`}
                      </div>
                      <div className="text-xs text-gray-500 font-mono">
                        ID: {chat.linked_channel.telegram_chat_id}
                      </div>
                      {chat.linked_channel.username && (
                        <a
                          href={`https://t.me/${chat.linked_channel.username}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:underline"
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
              <div className="text-center py-6">
                <Radio className="h-10 w-10 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500 mb-3">Канал для пересылки не привязан</p>
                <button
                  onClick={() => setShowChannelSelector(!showChannelSelector)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                >
                  <Plus className="h-4 w-4 inline mr-2" />
                  Привязать канал
                </button>
              </div>
            )}

            {showChannelSelector && availableChannels && availableChannels.length > 0 && (
              <div className="mt-4 border-t pt-4">
                <h3 className="text-lg font-medium text-gray-900 mb-3">Выберите канал для привязки:</h3>
                <div className="grid grid-cols-1 gap-3">
                  {availableChannels.map((channel) => (
                    <div
                      key={channel.id}
                      className="border border-gray-200 rounded-lg p-3 hover:border-blue-300 hover:bg-blue-50 cursor-pointer transition-colors"
                      onClick={() => handleLinkChannel(channel.id)}
                    >
                      <div className="flex items-center space-x-2">
                        <Radio className="h-4 w-4 text-green-500" />
                        <div>
                          <div className="font-medium text-gray-900 text-sm">
                            {channel.title || `Канал ${channel.telegram_chat_id}`}
                          </div>
                          <div className="text-xs text-gray-500 font-mono">
                            ID: {channel.telegram_chat_id}
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
                <p className="text-gray-500 text-center py-4 text-sm">
                  У вас нет доступных каналов. Добавьте бота как администратора в канал, чтобы привязать его.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Правая колонка - Участники */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <Users className="h-5 w-5 mr-2 text-green-500" />
              Участники чата ({membersData?.length || 0})
            </h2>
            {membersLoading ? (
              <div className="flex justify-center py-6">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              </div>
            ) : membersData && membersData.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {membersData.map((member) => (
                  <div key={member.id} className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start space-x-2">
                      <div className="flex-shrink-0">
                        {member.is_bot ? (
                          <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center">
                            <Settings className="w-3 h-3 text-red-600" />
                          </div>
                        ) : (
                          <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                            <User className="w-3 h-3 text-blue-600" />
                          </div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-1 mb-1">
                          <h3 className="text-xs font-medium text-gray-900 truncate">
                            {member.first_name || ''} {member.last_name || ''} {!member.first_name && !member.last_name && `ID: ${member.telegram_user_id}`}
                          </h3>
                          {member.is_bot && (
                            <span className="inline-flex items-center px-1 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                              Бот
                            </span>
                          )}
                          {member.is_premium && (
                            <span className="inline-flex items-center px-1 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                              Premium
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-gray-500 mb-1">
                          ID: {member.telegram_user_id}
                          {member.username && <span className="ml-1">@{member.username}</span>}
                        </div>
                        {member.joined_at && (
                          <div className="text-xs text-gray-400 mb-1">
                            Присоединился: {new Date(member.joined_at).toLocaleDateString('ru-RU')}
                          </div>
                        )}
                        {member.user_groups && member.user_groups.length > 0 && (
                          <div className="text-xs text-gray-500">
                            <span className="text-gray-400">Также в группах:</span>{' '}
                            {member.user_groups.slice(0, 2).map((group, index) => (
                              <span key={index} className="inline-flex items-center px-1 py-0.5 rounded text-xs bg-gray-100 text-gray-700 mr-1 mb-1">
                                {group.title.length > 15 ? `${group.title.substring(0, 15)}...` : group.title}
                              </span>
                            ))}
                            {member.user_groups.length > 2 && (
                              <span className="text-gray-400">+ещё {member.user_groups.length - 2}</span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6">
                <Users className="h-10 w-10 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500 mb-2">Участники не найдены</p>
                <p className="text-xs text-gray-400">
                  Информация об участниках может быть недоступна
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};