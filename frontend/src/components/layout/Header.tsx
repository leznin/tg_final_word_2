import React from 'react';
import { LogOut, Bot, Menu } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';

interface HeaderProps {
  onMobileMenuToggle?: () => void;
  isMobile?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ onMobileMenuToggle, isMobile }) => {
  const { logout } = useAuth();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-4 md:px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          {/* Mobile menu button */}
          {isMobile && onMobileMenuToggle && (
            <button
              onClick={onMobileMenuToggle}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors md:hidden"
              aria-label="Открыть меню"
            >
              <Menu className="h-6 w-6" />
            </button>
          )}
          
          <div className="p-2 bg-blue-500 rounded-lg">
            <Bot className="h-6 w-6 text-white" />
          </div>
          <h1 className="text-lg md:text-xl font-semibold text-gray-800 truncate">
            <span className="hidden sm:inline">Админпанель Telegram бота</span>
            <span className="sm:hidden">Админпанель</span>
          </h1>
        </div>
        
        <button
          onClick={() => logout()}
          className="flex items-center space-x-2 px-3 md:px-4 py-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        >
          <LogOut className="h-4 w-4" />
          <span className="hidden sm:inline">Выход</span>
        </button>
      </div>
    </header>
  );
};