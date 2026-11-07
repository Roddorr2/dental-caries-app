import React from 'react';
import { formatConfidence } from '../../../utils/formatters';
import { CheckCircle2, XCircle, AlertOctagon, BarChart2 } from 'lucide-react';

export const EstadisticasModelo = ({ estadisticas }) => {
  if (!estadisticas || estadisticas.length === 0) {
    return (
      <div className="p-8 bg-slate-50 border border-slate-200 rounded-lg text-center text-xs text-slate-500 font-mono">
        Aún no hay diagnósticos clínicos validados suficientes para calcular métricas en producción de este modelo.
      </div>
    );
  }

  // Si viene una lista (como retorna el backend list[EstadisticasResponse]), tomamos el primer registro o mapeamos
  const stats = Array.isArray(estadisticas) ? estadisticas[0] : estadisticas;

  const {
    nombre_modelo,
    version,
    total_diagnosticos,
    total_validados,
    total_rechazados,
    tasa_validacion,
    tasa_segunda_opinion,
  } = stats;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 sm:p-6 shadow-subtle space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pb-3 border-b border-slate-100">
        <div>
          <h4 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <BarChart2 className="w-4 h-4 text-slate-700" />
            <span>Desempeño Diagnóstico en Práctica Clínica</span>
          </h4>
          <p className="text-xs text-slate-500 font-mono mt-0.5">
            Métricas de precisión basadas en validaciones de odontólogos colegiados
          </p>
        </div>

        <span className="text-xs font-mono text-slate-600 bg-slate-100 px-2.5 py-1 rounded-md self-start sm:self-auto font-medium">
          {nombre_modelo} v{version}
        </span>
      </div>

      {/* Tarjetas de indicadores de producción */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-4 font-mono">
        <div className="p-2.5 sm:p-3 bg-slate-50 border border-slate-200 rounded-lg min-w-0">
          <span className="text-[10px] text-slate-400 block uppercase truncate">Total Casos</span>
          <span className="text-base sm:text-lg font-bold text-slate-900 block mt-1">
            {total_diagnosticos || 0}
          </span>
          <span className="text-[10px] text-slate-500 truncate block">Evaluados por IA</span>
        </div>

        <div className="p-2.5 sm:p-3 bg-emerald-50/50 border border-emerald-200 rounded-lg min-w-0">
          <div className="flex items-center gap-1.5 text-emerald-800">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
            <span className="text-[10px] uppercase font-semibold truncate">Validados</span>
          </div>
          <span className="text-base sm:text-lg font-bold text-emerald-900 block mt-1">
            {total_validados || 0}
          </span>
          <span className="text-[10px] text-emerald-700 truncate block">Aceptados</span>
        </div>

        <div className="p-2.5 sm:p-3 bg-rose-50/50 border border-rose-200 rounded-lg min-w-0">
          <div className="flex items-center gap-1.5 text-rose-800">
            <XCircle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
            <span className="text-[10px] uppercase font-semibold truncate">Rechazados</span>
          </div>
          <span className="text-base sm:text-lg font-bold text-rose-900 block mt-1">
            {total_rechazados || 0}
          </span>
          <span className="text-[10px] text-rose-700 truncate block">Desestimados</span>
        </div>

        <div className="p-2.5 sm:p-3 bg-amber-50/50 border border-amber-200 rounded-lg min-w-0">
          <div className="flex items-center gap-1.5 text-amber-800">
            <AlertOctagon className="w-3.5 h-3.5 text-amber-600 shrink-0" />
            <span className="text-[10px] uppercase font-semibold truncate">2da Opinión</span>
          </div>
          <span className="text-base sm:text-lg font-bold text-amber-900 block mt-1">
            {formatConfidence(tasa_segunda_opinion)}
          </span>
          <span className="text-[10px] text-amber-700 truncate block">Baja confianza</span>
        </div>
      </div>

      {/* Barra visual de Tasa de Validación */}
      <div className="space-y-2 pt-2">
        <div className="flex items-center justify-between text-xs font-mono">
          <span className="text-slate-600 font-semibold">Tasa de Aceptación Clínica</span>
          <span className="font-bold text-emerald-800">
            {formatConfidence(tasa_validacion)}
          </span>
        </div>
        <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden flex border border-slate-200">
          <div
            className="bg-emerald-600 transition-all duration-300"
            style={{ width: `${Math.min(100, Math.max(0, (tasa_validacion || 0) * 100))}%` }}
          />
          <div
            className="bg-rose-500 transition-all duration-300"
            style={{ width: `${Math.min(100, Math.max(0, 100 - (tasa_validacion || 0) * 100))}%` }}
          />
        </div>
        <div className="flex justify-between text-[10px] font-mono text-slate-400">
          <span>0%</span>
          <span>Objetivo clínico mínimo: 85%</span>
          <span>100%</span>
        </div>
      </div>
    </div>
  );
};
