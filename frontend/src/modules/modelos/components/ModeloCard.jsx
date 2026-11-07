import React from 'react';
import { Cpu, CheckCircle2, AlertTriangle, Award } from 'lucide-react';
import { Badge } from '../../../shared/components/Badge';
import { formatConfidence } from '../../../utils/formatters';
import { TIPO_MODELO_LABELS } from '../constants';

export const ModeloCard = ({ modelo, isSelected = false, onSelect = null }) => {
  if (!modelo) return null;

  const {
    id,
    nombre,
    version,
    tipo,
    f1_score,
    precision_score,
    recall_score,
    aprobado_produccion,
  } = modelo;

  return (
    <div
      role={onSelect ? 'button' : undefined}
      tabIndex={onSelect ? 0 : undefined}
      onClick={() => onSelect && onSelect(modelo)}
      onKeyDown={(e) => {
        if (onSelect && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          onSelect(modelo);
        }
      }}
      className={`bg-white border rounded-xl p-4 shadow-subtle transition-all select-none space-y-3 ${
        isSelected
          ? 'border-slate-900 ring-2 ring-slate-900/10 shadow-md'
          : 'border-slate-200 hover:border-slate-300'
      } ${onSelect ? 'cursor-pointer active:scale-[0.99] active:bg-slate-50' : ''}`}
    >
      {/* Fila superior: Icono, versión y Badge de estado (sin desbordamiento) */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className="w-8 h-8 rounded-lg bg-slate-100 border border-slate-200/80 flex items-center justify-center text-slate-700 shrink-0">
            <Cpu className="w-4 h-4 text-slate-600" />
          </div>
          <span className="text-[10px] font-mono font-semibold text-slate-600 bg-slate-100 border border-slate-200/70 px-2 py-0.5 rounded shrink-0">
            v{version}
          </span>
        </div>

        <Badge
          variant={aprobado_produccion ? 'success' : 'neutral'}
          showDot
          size="sm"
          className="shrink-0 text-[10px]"
        >
          {aprobado_produccion ? 'Producción' : 'Experimental'}
        </Badge>
      </div>

      {/* Nombre del modelo y arquitectura clínica */}
      <div className="min-w-0">
        <h4 className="text-sm font-bold text-slate-900 tracking-tight break-words leading-snug">
          {nombre}
        </h4>
        <p className="text-[11px] text-slate-500 font-mono mt-0.5 break-words">
          {TIPO_MODELO_LABELS[tipo] || tipo}
        </p>
      </div>

      {/* Grid de Métricas de Validación Clínica */}
      <div className="grid grid-cols-3 gap-1.5 sm:gap-2 pt-3 border-t border-slate-100 text-center font-mono">
        <div className="p-2 bg-slate-50 rounded border border-slate-100 min-w-0">
          <span className="text-[8.5px] sm:text-[9px] text-slate-400 uppercase block tracking-tight">F1-Score</span>
          <span className={`text-xs sm:text-sm font-bold block mt-0.5 ${f1_score >= 0.85 ? 'text-emerald-700' : 'text-slate-800'}`}>
            {formatConfidence(f1_score)}
          </span>
        </div>

        <div className="p-2 bg-slate-50 rounded border border-slate-100 min-w-0">
          <span className="text-[8.5px] sm:text-[9px] text-slate-400 uppercase block tracking-tight">Precisión</span>
          <span className="text-xs sm:text-sm font-bold text-slate-800 block mt-0.5">
            {formatConfidence(precision_score)}
          </span>
        </div>

        <div className="p-2 bg-slate-50 rounded border border-slate-100 min-w-0">
          <span className="text-[8.5px] sm:text-[9px] text-slate-400 uppercase block tracking-tight">Sensibilidad</span>
          <span className="text-xs sm:text-sm font-bold text-slate-800 block mt-0.5">
            {formatConfidence(recall_score)}
          </span>
        </div>
      </div>
    </div>
  );
};

