import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useEstudiosList } from '../hooks/useEstudios';
import { Button } from '../../../shared/components/Button';
import { Badge } from '../../../shared/components/Badge';
import { Loader } from '../../../shared/components/Loader';
import { formatDate, formatEstadoPipeline } from '../../../utils/formatters';
import { TIPO_EXAMEN_LABELS } from '../constants';
import {
  FolderOpen,
  Plus,
  Search,
  Camera,
  ArrowRight,
  FileText,
  User,
} from 'lucide-react';

export const EstudiosList = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEstado, setSelectedEstado] = useState('TODOS');

  const { data: estudios = [], isLoading, error } = useEstudiosList();

  const filteredEstudios = useMemo(() => {
    return estudios.filter((e) => {
      // Filtro de estado
      if (selectedEstado !== 'TODOS' && e.estado_procesamiento !== selectedEstado) {
        return false;
      }
      // Filtro de búsqueda
      if (!searchTerm) return true;
      const term = searchTerm.toLowerCase();
      const paciente = (e.paciente_nombre || '').toLowerCase();
      const dni = (e.paciente_dni || '').toLowerCase();
      const tipo = (TIPO_EXAMEN_LABELS[e.tipo_examen] || e.tipo_examen || '').toLowerCase();
      return paciente.includes(term) || dni.includes(term) || tipo.includes(term);
    });
  }, [estudios, selectedEstado, searchTerm]);

  const estadoBadgeVariant = (estado) => {
    switch (estado) {
      case 'PROCESADO':
        return 'success';
      case 'EN_ANALISIS':
        return 'warning';
      default:
        return 'neutral';
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Cabecera Clínica */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white border border-slate-200 rounded-xl p-5 shadow-subtle">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-slate-900 text-white flex items-center justify-center shrink-0 shadow-sm">
            <Camera className="w-5 h-5 text-slate-100" />
          </div>
          <div>
            <h2 className="text-base sm:text-lg font-bold text-slate-900 tracking-tight">
              Estudios Fotográficos Intraorales
            </h2>
            <p className="text-xs text-slate-500 font-sans">
              Historial de adquisiciones fotográficas e informes para apoyo al diagnóstico clínico
            </p>
          </div>
        </div>

        <Button
          variant="primary"
          icon={Plus}
          onClick={() => navigate('/estudios/nuevo')}
          className="shadow-sm self-start sm:self-auto"
        >
          Nuevo Estudio
        </Button>
      </div>

      {/* Controles de Búsqueda y Filtros */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-subtle flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        {/* Input de Búsqueda */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Buscar por paciente, DNI o tipo de estudio..."
            className="w-full pl-9 pr-3 py-2 text-xs border border-slate-300 rounded-lg bg-slate-50/50 focus:bg-white focus:outline-none focus:ring-1 focus:ring-slate-900 font-sans transition-colors"
          />
        </div>

        {/* Pestañas de Estado */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
          {[
            { id: 'TODOS', label: 'Todos' },
            { id: 'PROCESADO', label: 'Procesados' },
            { id: 'EN_ANALISIS', label: 'En Análisis' },
            { id: 'PENDIENTE', label: 'Pendientes' },
          ].map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setSelectedEstado(tab.id)}
              className={`px-3 py-1.5 text-xs rounded-lg font-medium whitespace-nowrap transition-colors ${
                selectedEstado === tab.id
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-slate-900'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Listado de Estudios */}
      {isLoading ? (
        <Loader size="lg" message="Cargando repositorio de estudios intraorales..." className="py-20" />
      ) : error ? (
        <div className="p-8 text-center bg-white border border-rose-200 rounded-xl space-y-2">
          <p className="text-sm font-semibold text-rose-800">Error al cargar estudios</p>
          <p className="text-xs text-slate-500 font-sans">{error?.message || 'Error de conexión con el servidor.'}</p>
        </div>
      ) : filteredEstudios.length === 0 ? (
        <div className="p-12 text-center bg-white border border-slate-200 rounded-xl space-y-3 shadow-subtle">
          <FolderOpen className="w-10 h-10 text-slate-300 mx-auto" />
          <h3 className="text-sm font-semibold text-slate-800">No se encontraron estudios</h3>
          <p className="text-xs text-slate-500 font-sans max-w-sm mx-auto">
            {searchTerm || selectedEstado !== 'TODOS'
              ? 'No hay registros que coincidan con los criterios de filtro aplicados.'
              : 'Aún no se han registrado estudios fotográficos en la clínica.'}
          </p>
          {!searchTerm && selectedEstado === 'TODOS' && (
            <Button
              variant="outline"
              size="sm"
              icon={Plus}
              onClick={() => navigate('/estudios/nuevo')}
              className="mt-2"
            >
              Iniciar Primer Estudio
            </Button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredEstudios.map((estudio) => {
            const isProcesado = estudio.estado_procesamiento === 'PROCESADO';

            return (
              <div
                key={estudio.id}
                className="bg-white border border-slate-200 rounded-xl p-4 shadow-subtle hover:shadow-md hover:border-slate-300 transition-all flex flex-col justify-between space-y-3.5"
              >
                {/* Header de la tarjeta */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-[11px] font-mono font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200/60 shrink-0">
                      #{estudio.id.slice(0, 8)}
                    </span>
                    <Badge
                      variant={estadoBadgeVariant(estudio.estado_procesamiento)}
                      size="sm"
                      showDot
                      className="shrink-0"
                    >
                      {formatEstadoPipeline(estudio.estado_procesamiento)}
                    </Badge>
                  </div>

                  <div>
                    <h3 className="text-sm font-bold text-slate-900 tracking-tight leading-snug line-clamp-1">
                      {TIPO_EXAMEN_LABELS[estudio.tipo_examen] || estudio.tipo_examen}
                    </h3>
                    <p className="text-[11px] text-slate-500 font-mono mt-0.5">
                      {formatDate(estudio.created_at, true)}
                    </p>
                  </div>
                </div>

                {/* Metadatos clínicos: Paciente e imágenes */}
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/60 space-y-2 text-xs">
                  <div className="flex items-center gap-1.5 text-slate-800 font-medium truncate">
                    <User className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <span className="truncate">{estudio.paciente_nombre || 'Paciente no identificado'}</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono pt-1.5 border-t border-slate-200/50">
                    <span>DNI: {estudio.paciente_dni || 'N/D'}</span>
                    <span className="inline-flex items-center gap-1 font-sans text-slate-600">
                      <Camera className="w-3.5 h-3.5 text-slate-400" />
                      <span>{estudio.total_imagenes} {estudio.total_imagenes === 1 ? 'foto' : 'fotos'}</span>
                    </span>
                  </div>
                </div>

                {/* Acciones clínicas */}
                <div className="pt-1 flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => navigate(`/estudios/${estudio.id}`)}
                    className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition-colors shadow-2xs"
                  >
                    <span>Ver Estudio</span>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
                  </button>

                  {isProcesado && estudio.diagnostico_id && (
                    <button
                      type="button"
                      onClick={() => navigate(`/diagnosticos/${estudio.diagnostico_id}`)}
                      className="inline-flex items-center justify-center gap-1.5 px-3.5 py-2 text-xs font-semibold rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 transition-colors shadow-2xs shrink-0"
                      title="Ver Informe CDSS"
                    >
                      <FileText className="w-3.5 h-3.5 text-white/90" />
                      <span>Informe</span>
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
