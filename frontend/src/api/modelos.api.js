import { apiClient } from './client';

/**
 * API Modelos ML y Métricas — Bounded Context 4 & 5
 * Endpoints:
 * - GET /modelos/                    → Listar modelos registrados con métricas de entrenamiento
 * - GET /modelos/{id}/estadisticas   → Estadísticas de producción validadas por odontólogos
 */

export const modelosApi = {
  /**
   * Lista todos los modelos de aprendizaje automático registrados
   */
  listar: () => {
    return apiClient.get('/modelos/');
  },

  /**
   * Obtiene estadísticas de rendimiento clínico en producción para un modelo específico
   * @param {string} modeloId - UUID del modelo
   */
  obtenerEstadisticas: (modeloId) => {
    return apiClient.get(`/modelos/${modeloId}/estadisticas`);
  },
};
