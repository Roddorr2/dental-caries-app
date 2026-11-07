/**
 * formatters.js
 * =============
 * Utilidades de formateo para el dominio clínico odontológico.
 * Garantiza un lenguaje clínico riguroso sin fugas de base de datos.
 */

/**
 * Formatea fechas ISO a formato legible clínico en español
 * @param {string | Date | null | undefined} dateInput
 * @param {boolean} includeTime
 * @returns {string}
 */
export function formatDate(dateInput, includeTime = false) {
  if (!dateInput) return '—';
  try {
    const d = typeof dateInput === 'string' ? new Date(dateInput) : dateInput;
    if (isNaN(d.getTime())) return String(dateInput);

    const day = String(d.getDate()).padStart(2, '0');
    const monthNames = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
    const month = monthNames[d.getMonth()];
    const year = d.getFullYear();

    if (includeTime) {
      const hours = String(d.getHours()).padStart(2, '0');
      const minutes = String(d.getMinutes()).padStart(2, '0');
      return `${day} ${month} ${year}, ${hours}:${minutes}`;
    }
    return `${day} ${month} ${year}`;
  } catch {
    return '—';
  }
}

/**
 * Formatea porcentaje de confianza clínica (0.0 a 1.0 -> "87%")
 * @param {number | null | undefined} val
 * @returns {string}
 */
export function formatConfidence(val) {
  if (val === null || val === undefined || isNaN(val)) return '—';
  const percentage = val > 1 ? val : Math.round(val * 100);
  return `${percentage}%`;
}

/**
 * Formatea latencia de inferencia en ms
 * @param {number | null | undefined} ms
 * @returns {string}
 */
export function formatLatency(ms) {
  if (ms === null || ms === undefined || isNaN(ms)) return '—';
  return `${Math.round(ms)} ms`;
}

/**
 * Formatea hash SHA-256 para display compacto clínico
 * @param {string | null | undefined} hash
 * @returns {string}
 */
export function formatShortHash(hash) {
  if (!hash || typeof hash !== 'string') return '—';
  if (hash.length <= 12) return hash;
  return `${hash.slice(0, 8)}...${hash.slice(-4)}`;
}

/**
 * Mapeo de cuadrante FDI a descripción anatómica clínica
 */
export const CUADRANTES_DESCRIPCION = {
  1: 'Superior Derecho',
  2: 'Superior Izquierdo',
  3: 'Inferior Izquierdo',
  4: 'Inferior Derecho',
};

/**
 * Mapeo de piezas dentales FDI más comunes
 */
export const DIENTES_FDI_NOMBRES = {
  18: 'Tercer Molar Sup. Der.',
  17: 'Segundo Molar Sup. Der.',
  16: 'Primer Molar Sup. Der.',
  15: 'Segundo Premolar Sup. Der.',
  14: 'Primer Premolar Sup. Der.',
  13: 'Canino Sup. Der.',
  12: 'Incisivo Lateral Sup. Der.',
  11: 'Incisivo Central Sup. Der.',
  21: 'Incisivo Central Sup. Izq.',
  22: 'Incisivo Lateral Sup. Izq.',
  23: 'Canino Sup. Izq.',
  24: 'Primer Premolar Sup. Izq.',
  25: 'Segundo Premolar Sup. Izq.',
  26: 'Primer Molar Sup. Izq.',
  27: 'Segundo Molar Sup. Izq.',
  28: 'Tercer Molar Sup. Izq.',
  38: 'Tercer Molar Inf. Izq.',
  37: 'Segundo Molar Inf. Izq.',
  36: 'Primer Molar Inf. Izq.',
  35: 'Segundo Premolar Inf. Izq.',
  34: 'Primer Premolar Inf. Izq.',
  33: 'Canino Inf. Izq.',
  32: 'Incisivo Lateral Inf. Izq.',
  31: 'Incisivo Central Inf. Izq.',
  41: 'Incisivo Central Inf. Der.',
  42: 'Incisivo Lateral Inf. Der.',
  43: 'Canino Inf. Der.',
  44: 'Primer Premolar Inf. Der.',
  45: 'Segundo Premolar Inf. Der.',
  46: 'Primer Molar Inf. Der.',
  47: 'Segundo Molar Inf. Der.',
  48: 'Tercer Molar Inf. Der.',
};

/**
 * Formatea pieza dental FDI
 * @param {number | string | null | undefined} diente
 * @param {number | string | null | undefined} cuadrante
 * @returns {string}
 */
export function formatPiezaDental(diente, cuadrante) {
  if (!diente && !cuadrante) return 'Región no especificada';
  if (diente) {
    const nombre = DIENTES_FDI_NOMBRES[Number(diente)];
    return nombre ? `Pieza ${diente} (${nombre})` : `Pieza ${diente}`;
  }
  return `Cuadrante ${cuadrante} (${CUADRANTES_DESCRIPCION[cuadrante] || 'General'})`;
}

/**
 * Traduce patología a etiqueta médica formal
 */
export function formatPatologia(patologia) {
  const map = {
    CARIES: 'Caries Dental',
    FRACTURA: 'Fractura Dental',
    CALCULO_DENTAL: 'Cálculo Dental',
  };
  return map[patologia] || patologia || 'Hallazgo no clasificado';
}

/**
 * Traduce tipo de vista fotográfica
 */
export function formatTipoVista(vista) {
  const map = {
    OCLUSAL_MANDIBULAR: 'Oclusal Mandibular',
    OCLUSAL_MAXILAR: 'Oclusal Maxilar',
    FRONTAL_VESTIBULAR: 'Frontal Vestibular',
    LATERAL_DERECHA: 'Lateral Derecha',
    LATERAL_IZQUIERDA: 'Lateral Izquierda',
  };
  return map[vista] || vista || 'Vista no especificada';
}

/**
 * Traduce severidad clínica
 */
export function formatSeveridad(severidad) {
  const map = {
    LEVE: 'Leve',
    MODERADA: 'Moderada',
    SEVERA: 'Severa',
  };
  return map[severidad] || severidad || 'No determinada';
}

/**
 * Traduce estado del diagnóstico
 */
export function formatEstadoDiagnostico(estado) {
  const map = {
    SUGERIDO_IA: 'Revisión Pendiente',
    EN_REVISION: 'En Revisión Clínica',
    VALIDADO: 'Validado',
    RECHAZADO: 'Rechazado',
  };
  return map[estado] || estado;
}

/**
 * Traduce estado del estudio imagenológico
 */
export function formatEstadoPipeline(estado) {
  const map = {
    PENDIENTE: 'Pendiente',
    EN_ANALISIS: 'En Análisis',
    PROCESADO: 'Completado',
    COMPLETADO: 'Completado',
    ESTUDIO_IMAGENOLOGICO: 'Completado',
    ESTUDIO_IMAGENOLOGICO_COMPLETO: 'Completado',
    FALLIDO: 'Error',
    ERROR: 'Error',
  };
  return map[estado] || estado || 'Pendiente';
}
