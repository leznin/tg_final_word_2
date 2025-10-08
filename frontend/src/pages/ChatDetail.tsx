import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Users, Radio, Settings, Calendar, User, Link, Unlink, Plus, Trash2, Clock, MessageSquare, FileText, ExternalLink, Search, ChevronLeft, ChevronRight } from 'lucide-react';
import { useChatDetail, useAvailableChannels, useLinkChannel, useUnlinkChannel, useChatModerators, useRemoveModerator, useChatMembers, useChatSubscriptionStatus, useCreateChatSubscription, useDeactivateChatSubscription } from '../hooks/useChats';
import { Loading } from '../components/ui/Loading';
import { StatsCard } from '../components/ui/StatsCard';

export const ChatDetail: React.FC = () => {
  const { chatId } = useParams<{ chatId: string }>();
  const navigate = useNavigate();
  const { data, isLoading } = useChatDetail(chatId!);
  const [showChannelSelector, setShowChannelSelector] = useState(false);
  const [showSubscriptionForm, setShowSubscriptionForm] = useState(false);
  const [subscriptionForm, setSubscriptionForm] = useState({
    subscription_type: 'month' as 'month' | 'year',
    price_stars: 1,
    currency: 'XTR',
    end_date: ''
  });

  // Chat members search and pagination state
  const [memberSearch, setMemberSearch] = useState('');
  const [memberPage, setMemberPage] = useState(1);
  const [memberPageSize] = useState(30);

  // Reset page when search changes
  useEffect(() => {
    setMemberPage(1);
  }, [memberSearch]);

  // Hooks for channel linking
  const { data: availableChannels } = useAvailableChannels(data?.chat.admin_user_id || 0);
  const linkChannelMutation = useLinkChannel();
  const unlinkChannelMutation = useUnlinkChannel();

  // Hooks for moderators
  const { data: moderatorsData } = useChatModerators(chatId!);
  const removeModeratorMutation = useRemoveModerator();

  // Hooks for chat members
  const { data: membersData, isLoading: membersLoading } = useChatMembers(chatId!, memberSearch, memberPage, memberPageSize);

  // Hook for chat subscription status
  const { data: subscriptionStatus } = useChatSubscriptionStatus(chatId!);

  // Hooks for subscription management
  const createSubscriptionMutation = useCreateChatSubscription();
  const deactivateSubscriptionMutation = useDeactivateChatSubscription();

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

  const handleCreateSubscription = async () => {
    try {
      const subscriptionData = {
        chat_id: chat.id,
        subscription_type: subscriptionForm.subscription_type,
        price_stars: subscriptionForm.price_stars,
        currency: subscriptionForm.currency,
        start_date: new Date(),
        end_date: new Date(subscriptionForm.end_date),
        is_active: true
      };

      await createSubscriptionMutation.mutateAsync(subscriptionData);
      setShowSubscriptionForm(false);
      setSubscriptionForm({
        subscription_type: 'month',
        price_stars: 1,
        currency: 'XTR',
        end_date: ''
      });
      alert('Подписка успешно создана!');
    } catch (error) {
      console.error('Failed to create subscription:', error);
      alert('Не удалось создать подписку');
    }
  };

  const handleDeactivateSubscription = async (subscriptionId: number) => {
    if (window.confirm('Вы уверены, что хотите деактивировать эту подписку?')) {
      try {
        await deactivateSubscriptionMutation.mutateAsync(subscriptionId);
        alert('Подписка успешно деактивирована!');
      } catch (error) {
        console.error('Failed to deactivate subscription:', error);
        alert('Не удалось деактивировать подписку');
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
      value: chat.member_count || membersData?.length || 0,
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
    <div className="space-y-4">
      {/* Компактный заголовок с метриками */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => navigate('/chats')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-all duration-200 hover:shadow-md"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-xl font-bold text-gray-900">{chat.chat_title}</h1>
              <div className="flex items-center space-x-2 mt-1">
                <span className="text-xs text-gray-600 font-mono">ID: {chat.chat_id}</span>
                <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                  chat.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {chat.is_active ? 'Активен' : 'Неактивен'}
                </span>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-2 text-xs text-gray-500">
            <Calendar className="h-3 w-3" />
            <span>Добавлен {new Date(chat.added_date).toLocaleDateString('ru-RU')}</span>
          </div>
        </div>

        {/* Компактные метрики в одной строке */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {statsCards.map((stat, index) => (
            <div key={index} className="bg-gradient-to-r from-white to-gray-50 rounded-lg p-3 border border-gray-100 hover:shadow-md transition-all duration-200">
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${stat.gradient.replace('to-', 'bg-').replace('-600', '-500')} bg-opacity-20`}>
                  <stat.icon className="h-4 w-4 text-current" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium text-gray-600">{stat.title}</p>
                  <p className="text-lg font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Статусные индикаторы */}
        <div className="flex flex-wrap items-center gap-2 mt-3 pt-3 border-t border-gray-100">
          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
            chat.delete_messages_enabled ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
          }`}>
            Удаление: {chat.delete_messages_enabled ? 'Вкл' : 'Откл'}
          </span>
          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
            (subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'bg-green-100 text-green-800' :
            (!subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'bg-yellow-100 text-yellow-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            AI проверка: {
              (subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'Активна' :
              (!subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'Требуется оплата' :
              'Отключена'
            }
          </span>
        </div>
      </div>

      {/* AI проверка и управление подпиской в компактном виде */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* AI проверка контента */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-4 hover:shadow-xl transition-all duration-200">
          <div className="flex items-center space-x-2 mb-3">
            <div className={`p-2 rounded-lg ${
              (subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'bg-green-100' :
              (!subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'bg-yellow-100' :
              'bg-gray-100'
            }`}>
              <Settings className={`h-4 w-4 ${
                (subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'text-green-600' :
                (!subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'text-yellow-600' :
                'text-gray-600'
              }`} />
            </div>
            <h3 className="text-sm font-semibold text-gray-900">AI проверка контента</h3>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${
                  (subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'bg-green-500' :
                  (!subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'bg-yellow-500' :
                  'bg-gray-400'
                }`} />
                <span className="text-sm font-medium text-gray-900">
                  {chat.ai_content_check_enabled ? 'Включена' : 'Отключена'}
                </span>
              </div>
              <span className={`text-xs px-2 py-1 rounded-full ${
                (subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'bg-green-100 text-green-800' :
                (!subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'bg-yellow-100 text-yellow-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {(subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'Активна' :
                 (!subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'Требуется оплата' :
                 'Отключена'}
              </span>
            </div>

            <p className="text-xs text-gray-600 leading-relaxed">
              {(subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'Подписка активна, проверка сообщений работает' :
               (!subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'Требуется оплата подписки для работы AI проверки' :
               'Функция отключена администратором'}
            </p>
          </div>
        </div>

        {/* Управление подпиской */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-4 hover:shadow-xl transition-all duration-200">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <div className={`p-2 rounded-lg ${chat.active_subscription ? 'bg-green-100' : 'bg-gray-100'}`}>
                <Settings className={`h-4 w-4 ${chat.active_subscription ? 'text-green-600' : 'text-gray-600'}`} />
              </div>
              <h3 className="text-sm font-semibold text-gray-900">Управление подпиской</h3>
            </div>
            {!chat.active_subscription && (
              <button
                onClick={() => setShowSubscriptionForm(!showSubscriptionForm)}
                className="px-3 py-1 bg-green-600 text-white text-xs rounded-lg hover:bg-green-700 transition-all duration-200 hover:shadow-md"
              >
                <Plus className="h-3 w-3 inline mr-1" />
                Создать
              </button>
            )}
          </div>

          {chat.active_subscription ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                  <span className="text-sm font-medium text-gray-900">Подписка активна</span>
                </div>
                <button
                  onClick={() => handleDeactivateSubscription(chat.active_subscription!.id)}
                  disabled={deactivateSubscriptionMutation.isPending}
                  className="px-2 py-1 text-xs text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md transition-all duration-200 disabled:opacity-50"
                >
                  Деактивировать
                </button>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-gray-50 rounded-lg p-2">
                  <div className="text-gray-600">Стоимость</div>
                  <div className="font-medium text-gray-900">{chat.active_subscription.price_stars} ⭐</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-2">
                  <div className="text-gray-600">Тип</div>
                  <div className="font-medium text-gray-900">
                    {chat.active_subscription.subscription_type === 'month' ? 'Месяц' : 'Год'}
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-2">
                  <div className="text-gray-600">Начало</div>
                  <div className="font-medium text-gray-900 text-xs">
                    {new Date(chat.active_subscription.start_date).toLocaleDateString('ru-RU')}
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-2">
                  <div className="text-gray-600">Окончание</div>
                  <div className={`font-medium text-xs ${new Date(chat.active_subscription.end_date) < new Date() ? 'text-red-600' : 'text-green-600'}`}>
                    {new Date(chat.active_subscription.end_date).toLocaleDateString('ru-RU')}
                    {new Date(chat.active_subscription.end_date) < new Date() && (
                      <span className="block text-red-500">(истекла)</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-gray-400"></div>
                <span className="text-sm font-medium text-gray-900">Нет активной подписки</span>
              </div>
              <p className="text-xs text-gray-600">Чат не имеет платной подписки на AI проверку</p>
            </div>
          )}

          {/* Форма создания подписки */}
          {showSubscriptionForm && (
            <div className="mt-4 pt-4 border-t border-gray-100">
              <h4 className="text-sm font-medium text-gray-900 mb-3">Создать подписку</h4>
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Тип</label>
                    <select
                      value={subscriptionForm.subscription_type}
                      onChange={(e) => setSubscriptionForm(prev => ({
                        ...prev,
                        subscription_type: e.target.value as 'month' | 'year'
                      }))}
                      className="w-full px-2 py-1 text-xs border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    >
                      <option value="month">Месяц</option>
                      <option value="year">Год</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Стоимость</label>
                    <input
                      type="number"
                      min="1"
                      value={subscriptionForm.price_stars}
                      onChange={(e) => setSubscriptionForm(prev => ({
                        ...prev,
                        price_stars: parseInt(e.target.value) || 1
                      }))}
                      className="w-full px-2 py-1 text-xs border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Дата окончания</label>
                  <input
                    type="datetime-local"
                    value={subscriptionForm.end_date}
                    onChange={(e) => setSubscriptionForm(prev => ({
                      ...prev,
                      end_date: e.target.value
                    }))}
                    className="w-full px-2 py-1 text-xs border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  />
                </div>
                <div className="flex justify-end space-x-2">
                  <button
                    onClick={() => setShowSubscriptionForm(false)}
                    className="px-3 py-1 text-xs text-gray-600 hover:text-gray-800"
                  >
                    Отмена
                  </button>
                  <button
                    onClick={handleCreateSubscription}
                    disabled={createSubscriptionMutation.isPending || !subscriptionForm.end_date}
                    className="px-3 py-1 bg-green-600 text-white text-xs rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {createSubscriptionMutation.isPending ? '...' : 'Создать'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Информация о чате в компактных карточках */}
      {(chat.description || chat.invite_link || chat.last_info_update) && (
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-4 hover:shadow-xl transition-all duration-200">
          <div className="flex items-center space-x-2 mb-4">
            <div className="p-2 rounded-lg bg-blue-100">
              <MessageSquare className="h-4 w-4 text-blue-600" />
            </div>
            <h3 className="text-sm font-semibold text-gray-900">Информация о чате</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {chat.description && (
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3 border border-blue-200 hover:shadow-md transition-all duration-200">
                <div className="flex items-start space-x-2">
                  <FileText className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <h4 className="text-xs font-medium text-blue-900 mb-1">Описание</h4>
                    <p className="text-xs text-blue-800 leading-relaxed line-clamp-3">{chat.description}</p>
                  </div>
                </div>
              </div>
            )}

            {chat.invite_link && (
              <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-3 border border-green-200 hover:shadow-md transition-all duration-200">
                <div className="flex items-start space-x-2">
                  <ExternalLink className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <h4 className="text-xs font-medium text-green-900 mb-1">Пригласительная ссылка</h4>
                    <a
                      href={chat.invite_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-green-700 hover:text-green-900 hover:underline block truncate"
                      title={chat.invite_link}
                    >
                      {chat.invite_link}
                    </a>
                  </div>
                </div>
              </div>
            )}

            {chat.last_info_update && (
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-3 border border-purple-200 hover:shadow-md transition-all duration-200">
                <div className="flex items-start space-x-2">
                  <Calendar className="h-4 w-4 text-purple-500 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <h4 className="text-xs font-medium text-purple-900 mb-1">Последнее обновление</h4>
                    <p className="text-xs text-purple-800">
                      {new Date(chat.last_info_update).toLocaleDateString('ru-RU', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Двухколоночный layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Левая колонка - Модераторы */}
        <div className="space-y-4">
          {/* Модераторы */}
          <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-4 hover:shadow-xl transition-all duration-200">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <div className="p-2 rounded-lg bg-purple-100">
                  <Users className="h-4 w-4 text-purple-600" />
                </div>
                <h3 className="text-sm font-semibold text-gray-900">Модераторы</h3>
                <span className="text-xs text-gray-500 bg-purple-50 px-2 py-1 rounded-full">
                  {moderatorsData?.length || moderators.length}
                </span>
              </div>
            </div>

            {(moderatorsData || moderators).length > 0 ? (
              <div className="grid grid-cols-1 gap-2">
                {(moderatorsData || moderators).map((moderator) => (
                  <div key={moderator.id} className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-3 border border-purple-200 hover:shadow-md hover:from-purple-100 hover:to-purple-200 transition-all duration-200">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3 flex-1 min-w-0">
                        <div className="flex-shrink-0">
                          <div className="w-8 h-8 bg-purple-200 rounded-full flex items-center justify-center">
                            <User className="w-3 h-3 text-purple-700" />
                          </div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="text-xs font-medium text-purple-900 truncate">
                            {'moderator_name' in moderator ? moderator.moderator_name : `${moderator.first_name || ''} ${moderator.last_name || ''}`.trim() || `Пользователь ${moderator.moderator_user_id}`}
                          </h4>
                          <div className="flex items-center space-x-2 mt-1">
                            <span className="text-xs text-purple-700 font-mono">
                              ID: {moderator.moderator_user_id}
                            </span>
                            {('moderator_username' in moderator ? moderator.moderator_username : moderator.username) && (
                              <a
                                href={`https://t.me/${'moderator_username' in moderator ? moderator.moderator_username : moderator.username}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-purple-600 hover:text-purple-800 hover:underline truncate"
                              >
                                @{'moderator_username' in moderator ? moderator.moderator_username : moderator.username}
                              </a>
                            )}
                          </div>
                          <div className="text-xs text-purple-600 mt-1">
                            Добавлен: {'added_date' in moderator ? new Date(moderator.added_date).toLocaleDateString('ru-RU') : 'created_at' in moderator ? new Date(moderator.created_at).toLocaleDateString('ru-RU') : 'Неизвестно'}
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => handleRemoveModerator(moderator.id)}
                        disabled={removeModeratorMutation.isPending}
                        className="text-red-500 hover:text-red-700 disabled:opacity-50 p-1 rounded hover:bg-red-50 transition-all duration-200 hover:shadow-sm"
                        title="Удалить модератора"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6 bg-gray-50 rounded-lg">
                <Users className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                <p className="text-xs text-gray-500 mb-1">Модераторы не назначены</p>
                <p className="text-xs text-gray-400">
                  Назначьте модераторов через Telegram бота
                </p>
              </div>
            )}
          </div>

          {/* Привязанный канал */}
          <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-4 hover:shadow-xl transition-all duration-200">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <div className="p-2 rounded-lg bg-blue-100">
                  <Link className="h-4 w-4 text-blue-600" />
                </div>
                <h3 className="text-sm font-semibold text-gray-900">Привязанный канал</h3>
              </div>
              {!chat.linked_channel && (
                <button
                  onClick={() => setShowChannelSelector(!showChannelSelector)}
                  className="px-3 py-1 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700 transition-all duration-200 hover:shadow-md"
                >
                  <Plus className="h-3 w-3 inline mr-1" />
                  Привязать
                </button>
              )}
            </div>

            {chat.linked_channel ? (
              <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-3 border border-blue-200 hover:shadow-md transition-all duration-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-blue-200 rounded-full flex items-center justify-center">
                        <Radio className="w-3 h-3 text-blue-700" />
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-xs font-medium text-blue-900 truncate">
                        {chat.linked_channel.title || `Канал ${chat.linked_channel.telegram_chat_id}`}
                      </h4>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="text-xs text-blue-700 font-mono">
                          ID: {chat.linked_channel.telegram_chat_id}
                        </span>
                        {chat.linked_channel.username && (
                          <a
                            href={`https://t.me/${chat.linked_channel.username}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-blue-600 hover:text-blue-800 hover:underline"
                          >
                            @{chat.linked_channel.username}
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={handleUnlinkChannel}
                    disabled={unlinkChannelMutation.isPending}
                    className="text-red-500 hover:text-red-700 disabled:opacity-50 p-1 rounded hover:bg-red-50 transition-all duration-200 hover:shadow-sm"
                    title="Отвязать канал"
                  >
                    <Unlink className="h-3 w-3" />
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-4 bg-gray-50 rounded-lg">
                <Radio className="h-6 w-6 text-gray-300 mx-auto mb-2" />
                <p className="text-xs text-gray-500 mb-2">Канал для пересылки не привязан</p>
              </div>
            )}

            {/* Селектор каналов */}
            {showChannelSelector && availableChannels && availableChannels.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-100">
                <h4 className="text-xs font-medium text-gray-900 mb-3">Выберите канал для привязки:</h4>
                <div className="grid grid-cols-1 gap-2 max-h-40 overflow-y-auto">
                  {availableChannels.map((channel) => (
                    <div
                      key={channel.id}
                      className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-2 border border-green-200 hover:shadow-md hover:from-green-100 hover:to-green-200 cursor-pointer transition-all duration-200"
                      onClick={() => handleLinkChannel(channel.id)}
                    >
                      <div className="flex items-center space-x-2">
                        <Radio className="h-3 w-3 text-green-600 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-medium text-green-900 truncate">
                            {channel.title || `Канал ${channel.telegram_chat_id}`}
                          </div>
                          <div className="text-xs text-green-700 font-mono">
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
                    className="px-3 py-1 text-xs text-gray-600 hover:text-gray-800"
                  >
                    Отмена
                  </button>
                </div>
              </div>
            )}

            {showChannelSelector && (!availableChannels || availableChannels.length === 0) && (
              <div className="mt-4 pt-4 border-t border-gray-100">
                <p className="text-xs text-gray-500 text-center py-4">
                  У вас нет доступных каналов. Добавьте бота как администратора в канал, чтобы привязать его.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Правая колонка - Участники */}
        <div className="space-y-4">
          <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-4 hover:shadow-xl transition-all duration-200">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <div className="p-2 rounded-lg bg-green-100">
                  <Users className="h-4 w-4 text-green-600" />
                </div>
                <h3 className="text-sm font-semibold text-gray-900">Участники чата</h3>
                <span className="text-xs text-gray-500 bg-green-50 px-2 py-1 rounded-full">
                  {membersData?.total || 0}
                </span>
              </div>
            </div>

            {/* Search field */}
            <div className="mb-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Поиск по имени, username или ID..."
                  value={memberSearch}
                  onChange={(e) => setMemberSearch(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>

            {membersLoading ? (
              <div className="flex justify-center py-6">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
              </div>
            ) : membersData && membersData.members && membersData.members.length > 0 ? (
              <>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-80 overflow-y-auto">
                  {membersData.members.map((member) => (
                    <div key={member.id} className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-3 border border-green-200 hover:shadow-md hover:from-green-100 hover:to-green-200 transition-all duration-200">
                      <div className="flex items-start space-x-2">
                        <div className="flex-shrink-0">
                          {member.is_bot ? (
                            <div className="w-6 h-6 bg-red-200 rounded-full flex items-center justify-center">
                              <Settings className="w-2.5 h-2.5 text-red-700" />
                            </div>
                          ) : (
                            <div className="w-6 h-6 bg-green-200 rounded-full flex items-center justify-center">
                              <User className="w-2.5 h-2.5 text-green-700" />
                            </div>
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-1 mb-1">
                            <h4 className="text-xs font-medium text-green-900 truncate">
                              {member.first_name || ''} {member.last_name || ''} {!member.first_name && !member.last_name && `ID: ${member.telegram_user_id}`}
                            </h4>
                            {member.is_bot && (
                              <span className="inline-flex items-center px-1 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                                Бот
                              </span>
                            )}
                            {member.is_premium && (
                              <span className="inline-flex items-center px-1 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                                ⭐
                              </span>
                            )}
                          </div>
                          <div className="text-xs text-green-700 mb-1">
                            <span className="font-mono">ID: {member.telegram_user_id}</span>
                            {member.username && <span className="ml-1">@{member.username}</span>}
                          </div>
                          {member.joined_at && (
                            <div className="text-xs text-green-600">
                              {new Date(member.joined_at).toLocaleDateString('ru-RU')}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Pagination */}
                {membersData.total > memberPageSize && (
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <div className="flex items-center justify-between">
                      <div className="text-xs text-gray-500">
                        Показаны {((memberPage - 1) * memberPageSize) + 1}-{Math.min(memberPage * memberPageSize, membersData.total)} из {membersData.total}
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => setMemberPage(prev => Math.max(1, prev - 1))}
                          disabled={memberPage === 1}
                          className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <ChevronLeft className="h-4 w-4" />
                        </button>
                        <span className="text-xs text-gray-600">
                          {memberPage} из {Math.ceil(membersData.total / memberPageSize)}
                        </span>
                        <button
                          onClick={() => setMemberPage(prev => prev + 1)}
                          disabled={memberPage >= Math.ceil(membersData.total / memberPageSize)}
                          className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <ChevronRight className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-6 bg-gray-50 rounded-lg">
                <Users className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                <p className="text-xs text-gray-500 mb-1">Участники не найдены</p>
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