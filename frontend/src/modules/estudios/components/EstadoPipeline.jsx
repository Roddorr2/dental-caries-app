import React from 'react';
import { Loader2, CheckCircle2, XCircle, Cpu, Clock, HardDrive } from 'lucide-react';
import { formatLatency } from '../../../utils/formatters';

/**
 * EstadoPipeline
 * Muestra el estado del pipeline de inferencia IA en tiempo real (inline).
 */
export const EstadoPipeline = ({ inferencia, onVerDiagnostico = null }) => {
  if (!inferencia) return null;

  const { estado, worker_id, gpu_utilizada, tiempo_ms, error_mensaje } = inferencia;

  const isCompleted = estado === 'COMPLETADO';
  const isFailed = estado === 'FALLIDO';
  const isPending = estado === 'PENDIENTE';
  const isInProgress = estado === 'EN_PROCESO';

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-subtle space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2.5">
          {isCompleted && <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />}
          {isFailed && <XCircle className="w-5 h-5 text-rose-600 shrink-0" />}
          {(isPending || isInProgress) && (
            <Loader2 className="w-5 h-5 text-amber-600 animate-spin shrink-0" />
          )}

          <div>
            <h4 className="text-sm font-semibold text-slate-900 tracking-tight">
              Análisis Asistido por IA
            </h4>
            <p className="text-xs text-slate-500 font-sans">
              {isPending && 'En espera de análisis por IA'}
              {isInProgress && 'Analizando superficie y piezas dentales en fotografía intraoral...'}
              {isCompleted && 'Análisis finalizado — Hallazgos clínicos identificados'}
              {isFailed && 'No se pudo completar el análisis del estudio'}
            </p>
          </div>
        </div>

        {isCompleted && onVerDiagnostico && (
          <button
            type="button"
            onClick={onVerDiagnostico}
            className="px-3 py-1.5 bg-slate-900 text-white rounded text-xs font-medium hover:bg-slate-800 transition-colors shadow-sm"
          >
            Revisar Diagnóstico
          </button>
        )}
      </div>

      {/* Indicadores técnicos de ejecución */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
        <div className="flex items-center gap-2 p-2 bg-slate-50 rounded border border-slate-200/80">
          <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          <div>
            <span className="text-[10px] text-slate-400 block uppercase">Tiempo de Procesamiento</span>
            <span className="text-slate-700 font-medium">{formatLatency(tiempo_ms)}</span>
          </div>
        </div>

        <div className="flex items-center gap-2 p-2 bg-slate-50 rounded border border-slate-200/80">
          <Cpu className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          <div>
            <span className="text-[10px] text-slate-400 block uppercase">Aceleración</span>
            <span className="text-slate-700 font-medium">{gpu_utilizada || 'Procesador Estándar'}</span>
          </div>
        </div>

        <div className="flex items-center gap-2 p-2 bg-slate-50 rounded border border-slate-200/80">
          <HardDrive className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          <div>
            <span className="text-[10px] text-slate-400 block uppercase">Nodo Asignado</span>
            <span className="text-slate-700 font-medium truncate max-w-[120px]">
              {worker_id ? `#${worker_id.slice(0, 8)}` : 'Asignado'}
            </span>
          </div>
        </div>
      </div>

      {/* Mensaje de error si falló */}
      {isFailed && error_mensaje && (
        <div className="p-3 bg-rose-50 border border-rose-200 rounded text-xs text-rose-800 font-mono">
          <strong>Fallo:</strong> {error_mensaje}
        </div>
      )}
    </div>
  );
};
