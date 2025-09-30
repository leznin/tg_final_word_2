import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, Edit, Trash2, Star, Calendar, DollarSign } from 'lucide-react';
import { useSubscriptionPrices } from '../hooks/useSubscriptionPrices';
import { Loading } from '../components/ui/Loading';

interface SubscriptionPrice {
  id: number;
  subscription_type: string;
  price_stars: number;
  currency: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export const SubscriptionPrices: React.FC = () => {
  const navigate = useNavigate();
  const { data: prices, isLoading, refetch } = useSubscriptionPrices();
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingPrice, setEditingPrice] = useState<SubscriptionPrice | null>(null);
  const [formData, setFormData] = useState({
    subscription_type: 'month',
    price_stars: 10,
    currency: 'XTR'
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const url = editingPrice
        ? `/api/subscription-prices/${editingPrice.id}`
        : '/api/subscription-prices';

      const method = editingPrice ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        refetch();
        setShowAddForm(false);
        setEditingPrice(null);
        setFormData({ subscription_type: 'month', price_stars: 10, currency: 'XTR' });
        alert(editingPrice ? 'Цена обновлена успешно!' : 'Цена добавлена успешно!');
      } else {
        alert('Ошибка при сохранении цены');
      }
    } catch (error) {
      console.error('Error saving subscription price:', error);
      alert('Произошла ошибка при сохранении');
    }
  };

  const handleEdit = (price: SubscriptionPrice) => {
    setEditingPrice(price);
    setFormData({
      subscription_type: price.subscription_type,
      price_stars: price.price_stars,
      currency: price.currency
    });
    setShowAddForm(true);
  };

  const handleDelete = async (priceId: number) => {
    if (!confirm('Вы уверены, что хотите деактивировать эту цену подписки?')) {
      return;
    }

    try {
      const response = await fetch(`/api/subscription-prices/${priceId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        refetch();
        alert('Цена деактивирована успешно!');
      } else {
        alert('Ошибка при деактивации цены');
      }
    } catch (error) {
      console.error('Error deleting subscription price:', error);
      alert('Произошла ошибка при деактивации');
    }
  };

  const handleCancel = () => {
    setShowAddForm(false);
    setEditingPrice(null);
    setFormData({ subscription_type: 'month', price_stars: 10, currency: 'XTR' });
  };

  if (isLoading) return <Loading />;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Управление ценами подписок</h1>
            <p className="mt-2 text-sm text-gray-600">
              Настройка цен на AI проверку контента для чатов
            </p>
          </div>
        </div>
        <button
          onClick={() => setShowAddForm(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          Добавить цену
        </button>
      </div>

      {/* Add/Edit Form */}
      {showAddForm && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            {editingPrice ? 'Редактировать цену' : 'Добавить цену подписки'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Тип подписки
                </label>
                <select
                  value={formData.subscription_type}
                  onChange={(e) => setFormData({ ...formData, subscription_type: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="month">Месячная</option>
                  <option value="year">Годовая</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Цена (звезд)
                </label>
                <div className="relative">
                  <Star className="absolute left-3 top-1/2 transform -translate-y-1/2 text-yellow-500 h-4 w-4" />
                  <input
                    type="number"
                    min="1"
                    value={formData.price_stars}
                    onChange={(e) => setFormData({ ...formData, price_stars: parseInt(e.target.value) })}
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Валюта
                </label>
                <input
                  type="text"
                  value={formData.currency}
                  onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                {editingPrice ? 'Обновить' : 'Добавить'}
              </button>
              <button
                type="button"
                onClick={handleCancel}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
              >
                Отмена
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Prices List */}
      <div className="bg-white rounded-lg shadow-sm">
        <div className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Текущие цены</h2>

          {prices && prices.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {prices.map((price) => (
                <div
                  key={price.id}
                  className={`border rounded-lg p-4 ${
                    price.is_active ? 'border-green-200 bg-green-50' : 'border-gray-200 bg-gray-50'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <div className={`w-3 h-3 rounded-full ${
                        price.is_active ? 'bg-green-500' : 'bg-gray-400'
                      }`} />
                      <span className={`text-sm font-medium ${
                        price.is_active ? 'text-green-800' : 'text-gray-600'
                      }`}>
                        {price.is_active ? 'Активна' : 'Неактивна'}
                      </span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <button
                        onClick={() => handleEdit(price)}
                        className="text-blue-600 hover:text-blue-800 p-1"
                        title="Редактировать"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(price.id)}
                        className="text-red-600 hover:text-red-800 p-1"
                        title="Деактивировать"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Calendar className="h-4 w-4 text-gray-500" />
                      <span className="text-sm font-medium text-gray-900">
                        {price.subscription_type === 'month' ? 'Месячная подписка' : 'Годовая подписка'}
                      </span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <Star className="h-4 w-4 text-yellow-500" />
                      <span className="text-lg font-bold text-gray-900">
                        {price.price_stars} {price.currency}
                      </span>
                    </div>

                    <div className="text-xs text-gray-500">
                      Создано: {new Date(price.created_at).toLocaleDateString('ru-RU')}
                    </div>
                    {price.updated_at !== price.created_at && (
                      <div className="text-xs text-gray-500">
                        Обновлено: {new Date(price.updated_at).toLocaleDateString('ru-RU')}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <DollarSign className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Цены подписок не настроены
              </h3>
              <p className="text-gray-500 mb-4">
                Добавьте цены для месячных и годовых подписок на AI проверку контента
              </p>
              <button
                onClick={() => setShowAddForm(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Добавить первую цену
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Info Section */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-2">
          Информация о платежах
        </h3>
        <div className="text-sm text-blue-800 space-y-1">
          <p>• Цены указываются в Telegram Stars (звездах)</p>
          <p>• Каждая подписка применяется отдельно к каждому чату</p>
          <p>• Пользователи оплачивают подписку через Telegram Stars</p>
          <p>• После оплаты AI проверка контента активируется автоматически</p>
        </div>
      </div>
    </div>
  );
};

