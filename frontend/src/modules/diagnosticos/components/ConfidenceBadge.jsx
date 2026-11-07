import React from 'react';
import { formatConfidence } from '../../../utils/formatters';
import { ShieldCheck, AlertTriangle, AlertOctagon } from 'lucide-react';

/**
 * ConfidenceBadge
 * Muestra el nivel y porcentaje de confianza clínica con código semántico estricto:
 * - ALTA (>= 80%): Verde clínico
 * - MEDIA (60% - 79%): Ámbar clínico
 * - BAJA (< 60%): Carmesí clínico (Segunda opinión obligatoria)
 */
export const ConfidenceBadge = ({
  categoria = 'MEDIA', // 'ALTA' | 'MEDIA' | 'BAJA'
  confianza = null,
  size = 'md', // 'sm' | 'md' | 'lg'
  showIcon = true,
  className = '',
}) => {
  const normalizedCategoria = (categoria || 'MEDIA').toUpperCase();

  const styles = {
    ALTA: {
      bg: 'bg-emerald-50',
      border: 'border-emerald-200',
      text: 'text-emerald-800',
      dot: 'bg-emerald-500',
      Icon: ShieldCheck,
      label: 'Alta Confianza',
    },
    MEDIA: {
      bg: 'bg-amber-50',
      border: 'border-amber-200',
      text: 'text-amber-800',
      dot: 'bg-amber-500',
      Icon: AlertTriangle,
      label: 'Confianza Media',
    },
    BAJA: {
      bg: 'bg-rose-50',
      border: 'border-rose-200',
      text: 'text-rose-800',
      dot: 'bg-rose-500',
      Icon: AlertOctagon,
      label: '2da Opinión Requerida',
    },
  }[normalizedCategoria] || {
    bg: 'bg-slate-100',
    border: 'border-slate-200',
    text: 'text-slate-700',
    dot: 'bg-slate-400',
    Icon: AlertTriangle,
    label: normalizedCategoria,
  };

  const IconComponent = styles.Icon;

  const sizeStyles = {
    sm: 'text-[11px] px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5',
    lg: 'text-sm px-3 py-1.5 gap-2',
  }[size] || 'text-xs px-2.5 py-1 gap-1.5';

  return (
    <span
      className={`inline-flex items-center font-mono border rounded-md font-medium tracking-tight ${styles.bg} ${styles.border} ${styles.text} ${sizeStyles} ${className}`}
    >
      {showIcon && <IconComponent className="w-3.5 h-3.5 shrink-0" />}
      <span>{styles.label}</span>
      {confianza !== null && (
        <span className="opacity-80">
          ({formatConfidence(confianza)})
        </span>
      )}
    </span>
  );
};
