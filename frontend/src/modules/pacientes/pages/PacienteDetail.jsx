import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePacienteDetail } from '../hooks/usePacientes';
import { Button } from '../../../shared/components/Button';
import { Badge } from '../../../shared/components/Badge';
import { Loader } from '../../../shared/components/Loader';
import { formatDate } from '../../../utils/formatters';
import { SEXO_LABELS } from '../constants';
import {
  ArrowLeft,
  User,
  CreditCard,
  Calendar,
  Phone,
  Mail,
  FolderPlus,
  Activity,
  AlertCircle,
} from 'lucide-react';

export const PacienteDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: paciente, isLoading, error } = usePacienteDetail(id);

  if (isLoading) {
    return <Loader size="lg" message="Cargando expediente del paciente..." className="py-20" />;
  }

  if (error || !paciente) {
    return (
      <div className="p-6 bg-white border border-rose-200 rounded-lg text-center space-y-4">
        <AlertCircle className="w-8 h-8 text-rose-600 mx-auto" />
        <h3 className="text-base font-semibold text-slate-900">
          No se encontró el paciente solicitado
        </h3>
        <p className="text-xs text-slate-500 font-mono">
          {error?.message || 'El identificador de paciente no existe en el sistema.'}
        </p>
        <Button variant="secondary" onClick={() => navigate('/pacientes')}>
          Volver a Pacientes
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-5 max-w-5xl mx-auto min-w-0">
      {/* Barra superior de navegación responsiva */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <button
          type="button"
          onClick={() => navigate('/pacientes')}
          className="inline-flex items-center gap-2 text-xs font-mono text-slate-600 hover:text-slate-900 transition-colors py-1 self-start"
        >
          <ArrowLeft className="w-4 h-4 text-slate-500" />
          <span>Volver al listado de pacientes</span>
        </button>

        <Button
          variant="primary"
          icon={FolderPlus}
          onClick={() => navigate(`/estudios/nuevo?paciente_id=${paciente.id}`)}
          className="w-full sm:w-auto shadow-sm"
        >
          <span className="sm:hidden">Nuevo Estudio</span>
          <span className="hidden sm:inline">Nuevo Estudio para este Paciente</span>
        </Button>
      </div>

      {/* Tarjeta de Ficha Clínica */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 sm:p-6 shadow-subtle min-w-0">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pb-5 border-b border-slate-100">
          <div className="flex items-start gap-3.5 sm:gap-4 min-w-0">
            <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-700 font-bold text-lg shrink-0 shadow-inner">
              <User className="w-6 h-6 sm:w-7 sm:h-7 text-slate-600" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="text-lg sm:text-xl font-bold text-slate-900 tracking-tight break-words">
                  {paciente.apellidos}, {paciente.nombres}
                </h2>
                <Badge
                  variant={paciente.estado === 'ACTIVO' ? 'success' : 'neutral'}
                  showDot
                  size="sm"
                  className="shrink-0"
                >
                  {paciente.estado}
                </Badge>
              </div>
              <p className="font-mono text-xs text-slate-500 mt-1.5 flex flex-wrap items-center gap-x-2 gap-y-1">
                <span className="font-semibold text-slate-700">DNI: {paciente.dni}</span>
                <span className="text-slate-300">·</span>
                <span>H.C. #{paciente.id?.slice(0, 8)}</span>
              </p>
            </div>
          </div>
        </div>

        {/* Datos demográficos y clínicos en cards legibles para móvil */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 pt-5 text-xs">
          <div className="p-3 rounded-lg bg-slate-50/80 border border-slate-100">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block font-mono">
              Fecha de Nacimiento
            </span>
            <span className="font-mono text-slate-800 text-sm font-medium mt-1 block">
              {formatDate(paciente.fecha_nacimiento)}
            </span>
          </div>

          <div className="p-3 rounded-lg bg-slate-50/80 border border-slate-100">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block font-mono">
              Sexo Biológico
            </span>
            <span className="text-slate-800 text-sm font-medium mt-1 block">
              {SEXO_LABELS[paciente.sexo] || paciente.sexo}
            </span>
          </div>

          <div className="p-3 rounded-lg bg-slate-50/80 border border-slate-100">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block font-mono">
              Teléfono de Contacto
            </span>
            <span className="font-mono text-slate-800 text-sm font-medium mt-1 block truncate">
              {paciente.telefono || '—'}
            </span>
          </div>

          <div className="p-3 rounded-lg bg-slate-50/80 border border-slate-100">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block font-mono">
              Correo Electrónico
            </span>
            <span className="text-slate-800 text-sm font-medium mt-1 block truncate" title={paciente.email}>
              {paciente.email || '—'}
            </span>
          </div>
        </div>
      </div>

      {/* Historial de Estudios / Acciones Rápidas */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 sm:p-6 shadow-subtle min-w-0">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
          <div>
            <h3 className="text-sm font-bold text-slate-900 tracking-tight">
              Flujo Imagenológico y Diagnósticos
            </h3>
            <p className="text-xs text-slate-500 font-sans mt-0.5">
              Estudios fotográficos y análisis asistidos asociados
            </p>
          </div>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => navigate(`/estudios/nuevo?paciente_id=${paciente.id}`)}
            className="w-full sm:w-auto"
          >
            Registrar Estudio Fotográfico
          </Button>
        </div>

        <div className="py-10 text-center text-xs text-slate-500 px-4">
          <div className="w-12 h-12 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center mx-auto mb-3 text-slate-400">
            <Activity className="w-6 h-6 stroke-[1.5]" />
          </div>
          <p className="max-w-md mx-auto text-slate-600">
            Para analizar fotografías intraorales de este paciente, proceda a registrar un nuevo estudio o verifique los existentes.
          </p>
        </div>
      </div>
    </div>
  );
};
