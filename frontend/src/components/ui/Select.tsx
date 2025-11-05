import React from 'react';
import { ChevronDown } from 'lucide-react';

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  helperText?: string;
  icon?: React.ReactNode;
  variant?: 'default' | 'primary' | 'success' | 'danger';
}

export const Select: React.FC<SelectProps> = ({
  label,
  error,
  helperText,
  icon,
  variant = 'default',
  className = '',
  children,
  ...props
}) => {
  const variantClasses = {
    default: 'border-gray-300 focus:border-blue-500 focus:ring-blue-500',
    primary: 'border-blue-300 focus:border-blue-600 focus:ring-blue-600',
    success: 'border-green-300 focus:border-green-600 focus:ring-green-600',
    danger: 'border-red-300 focus:border-red-600 focus:ring-red-600',
  };

  const variantBg = {
    default: 'bg-white',
    primary: 'bg-blue-50',
    success: 'bg-green-50',
    danger: 'bg-red-50',
  };

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">
            {icon}
          </div>
        )}
        <select
          className={`
            w-full px-4 py-2.5 pr-10
            ${icon ? 'pl-10' : ''}
            ${variantBg[variant]}
            border ${error ? 'border-red-500 focus:border-red-600 focus:ring-red-600' : variantClasses[variant]}
            rounded-lg
            text-gray-900
            font-medium
            appearance-none
            focus:outline-none focus:ring-2 focus:ring-opacity-50
            transition-all duration-200
            cursor-pointer
            hover:border-gray-400
            disabled:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-500
            shadow-sm
            ${className}
          `}
          {...props}
        >
          {children}
        </select>
        <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
          <ChevronDown className={`w-5 h-5 transition-colors ${error ? 'text-red-500' : 'text-gray-400'}`} />
        </div>
      </div>
      {error && (
        <p className="mt-1.5 text-sm text-red-600 flex items-center gap-1">
          <span className="font-medium">⚠</span> {error}
        </p>
      )}
      {helperText && !error && (
        <p className="mt-1.5 text-sm text-gray-500">
          {helperText}
        </p>
      )}
    </div>
  );
};
