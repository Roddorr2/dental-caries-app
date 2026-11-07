import React, { useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useEstudioDetail, useSolicitarAnalisis } from '../hooks/useEstudios';
import { useInferencia } from '../hooks/useInferencia';
import { EstadoPipeline } from '../components/EstadoPipeline';
import { CalidadBadge } from '../components/CalidadBadge';
import { Button } from '../../../shared/components/Button';
import { Badge } from '../../../shared/components/Badge';
import { Loader } from '../../../shared/components/Loader';
import { formatDate, formatEstadoPipeline } from '../../../utils/formatters';
import { TIPO_EXAMEN_LABELS } from '../constants';
import {
  ArrowLeft,
  Folder,
  Image as ImageIcon,
  Sparkles,
  Plus,
  AlertCircle,
  Stethoscope,
} from 'lucide-react';

export const EstudioDetail = () => {
  const { id: estudioId } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const inferenciaIdParam = searchParams.get('inferencia_id');

  const { data: estudio, isLoading: isLoadingEstudio, error } = useEstudioDetail(estudioId);
  const solicitarAnalisisMutation = useSolicitarAnalisis(estudioId);

  // Polling de inferencia inline en tiempo real
  const [activeInferenciaId, setActiveInferenciaId] = useState(inferenciaIdParam);
  const { inferencia, isCompleted } = useInferencia(activeInferenciaId, estudioId);

  const [actionError, setActionError] = useState(null);

  const handleTriggerAnalysis = async () => {
    try {
      setActionError(null);
      // Ejecución directa del motor CDSS oficial calibrado
      const res = await solicitarAnalisisMutation.mutateAsync();
      const newInferenciaId = res?.inferencia_id || res?.id;
      setActiveInferenciaId(newInferenciaId);
    } catch (err) {
      setActionError(err.message || 'Error al solicitar análisis clínico con CDSS.');
    }
  };


  if (isLoadingEstudio) {
    return <Loader size="lg" message="Cargando estudio fotográfico intraoral..." className="py-20" />;
  }

  if (error || !estudio) {
    return (
      <div className="p-6 bg-white border border-rose-200 rounded-lg text-center space-y-4">
        <AlertCircle className="w-8 h-8 text-rose-600 mx-auto" />
        <h3 className="text-base font-semibold text-slate-900">Estudio no encontrado</h3>
        <p className="text-xs text-slate-500 font-sans">{error?.message || 'Identificador clínico inválido.'}</p>
        <Button variant="secondary" onClick={() => navigate('/pacientes')}>
          Volver
        </Button>
      </div>
    );
  }

  const imagenes = estudio.imagenes || [];
  const estadoBadgeVariant = {
    PENDIENTE: 'neutral',
    EN_ANALISIS: 'warning',
    PROCESADO: 'success',
  }[estudio.estado_procesamiento] || 'neutral';

  return (
    <div className="max-w-5xl mx-auto space-y-5 min-w-0">
      {/* Botón superior de retroceso y acciones */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-1.5 text-xs font-mono text-slate-500 hover:text-slate-900 transition-colors py-1 self-start"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Volver</span>
        </button>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Button
            size="sm"
            variant="outline"
            icon={Plus}
            onClick={() => navigate(`/estudios/${estudioId}/subir-imagen`)}
            className="flex-1 sm:flex-none"
          >
            Agregar Imagen
          </Button>

          {imagenes.length > 0 && estudio.estado_procesamiento !== 'EN_ANALISIS' && (
            <Button
              size="sm"
              variant="primary"
              icon={Sparkles}
              onClick={handleTriggerAnalysis}
              isLoading={solicitarAnalisisMutation.isPending}
              className="flex-1 sm:flex-none"
            >
              Reanalizar con IA
            </Button>
          )}
        </div>
      </div>

      {actionError && (
        <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-800 flex items-center gap-2 font-mono">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
          <span>{actionError}</span>
        </div>
      )}

      {/* Tarjeta de Resumen del Estudio */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 sm:p-6 shadow-subtle space-y-5 min-w-0">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pb-4 border-b border-slate-100">
          <div className="flex items-start gap-3.5 sm:gap-4 min-w-0">
            <div className="w-12 h-12 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-700 shrink-0 shadow-inner">
              <Folder className="w-6 h-6 text-slate-600" />
            </div>
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="text-base sm:text-lg font-bold text-slate-900 tracking-tight break-words">
                  {TIPO_EXAMEN_LABELS[estudio.tipo_examen] || estudio.tipo_examen}
                </h2>
                <Badge variant={estadoBadgeVariant} showDot size="sm">
                  {formatEstadoPipeline(estudio.estado_procesamiento)}
                </Badge>
              </div>
              <p className="font-mono text-xs text-slate-500 mt-1 flex flex-wrap items-center gap-x-2 gap-y-0.5">
                <span>Estudio #{estudio.id?.slice(0, 8)}</span>
                <span className="text-slate-300">·</span>
                <span>{formatDate(estudio.created_at, true)}</span>
              </p>
            </div>
          </div>
        </div>

        {/* Metadatos clínicos del estudio */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
          <div className="p-3 bg-slate-50/80 rounded-lg border border-slate-100">
            <span className="text-[10px] text-slate-400 block uppercase font-mono">Paciente Vinculado</span>
            <span className="text-slate-800 font-semibold truncate block mt-0.5">
              H.C. #{estudio.paciente_id?.slice(0, 8)}
            </span>
          </div>

          <div className="p-3 bg-slate-50/80 rounded-lg border border-slate-100">
            <span className="text-[10px] text-slate-400 block uppercase font-mono">Total Fotografías</span>
            <span className="text-slate-800 font-semibold block mt-0.5">
              {imagenes.length} {imagenes.length === 1 ? 'fotografía registrada' : 'fotografías registradas'}
            </span>
          </div>

          <div className="p-3 bg-slate-50/80 rounded-lg border border-slate-100">
            <span className="text-[10px] text-slate-400 block uppercase font-mono">Estado del Estudio</span>
            <span className="text-slate-800 font-semibold block mt-0.5">
              {formatEstadoPipeline(estudio.estado_procesamiento)}
            </span>
          </div>
        </div>
      </div>

      {/* Monitoreo inline del pipeline de inferencia IA (si está activo o completado) */}
      {inferencia && (
        <EstadoPipeline
          inferencia={inferencia}
          onVerDiagnostico={() => navigate('/revision')}
        />
      )}

      {/* Galería de Fotografías intraorales asociadas */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 sm:p-6 shadow-subtle space-y-4 min-w-0">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
          <div>
            <h3 className="text-sm font-bold text-slate-900 tracking-tight">
              Fotografías del Estudio ({imagenes.length})
            </h3>
            <p className="text-xs text-slate-500 font-sans mt-0.5">
              Archivo fotográfico intraoral analizado por el modelo
            </p>
          </div>
          <Button
            size="sm"
            variant="outline"
            icon={Plus}
            onClick={() => navigate(`/estudios/${estudioId}/subir-imagen`)}
            className="w-full sm:w-auto"
          >
            Subir Fotografía
          </Button>
        </div>

        {imagenes.length === 0 ? (
          <div className="py-12 text-center text-xs text-slate-400 font-mono">
            <ImageIcon className="w-8 h-8 text-slate-300 mx-auto mb-2" />
            <p>No hay fotografías cargadas en este estudio.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {imagenes.map((img) => (
              <div
                key={img.id}
                className="border border-slate-200 rounded-lg overflow-hidden bg-slate-50 flex flex-col"
              >
                <div className="h-40 bg-slate-900 flex items-center justify-center p-2 relative">
                  <ImageIcon className="w-10 h-10 text-slate-600" />
                  <span className="absolute bottom-2 left-2 text-[10px] font-mono text-slate-300 bg-slate-800/80 px-1.5 py-0.5 rounded">
                    {img.tipo_vista}
                  </span>
                </div>
                <div className="p-3 text-xs space-y-2 bg-white flex-1 flex flex-col justify-between">
                  <div>
                    <p className="font-semibold text-slate-900 truncate">
                      {img.nombre_archivo}
                    </p>
                    <p className="text-[10px] font-mono text-slate-400 mt-0.5">
                      {formatDate(img.created_at)}
                    </p>
                  </div>
                  <CalidadBadge calidadSuficiente={img.calidad_suficiente} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
