import React from 'react';
import { Inbox } from 'lucide-react';

/**
 * Estado vacío austero y claro
 */
export const EmptyState = ({
  icon: Icon = Inbox,
  title = 'No se encontraron registros',
  description = 'No hay datos clínicos disponibles en este momento.',
  action = null,
  bordered = true,
  className = '',
}) => {
  return (
    <div
      className={`flex flex-col items-center justify-center p-8 text-center ${
        bordered ? 'bg-white border border-slate-200 rounded-lg shadow-subtle' : ''
      } ${className}`}
    >
      <div className="w-10 h-10 rounded-md bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-500 mb-3">
        <Icon className="w-5 h-5 stroke-[1.5]" />
      </div>
      <h4 className="text-sm font-semibold text-slate-900 tracking-tight">
        {title}
      </h4>
      <p className="text-xs text-slate-500 max-w-sm mt-1 mb-4 font-sans">
        {description}
      </p>
      {action && <div className="mt-1">{action}</div>}
    </div>
  );
};
