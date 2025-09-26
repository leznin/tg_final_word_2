import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, Radio, Users, User, ArrowRight } from 'lucide-react';
import { useDashboard } from '../hooks/useDashboard';
import { StatsCard } from '../components/ui/StatsCard';
import { Loading } from '../components/ui/Loading';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { data: stats, isLoading } = useDashboard();

  if (isLoading) return <Loading />;

  const statsConfig = [
    {
      title: 'Активные чаты',
      value: stats?.total_chats || 0,
      icon: MessageSquare,
      gradient: 'bg-gradient-to-r from-blue-500 to-blue-600',
      onClick: () => navigate('/chats')
    },
    {
      title: 'Привязанные каналы',
      value: stats?.total_channels || 0,
      icon: Radio,
      gradient: 'bg-gradient-to-r from-green-500 to-green-600',
    },
    {
      title: 'Модераторы',
      value: stats?.total_moderators || 0,
      icon: Users,
      gradient: 'bg-gradient-to-r from-purple-500 to-purple-600',
      onClick: () => navigate('/moderators')
    },
    {
      title: 'Уникальные пользователи',
      value: stats?.total_users || 0,
      icon: User,
      gradient: 'bg-gradient-to-r from-orange-500 to-orange-600',
    },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-sm text-gray-600">
          Обзор статистики и быстрый доступ к основным функциям
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statsConfig.map((stat, index) => (
          <StatsCard key={index} {...stat} />
        ))}
      </div>

      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Быстрые действия</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => navigate('/chats')}
            className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group"
          >
            <div className="flex items-center space-x-3">
              <MessageSquare className="h-5 w-5 text-blue-500" />
              <span className="font-medium">Управление чатами</span>
            </div>
            <ArrowRight className="h-4 w-4 text-gray-400 group-hover:text-gray-600" />
          </button>
          
          <button
            onClick={() => navigate('/moderators')}
            className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group"
          >
            <div className="flex items-center space-x-3">
              <Users className="h-5 w-5 text-purple-500" />
              <span className="font-medium">Управление модераторами</span>
            </div>
            <ArrowRight className="h-4 w-4 text-gray-400 group-hover:text-gray-600" />
          </button>
        </div>
      </div>
    </div>
  );
};