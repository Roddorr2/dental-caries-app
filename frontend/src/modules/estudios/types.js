/**
 * @typedef {Object} ImagenIntraoral
 * @property {string} id - UUID de la imagen
 * @property {'OCLUSAL_MANDIBULAR'|'OCLUSAL_MAXILAR'|'FRONTAL_VESTIBULAR'|'LATERAL_DERECHA'|'LATERAL_IZQUIERDA'} tipo_vista
 * @property {'jpg'|'jpeg'|'png'} formato
 * @property {string} nombre_archivo
 * @property {boolean} calidad_suficiente
 * @property {string} created_at
 */

/**
 * @typedef {Object} Estudio
 * @property {string} id - UUID del estudio
 * @property {string} paciente_id - UUID del paciente
 * @property {'FOTOGRAFIA_INTRAORAL'|'SERIE_COMPLETA'|'OCLUSAL_MANDIBULAR'|'OCLUSAL_MAXILAR'|'FRONTAL_VESTIBULAR'|'LATERAL_DERECHA'|'LATERAL_IZQUIERDA'} tipo_examen
 * @property {'PENDIENTE'|'EN_ANALISIS'|'PROCESADO'} estado_procesamiento
 * @property {ImagenIntraoral[]} imagenes
 * @property {string} created_at
 */

/**
 * @typedef {Object} InferenciaIA
 * @property {string} id
 * @property {string} estudio_id
 * @property {string} modelo_ml_id
 * @property {'PENDIENTE'|'EN_PROCESO'|'COMPLETADO'|'FALLIDO'} estado
 * @property {string|null} worker_id
 * @property {string|null} gpu_utilizada
 * @property {number|null} tiempo_ms
 * @property {string|null} error_mensaje
 * @property {string} created_at
 * @property {string|null} completed_at
 */
export {};
