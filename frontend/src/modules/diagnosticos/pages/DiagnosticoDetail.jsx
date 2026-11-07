import React, { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  useDiagnosticoDetail,
  useValidarDiagnostico,
  useRechazarDiagnostico,
} from '../hooks/useDiagnosticos';
import { HallazgoBbox } from '../components/HallazgoBbox';
import { HallazgosList } from '../components/HallazgosList';
import { ConfidenceBadge } from '../components/ConfidenceBadge';
import { ValidarForm } from '../components/ValidarForm';
import { RechazarForm } from '../components/RechazarForm';
import { Modal } from '../../../shared/components/Modal';
import { Badge } from '../../../shared/components/Badge';
import { Button } from '../../../shared/components/Button';
import { Loader } from '../../../shared/components/Loader';
import { formatDate, formatEstadoDiagnostico } from '../../../utils/formatters';
import {
  ArrowLeft,
  CheckCircle2,
  XCircle,
  Eye,
  EyeOff,
  SunMedium,
  ZoomIn,
  AlertCircle,
  UserCheck,
  Calendar,
  Layers,
  FileCheck,
} from 'lucide-react';

export const DiagnosticoDetail = () => {
  const { id: diagnosticoId } = useParams();
  const navigate = useNavigate();

  const { data: diagnostico, isLoading, error, refetch } = useDiagnosticoDetail(diagnosticoId);

  const validarMutation = useValidarDiagnostico();
  const rechazarMutation = useRechazarDiagnostico();

  // Estados locales de la vista fotográfica clínica
  const [selectedHallazgoId, setSelectedHallazgoId] = useState(null);
  const [visibleHallazgoIds, setVisibleHallazgoIds] = useState(new Set());
  const [invertContrast, setInvertContrast] = useState(false);
  const [contrastHigh, setContrastHigh] = useState(false);

  // Modales clínicos
  const [isValidarOpen, setIsValidarOpen] = useState(false);
  const [isRechazarOpen, setIsRechazarOpen] = useState(false);
  const [mutationError, setMutationError] = useState(null);

  // Inicializar visibilidad de todos los hallazgos al cargar
  React.useEffect(() => {
    if (diagnostico?.hallazgos) {
      const allIds = new Set(diagnostico.hallazgos.map((h) => h.id));
      setVisibleHallazgoIds(allIds);
    }
  }, [diagnostico]);

  const toggleFindingVisibility = (id) => {
    setVisibleHallazgoIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const toggleAllVisibility = () => {
    if (!diagnostico?.hallazgos) return;
    if (visibleHallazgoIds.size === diagnostico.hallazgos.length) {
      setVisibleHallazgoIds(new Set());
    } else {
      setVisibleHallazgoIds(new Set(diagnostico.hallazgos.map((h) => h.id)));
    }
  };

  const handleValidarSubmit = async (payload) => {
    try {
      setMutationError(null);
      await validarMutation.mutateAsync({
        id: diagnosticoId,
        odontologo_id: payload.odontologo_id,
        notas: payload.notas,
      });
      setIsValidarOpen(false);
      refetch();
    } catch (err) {
      setMutationError(err.message || 'Error al validar el diagnóstico');
    }
  };

  const handleRechazarSubmit = async (payload) => {
    try {
      setMutationError(null);
      await rechazarMutation.mutateAsync({
        id: diagnosticoId,
        odontologo_id: payload.odontologo_id,
        motivo: payload.motivo,
      });
      setIsRechazarOpen(false);
      refetch();
    } catch (err) {
      setMutationError(err.message || 'Error al rechazar el diagnóstico');
    }
  };

  if (isLoading) {
    return <Loader size="lg" message="Cargando estudio fotográfico y hallazgos..." className="py-24" />;
  }

  if (error || !diagnostico) {
    return (
      <div className="p-8 bg-white border border-rose-200 rounded-lg text-center space-y-4 max-w-lg mx-auto">
        <AlertCircle className="w-10 h-10 text-rose-600 mx-auto" />
        <h3 className="text-base font-semibold text-slate-900">
          Diagnóstico Clínico No Disponible
        </h3>
        <p className="text-xs text-slate-500 font-mono">
          {error?.message || 'El identificador de diagnóstico no fue encontrado en la base de datos.'}
        </p>
        <Button variant="secondary" onClick={() => navigate('/revision')}>
          Volver a la Cola de Revisión
        </Button>
      </div>
    );
  }

  const {
    estado,
    confianza_global,
    categoria_confianza,
    hallazgos = [],
    fecha_generacion,
    fecha_validacion,
    notas_validacion,
    motivo_rechazo,
    estudio_id,
    paciente_id,
  } = diagnostico;

  const isPendingReview = estado === 'SUGERIDO_IA' || estado === 'EN_REVISION';
  const isValidated = estado === 'VALIDADO';
  const isRejected = estado === 'RECHAZADO';

  // Usamos una ruta de radiografía de muestra o servicio de imágenes del estudio
  const radiographySrc = '/samples/sample_case_1.jpg';

  return (
    <div className="space-y-4 max-w-7xl mx-auto flex flex-col min-h-full lg:h-[calc(100vh-6rem)]">
      {/* Barra superior de herramientas clínicas (Radiology Viewer Bar) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3.5 bg-white border border-slate-200 rounded-xl px-4 py-3 shadow-subtle shrink-0">
        <div className="flex items-start sm:items-center gap-3 min-w-0">
          <button
            type="button"
            onClick={() => navigate('/revision')}
            className="w-8 h-8 flex items-center justify-center rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors shrink-0 mt-0.5 sm:mt-0"
            title="Volver a la cola"
            aria-label="Volver a la cola de revisión"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>

          <div className="hidden sm:block h-5 w-[1px] bg-slate-200 shrink-0" />

          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-bold text-sm text-slate-900 tracking-tight">
                Diagnóstico Asistido por IA
              </span>
              <ConfidenceBadge
                categoria={categoria_confianza}
                confianza={confianza_global}
                size="sm"
              />
              <Badge
                variant={
                  isValidated ? 'success' : isRejected ? 'danger' : 'warning'
                }
                showDot
                size="sm"
              >
                {formatEstadoDiagnostico(estado)}
              </Badge>
            </div>
            <p className="text-[11px] font-mono text-slate-400 mt-0.5 truncate">
              Caso #{diagnosticoId?.slice(0, 8)} · Estudio #{estudio_id?.slice(0, 8)}
            </p>
          </div>
        </div>

        {/* Acciones principales de validación (solo si está pendiente) */}
        {isPendingReview && (
          <div className="flex items-center gap-2 w-full sm:w-auto shrink-0 pt-1 sm:pt-0 border-t sm:border-t-0 border-slate-100">
            <Button
              size="sm"
              variant="secondary"
              onClick={() => setIsRechazarOpen(true)}
              className="text-xs border-slate-300 text-rose-700 hover:bg-rose-50 flex-1 sm:flex-none"
              icon={XCircle}
            >
              Rechazar
            </Button>
            <Button
              size="sm"
              variant="primary"
              onClick={() => setIsValidarOpen(true)}
              className="text-xs bg-slate-900 text-white flex-1 sm:flex-none shadow-sm"
              icon={CheckCircle2}
            >
              Validar Diagnóstico
            </Button>
          </div>
        )}
      </div>

      {/* Grid principal: Visor Radiológico a la izquierda + Panel Clínico a la derecha */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-4 min-h-0 lg:overflow-hidden">
        {/* Lado izquierdo: Visor de Radiografía Intraoral con SVG overlay */}
        <div className="lg:col-span-8 bg-slate-950 rounded-xl border border-slate-300 flex flex-col overflow-hidden relative shadow-subtle min-h-[320px] sm:min-h-[420px] lg:h-full">
          {/* Controles del visor (Radiology contrast / overlay toggles) */}
          <div className="h-10 px-3 bg-slate-900/95 border-b border-slate-800 flex items-center justify-between text-xs text-slate-300 font-mono z-10 gap-2">
            <div className="flex items-center gap-2 truncate">
              <span className="text-[10px] text-slate-400 uppercase tracking-widest font-sans truncate">
                Visor Fotográfico
              </span>
              <span className="hidden sm:inline">·</span>
              <span className="hidden sm:inline text-[11px] text-slate-400 font-sans truncate">
                {visibleHallazgoIds.size} de {hallazgos.length} delimitaciones
              </span>
            </div>

            <div className="flex items-center gap-2 sm:gap-3 shrink-0">
              {/* Inversión de contraste */}
              <button
                type="button"
                onClick={() => setInvertContrast(!invertContrast)}
                className={`px-2 py-1 rounded text-xs transition-colors flex items-center gap-1 ${
                  invertContrast ? 'text-amber-400 bg-slate-800' : 'text-slate-400 hover:text-white'
                }`}
                title="Invertir colores para inspección de contraste"
              >
                <SunMedium className="w-3.5 h-3.5" />
                <span className="text-[10px]">Invertir</span>
              </button>

              {/* Toggle de todas las delimitaciones */}
              <button
                type="button"
                onClick={toggleAllVisibility}
                className="px-2 py-1 rounded text-xs text-slate-400 hover:text-white transition-colors flex items-center gap-1"
                title="Alternar todas las delimitaciones"
              >
                {visibleHallazgoIds.size > 0 ? (
                  <>
                    <Eye className="w-3.5 h-3.5" />
                    <span className="text-[10px]">Ocultar</span>
                  </>
                ) : (
                  <>
                    <EyeOff className="w-3.5 h-3.5" />
                    <span className="text-[10px]">Mostrar</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Área de imagen centrada con filtro de contraste e inversión */}
          <div
            className={`flex-1 flex items-center justify-center p-3 sm:p-4 overflow-auto bg-slate-950 min-h-[260px] ${
              invertContrast ? 'filter invert contrast-125' : ''
            }`}
          >
            <HallazgoBbox
              src={radiographySrc}
              alt="Fotografía Intraoral del Estudio"
              hallazgos={hallazgos}
              selectedHallazgoId={selectedHallazgoId}
              onSelectHallazgo={(h) => setSelectedHallazgoId(h.id)}
              visibleHallazgoIds={visibleHallazgoIds}
            />
          </div>
        </div>

        {/* Lado derecho: Panel clínico de hallazgos y dictamen */}
        <div className="lg:col-span-4 flex flex-col gap-4 overflow-y-auto min-h-0">
          {/* Tarjeta de estado de validación si ya fue procesado */}
          {isValidated && (
            <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-xs space-y-2 shadow-subtle">
              <div className="flex items-center gap-2 text-emerald-800 font-semibold">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>Validado Clínicamente</span>
              </div>
              <p className="text-emerald-900 font-mono text-[11px]">
                Validado el {formatDate(fecha_validacion, true)}
              </p>
              {notas_validacion && (
                <div className="pt-2 border-t border-emerald-200 text-emerald-950">
                  <span className="text-[10px] font-mono text-emerald-700 uppercase block">
                    Notas del Odontólogo:
                  </span>
                  <p className="italic mt-0.5 font-sans">"{notas_validacion}"</p>
                </div>
              )}
            </div>
          )}

          {isRejected && (
            <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs space-y-2 shadow-subtle">
              <div className="flex items-center gap-2 text-rose-800 font-semibold">
                <XCircle className="w-4 h-4 text-rose-600 shrink-0" />
                <span>Diagnóstico Rechazado</span>
              </div>
              {motivo_rechazo && (
                <div className="pt-2 border-t border-rose-200 text-rose-950">
                  <span className="text-[10px] font-mono text-rose-700 uppercase block">
                    Motivo Clínico:
                  </span>
                  <p className="italic mt-0.5 font-sans">"{motivo_rechazo}"</p>
                </div>
              )}
            </div>
          )}

          {/* Lista de Hallazgos con selección y toggle individual */}
          <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-subtle flex-1 flex flex-col">
            <h3 className="text-xs font-semibold text-slate-800 uppercase tracking-wider font-mono mb-3">
              Hallazgos Intraorales ({hallazgos.length})
            </h3>

            <div className="flex-1 overflow-y-auto">
              <HallazgosList
                hallazgos={hallazgos}
                selectedHallazgoId={selectedHallazgoId}
                onSelectHallazgo={(h) => setSelectedHallazgoId(h.id)}
                visibleHallazgoIds={visibleHallazgoIds}
                onToggleVisibility={toggleFindingVisibility}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Modal de Validación */}
      <Modal
        isOpen={isValidarOpen}
        onClose={() => {
          setIsValidarOpen(false);
          setMutationError(null);
        }}
        title="Validar Diagnóstico Clínico"
        subtitle="Confirmación clínica médica y emisión de dictamen"
      >
        {mutationError && (
          <div className="mb-3 p-3 bg-rose-50 border border-rose-200 rounded text-xs text-rose-700 font-sans">
            {mutationError}
          </div>
        )}
        <ValidarForm
          diagnostico={diagnostico}
          onValidar={handleValidarSubmit}
          isLoading={validarMutation.isPending}
          onCancel={() => {
            setIsValidarOpen(false);
            setMutationError(null);
          }}
        />
      </Modal>

      {/* Modal de Rechazo */}
      <Modal
        isOpen={isRechazarOpen}
        onClose={() => {
          setIsRechazarOpen(false);
          setMutationError(null);
        }}
        title="Rechazar Diagnóstico Sugerido"
        subtitle="Registro de desestimación clínica para calibración de IA"
      >
        {mutationError && (
          <div className="mb-3 p-3 bg-rose-50 border border-rose-200 rounded text-xs text-rose-700 font-mono">
            {mutationError}
          </div>
        )}
        <RechazarForm
          diagnostico={diagnostico}
          onRechazar={handleRechazarSubmit}
          isLoading={rechazarMutation.isPending}
          onCancel={() => {
            setIsRechazarOpen(false);
            setMutationError(null);
          }}
        />
      </Modal>
    </div>
  );
};
