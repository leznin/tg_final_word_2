import React, { useState } from 'react';
import { Calendar, TrendingUp, Edit, Save, X, Star, MoreVertical, Play, Pause } from 'lucide-react';

interface SubscriptionPrice {
  id: number;
  subscription_type: string;
  price_stars: number;
  currency: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface SubscriptionPriceCardProps {
  price: SubscriptionPrice;
  onEdit: (id: number, newPrice: number) => void;
  onToggle: (id: number) => void;
  onDelete?: (id: number) => void;
}

export const SubscriptionPriceCard: React.FC<SubscriptionPriceCardProps> = ({
  price,
  onEdit,
  onToggle,
  onDelete
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(price.price_stars.toString());
  const [showMenu, setShowMenu] = useState(false);

  const isMonthly = price.subscription_type === 'month';
  const Icon = isMonthly ? Calendar : TrendingUp;

  const handleSave = () => {
    const newPrice = parseInt(editValue);
    if (!isNaN(newPrice) && newPrice >= 0) {
      onEdit(price.id, newPrice);
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    setEditValue(price.price_stars.toString());
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSave();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  return (
    <div className="group relative bg-white/70 backdrop-blur-sm border border-white/20 rounded-xl p-4 hover:bg-white/90 hover:shadow-lg hover:shadow-blue-500/10 hover:scale-[1.02] hover:-translate-y-0.5 transition-all duration-300 ease-out">
      {/* Status indicator */}
      <div className="absolute top-2 right-2 flex items-center space-x-1">
        <div className={`w-2 h-2 rounded-full ${price.is_active ? 'bg-emerald-400 shadow-emerald-400/50 shadow-lg' : 'bg-slate-400'}`} />
        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-1 rounded-md hover:bg-black/5 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
          >
            <MoreVertical className="h-3 w-3 text-slate-400" />
          </button>

          {/* Dropdown menu */}
          {showMenu && (
            <div className="absolute right-0 top-6 z-10 bg-white/95 backdrop-blur-sm border border-white/20 rounded-lg shadow-lg py-1 min-w-[120px]">
              <button
                onClick={() => {
                  onToggle(price.id);
                  setShowMenu(false);
                }}
                className="w-full px-3 py-2 text-left text-xs hover:bg-slate-50 flex items-center space-x-2"
              >
                {price.is_active ? (
                  <>
                    <Pause className="h-3 w-3 text-orange-500" />
                    <span>Деактивировать</span>
                  </>
                ) : (
                  <>
                    <Play className="h-3 w-3 text-emerald-500" />
                    <span>Активировать</span>
                  </>
                )}
              </button>
              {onDelete && (
                <button
                  onClick={() => {
                    if (confirm('Удалить эту цену подписки?')) {
                      onDelete(price.id);
                      setShowMenu(false);
                    }
                  }}
                  className="w-full px-3 py-2 text-left text-xs hover:bg-red-50 text-red-600 flex items-center space-x-2"
                >
                  <X className="h-3 w-3" />
                  <span>Удалить</span>
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Main content */}
      <div className="flex items-start space-x-3">
        <div className={`p-2 rounded-lg flex-shrink-0 ${
          isMonthly
            ? 'bg-blue-100/80 text-blue-600'
            : 'bg-emerald-100/80 text-emerald-600'
        }`}>
          <Icon className="h-4 w-4" />
        </div>

        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold text-slate-900 mb-1">
            {isMonthly ? 'Месячная подписка' : 'Годовая подписка'}
          </h4>

          <div className="flex items-center space-x-2 mb-2">
            {isEditing ? (
              <div className="flex items-center space-x-1">
                <Star className="h-3 w-3 text-amber-500 flex-shrink-0" />
                <input
                  type="number"
                  min="0"
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="w-16 px-2 py-1 text-xs border border-slate-200 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-transparent bg-white/50"
                  autoFocus
                />
                <button
                  onClick={handleSave}
                  className="p-1 text-emerald-600 hover:bg-emerald-50 rounded"
                  title="Сохранить"
                >
                  <Save className="h-3 w-3" />
                </button>
                <button
                  onClick={handleCancel}
                  className="p-1 text-slate-600 hover:bg-slate-50 rounded"
                  title="Отмена"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            ) : (
              <>
                <button
                  onClick={() => setIsEditing(true)}
                  className="flex items-center space-x-1 group/edit"
                >
                  <Star className="h-4 w-4 text-amber-500" />
                  <span className="text-lg font-bold text-slate-900 group-hover/edit:text-blue-600 transition-colors">
                    {price.price_stars}
                  </span>
                  <span className="text-xs text-slate-500 font-medium">
                    {price.currency}
                  </span>
                </button>
                <button
                  onClick={() => setIsEditing(true)}
                  className="p-1 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded opacity-0 group-hover:opacity-100 transition-all duration-200"
                  title="Редактировать цену"
                >
                  <Edit className="h-3 w-3" />
                </button>
              </>
            )}
          </div>

          <div className="text-xs text-slate-500">
            Создано {new Date(price.created_at).toLocaleDateString('ru-RU')}
          </div>
        </div>
      </div>

      {/* Click outside to close menu */}
      {showMenu && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setShowMenu(false)}
        />
      )}
    </div>
  );
};
