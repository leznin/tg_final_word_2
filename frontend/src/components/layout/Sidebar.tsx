import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, MessageSquare, Users, User, Bot, Shield, Send, X, UserCheck, UserCog } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { UserRole } from '../../types';

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home, roles: [UserRole.ADMIN] },
  { name: 'Чаты', href: '/chats', icon: MessageSquare, roles: [UserRole.ADMIN, UserRole.MANAGER] },
  { name: 'Пользователи и чаты', href: '/users-chats', icon: User, roles: [UserRole.ADMIN] },
  { name: 'Модераторы', href: '/moderators', icon: Users, roles: [UserRole.ADMIN] },
  { name: 'Управление доступом', href: '/admin-users', icon: UserCog, roles: [UserRole.ADMIN] },
  { name: 'Проверка пользователей', href: '/user-verification', icon: UserCheck, roles: [UserRole.ADMIN] },
  { name: 'Рассылка', href: '/broadcast', icon: Send, roles: [UserRole.ADMIN] },
  { name: 'AI Модерация', href: '/ai-moderation-payments', icon: Shield, roles: [UserRole.ADMIN] },
  { name: 'OpenRouter', href: '/openrouter', icon: Bot, roles: [UserRole.ADMIN] },
];

interface SidebarProps {
  isOpen?: boolean;
  isMobile?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen = true, isMobile = false, onClose }) => {
  const { user } = useAuth();
  
  const handleNavClick = () => {
    if (isMobile && onClose) {
      onClose();
    }
  };

  // Фильтруем навигацию по роли пользователя
  const filteredNavigation = navigation.filter(item => 
    !user?.role || item.roles.includes(user.role)
  );

  return (
    <>
      {/* Mobile backdrop */}
      {isMobile && isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}
      
      {/* Sidebar */}
      <aside className={`
        ${isMobile 
          ? `fixed top-0 left-0 z-50 h-full w-64 transform transition-transform duration-300 ease-in-out ${
              isOpen ? 'translate-x-0' : '-translate-x-full'
            } md:relative md:translate-x-0`
          : 'w-64'
        } 
        bg-gray-900 min-h-screen
      `}>
        {/* Mobile header with close button */}
        {isMobile && (
          <div className="flex items-center justify-between p-4 border-b border-gray-800 md:hidden">
            <h2 className="text-lg font-semibold text-white">Меню</h2>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
              aria-label="Закрыть меню"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        )}

        <nav className={`${isMobile ? 'mt-2' : 'mt-6'}`}>
          <div className="px-4 space-y-2">
            {filteredNavigation.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  onClick={handleNavClick}
                  className={({ isActive }) =>
                    `flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                      isActive
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                    }`
                  }
                >
                  <Icon className="mr-3 h-5 w-5 flex-shrink-0" />
                  <span className="truncate">{item.name}</span>
                </NavLink>
              );
            })}
          </div>
        </nav>
      </aside>
    </>
  );
};