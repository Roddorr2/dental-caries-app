import React, { useState, useEffect } from 'react';
import { Button } from '../../../shared/components/Button';
import { CheckCircle2, AlertCircle } from 'lucide-react';
import { diagnosticosApi } from '../../../api/diagnosticos.api';

export const ValidarForm = ({ diagnostico, onValidar, isLoading = false, onCancel = null }) => {
  const [odontologos, setOdontologos] = useState([]);
  const [selectedOdontologoId, setSelectedOdontologoId] = useState('');
  const [loadingOdontologos, setLoadingOdontologos] = useState(true);
  const [notas, setNotas] = useState('');
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
    if (!notas.trim()) {
      setError('Las notas clínicas de validación son obligatorias para el registro médico legal.');
      return;
    }
    if (!selectedOdontologoId) {
      setError('Debe seleccionar el odontólogo colegiado responsable de la firma.');
      return;
    }

    onValidar({
      odontologo_id: selectedOdontologoId,
      notas: notas.trim(),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Selector de Odontólogo Colegiado Responsable (RF-06) */}
      <div>
        <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1 font-mono">
          Odontólogo Responsable de la Firma *
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
            className="w-full h-10 px-3 text-base sm:text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-1 focus:ring-slate-900 font-sans"
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

      {/* Notas Clínicas */}
      <div>
        <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1 font-mono">
          Notas Clínicas de Validación *
        </label>
        <textarea
          value={notas}
          onChange={(e) => {
            setNotas(e.target.value);
            if (error) setError(null);
          }}
          rows={4}
          placeholder="Describa la corroboración clínica, plan de tratamiento recomendado o especificaciones diagnósticas..."
          className="w-full p-3 text-base sm:text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-1 focus:ring-slate-900 resize-none font-sans"
        />
        <p className="text-[11px] text-slate-400 mt-1 font-sans">
          Las notas quedarán registradas permanentemente en la historia clínica del paciente.
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
          variant="primary"
          type="submit"
          isLoading={isLoading}
          icon={CheckCircle2}
          className="w-full sm:w-auto"
        >
          Confirmar Validación Clínica
        </Button>
      </div>
    </form>
  );
};
