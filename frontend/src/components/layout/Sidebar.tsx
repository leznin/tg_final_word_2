import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, MessageSquare, Users, Settings, User, Bot } from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Чаты', href: '/chats', icon: MessageSquare },
  { name: 'Пользователи и чаты', href: '/users-chats', icon: User },
  { name: 'Модераторы', href: '/moderators', icon: Users },
  { name: 'OpenRouter', href: '/openrouter', icon: Bot },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-gray-900 min-h-screen">
      <nav className="mt-6">
        <div className="px-4 space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  `flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                  }`
                }
              >
                <Icon className="mr-3 h-5 w-5" />
                {item.name}
              </NavLink>
            );
          })}
        </div>
      </nav>
    </aside>
  );
};