// Fixed rates based on real Telegram Stars data:
// Purchase: 500 stars = 9.39 USD => 1 star = 0.01878 USD
// Withdrawal: 400 stars = 5.21 USD => 1 star = 0.013025 USD
// Using purchase rate for subscription pricing
const STARS_TO_USD_RATE = 0.01878; // Based on 500 stars = 9.39 USD
const USD_TO_RUB_RATE = 90.0; // Fixed RUB rate

interface CurrencyRate {
  usd: number;
  rub: number;
  lastUpdated: Date;
}

export const useCurrencyConverter = () => {
  // Return fixed rates instead of fetching from API
  const rates: CurrencyRate = {
    usd: 1.0, // USDT = USD
    rub: USD_TO_RUB_RATE,
    lastUpdated: new Date(),
  };

  // Convert functions using fixed rates
  const convertStarsToUSDT = (stars: number): number => {
    // Convert Stars to USD, then to USDT (1:1 ratio)
    return stars * STARS_TO_USD_RATE;
  };

  const convertStarsToRUB = (stars: number): number => {
    const usdAmount = stars * STARS_TO_USD_RATE;
    return usdAmount * USD_TO_RUB_RATE;
  };

  const convertUSDTToStars = (usdt: number): number => {
    return usdt / STARS_TO_USD_RATE;
  };

  const formatCurrency = (amount: number, currency: 'USDT' | 'RUB' | 'USD'): string => {
    if (amount === 0) return '0';

    switch (currency) {
      case 'USDT':
        return `${amount.toFixed(4)} USDT`;
      case 'RUB':
        return `${Math.round(amount)} ₽`;
      case 'USD':
        return `$${amount.toFixed(2)}`;
      default:
        return amount.toString();
    }
  };

  return {
    rates,
    isLoading: false,
    error: null,
    refetch: () => {}, // No-op since we use fixed rates
    convertStarsToUSDT,
    convertStarsToRUB,
    convertUSDTToStars,
    formatCurrency,
    lastUpdated: rates.lastUpdated,
  };
};
