import React, { useState } from 'react';
import { Button } from '../../../shared/components/Button';
import { AlertCircle } from 'lucide-react';

export const PacienteForm = ({ onSubmit, isLoading = false, onCancel = null }) => {
  const [formData, setFormData] = useState({
    dni: '',
    nombres: '',
    apellidos: '',
    fecha_nacimiento: '',
    sexo: 'M',
    telefono: '',
    email: '',
  });

  const [errors, setErrors] = useState({});

  const validate = () => {
    const newErrors = {};
    if (!/^\d{8}$/.test(formData.dni.trim())) {
      newErrors.dni = 'El DNI debe tener exactamente 8 dígitos numéricos.';
    }
    if (!formData.nombres.trim()) {
      newErrors.nombres = 'El nombre es obligatorio.';
    }
    if (!formData.apellidos.trim()) {
      newErrors.apellidos = 'Los apellidos son obligatorios.';
    }
    if (!formData.fecha_nacimiento) {
      newErrors.fecha_nacimiento = 'La fecha de nacimiento es requerida.';
    }
    if (!formData.telefono.trim()) {
      newErrors.telefono = 'El teléfono de contacto es obligatorio.';
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email.trim())) {
      newErrors.email = 'Ingrese un correo electrónico válido.';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 sm:gap-4">
        {/* DNI */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
            DNI (8 dígitos) *
          </label>
          <input
            type="text"
            name="dni"
            value={formData.dni}
            onChange={handleChange}
            maxLength={8}
            placeholder="72849102"
            className={`w-full h-10 px-3 text-base sm:text-sm font-mono border rounded-lg focus:outline-none focus:ring-1 ${
              errors.dni
                ? 'border-rose-400 focus:ring-rose-500 bg-rose-50/30'
                : 'border-slate-300 focus:ring-slate-900 bg-white'
            }`}
          />
          {errors.dni && (
            <p className="mt-1 text-xs text-rose-600 flex items-center gap-1 font-mono">
              <AlertCircle className="w-3 h-3 shrink-0" /> {errors.dni}
            </p>
          )}
        </div>

        {/* Sexo Biológico */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
            Sexo Biológico *
          </label>
          <select
            name="sexo"
            value={formData.sexo}
            onChange={handleChange}
            className="w-full h-10 px-3 text-base sm:text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-slate-900 bg-white"
          >
            <option value="M">Masculino</option>
            <option value="F">Femenino</option>
            <option value="OTRO">Otro</option>
          </select>
        </div>

        {/* Nombres */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
            Nombres *
          </label>
          <input
            type="text"
            name="nombres"
            value={formData.nombres}
            onChange={handleChange}
            placeholder="Juan Alberto"
            className={`w-full h-10 px-3 text-base sm:text-sm border rounded-lg focus:outline-none focus:ring-1 ${
              errors.nombres
                ? 'border-rose-400 focus:ring-rose-500 bg-rose-50/30'
                : 'border-slate-300 focus:ring-slate-900 bg-white'
            }`}
          />
          {errors.nombres && (
            <p className="mt-1 text-xs text-rose-600 flex items-center gap-1">
              <AlertCircle className="w-3 h-3 shrink-0" /> {errors.nombres}
            </p>
          )}
        </div>

        {/* Apellidos */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
            Apellidos *
          </label>
          <input
            type="text"
            name="apellidos"
            value={formData.apellidos}
            onChange={handleChange}
            placeholder="Pérez Vargas"
            className={`w-full h-10 px-3 text-base sm:text-sm border rounded-lg focus:outline-none focus:ring-1 ${
              errors.apellidos
                ? 'border-rose-400 focus:ring-rose-500 bg-rose-50/30'
                : 'border-slate-300 focus:ring-slate-900 bg-white'
            }`}
          />
          {errors.apellidos && (
            <p className="mt-1 text-xs text-rose-600 flex items-center gap-1">
              <AlertCircle className="w-3 h-3 shrink-0" /> {errors.apellidos}
            </p>
          )}
        </div>

        {/* Fecha de Nacimiento */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
            Fecha de Nacimiento *
          </label>
          <input
            type="date"
            name="fecha_nacimiento"
            value={formData.fecha_nacimiento}
            onChange={handleChange}
            max={new Date().toISOString().split('T')[0]}
            className={`w-full h-10 px-3 text-base sm:text-sm font-mono border rounded-lg focus:outline-none focus:ring-1 ${
              errors.fecha_nacimiento
                ? 'border-rose-400 focus:ring-rose-500 bg-rose-50/30'
                : 'border-slate-300 focus:ring-slate-900 bg-white'
            }`}
          />
          {errors.fecha_nacimiento && (
            <p className="mt-1 text-xs text-rose-600 flex items-center gap-1">
              <AlertCircle className="w-3 h-3 shrink-0" /> {errors.fecha_nacimiento}
            </p>
          )}
        </div>

        {/* Teléfono */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
            Teléfono de Contacto *
          </label>
          <input
            type="tel"
            name="telefono"
            value={formData.telefono}
            onChange={handleChange}
            placeholder="987654321"
            className={`w-full h-10 px-3 text-base sm:text-sm font-mono border rounded-lg focus:outline-none focus:ring-1 ${
              errors.telefono
                ? 'border-rose-400 focus:ring-rose-500 bg-rose-50/30'
                : 'border-slate-300 focus:ring-slate-900 bg-white'
            }`}
          />
          {errors.telefono && (
            <p className="mt-1 text-xs text-rose-600 flex items-center gap-1">
              <AlertCircle className="w-3 h-3 shrink-0" /> {errors.telefono}
            </p>
          )}
        </div>
      </div>

      {/* Correo Electrónico */}
      <div>
        <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
          Correo Electrónico *
        </label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          placeholder="paciente@correo.pe"
          className={`w-full h-10 px-3 text-base sm:text-sm border rounded-lg focus:outline-none focus:ring-1 ${
            errors.email
              ? 'border-rose-400 focus:ring-rose-500 bg-rose-50/30'
              : 'border-slate-300 focus:ring-slate-900 bg-white'
          }`}
        />
        {errors.email && (
          <p className="mt-1 text-xs text-rose-600 flex items-center gap-1">
            <AlertCircle className="w-3 h-3 shrink-0" /> {errors.email}
          </p>
        )}
      </div>

      {/* Acciones */}
      <div className="pt-4 border-t border-slate-200 flex flex-col-reverse sm:flex-row sm:items-center sm:justify-end gap-2.5">
        {onCancel && (
          <Button variant="secondary" onClick={onCancel} type="button" className="w-full sm:w-auto">
            Cancelar
          </Button>
        )}
        <Button variant="primary" type="submit" isLoading={isLoading} className="w-full sm:w-auto">
          Registrar Paciente
        </Button>
      </div>
    </form>
  );
};
