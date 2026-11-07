import React from 'react';
import { CheckCircle2, AlertTriangle } from 'lucide-react';

/**
 * CalidadBadge
 * Indicador visual austero del control de calidad radiográfica
 */
export const CalidadBadge = ({
  calidadSuficiente = true,
  nitidez = null,
  iluminacion = null,
}) => {
  return (
    <div className="inline-flex items-center gap-2">
      <span
        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono border ${
          calidadSuficiente
            ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
            : 'bg-rose-50 text-rose-800 border-rose-200'
        }`}
      >
        {calidadSuficiente ? (
          <>
            <CheckCircle2 className="w-3 h-3 text-emerald-600 shrink-0" />
            <span>Calidad Diagnóstica OK</span>
          </>
        ) : (
          <>
            <AlertTriangle className="w-3 h-3 text-rose-600 shrink-0" />
            <span>Calidad Insuficiente</span>
          </>
        )}
      </span>

      {(nitidez !== null || iluminacion !== null) && (
        <span className="text-[10px] font-mono text-slate-500">
          {nitidez !== null && `Nitidez: ${Math.round(nitidez * 100)}%`}
          {nitidez !== null && iluminacion !== null && ' · '}
          {iluminacion !== null && `Ilum: ${Math.round(iluminacion * 100)}%`}
        </span>
      )}
    </div>
  );
};
