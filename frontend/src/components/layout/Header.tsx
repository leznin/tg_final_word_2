import React from 'react';
import { LogOut, Bot } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';

export const Header: React.FC = () => {
  const { logout } = useAuth();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-500 rounded-lg">
            <Bot className="h-6 w-6 text-white" />
          </div>
          <h1 className="text-xl font-semibold text-gray-800">
            Админпанель Telegram бота
          </h1>
        </div>
        
        <button
          onClick={() => logout()}
          className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        >
          <LogOut className="h-4 w-4" />
          <span>Выход</span>
        </button>
      </div>
    </header>
  );
};