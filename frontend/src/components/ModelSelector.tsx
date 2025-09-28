import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Search, Bot, DollarSign, Filter, X, SlidersHorizontal } from 'lucide-react';
import { OpenRouterModel } from '../types';

interface ModelSelectorProps {
  models: OpenRouterModel[];
  value: string;
  onChange: (modelId: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  models,
  value,
  onChange,
  placeholder = "Выберите модель...",
  disabled = false
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const [showFilters, setShowFilters] = useState(false);
  const [priceFilter, setPriceFilter] = useState<{ min: number | null; max: number | null }>({
    min: null,
    max: null
  });
  const containerRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Get model price for filtering (uses the higher of prompt/completion prices)
  const getModelPrice = (model: OpenRouterModel): number | null => {
    if (!model.pricing) return null;

    const promptPrice = model.pricing.prompt ? parseFloat(model.pricing.prompt) : null;
    const completionPrice = model.pricing.completion ? parseFloat(model.pricing.completion) : null;

    if (promptPrice === null && completionPrice === null) return null;

    // Use the higher price for filtering (worst case scenario)
    return Math.max(promptPrice || 0, completionPrice || 0);
  };

  // Filter models based on search term and price
  const filteredModels = models.filter(model => {
    // Search term filter
    const matchesSearch = model.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (model.description && model.description.toLowerCase().includes(searchTerm.toLowerCase()));

    // Price filter
    const modelPrice = getModelPrice(model);
    const matchesPrice = priceFilter.min === null || priceFilter.max === null ||
      (modelPrice !== null && modelPrice >= (priceFilter.min || 0) && modelPrice <= (priceFilter.max || Infinity));

    return matchesSearch && matchesPrice;
  });

  // Get selected model
  const selectedModel = models.find(model => model.id === value);

  // Format pricing for display
  const formatPricing = (pricing: Record<string, any> | undefined) => {
    if (!pricing) return null;

    const promptPrice = pricing.prompt ? parseFloat(pricing.prompt) : null;
    const completionPrice = pricing.completion ? parseFloat(pricing.completion) : null;

    if (promptPrice === null && completionPrice === null) return null;

    return {
      prompt: promptPrice ? `$${(promptPrice * 1000000).toFixed(2)}M` : null,
      completion: completionPrice ? `$${(completionPrice * 1000000).toFixed(2)}M` : null
    };
  };

  // Reset filters
  const resetFilters = () => {
    setPriceFilter({ min: null, max: null });
    setSearchTerm('');
  };

  // Get available price range for suggestions
  const getPriceRange = () => {
    const prices = models
      .map(model => getModelPrice(model))
      .filter(price => price !== null)
      .sort((a, b) => (a || 0) - (b || 0));

    if (prices.length === 0) return { min: 0, max: 100 };

    return {
      min: Math.floor((prices[0] || 0) * 1000000),
      max: Math.ceil((prices[prices.length - 1] || 0) * 1000000)
    };
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setHighlightedIndex(-1);
        // Don't reset filters when closing dropdown
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Focus search input when dropdown opens
  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isOpen]);

  const handleToggle = () => {
    if (disabled) return;
    setIsOpen(!isOpen);
    setHighlightedIndex(-1);
  };

