import React, { useState, useEffect } from 'react';
import { Button } from '../../../shared/components/Button';
import { XCircle, AlertCircle } from 'lucide-react';
import { diagnosticosApi } from '../../../api/diagnosticos.api';

export const RechazarForm = ({ diagnostico, onRechazar, isLoading = false, onCancel = null }) => {
  const [odontologos, setOdontologos] = useState([]);
  const [selectedOdontologoId, setSelectedOdontologoId] = useState('');
  const [loadingOdontologos, setLoadingOdontologos] = useState(true);
  const [motivo, setMotivo] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    diagnosticosApi.obtenerOdontologosAutorizados()
      .then((res) => {
        if (!isMounted) return;
        const data = res?.data || [];
        setOdontologos(data);
        if (data.length > 0) {
          setSelectedOdontologoId(data[0].id);
        }
      })
      .catch((err) => {
        console.error('Error al cargar odontólogos autorizados:', err);
      })
      .finally(() => {
        if (isMounted) setLoadingOdontologos(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!motivo.trim()) {
      setError('Debe especificar el motivo clínico para rechazar la sugerencia de la IA.');
      return;
    }
    if (!selectedOdontologoId) {
      setError('Debe seleccionar el odontólogo colegiado que rechaza el diagnóstico.');
      return;
    }

    onRechazar({
      odontologo_id: selectedOdontologoId,
      motivo: motivo.trim(),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Selector de Odontólogo Colegiado Revisor (RF-06) */}
      <div>
        <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1 font-mono">
          Odontólogo Responsable del Rechazo *
        </label>
        {loadingOdontologos ? (
          <div className="p-2.5 text-xs text-slate-400 border border-slate-200 rounded bg-slate-50 font-mono">
            Cargando profesionales habilitados...
          </div>
        ) : (
          <select
            value={selectedOdontologoId}
            onChange={(e) => {
              setSelectedOdontologoId(e.target.value);
              if (error) setError(null);
            }}
            className="w-full h-10 px-3 text-base sm:text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-1 focus:ring-rose-500 font-sans"
          >
            {odontologos.length === 0 ? (
              <option value="">No hay odontólogos registrados con habilitación</option>
            ) : (
              odontologos.map((od) => (
                <option key={od.id} value={od.id}>
                  {od.nombre_completo || `${od.nombres} ${od.apellidos}`} — {od.numero_colegiatura}
                </option>
              ))
            )}
          </select>
        )}
        <p className="text-[11px] text-slate-400 mt-1 font-sans">
          Firma colegiada registrada en auditoría clínica según normativa de salud (RF-06).
        </p>
      </div>

      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-800 flex items-center gap-2 font-mono">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Motivo de rechazo */}
      <div>
        <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1 font-mono">
          Motivo Clínico del Rechazo *
        </label>
        <textarea
          value={motivo}
          onChange={(e) => {
            setMotivo(e.target.value);
            if (error) setError(null);
          }}
          rows={4}
          placeholder="Ej: Falso positivo por reflejo o saliva; sin evidencia de desmineralización clínica..."
          className="w-full p-3 text-base sm:text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-1 focus:ring-rose-500 resize-none font-sans"
        />
        <p className="text-[11px] text-slate-400 mt-1 font-sans">
          Este feedback se registrará para la re-evaluación y métricas de desempeño del modelo.
        </p>
      </div>

      {/* Acciones */}
      <div className="pt-3 border-t border-slate-200 flex flex-col-reverse sm:flex-row sm:items-center sm:justify-end gap-2.5">
        {onCancel && (
          <Button variant="secondary" onClick={onCancel} type="button" className="w-full sm:w-auto">
            Cancelar
          </Button>
        )}
        <Button
          variant="danger"
          type="submit"
          isLoading={isLoading}
          icon={XCircle}
          className="w-full sm:w-auto"
        >
          Rechazar Diagnóstico
        </Button>
      </div>
    </form>
  );
};
