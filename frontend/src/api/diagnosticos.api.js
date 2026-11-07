import { apiClient } from './client';

/**
 * API Diagnósticos Asistidos por IA — Bounded Context 3
 * Endpoints:
 * - GET  /diagnosticos/pendientes         → Cola de revisión clínica (CQRS Read Model)
 * - GET  /diagnosticos/{id}               → Detalle de diagnóstico y hallazgos
 * - POST /diagnosticos/{id}/validar       → Validar diagnóstico sugerido por IA
 * - POST /diagnosticos/{id}/rechazar      → Rechazar diagnóstico con motivo
 */

export const diagnosticosApi = {
  /**
   * Obtiene la lista de odontólogos autorizados para la firma diagnóstica
   */
  obtenerOdontologosAutorizados: () => {
    return apiClient.get('/diagnosticos/odontologos');
  },

  /**
   * Consulta la cola de revisión de diagnósticos pendientes
   * @param {Object} [params]
   * @param {boolean} [params.solo_segunda_opinion=false]
   * @param {number} [params.limit=20]
   * @param {number} [params.offset=0]
   */
  obtenerColaRevision: (params = {}) => {
    return apiClient.get('/diagnosticos/pendientes', { params });
  },

  /**
   * Obtiene un diagnóstico por ID con sus hallazgos y bounding boxes
   * @param {string} id - UUID del diagnóstico
   */
  obtenerPorId: (id) => {
    return apiClient.get(`/diagnosticos/${id}`);
  },

  /**
   * El odontólogo valida un diagnóstico sugerido por IA
   * @param {string} id - UUID del diagnóstico
   * @param {Object} data
   * @param {string} data.odontologo_id - UUID
   * @param {string} data.notas - Notas clínicas obligatorias
   */
  validar: (id, data) => {
    return apiClient.post(`/diagnosticos/${id}/validar`, data);
  },

  /**
   * El odontólogo rechaza un diagnóstico sugerido por IA
   * @param {string} id - UUID del diagnóstico
   * @param {Object} data
   * @param {string} data.odontologo_id - UUID
   * @param {string} data.motivo - Motivo obligatorio del rechazo
   */
  rechazar: (id, data) => {
    return apiClient.post(`/diagnosticos/${id}/rechazar`, data);
  },
};
