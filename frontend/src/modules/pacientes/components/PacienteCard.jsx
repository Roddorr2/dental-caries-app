import React from 'react';
import { User, Phone, Mail, CreditCard, ChevronRight } from 'lucide-react';
import { Badge } from '../../../shared/components/Badge';
import { SEXO_LABELS } from '../constants';

export const PacienteCard = ({ paciente, onSelect = null }) => {
  if (!paciente) return null;

  // Cálculo de edad clínica aproximada
  const calcularEdad = (fechaNac) => {
    if (!fechaNac) return null;
    const diff = Date.now() - new Date(fechaNac).getTime();
    const ageDate = new Date(diff);
    return Math.abs(ageDate.getUTCFullYear() - 1970);
  };

  const edad = calcularEdad(paciente.fecha_nacimiento);

  return (
    <div
      role={onSelect ? 'button' : undefined}
      tabIndex={onSelect ? 0 : undefined}
      onClick={() => onSelect && onSelect(paciente)}
      onKeyDown={(e) => {
        if (onSelect && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          onSelect(paciente);
        }
      }}
      className={`bg-white border border-slate-200 rounded-xl p-4 sm:p-5 shadow-subtle transition-all select-none ${
        onSelect
          ? 'cursor-pointer hover:border-slate-300 active:scale-[0.99] active:bg-slate-50'
          : ''
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 min-w-0">
          <div className="w-10 h-10 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-700 font-semibold text-sm shrink-0 shadow-inner">
            <User className="w-5 h-5 text-slate-600" />
          </div>
          <div className="min-w-0">
            <h4 className="text-sm font-bold text-slate-900 tracking-tight truncate">
              {paciente.apellidos}, {paciente.nombres}
            </h4>
            <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5 mt-0.5">
              <span className="font-mono text-xs text-slate-500 flex items-center gap-1">
                <CreditCard className="w-3 h-3 text-slate-400" />
                DNI {paciente.dni}
              </span>
              {edad !== null && (
                <span className="text-xs text-slate-400 font-mono">
                  · {edad} años ({SEXO_LABELS[paciente.sexo] || paciente.sexo})
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <Badge
            variant={paciente.estado === 'ACTIVO' ? 'success' : 'neutral'}
            showDot
            size="sm"
          >
            {paciente.estado}
          </Badge>
          {onSelect && (
            <ChevronRight className="w-4 h-4 text-slate-400" />
          )}
        </div>
      </div>

      <div className="mt-3.5 pt-3 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-600">
        <div className="flex items-center gap-2 truncate">
          <Phone className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          <span className="font-mono truncate">{paciente.telefono || '—'}</span>
        </div>
        <div className="flex items-center gap-2 truncate">
          <Mail className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          <span className="font-mono truncate">{paciente.email || '—'}</span>
        </div>
      </div>
    </div>
  );
};
