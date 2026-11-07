/**
 * @typedef {Object} ModeloML
 * @property {string} id - UUID
 * @property {string} nombre
 * @property {string} version
 * @property {'YOLO'|'SVM'|'RANDOM_FOREST'|'MOBILENET'|'EFFICIENTNET'} tipo
 * @property {number} f1_score
 * @property {number} precision_score
 * @property {number} recall_score
 * @property {boolean} aprobado_produccion
 * @property {string} created_at
 */

/**
 * @typedef {Object} EstadisticasModelo
 * @property {string} modelo_ml_id
 * @property {string} nombre_modelo
 * @property {string} version
 * @property {number} total_diagnosticos
 * @property {number} total_validados
 * @property {number} total_rechazados
 * @property {number} tasa_validacion
 * @property {number} tasa_segunda_opinion
 */
export {};
