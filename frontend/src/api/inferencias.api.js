import { apiClient } from './client';

/**
 * API Inferencias IA
 * Endpoint:
 * - GET /inferencias/{id} → Polling de estado del pipeline de inferencia
 */

export const inferenciasApi = {
  /**
   * Obtiene el estado actual del procesamiento de una inferencia IA
   * @param {string} id - UUID de la inferencia
   */
  obtenerPorId: (id) => {
    return apiClient.get(`/inferencias/${id}`);
  },
};
