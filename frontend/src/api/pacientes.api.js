import { apiClient } from './client';

/**
 * API Pacientes — Bounded Context 1
 * Endpoints:
 * - GET  /pacientes/          → Listar pacientes activos
 * - GET  /pacientes/{id}      → Obtener paciente por ID
 * - POST /pacientes/          → Registrar nuevo paciente
 */

export const pacientesApi = {
  /**
   * Lista pacientes en estado ACTIVO
   * @param {Object} [params]
   * @param {number} [params.limit=50]
   * @param {number} [params.offset=0]
   */
  listar: (params = { limit: 50, offset: 0 }) => {
    return apiClient.get('/pacientes/', { params });
  },

  /**
   * Obtiene un paciente por su identificador UUID
   * @param {string} id
   */
  obtenerPorId: (id) => {
    return apiClient.get(`/pacientes/${id}`);
  },

  /**
   * Registra un nuevo paciente
   * @param {Object} data
   * @param {string} data.dni - 8 dígitos
   * @param {string} data.nombres
   * @param {string} data.apellidos
   * @param {string} data.fecha_nacimiento - YYYY-MM-DD
   * @param {'M'|'F'|'OTRO'} data.sexo
   * @param {string} data.telefono
   * @param {string} data.email
   */
  registrar: (data) => {
    return apiClient.post('/pacientes/', data);
  },
};
