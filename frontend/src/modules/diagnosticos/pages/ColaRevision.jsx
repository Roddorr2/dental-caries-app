import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useColaRevision } from '../hooks/useColaRevision';
import { DiagnosticoCard } from '../components/DiagnosticoCard';
import { EmptyState } from '../../../shared/components/EmptyState';
import { ConfidenceBadge } from '../components/ConfidenceBadge';
import { Badge } from '../../../shared/components/Badge';
import { Table } from '../../../shared/components/Table';
import { Button } from '../../../shared/components/Button';
import { usePagination } from '../../../shared/hooks/usePagination';
import { formatDate } from '../../../utils/formatters';
import { Activity, AlertOctagon, RefreshCw, CheckCircle, ArrowRight } from 'lucide-react';

export const ColaRevision = () => {
  const navigate = useNavigate();
  const [soloSegundaOpinion, setSoloSegundaOpinion] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const { page, setPage, pageSize, limit, offset } = usePagination(1, 20);

  const {
    data: items = [],
    isLoading,
    isRefetching,
    refetch,
    error,
  } = useColaRevision({
    soloSegundaOpinion,
    limit,
    offset,
    autoRefresh,
  });

  const columns = [
    {
      header: 'Confianza del Modelo',
      accessor: 'categoria_confianza',
      className: 'w-48',
      render: (item) => (
        <div className="flex items-center gap-2">
          <ConfidenceBadge
            categoria={item.categoria_confianza}
            confianza={item.confianza_global}
            size="sm"
          />
        </div>
      ),
    },
    {
      header: 'Paciente',
      accessor: 'paciente_nombre',
      render: (item) => (
        <div>
          <span className="font-semibold text-slate-900 block">
            {item.paciente_nombre || 'Paciente sin nombre'}
          </span>
          <span className="font-mono text-[11px] text-slate-400">
            H.C. #{item.paciente_id?.slice(0, 8)}
          </span>
        </div>
      ),
    },
    {
      header: 'Estudio Clínico',
      accessor: 'tipo_examen',
      render: (item) => (
        <span className="font-medium text-slate-700 text-xs">
          {item.tipo_examen}
        </span>
      ),
    },
    {
      header: 'Fecha de Análisis',
      accessor: 'fecha_generacion',
      className: 'w-40 text-xs text-slate-500 font-sans',
      render: (item) => formatDate(item.fecha_generacion, true),
    },
    {
      header: 'Condición Clínica',
      accessor: 'segunda_opinion',
      className: 'w-44 text-center',
      render: (item) =>
        item.segunda_opinion ? (
          <Badge variant="danger" showDot size="sm">
            2da Opinión
          </Badge>
        ) : (
          <Badge variant="warning" showDot size="sm">
            Pendiente
          </Badge>
        ),
    },
    {
      header: '',
      key: 'actions',
      className: 'w-24 text-right',
      render: (item) => (
        <Button
          size="sm"
          variant="primary"
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/diagnosticos/${item.diagnostico_id}`);
          }}
          className="text-xs h-7 px-2.5"
        >
          Revisar
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-5">
      {/* Cabecera de la Cola de Revisión */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Activity className="w-5 h-5 text-slate-700" />
            <span>Cola de Revisión Diagnóstica</span>
          </h2>
          <p className="text-xs text-slate-500 font-mono mt-0.5">
            Diagnósticos asistidos pendientes de validación médica colegiada
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Botón de recarga manual */}
          <button
            type="button"
            onClick={() => refetch()}
            disabled={isRefetching}
            className="p-1.5 rounded border border-slate-300 bg-white text-slate-600 hover:bg-slate-50 disabled:opacity-50"
            title="Actualizar cola"
            aria-label="Actualizar cola de revisión"
          >
            <RefreshCw className={`w-4 h-4 ${isRefetching ? 'animate-spin' : ''}`} />
          </button>

          {/* Toggle de Auto-refresh */}
          <label className="inline-flex items-center gap-2 text-xs font-mono text-slate-600 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-slate-300 text-slate-900 focus:ring-slate-900 h-3.5 w-3.5"
            />
            <span>Auto-actualizar (5s)</span>
          </label>
        </div>
      </div>

      {/* Barra de filtros clínicos */}
      <div className="bg-white p-3 sm:p-3.5 border border-slate-200 rounded-xl shadow-subtle flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => {
              setSoloSegundaOpinion(false);
              setPage(1);
            }}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              !soloSegundaOpinion
                ? 'bg-slate-900 text-white shadow-sm'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Todos los Pendientes
          </button>

          <button
            type="button"
            onClick={() => {
              setSoloSegundaOpinion(true);
              setPage(1);
            }}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold inline-flex items-center gap-1.5 transition-colors ${
              soloSegundaOpinion
                ? 'bg-rose-600 text-white shadow-sm'
                : 'bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200'
            }`}
          >
            <AlertOctagon className="w-3.5 h-3.5" />
            <span>Segunda Opinión Requerida</span>
          </button>
        </div>

        <span className="font-mono text-xs text-slate-500">
          Mostrando {items.length} casos en espera
        </span>
      </div>

      {/* Vista Desktop: Tabla clínica de pendientes */}
      <div className="hidden md:block">
        <Table
          columns={columns}
          data={items}
          isLoading={isLoading}
          emptyMessage="Cola de revisión vacía"
          emptyDescription={
            soloSegundaOpinion
              ? 'No existen casos de confianza baja que requieran segunda opinión.'
              : 'Todos los diagnósticos sugeridos por la IA han sido revisados y validados.'
          }
          onRowClick={(item) => navigate(`/diagnosticos/${item.diagnostico_id}`)}
        />
      </div>

      {/* Vista Mobile (< md): Lista de tarjetas táctiles de diagnóstico */}
      <div className="md:hidden space-y-3">
        {isLoading ? (
          <div className="bg-white border border-slate-200 rounded-xl p-8 text-center text-xs text-slate-500 font-sans shadow-subtle">
            Cargando cola de revisión...
          </div>
        ) : items.length === 0 ? (
          <EmptyState
            title="Cola de revisión vacía"
            description={
              soloSegundaOpinion
                ? 'No existen casos de confianza baja que requieran segunda opinión.'
                : 'Todos los diagnósticos sugeridos por la IA han sido revisados y validados.'
            }
          />
        ) : (
          <div className="space-y-2.5">
            {items.map((item) => (
              <DiagnosticoCard
                key={item.diagnostico_id}
                diagnostico={item}
                onSelect={(d) => navigate(`/diagnosticos/${d.diagnostico_id || d.id}`)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
