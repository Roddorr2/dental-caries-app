import React from 'react';
import { Loader2 } from 'lucide-react';

/**
 * Loader clínico: spinner sobrio o skeleton screens
 */
export const Loader = ({
  size = 'md',
  message = 'Cargando datos clínicos...',
  fullScreen = false,
  className = '',
}) => {
  const sizeMap = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  const content = (
    <div className={`flex flex-col items-center justify-center p-6 text-slate-500 gap-3 ${className}`}>
      <Loader2 className={`${sizeMap[size]} animate-spin text-slate-700`} />
      {message && <p className="text-xs font-mono text-slate-500">{message}</p>}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-slate-50/80 backdrop-blur-none flex items-center justify-center z-50">
        {content}
      </div>
    );
  }

  return content;
};

export const Skeleton = ({ className = '' }) => {
  return (
    <div
      className={`animate-pulse bg-slate-200 rounded ${className}`}
      aria-hidden="true"
    />
  );
};
