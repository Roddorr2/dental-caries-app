/**
 * @typedef {Object} Hallazgo
 * @property {string} id - UUID del hallazgo
 * @property {string} imagen_id - UUID de la imagen
 * @property {'CARIES'|'FRACTURA'|'CALCULO_DENTAL'} tipo_patologia
 * @property {'LEVE'|'MODERADA'|'SEVERA'} severidad
 * @property {number} confianza - 0.0 a 1.0
 * @property {number|null} diente_numero - Notación FDI (11 a 48)
 * @property {number|null} cuadrante - Cuadrante (1 a 4)
 * @property {number|null} bbox_x - Coordenada X normalizada (0.0 a 1.0) o absoluta
 * @property {number|null} bbox_y - Coordenada Y normalizada (0.0 a 1.0) o absoluta
 * @property {number|null} bbox_width - Ancho normalizado (0.0 a 1.0) o absoluto
 * @property {number|null} bbox_height - Alto normalizado (0.0 a 1.0) o absoluto
 * @property {string|null} descripcion_clinica
 */

/**
 * @typedef {Object} Diagnostico
 * @property {string} id - UUID del diagnóstico
 * @property {string} estudio_id - UUID del estudio
 * @property {string} paciente_id - UUID del paciente
 * @property {'SUGERIDO_IA'|'EN_REVISION'|'VALIDADO'|'RECHAZADO'} estado
 * @property {number} confianza_global - 0.0 a 1.0
 * @property {'ALTA'|'MEDIA'|'BAJA'} categoria_confianza
 * @property {Hallazgo[]} hallazgos
 * @property {string} fecha_generacion
 * @property {string|null} fecha_validacion
 * @property {string|null} notas_validacion
 * @property {string|null} motivo_rechazo
 */

/**
 * @typedef {Object} ColaRevisionItem
 * @property {string} diagnostico_id
 * @property {string} paciente_id
 * @property {string} paciente_nombre
 * @property {string} estudio_id
 * @property {string} tipo_examen
 * @property {number} confianza_global
 * @property {'ALTA'|'MEDIA'|'BAJA'} categoria_confianza
 * @property {boolean} segunda_opinion
 * @property {string} fecha_generacion
 */
export {};
