import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { Bot, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const { login, loginLoading, loginError, isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email.length >= 1 && password.length >= 1) {
      login({ email, password });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 via-purple-600 to-indigo-700 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-8">
        <div className="bg-white rounded-2xl shadow-2xl p-6 md:p-8">
          <div className="text-center mb-6 md:mb-8">
            <div className="mx-auto h-12 w-12 md:h-16 md:w-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-4">
              <Bot className="h-6 w-6 md:h-8 md:w-8 text-white" />
            </div>
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900">Вход в систему</h2>
            <p className="mt-2 text-sm text-gray-600">
              Админпанель Telegram бота
            </p>
          </div>

          <form className="space-y-4 md:space-y-6" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <div className="mt-1">
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full px-3 py-3 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                  placeholder="Введите email"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Пароль
              </label>
              <div className="mt-1 relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full px-3 py-3 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                  placeholder="Введите пароль"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center touch-target"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>

            {loginError && (
              <div className={`rounded-md p-4 ${
                (loginError as any)?.response?.status === 429
                  ? 'bg-yellow-50 border border-yellow-200'
                  : 'bg-red-50'
              }`}>
                <div className={`text-sm ${
                  (loginError as any)?.response?.status === 429
                    ? 'text-yellow-800'
                    : 'text-red-700'
                }`}>
                  {(loginError as any)?.response?.data?.detail ||
                   (loginError as any)?.response?.data?.message ||
                   'Ошибка входа'}
                </div>
                {(loginError as any)?.response?.status === 429 && (
                  <div className="text-xs text-yellow-600 mt-2">
                    Попробуйте позже или обратитесь к администратору
                  </div>
                )}
              </div>
            )}

            <div>
              <button
                type="submit"
                disabled={loginLoading || email.length < 1 || password.length < 1}
                className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transform transition hover:scale-105"
              >
                {loginLoading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                ) : (
                  'Войти'
                )}
              </button>
            </div>
          </form>

          <div className="mt-6 text-center text-xs text-gray-500">
            Максимум 5 попыток входа за 15 минут с одного устройства
          </div>
        </div>
      </div>
    </div>
  );
};