  const handleModelSelect = (model: OpenRouterModel) => {
    onChange(model.id);
    setIsOpen(false);
    setHighlightedIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex(prev =>
          prev < filteredModels.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex(prev => prev > 0 ? prev - 1 : prev);
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < filteredModels.length) {
          handleModelSelect(filteredModels[highlightedIndex]);
        }
        break;
      case 'Escape':
        e.preventDefault();
        setIsOpen(false);
        setHighlightedIndex(-1);
        break;
    }
  };

  return (
    <div className="relative" ref={containerRef}>
      {/* Trigger button */}
      <button
        type="button"
        onClick={handleToggle}
        disabled={disabled}
        className={`w-full px-3 py-2 text-left border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent flex items-center justify-between ${
          disabled ? 'bg-gray-50 cursor-not-allowed' : 'bg-white hover:bg-gray-50'
        }`}
      >
        <div className="flex items-center space-x-2 flex-1 min-w-0">
          <Bot className="h-4 w-4 text-green-500 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            {selectedModel ? (
              <div className="truncate">
                <span className="font-medium text-gray-900">{selectedModel.name}</span>
              </div>
            ) : (
              <span className="text-gray-500">{placeholder}</span>
            )}
          </div>
        </div>
        <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-96 overflow-hidden">
          {/* Search and filter controls */}
          <div className="p-2 border-b border-gray-200 space-y-2">
            {/* Search input */}
            <div className="relative">
              <Search className="h-4 w-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              <input
                ref={searchInputRef}
                type="text"
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setHighlightedIndex(-1);
                }}
                onKeyDown={handleKeyDown}
                placeholder="Поиск моделей..."
                className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-transparent"
              />
            </div>

            {/* Filter toggle and reset */}
            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center space-x-1 text-xs text-gray-600 hover:text-gray-800"
              >
                <SlidersHorizontal className="h-3 w-3" />
                <span>Фильтры</span>
                <ChevronDown className={`h-3 w-3 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
              </button>

              {/* Reset filters button */}
              {(searchTerm || priceFilter.min !== null || priceFilter.max !== null) && (
                <button
                  type="button"
                  onClick={resetFilters}
                  className="flex items-center space-x-1 text-xs text-red-600 hover:text-red-800"
                >
                  <X className="h-3 w-3" />
                  <span>Сбросить</span>
                </button>
              )}
            </div>

            {/* Price filters */}
            {showFilters && (
              <div className="space-y-2 pt-2 border-t border-gray-100">
                <div className="text-xs font-medium text-gray-700">Цена за миллион токенов ($)</div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Мин</label>
                    <input
                      type="number"
                      value={priceFilter.min || ''}
                      onChange={(e) => setPriceFilter(prev => ({
                        ...prev,
                        min: e.target.value ? parseFloat(e.target.value) : null
                      }))}
                      placeholder="0"
                      min="0"
                      step="0.01"
                      className="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Макс</label>
                    <input
                      type="number"
                      value={priceFilter.max || ''}
                      onChange={(e) => setPriceFilter(prev => ({
                        ...prev,
                        max: e.target.value ? parseFloat(e.target.value) : null
                      }))}
                      placeholder="∞"
                      min="0"
                      step="0.01"
                      className="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <div className="text-xs text-gray-500">
                  Диапазон: ${getPriceRange().min} - ${getPriceRange().max}
                </div>
              </div>
            )}
          </div>

          {/* Models list */}
          <div className="max-h-80 overflow-y-auto">
            {filteredModels.length === 0 ? (
              <div className="p-4 text-center text-gray-500 text-sm">
                Модели не найдены
              </div>
            ) : (
              filteredModels.map((model, index) => {
                const pricing = formatPricing(model.pricing);
                const isSelected = model.id === value;
                const isHighlighted = index === highlightedIndex;

                return (
                  <button
                    key={model.id}
                    type="button"
                    onClick={() => handleModelSelect(model)}
                    className={`w-full px-4 py-3 text-left hover:bg-gray-50 focus:outline-none focus:bg-gray-50 ${
                      isSelected ? 'bg-green-50 border-l-4 border-green-500' : ''
                    } ${isHighlighted ? 'bg-gray-100' : ''}`}
                  >
                    <div className="space-y-1">
                      {/* Model name and description */}
                      <div>
                        <div className="font-medium text-gray-900 text-sm">
                          {model.name}
                        </div>
                        {model.description && (
                          <div className="text-xs text-gray-600 mt-1 line-clamp-2">
                            {model.description}
                          </div>
                        )}
                      </div>

                      {/* Pricing and features */}
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        {pricing && (
                          <div className="flex items-center space-x-2">
                            <DollarSign className="h-3 w-3" />
                            <span>
                              {pricing.prompt && `Prompt: ${pricing.prompt}`}
                              {pricing.prompt && pricing.completion && ' / '}
                              {pricing.completion && `Completion: ${pricing.completion}`}
                            </span>
                          </div>
                        )}
                        <div className="flex items-center space-x-2">
                          {model.supports_function_calling && (
                            <span className="px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">
                              Functions
                            </span>
                          )}
                          {model.supports_vision && (
                            <span className="px-1.5 py-0.5 bg-purple-100 text-purple-700 rounded text-xs">
                              Vision
                            </span>
                          )}
                          {model.context_length && (
                            <span className="px-1.5 py-0.5 bg-gray-100 text-gray-700 rounded text-xs">
                              {model.context_length.toLocaleString()} tokens
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </button>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
};
