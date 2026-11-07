import React from 'react';
import {
  formatPiezaDental,
  formatPatologia,
  formatSeveridad,
  formatConfidence,
} from '../../../utils/formatters';
import { SEVERIDAD_COLORES } from '../constants';
import { Eye, EyeOff, AlertCircle } from 'lucide-react';

export const HallazgosList = ({
  hallazgos = [],
  selectedHallazgoId = null,
  onSelectHallazgo = null,
  visibleHallazgoIds = null,
  onToggleVisibility = null,
}) => {
  if (hallazgos.length === 0) {
    return (
      <div className="p-6 bg-slate-50 border border-slate-200 rounded-lg text-center text-xs text-slate-500 font-sans">
        No se detectaron hallazgos patológicos en esta fotografía intraoral.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs text-slate-500 pb-1 font-sans uppercase tracking-wider">
        <span>Patologías Detectadas ({hallazgos.length})</span>
        <span>Visibilidad</span>
      </div>

      <div className="divide-y divide-slate-100 border border-slate-200 rounded-lg bg-white overflow-hidden shadow-subtle">
        {hallazgos.map((h, idx) => {
          const isSelected = selectedHallazgoId === h.id;
          const isVisible = !visibleHallazgoIds || visibleHallazgoIds.has(h.id);
          const severidadColor = SEVERIDAD_COLORES[h.severidad] || SEVERIDAD_COLORES.MODERADA;

          return (
            <div
              key={h.id || idx}
              onClick={() => onSelectHallazgo && onSelectHallazgo(h)}
              className={`p-3 text-xs flex items-center justify-between gap-3 cursor-pointer transition-colors ${
                isSelected
                  ? 'bg-slate-100/90 font-medium'
                  : 'hover:bg-slate-50'
              }`}
            >
              <div className="flex items-start gap-3 min-w-0">
                <span
                  className="w-2.5 h-2.5 rounded-full mt-1 shrink-0"
                  style={{ backgroundColor: severidadColor.stroke }}
                  title={`Severidad: ${h.severidad}`}
                />

                <div className="space-y-0.5 truncate">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-slate-900 truncate">
                      {formatPatologia(h.tipo_patologia)}
                    </span>
                    <span
                      className="px-1.5 py-0.2 rounded text-[10px] font-mono border"
                      style={{
                        backgroundColor: severidadColor.bg,
                        borderColor: severidadColor.border,
                        color: severidadColor.text,
                      }}
                    >
                      {formatSeveridad(h.severidad)}
                    </span>
                  </div>

                  <p className="text-[11px] text-slate-600 font-mono">
                    {formatPiezaDental(h.diente_numero, h.cuadrante)}
                  </p>

                  {h.descripcion_clinica && (
                    <p className="text-[11px] text-slate-500 italic truncate">
                      "{h.descripcion_clinica}"
                    </p>
                  )}
                </div>
              </div>

              {/* Controles: Porcentaje de confianza y Toggle de visibilidad */}
              <div className="flex items-center gap-3 shrink-0">
                <span className="font-mono text-xs font-medium text-slate-700">
                  {formatConfidence(h.confianza)}
                </span>

                {onToggleVisibility && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleVisibility(h.id);
                    }}
                    className={`p-1 rounded hover:bg-slate-200 transition-colors ${
                      isVisible ? 'text-slate-700' : 'text-slate-300'
                    }`}
                    title={isVisible ? 'Ocultar recuadro' : 'Mostrar recuadro'}
                    aria-label="Alternar visibilidad del recuadro"
                  >
                    {isVisible ? (
                      <Eye className="w-4 h-4" />
                    ) : (
                      <EyeOff className="w-4 h-4" />
                    )}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
