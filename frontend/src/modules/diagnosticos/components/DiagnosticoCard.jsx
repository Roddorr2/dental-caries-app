import React from 'react';
import { ConfidenceBadge } from './ConfidenceBadge';
import { Badge } from '../../../shared/components/Badge';
import { formatDate, formatConfidence } from '../../../utils/formatters';
import { Activity, AlertTriangle, ArrowRight, CheckCircle2 } from 'lucide-react';

export const DiagnosticoCard = ({ diagnostico, onSelect = null }) => {
  if (!diagnostico) return null;

  const id = diagnostico.diagnostico_id || diagnostico.id;
  const confianza_global = diagnostico.confianza_global;
  const categoria_confianza = diagnostico.categoria_confianza;
  const estado = diagnostico.estado || (diagnostico.segunda_opinion ? '2DA_OPINION' : 'PENDIENTE');
  const hallazgos = diagnostico.hallazgos || [];
  const fecha_generacion = diagnostico.fecha_generacion;
  const segunda_opinion = diagnostico.segunda_opinion;
  const paciente_nombre = diagnostico.paciente_nombre;
  const paciente_id = diagnostico.paciente_id;
  const tipo_examen = diagnostico.tipo_examen;

  const isBajaConfianza = categoria_confianza === 'BAJA' || segunda_opinion;

  return (
    <div
      role={onSelect ? 'button' : undefined}
      tabIndex={onSelect ? 0 : undefined}
      onClick={() => onSelect && onSelect(diagnostico)}
      onKeyDown={(e) => {
        if (onSelect && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          onSelect(diagnostico);
        }
      }}
      className={`bg-white border rounded-xl p-4 sm:p-5 shadow-subtle transition-all select-none ${
        isBajaConfianza
          ? 'border-rose-200 hover:border-rose-300 bg-rose-50/20'
          : 'border-slate-200 hover:border-slate-300'
      } ${onSelect ? 'cursor-pointer active:scale-[0.99] active:bg-slate-50' : ''}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1.5 min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <ConfidenceBadge
              categoria={categoria_confianza}
              confianza={confianza_global}
              size="sm"
            />
            {isBajaConfianza && (
              <Badge variant="danger" size="sm" showDot>
                2da Opinión
              </Badge>
            )}
          </div>

          {paciente_nombre && (
            <div>
              <h4 className="text-sm font-bold text-slate-900 tracking-tight truncate">
                {paciente_nombre}
              </h4>
              {paciente_id && (
                <p className="font-mono text-[10px] text-slate-400">
                  H.C. #{paciente_id.slice(0, 8)}
                </p>
              )}
            </div>
          )}

          <p className="font-mono text-[11px] text-slate-500">
            {tipo_examen ? `${tipo_examen} · ` : ''}Fecha: {formatDate(fecha_generacion, true)}
          </p>
        </div>

        <Badge
          variant={
            estado === 'VALIDADO'
              ? 'success'
              : estado === 'RECHAZADO'
              ? 'danger'
              : isBajaConfianza
              ? 'danger'
              : 'warning'
          }
          size="sm"
          showDot
          className="shrink-0"
        >
          {estado === '2DA_OPINION' ? '2da Opinión' : estado}
        </Badge>
      </div>

      <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-600">
        <span className="font-mono text-[11px] text-slate-500">
          Caso #{id?.slice(0, 8)}
        </span>

        {onSelect && (
          <span className="inline-flex items-center gap-1 text-slate-900 font-semibold text-xs">
            <span>Revisar caso</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </span>
        )}
      </div>
    </div>
  );
};
