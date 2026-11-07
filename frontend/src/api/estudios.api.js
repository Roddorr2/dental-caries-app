import { apiClient } from './client';

/**
 * API Estudios e Imágenes — Bounded Context 2
 * Endpoints:
 * - POST /estudios/                    → Crear estudio
 * - GET  /estudios/{id}                → Obtener estudio con imágenes
 * - POST /estudios/{id}/imagenes       → Agregar imagen con metadatos y hash SHA-256
 * - POST /estudios/{id}/analisis       → Solicitar análisis IA sobre el estudio
 */

export const estudiosApi = {
  /**
   * Lista los estudios fotográficos clínicos
   * @param {Object} [params]
   * @param {string} [params.paciente_id]
   * @param {string} [params.estado]
   */
  listar: (params = {}) => {
    return apiClient.get('/estudios/', { params });
  },

  /**
   * Crea un nuevo estudio imagenológico
   * @param {Object} data
   * @param {string} data.paciente_id - UUID
   * @param {'FOTOGRAFIA_INTRAORAL'|'SERIE_COMPLETA'|'OCLUSAL_MANDIBULAR'|'OCLUSAL_MAXILAR'|'FRONTAL_VESTIBULAR'|'LATERAL_DERECHA'|'LATERAL_IZQUIERDA'} data.tipo_examen
   * @param {string} [data.region_examinada]
   * @param {string} [data.observaciones]
   */
  crear: (data) => {
    return apiClient.post('/estudios/', data);
  },

  /**
   * Obtiene un estudio por su ID
   * @param {string} id - UUID del estudio
   */
  obtenerPorId: (id) => {
    return apiClient.get(`/estudios/${id}`);
  },

  /**
   * Agrega una imagen intraoral al estudio
   * @param {string} estudioId - UUID del estudio
   * @param {Object} data
   * @param {'OCLUSAL_MANDIBULAR'|'OCLUSAL_MAXILAR'|'FRONTAL_VESTIBULAR'|'LATERAL_DERECHA'|'LATERAL_IZQUIERDA'} data.tipo_vista
   * @param {'jpg'|'jpeg'|'png'} data.formato
   * @param {string} data.ruta_almacenamiento
   * @param {string} data.nombre_archivo
   * @param {string} data.hash_sha256
   * @param {boolean} data.calidad_suficiente
   * @param {number} [data.nitidez]
   * @param {number} [data.iluminacion]
   */
  agregarImagen: (estudioId, data) => {
    return apiClient.post(`/estudios/${estudioId}/imagenes`, data);
  },

  /**
   * Solicita análisis de inferencia IA para el estudio (CDSS)
   * Si no se envía modeloMlId, el backend selecciona el detector oficial aprobado (best.pt).
   * @param {string} estudioId - UUID del estudio
   * @param {string} [modeloMlId] - UUID del modelo ML opcional
   */
  solicitarAnalisis: (estudioId, modeloMlId = null) => {
    const payload = modeloMlId ? { modelo_ml_id: modeloMlId } : {};
    return apiClient.post(`/estudios/${estudioId}/analisis`, payload);
  },
};

