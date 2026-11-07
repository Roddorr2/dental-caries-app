import React from 'react';

/**
 * Badge clínico con indicador de estado (dot) y colores semánticos
 */
export const Badge = ({
  children,
  variant = 'neutral', // 'neutral' | 'success' | 'warning' | 'danger' | 'info'
  size = 'md', // 'sm' | 'md'
  showDot = false,
  className = '',
}) => {
  const variantStyles = {
    neutral: 'bg-slate-100 text-slate-700 border-slate-200',
    success: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    warning: 'bg-amber-50 text-amber-800 border-amber-200',
    danger: 'bg-rose-50 text-rose-800 border-rose-200',
    info: 'bg-blue-50 text-blue-800 border-blue-200',
  };

  const dotStyles = {
    neutral: 'bg-slate-400',
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
    danger: 'bg-rose-500',
    info: 'bg-blue-500',
  };

  const sizeStyles = {
    sm: 'text-xs px-2 py-0.5 font-normal',
    md: 'text-xs px-2.5 py-1 font-medium',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 border rounded-md whitespace-nowrap shrink-0 select-none ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
    >
      {showDot && (
        <span
          className={`w-1.5 h-1.5 rounded-full shrink-0 ${dotStyles[variant]}`}
          aria-hidden="true"
        />
      )}
      <span className="truncate">{children}</span>
    </span>
  );
};
