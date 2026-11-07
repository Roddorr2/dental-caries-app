import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useCrearEstudio } from '../hooks/useEstudios';
import { usePacientesList } from '../../pacientes/hooks/usePacientes';
import { Button } from '../../../shared/components/Button';
import { TIPO_EXAMEN, TIPO_EXAMEN_LABELS } from '../constants';
import { ArrowLeft, AlertCircle, FolderPlus } from 'lucide-react';

export const CrearEstudio = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const preselectedPacienteId = searchParams.get('paciente_id') || '';

  const { data: pacientes = [], isLoading: isLoadingPacientes } = usePacientesList({ limit: 100 });
  const crearEstudioMutation = useCrearEstudio();

  const [formData, setFormData] = useState({
    paciente_id: preselectedPacienteId,
    tipo_examen: TIPO_EXAMEN.FOTOGRAFIA_INTRAORAL,
    region_examinada: '',
    observaciones: '',
  });

  const [error, setError] = useState(null);

  useEffect(() => {
    if (preselectedPacienteId && !formData.paciente_id) {
      setFormData((prev) => ({ ...prev, paciente_id: preselectedPacienteId }));
    }
  }, [preselectedPacienteId, formData.paciente_id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (error) setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.paciente_id) {
      setError('Debe seleccionar un paciente para vincular el estudio imagenológico.');
      return;
    }

    try {
      const response = await crearEstudioMutation.mutateAsync({
        paciente_id: formData.paciente_id,
        tipo_examen: formData.tipo_examen,
        region_examinada: formData.region_examinada || null,
        observaciones: formData.observaciones || null,
      });

      const estudioId = response?.id || response;
      navigate(`/estudios/${estudioId}/subir-imagen`);
    } catch (err) {
      setError(err.message || 'Error al crear el estudio.');
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <button
        type="button"
        onClick={() => navigate(-1)}
        className="inline-flex items-center gap-1.5 text-xs font-mono text-slate-500 hover:text-slate-900 transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Volver</span>
      </button>

      <div className="bg-white border border-slate-200 rounded-xl p-4 sm:p-6 shadow-subtle space-y-5">
        <div className="border-b border-slate-100 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-700 shadow-inner">
              <FolderPlus className="w-5 h-5 text-slate-700" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 tracking-tight">
                Crear Nuevo Estudio Imagenológico
              </h2>
              <p className="text-xs text-slate-500 font-sans mt-0.5">
                Paso 1: Parámetros del estudio fotográfico intraoral
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-800 flex items-center gap-2 font-sans">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Selección de Paciente */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1 font-mono">
              Paciente Clínico *
            </label>
            <select
              name="paciente_id"
              value={formData.paciente_id}
              onChange={handleChange}
              disabled={isLoadingPacientes}
              className="w-full h-10 px-3 text-base sm:text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-1 focus:ring-slate-900"
            >
              <option value="">-- Seleccionar paciente activo --</option>
              {pacientes.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.apellidos}, {p.nombres} — DNI: {p.dni}
                </option>
              ))}
            </select>
          </div>

          {/* Tipo de Examen */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1 font-mono">
              Tipo de Examen Fotográfico *
            </label>
            <select
              name="tipo_examen"
              value={formData.tipo_examen}
              onChange={handleChange}
              className="w-full h-10 px-3 text-base sm:text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-1 focus:ring-slate-900"
            >
              {Object.keys(TIPO_EXAMEN).map((tipo) => (
                <option key={tipo} value={tipo}>
                  {TIPO_EXAMEN_LABELS[tipo] || tipo}
                </option>
              ))}
            </select>
          </div>

          {/* Región examinada */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1 font-mono">
              Región Examinada (opcional)
            </label>
            <input
              type="text"
              name="region_examinada"
              value={formData.region_examinada}
              onChange={handleChange}
              placeholder="Ej: Zona Molar Inferior Izquierda, Pieza 36 y 37"
              className="w-full h-10 px-3 text-base sm:text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-1 focus:ring-slate-900"
            />
          </div>

          {/* Observaciones clínicas */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1 font-mono">
              Observaciones Clínicas (opcional)
            </label>
            <textarea
              name="observaciones"
              value={formData.observaciones}
              onChange={handleChange}
              rows={3}
              placeholder="Indicaciones preliminares del odontólogo remitente..."
              className="w-full p-3 text-base sm:text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-1 focus:ring-slate-900 resize-none font-sans"
            />
          </div>

          {/* Acciones */}
          <div className="pt-4 border-t border-slate-200 flex flex-col-reverse sm:flex-row sm:items-center sm:justify-end gap-2.5">
            <Button variant="secondary" onClick={() => navigate(-1)} type="button" className="w-full sm:w-auto">
              Cancelar
            </Button>
            <Button
              variant="primary"
              type="submit"
              isLoading={crearEstudioMutation.isPending}
              className="w-full sm:w-auto shadow-sm"
            >
              Continuar a Carga de Fotografías
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
