/**
 * @typedef {Object} Paciente
 * @property {string} id - UUID del paciente
 * @property {string} dni - Documento Nacional de Identidad (8 dígitos)
 * @property {string} nombres - Nombres
 * @property {string} apellidos - Apellidos
 * @property {string} fecha_nacimiento - Formato YYYY-MM-DD
 * @property {'M'|'F'|'OTRO'} sexo
 * @property {string} telefono
 * @property {string} email
 * @property {'ACTIVO'|'INACTIVO'} estado
 */

/**
 * @typedef {Object} PacienteCreateInput
 * @property {string} dni
 * @property {string} nombres
 * @property {string} apellidos
 * @property {string} fecha_nacimiento
 * @property {'M'|'F'|'OTRO'} sexo
 * @property {string} telefono
 * @property {string} email
 */
export {};
