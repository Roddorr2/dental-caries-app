export const ESTADO_DIAGNOSTICO = {
  SUGERIDO_IA: 'SUGERIDO_IA',
  EN_REVISION: 'EN_REVISION',
  VALIDADO: 'VALIDADO',
  RECHAZADO: 'RECHAZADO',
};

export const CATEGORIA_CONFIANZA = {
  ALTA: 'ALTA',     // >= 0.80 -> Verde clínico
  MEDIA: 'MEDIA',   // 0.60 - 0.79 -> Ámbar clínico
  BAJA: 'BAJA',     // < 0.60 -> Carmesí clínico (Segunda opinión)
};

export const TIPO_PATOLOGIA = {
  CARIES: 'CARIES',
  FRACTURA: 'FRACTURA',
  CALCULO_DENTAL: 'CALCULO_DENTAL',
};

export const SEVERIDAD = {
  LEVE: 'LEVE',
  MODERADA: 'MODERADA',
  SEVERA: 'SEVERA',
};

/**
 * Colores semánticos clínicos estrictos para patologías y severidades
 */
export const SEVERIDAD_COLORES = {
  LEVE: {
    stroke: '#16a34a', // Verde
    bg: '#f0fdf4',
    text: '#166534',
    border: '#bbf7d0',
  },
  MODERADA: {
    stroke: '#d97706', // Ámbar
    bg: '#fffbeb',
    text: '#92400e',
    border: '#fde68a',
  },
  SEVERA: {
    stroke: '#e11d48', // Carmesí
    bg: '#fff1f2',
    text: '#9f1239',
    border: '#fecdd3',
  },
};
