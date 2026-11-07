import React from 'react';
import { Folder, Image as ImageIcon, Calendar, ArrowRight } from 'lucide-react';
import { formatDate, formatEstadoPipeline } from '../../../utils/formatters';
import { Badge } from '../../../shared/components/Badge';
import { TIPO_EXAMEN_LABELS } from '../constants';

export const EstudioCard = ({ estudio, onSelect = null }) => {
  if (!estudio) return null;

  const estadoBadgeVariant = {
    PENDIENTE: 'neutral',
    EN_ANALISIS: 'warning',
    PROCESADO: 'success',
  }[estudio.estado_procesamiento] || 'neutral';

  return (
    <div
      onClick={() => onSelect && onSelect(estudio)}
      className={`bg-white border border-slate-200 rounded-lg p-5 shadow-subtle hover:border-slate-300 transition-colors ${
        onSelect ? 'cursor-pointer hover:shadow-card' : ''
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-md bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-700">
            <Folder className="w-4 h-4 text-slate-600" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-900 tracking-tight">
              {TIPO_EXAMEN_LABELS[estudio.tipo_examen] || estudio.tipo_examen}
            </h4>
            <p className="font-mono text-[11px] text-slate-400 mt-0.5">
              Estudio #{estudio.id.slice(0, 8)}
            </p>
          </div>
        </div>

        <Badge variant={estadoBadgeVariant} showDot size="sm">
          {formatEstadoPipeline(estudio.estado_procesamiento)}
        </Badge>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 font-mono">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <ImageIcon className="w-3.5 h-3.5 text-slate-400" />
            {(estudio.imagenes && estudio.imagenes.length) || 0} imágenes
          </span>
          <span className="flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-slate-400" />
            {formatDate(estudio.created_at)}
          </span>
        </div>

        {onSelect && (
          <span className="text-slate-400 hover:text-slate-800 transition-colors">
            <ArrowRight className="w-4 h-4" />
          </span>
        )}
      </div>
    </div>
  );
};
