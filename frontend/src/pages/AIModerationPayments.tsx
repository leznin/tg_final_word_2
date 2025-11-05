import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Shield, Calculator, DollarSign, Star, Percent, Zap, Edit, Plus, Save, X, TrendingUp, Calendar, Settings } from 'lucide-react';
import { useSubscriptionPrices } from '../hooks/useSubscriptionPrices';
import { Loading } from '../components/ui/Loading';
import { api } from '../utils/api';
import { Select } from '../components/ui/Select';

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
      const data = {
        subscription_type: editing.type,
        price_stars: editing.value,
        currency: 'XTR'
      };

      if (existingPrice) {
        await api.put(`/subscription-prices/${existingPrice.id}`, data);
      } else {
        await api.post('/subscription-prices/', data);
      }

      refetch();
      setEditing({ type: null, value: 0 });
      alert(`Цена ${editing.type === 'month' ? 'месячной' : 'годовой'} подписки обновлена!`);
    } catch (error) {
      alert('Ошибка при сохранении цены');
    }
  };

  // Handle creating new price
  const createNewPrice = async () => {
    try {
      await api.post('/subscription-prices/', newPriceData);

      refetch();
      setShowAddForm(false);
      setNewPriceData({ subscription_type: 'month', price_stars: 10, currency: 'XTR' });
      alert('Цена добавлена успешно!');
    } catch (error) {
      alert('Ошибка при добавлении цены');
    }
  };

  const updateCalculatedPrice = async () => {
    try {
      // Update monthly price if it has changed
      if (monthPrice && calculator.monthlyPrice !== monthPrice.price_stars) {
        await api.put(`/subscription-prices/${monthPrice.id}`, {
          price_stars: calculator.monthlyPrice,
          subscription_type: 'month',
          currency: 'XTR'
        });
      } else if (!monthPrice && calculator.monthlyPrice > 0) {
        // Create monthly price if it doesn't exist
        await api.post('/subscription-prices/', {
          subscription_type: 'month',
          price_stars: calculator.monthlyPrice,
          currency: 'XTR'
        });
      }

      // Update or create yearly price
      if (yearPrice && calculatedYearlyPrice !== yearPrice.price_stars) {
        await api.put(`/subscription-prices/${yearPrice.id}`, {
          price_stars: calculatedYearlyPrice,
          subscription_type: 'year',
          currency: 'XTR'
        });
      } else if (!yearPrice && calculatedYearlyPrice > 0) {
        await api.post('/subscription-prices/', {
          subscription_type: 'year',
          price_stars: calculatedYearlyPrice,
          currency: 'XTR'
        });
      }

      // Refresh data and show success message
      refetch();
      alert('Цены успешно обновлены!');
    } catch (error) {
      console.error('Error updating prices:', error);
      alert('Ошибка при обновлении цен');
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
            <h1 className="text-3xl font-bold text-slate-900">AI Модерация контента</h1>
            <p className="mt-2 text-sm text-slate-600">
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

      {/* Main Content */}
      <div className="space-y-6">

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

      {/* Compact Calculator */}
      <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-white/20 p-4 hover:bg-white/90 hover:shadow-lg hover:shadow-purple-500/10 transition-all duration-300">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-purple-100/80 rounded-lg">
              <Calculator className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Калькулятор цен</h2>
              <p className="text-xs text-slate-600">Автоматический расчет тарифов</p>
            </div>
          </div>
          <button
            onClick={updateCalculatedPrice}
            className="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 transition-colors disabled:opacity-50"
            disabled={!calculator.monthlyPrice || calculator.monthlyPrice <= 0}
          >
            <Settings className="h-3 w-3 mr-1.5" />
            Применить
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Monthly Price Input */}
          <div className="space-y-2">
            <label className="block text-xs font-medium text-slate-700">
              Месячная цена
            </label>
            <div className="relative">
              <Star className="absolute left-2.5 top-1/2 transform -translate-y-1/2 text-amber-500 h-3.5 w-3.5" />
              <input
                type="number"
                min="1"
                value={calculator.monthlyPrice}
                onChange={(e) => setCalculator(prev => ({
                  ...prev,
                  monthlyPrice: parseInt(e.target.value) || 0
                }))}
                className="w-full pl-8 pr-3 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white/50"
                placeholder="0"
              />
            </div>
          </div>

          {/* Discount Input */}
          <div className="space-y-2">
            <label className="block text-xs font-medium text-slate-700">
              Скидка на год (%)
            </label>
            <div className="relative">
              <Percent className="absolute left-2.5 top-1/2 transform -translate-y-1/2 text-slate-400 h-3.5 w-3.5" />
              <input
                type="number"
                min="0"
                max="50"
                value={calculator.yearlyDiscountPercent}
                onChange={(e) => setCalculator(prev => ({
                  ...prev,
                  yearlyDiscountPercent: parseInt(e.target.value) || 0
                }))}
                className="w-full pl-8 pr-3 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent bg-white/50"
              />
            </div>
          </div>

          {/* Quantity Input */}
          <div className="space-y-2">
            <label className="block text-xs font-medium text-slate-700">
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
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white/50"
            />
          </div>
        </div>

        {/* Results Row */}
        <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="bg-blue-50/80 rounded-lg p-3 border border-blue-200/50">
            <div className="text-xs text-blue-700 font-medium mb-1">Месяц</div>
            <div className="text-lg font-bold text-blue-600">{calculator.monthlyPrice} XTR</div>
            <div className="text-xs text-blue-600">за чат</div>
          </div>

          <div className="bg-emerald-50/80 rounded-lg p-3 border border-emerald-200/50">
            <div className="text-xs text-emerald-700 font-medium mb-1">Год</div>
            <div className="text-lg font-bold text-emerald-600">{calculatedYearlyPrice} XTR</div>
            <div className="text-xs text-emerald-600">
              -{calculator.yearlyDiscountPercent}% ({yearlySavings} XTR)
            </div>
          </div>

          <div className="bg-purple-50/80 rounded-lg p-3 border border-purple-200/50">
            <div className="text-xs text-purple-700 font-medium mb-1">Итого</div>
            <div className="text-lg font-bold text-purple-600">{totalPrice} XTR</div>
            <div className="text-xs text-purple-600">
              {calculator.quantity} × {calculator.monthlyPrice}
            </div>
          </div>
        </div>

        {/* Currency Converter Section */}
        <div className="mt-4 pt-4 border-t border-slate-200/50">
          <div className="flex items-center space-x-2 mb-3">
            <DollarSign className="h-4 w-4 text-emerald-600" />
            <span className="text-sm font-medium text-slate-700">Конвертер валют</span>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-white/50 rounded-lg p-2 border border-slate-200/50 text-center">
              <div className="text-xs text-slate-500">XTR</div>
              <div className="text-sm font-semibold text-slate-900">{totalPrice}</div>
            </div>
            <div className="bg-white/50 rounded-lg p-2 border border-slate-200/50 text-center">
              <div className="text-xs text-slate-500">USDT</div>
              <div className="text-sm font-semibold text-emerald-600">
                ≈{(totalPrice * 0.0188).toFixed(2)}
              </div>
            </div>
            <div className="bg-white/50 rounded-lg p-2 border border-slate-200/50 text-center">
              <div className="text-xs text-slate-500">RUB</div>
              <div className="text-sm font-semibold text-blue-600">
                ≈{Math.round(totalPrice * 0.0188 * 90)}
              </div>
            </div>
          </div>
          <div className="mt-2 text-xs text-slate-500 text-center">
            1 XTR ≈ 0.0188 USD ≈ 1.69 ₽
          </div>
        </div>
      </div>

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
              <Select
                label="Тип подписки"
                value={newPriceData.subscription_type}
                onChange={(e) => setNewPriceData(prev => ({
                  ...prev,
                  subscription_type: e.target.value as 'month' | 'year'
                }))}
                icon={<Calendar className="w-5 h-5" />}
              >
                <option value="month">Месячная</option>
                <option value="year">Годовая</option>
              </Select>

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
