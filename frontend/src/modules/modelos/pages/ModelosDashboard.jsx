import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useModelosList, useModeloEstadisticas } from '../hooks/useModelos';
import { ModeloCard } from '../components/ModeloCard';
import { EstadisticasModelo } from '../components/EstadisticasModelo';
import { Loader } from '../../../shared/components/Loader';
import { Cpu, AlertCircle, RefreshCw, ArrowLeft, ShieldCheck } from 'lucide-react';

export const ModelosDashboard = () => {
  const navigate = useNavigate();
  const { data: modelos = [], isLoading, error, refetch } = useModelosList();
  const [selectedModeloId, setSelectedModeloId] = useState(null);

  useEffect(() => {
    if (modelos.length > 0 && !selectedModeloId) {
      // Priorizar modelo en producción
      const prod = modelos.find((m) => m.aprobado_produccion) || modelos[0];
      setSelectedModeloId(prod.id);
    }
  }, [modelos, selectedModeloId]);

  const {
    data: estadisticas,
    isLoading: isLoadingStats,
    refetch: refetchStats,
  } = useModeloEstadisticas(selectedModeloId);

  if (isLoading) {
    return <Loader size="lg" message="Cargando modelos y registros de evaluación..." className="py-24" />;
  }

  const selectedModelo = modelos.find((m) => m.id === selectedModeloId);

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Botón de retorno a la estación clínica */}
      <button
        type="button"
        onClick={() => navigate('/revision')}
        className="inline-flex items-center gap-1.5 text-xs font-mono text-slate-500 hover:text-slate-900 transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Volver a Estación Clínica</span>
      </button>

      {/* Cabecera del Panel de Auditoría Técnica */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white border border-slate-200 rounded-xl p-5 shadow-subtle">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-lg bg-slate-900 text-white flex items-center justify-center shrink-0 shadow-sm mt-0.5">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base sm:text-lg font-bold text-slate-900 tracking-tight">
                Auditoría Técnica del Motor CDSS & Gobernanza
              </h2>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-semibold border border-slate-200">
                SaMD / MLOps
              </span>
            </div>
            <p className="text-xs text-slate-500 font-sans mt-0.5">
              Supervisión de métricas de generalización, umbrales operativos y validación en producción para tesis y aseguramiento de calidad
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={() => {
            refetch();
            if (selectedModeloId) refetchStats();
          }}
          className="inline-flex items-center justify-center gap-2 px-3.5 py-2 rounded-lg border border-slate-300 bg-white text-xs font-mono text-slate-700 hover:bg-slate-50 active:bg-slate-100 transition-colors w-full sm:w-auto shadow-sm"
        >
          <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
          <span>Actualizar Métricas</span>
        </button>
      </div>


      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 rounded text-xs text-rose-800 flex items-center gap-2 font-mono">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
          <span>Error al consultar modelos: {error.message}</span>
        </div>
      )}

      {/* Grid de Modelos Registrados */}
      <div className="space-y-3">
        <h3 className="text-xs font-semibold text-slate-700 uppercase tracking-wider font-mono">
          Modelos Registrados ({modelos.length})
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {modelos.map((m) => (
            <ModeloCard
              key={m.id}
              modelo={m}
              isSelected={selectedModeloId === m.id}
              onSelect={(mod) => setSelectedModeloId(mod.id)}
            />
          ))}
        </div>
      </div>

      {/* Estadísticas de Producción del Modelo Seleccionado */}
      <div className="space-y-3 pt-2">
        <h3 className="text-xs font-semibold text-slate-700 uppercase tracking-wider font-mono">
          Validación en Producción — {selectedModelo?.nombre || 'Seleccione un modelo'}
        </h3>

        {isLoadingStats ? (
          <Loader size="md" message="Consultando métricas clínicas de producción..." className="py-12 bg-white rounded-lg border border-slate-200" />
        ) : (
          <EstadisticasModelo estadisticas={estadisticas} />
        )}
      </div>
    </div>
  );
};
