import React from 'react';
import { DollarSign } from 'lucide-react';
import { useCurrencyConverter } from '../../hooks/useCurrencyConverter';

interface CurrencyConverterProps {
  starsAmount: number;
}

export const CurrencyConverter: React.FC<CurrencyConverterProps> = ({
  starsAmount
}) => {
  const {
    convertStarsToUSDT,
    convertStarsToRUB,
    formatCurrency
  } = useCurrencyConverter();

  const usdtAmount = convertStarsToUSDT(starsAmount);
  const rubAmount = convertStarsToRUB(starsAmount);

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <div className="flex items-center space-x-2 mb-4">
        <DollarSign className="h-5 w-5 text-green-600" />
        <h3 className="text-lg font-semibold text-gray-900">Конвертер валют</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        {/* Stars */}
        <div className="bg-white rounded-lg p-3 border">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Telegram Stars</div>
          <div className="text-lg font-semibold text-gray-900">{starsAmount}</div>
        </div>

        {/* USDT */}
        <div className="bg-white rounded-lg p-3 border">
          <div className="text-xs text-gray-500 uppercase tracking-wide">USDT</div>
          <div className="text-lg font-semibold text-green-600">{formatCurrency(usdtAmount, 'USDT')}</div>
        </div>

        {/* RUB */}
        <div className="bg-white rounded-lg p-3 border">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Рубли</div>
          <div className="text-lg font-semibold text-blue-600">{formatCurrency(rubAmount, 'RUB')}</div>
        </div>
      </div>

      {/* Exchange Rates Info */}
      <div className="bg-white rounded-lg p-3 border mb-3">
        <div className="text-sm text-gray-600 mb-2">Курс обмена:</div>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">1 Star = </span>
            <span className="font-medium">0.0188 USD</span>
          </div>
          <div>
            <span className="text-gray-500">1 USD = </span>
            <span className="font-medium">90 ₽</span>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="text-xs text-blue-800">
          <strong>Важно:</strong> Курсы основаны на реальных данных Telegram Stars.
          Для покупок: 500 Stars = 9.39 USD. Для снятия: 400 Stars = 5.21 USD.
        </div>
      </div>
    </div>
  );
};
