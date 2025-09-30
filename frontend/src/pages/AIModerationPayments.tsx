import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Shield, Calculator, DollarSign, Star, Percent, Zap, Edit, Plus, Save, X, TrendingUp, Calendar, Settings } from 'lucide-react';
import { useSubscriptionPrices } from '../hooks/useSubscriptionPrices';
import { Loading } from '../components/ui/Loading';
import { CurrencyConverter } from '../components/ui/CurrencyConverter';

interface SubscriptionPrice {
  id: number;
  subscription_type: string;
  price_stars: number;
  currency: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface CalculatorState {
  monthlyPrice: number;
  yearlyDiscountPercent: number;
  quantity: number;
}

interface EditingState {
  type: 'month' | 'year' | null;
  value: number;
}

export const AIModerationPayments: React.FC = () => {
  const navigate = useNavigate();
  const { data: prices, isLoading, refetch } = useSubscriptionPrices();
  const [calculator, setCalculator] = useState<CalculatorState>({
    monthlyPrice: 0,
    yearlyDiscountPercent: 20,
    quantity: 1
  });
  const [editing, setEditing] = useState<EditingState>({ type: null, value: 0 });
  const [showAddForm, setShowAddForm] = useState(false);
  const [newPriceData, setNewPriceData] = useState({
    subscription_type: 'month' as 'month' | 'year',
    price_stars: 10,
    currency: 'XTR'
  });

  // Get active prices
  const activePrices = prices?.filter(price => price.is_active) || [];
  const monthPrice = activePrices.find(price => price.subscription_type === 'month');
  const yearPrice = activePrices.find(price => price.subscription_type === 'year');

  // Initialize calculator with current prices
  useEffect(() => {
    if (monthPrice) {
      setCalculator(prev => ({
        ...prev,
        monthlyPrice: monthPrice.price_stars
      }));
    }
  }, [monthPrice]);

  // Calculator logic
  const calculatedYearlyPrice = Math.round(calculator.monthlyPrice * 12 * (1 - calculator.yearlyDiscountPercent / 100));
  const yearlySavings = calculator.monthlyPrice * 12 - calculatedYearlyPrice;
  const totalPrice = calculator.monthlyPrice * calculator.quantity;

  // Handle price editing
  const startEditing = (type: 'month' | 'year') => {
    const currentPrice = type === 'month' ? monthPrice : yearPrice;
    setEditing({
      type,
      value: currentPrice?.price_stars || 0
    });
  };

  const savePrice = async () => {
    if (!editing.type) return;

    try {
      const existingPrice = editing.type === 'month' ? monthPrice : yearPrice;
      const url = existingPrice ? `/api/subscription-prices/${existingPrice.id}` : '/api/subscription-prices';
      const method = existingPrice ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subscription_type: editing.type,
          price_stars: editing.value,
          currency: 'XTR'
        }),
      });

      if (response.ok) {
        refetch();
        setEditing({ type: null, value: 0 });
        alert(`Цена ${editing.type === 'month' ? 'месячной' : 'годовой'} подписки обновлена!`);
      }
    } catch (error) {
      alert('Ошибка при сохранении цены');
    }
  };

  // Handle creating new price
  const createNewPrice = async () => {
    try {
      const response = await fetch('/api/subscription-prices/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newPriceData),
      });

      if (response.ok) {
        refetch();
        setShowAddForm(false);
        setNewPriceData({ subscription_type: 'month', price_stars: 10, currency: 'XTR' });
        alert('Цена добавлена успешно!');
      }
    } catch (error) {
      alert('Ошибка при добавлении цены');
    }
  };

  const updateCalculatedPrice = () => {
    if (!yearPrice && calculatedYearlyPrice > 0) {
      // Auto-create yearly price
      setNewPriceData({
        subscription_type: 'year',
        price_stars: calculatedYearlyPrice,
        currency: 'XTR'
      });
      createNewPrice();
    } else if (yearPrice && calculatedYearlyPrice !== yearPrice.price_stars) {
      // Update existing yearly price
      setEditing({ type: 'year', value: calculatedYearlyPrice });
      savePrice();
    }
  };

  if (isLoading) return <Loading />;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">AI Модерация контента</h1>
            <p className="mt-2 text-sm text-gray-600">
              Управление ценами подписок и расчет оптимальных тарифов
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowAddForm(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-blue-600 hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-4 w-4 mr-2" />
            Добавить цену
          </button>
          <Shield className="h-8 w-8 text-blue-600" />
        </div>
      </div>

      {/* Current Prices Management */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Monthly Subscription */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow duration-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl">
                <Calendar className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Месячная подписка</h3>
                <p className="text-sm text-gray-600">AI проверка контента</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {editing.type === 'month' ? (
                <div className="flex items-center space-x-2">
                  <input
                    type="number"
                    min="1"
                    value={editing.value}
                    onChange={(e) => setEditing(prev => ({ ...prev, value: parseInt(e.target.value) || 0 }))}
                    className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                    autoFocus
                  />
                  <button
                    onClick={savePrice}
                    className="p-1 text-green-600 hover:text-green-800"
                    title="Сохранить"
                  >
                    <Save className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => setEditing({ type: null, value: 0 })}
                    className="p-1 text-red-600 hover:text-red-800"
                    title="Отмена"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ) : (
                <>
                  <button
                    onClick={() => startEditing('month')}
                    className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Редактировать цену"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <div className="text-right">
                    <div className="text-3xl font-bold text-gray-900 mb-1">
                      {monthPrice?.price_stars || '—'}
                    </div>
                    <div className="text-sm text-gray-500 uppercase tracking-wide">
                      {monthPrice?.currency || 'XTR'} / мес
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
          {monthPrice && (
            <div className="text-xs text-gray-500">
              Создано: {new Date(monthPrice.created_at).toLocaleDateString('ru-RU')}
            </div>
          )}
        </div>

        {/* Yearly Subscription */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow duration-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-gradient-to-br from-green-100 to-green-200 rounded-xl">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Годовая подписка</h3>
                <p className="text-sm text-gray-600">AI проверка контента</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {editing.type === 'year' ? (
                <div className="flex items-center space-x-2">
                  <input
                    type="number"
                    min="1"
                    value={editing.value}
                    onChange={(e) => setEditing(prev => ({ ...prev, value: parseInt(e.target.value) || 0 }))}
                    className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                    autoFocus
                  />
                  <button
                    onClick={savePrice}
                    className="p-1 text-green-600 hover:text-green-800"
                    title="Сохранить"
                  >
                    <Save className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => setEditing({ type: null, value: 0 })}
                    className="p-1 text-red-600 hover:text-red-800"
                    title="Отмена"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ) : (
                <>
                  <button
                    onClick={() => startEditing('year')}
                    className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    title="Редактировать цену"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <div className="text-right">
                    <div className="text-3xl font-bold text-gray-900 mb-1">
                      {yearPrice?.price_stars || calculatedYearlyPrice || '—'}
                    </div>
                    <div className="text-sm text-gray-500 uppercase tracking-wide">
                      {yearPrice?.currency || 'XTR'} / год
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
          {yearPrice ? (
            <div className="text-xs text-gray-500">
              Создано: {new Date(yearPrice.created_at).toLocaleDateString('ru-RU')}
            </div>
          ) : (
            <div className="text-xs text-blue-600">
              Рассчитано на основе месячной цены со скидкой {calculator.yearlyDiscountPercent}%
            </div>
          )}
        </div>
      </div>

      {/* Smart Price Calculator */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow duration-200">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-br from-purple-100 to-purple-200 rounded-lg">
              <Calculator className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Умный калькулятор цен</h2>
              <p className="text-sm text-gray-600">Автоматический расчет годовых тарифов</p>
            </div>
          </div>
          <button
            onClick={updateCalculatedPrice}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-green-600 hover:bg-green-700 transition-colors"
            disabled={!calculator.monthlyPrice || calculator.monthlyPrice <= 0}
          >
            <Settings className="h-4 w-4 mr-2" />
            Применить расчет
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Calculator Inputs */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Месячная цена (базовая)
              </label>
              <div className="relative">
                <Star className="absolute left-3 top-1/2 transform -translate-y-1/2 text-yellow-500 h-4 w-4" />
                <input
                  type="number"
                  min="1"
                  value={calculator.monthlyPrice}
                  onChange={(e) => setCalculator(prev => ({
                    ...prev,
                    monthlyPrice: parseInt(e.target.value) || 0
                  }))}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Введите месячную цену"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Скидка на год (%) - для привлечения клиентов
              </label>
              <div className="relative">
                <Percent className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <input
                  type="number"
                  min="0"
                  max="50"
                  value={calculator.yearlyDiscountPercent}
                  onChange={(e) => setCalculator(prev => ({
                    ...prev,
                    yearlyDiscountPercent: parseInt(e.target.value) || 0
                  }))}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Количество чатов
              </label>
              <input
                type="number"
                min="1"
                max="100"
                value={calculator.quantity}
                onChange={(e) => setCalculator(prev => ({
                  ...prev,
                  quantity: parseInt(e.target.value) || 1
                }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Calculator Results */}
          <div className="bg-gradient-to-br from-gray-50 to-blue-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
              Расчетные цены
            </h3>

            <div className="space-y-4">
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">Месячная подписка:</span>
                  <span className="text-lg font-bold text-blue-600">{calculator.monthlyPrice} XTR</span>
                </div>
                <div className="text-xs text-gray-500">за 1 чат в месяц</div>
              </div>

              <div className="bg-white rounded-lg p-4 border border-green-200">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">Годовая подписка:</span>
                  <span className="text-lg font-bold text-green-600">{calculatedYearlyPrice} XTR</span>
                </div>
                <div className="text-xs text-green-600">
                  Скидка {calculator.yearlyDiscountPercent}% = экономия {yearlySavings} XTR
                </div>
              </div>

              <div className="bg-white rounded-lg p-4 border border-purple-200">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">Итого за {calculator.quantity} чат(ов):</span>
                  <span className="text-lg font-bold text-purple-600">{totalPrice} XTR</span>
                </div>
                <div className="text-xs text-purple-600">
                  {calculator.quantity} × {calculator.monthlyPrice} XTR
                </div>
              </div>

              {calculator.yearlyDiscountPercent > 0 && (
                <div className="bg-green-100 rounded-lg p-3 border border-green-300">
                  <div className="flex items-center text-green-800">
                    <TrendingUp className="h-4 w-4 mr-2" />
                    <span className="text-sm font-medium">
                      Экономия при годовой подписке: {yearlySavings} XTR ({Math.round(yearlySavings / (calculator.monthlyPrice * 12) * 100)}%)
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Currency Converter */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow duration-200">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-gradient-to-br from-green-100 to-green-200 rounded-lg">
            <DollarSign className="h-6 w-6 text-green-600" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900">Конвертер в USDT</h2>
        </div>

        <CurrencyConverter starsAmount={totalPrice} />
      </div>

      {/* Add New Price Form */}
      {showAddForm && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-br from-orange-100 to-orange-200 rounded-lg">
                <Plus className="h-6 w-6 text-orange-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Добавить новую цену подписки</h2>
            </div>
            <button
              onClick={() => setShowAddForm(false)}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <form onSubmit={(e) => { e.preventDefault(); createNewPrice(); }} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Тип подписки
                </label>
                <select
                  value={newPriceData.subscription_type}
                  onChange={(e) => setNewPriceData(prev => ({
                    ...prev,
                    subscription_type: e.target.value as 'month' | 'year'
                  }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="month">Месячная</option>
                  <option value="year">Годовая</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Цена (звезд)
                </label>
                <div className="relative">
                  <Star className="absolute left-3 top-1/2 transform -translate-y-1/2 text-yellow-500 h-4 w-4" />
                  <input
                    type="number"
                    min="1"
                    value={newPriceData.price_stars}
                    onChange={(e) => setNewPriceData(prev => ({
                      ...prev,
                      price_stars: parseInt(e.target.value) || 1
                    }))}
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Валюта
                </label>
                <input
                  type="text"
                  value={newPriceData.currency}
                  onChange={(e) => setNewPriceData(prev => ({
                    ...prev,
                    currency: e.target.value
                  }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
            </div>

            <div className="flex items-center space-x-3 pt-4">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Добавить цену
              </button>
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
              >
                Отмена
              </button>
            </div>
          </form>
        </div>
      )}

      {/* All Prices List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center">
              <Settings className="h-6 w-6 mr-3 text-gray-600" />
              Все цены подписок
            </h2>
            <button
              onClick={() => setShowAddForm(true)}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-lg text-blue-600 bg-blue-50 hover:bg-blue-100 transition-colors"
            >
              <Plus className="h-4 w-4 mr-2" />
              Добавить
            </button>
          </div>

          {prices && prices.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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
                        onClick={() => {
                          const newStatus = !price.is_active;
                          fetch(`/api/subscription-prices/${price.id}`, {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ is_active: newStatus }),
                          }).then(() => refetch());
                        }}
                        className={`p-1 rounded ${
                          price.is_active
                            ? 'text-red-600 hover:bg-red-50'
                            : 'text-green-600 hover:bg-green-50'
                        }`}
                        title={price.is_active ? 'Деактивировать' : 'Активировать'}
                      >
                        {price.is_active ? '⏸️' : '▶️'}
                      </button>
                      <button
                        onClick={() => {
                          if (confirm('Удалить эту цену подписки?')) {
                            fetch(`/api/subscription-prices/${price.id}`, {
                              method: 'DELETE',
                            }).then(() => refetch());
                          }
                        }}
                        className="p-1 text-red-600 hover:bg-red-50 rounded"
                        title="Удалить"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      {price.subscription_type === 'month' ? (
                        <Calendar className="h-4 w-4 text-blue-500" />
                      ) : (
                        <TrendingUp className="h-4 w-4 text-green-500" />
                      )}
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
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-100 p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Shield className="h-5 w-5 text-blue-600" />
          </div>
          <h3 className="text-lg font-semibold text-blue-900">
            Как использовать калькулятор
          </h3>
        </div>
        <div className="text-sm text-blue-800 space-y-2 ml-11">
          <div className="flex items-start space-x-2">
            <div className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
            <p><strong>1.</strong> Введите месячную цену - это базовая стоимость подписки</p>
          </div>
          <div className="flex items-start space-x-2">
            <div className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
            <p><strong>2.</strong> Укажите скидку на год - привлекает клиентов к долгосрочным подпискам</p>
          </div>
          <div className="flex items-start space-x-2">
            <div className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
            <p><strong>3.</strong> Калькулятор автоматически рассчитает годовую цену и экономию</p>
          </div>
          <div className="flex items-start space-x-2">
            <div className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
            <p><strong>4.</strong> Нажмите "Применить расчет" чтобы сохранить рассчитанную годовую цену</p>
          </div>
        </div>
      </div>
    </div>
  );
};
