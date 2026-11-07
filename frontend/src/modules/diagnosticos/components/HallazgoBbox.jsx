import React, { useRef, useState, useEffect, useLayoutEffect } from 'react';
import { SEVERIDAD_COLORES } from '../constants';
import { formatConfidence, formatPatologia, formatSeveridad } from '../../../utils/formatters';

/**
 * HallazgoBbox.jsx
 * ================
 * Overlay SVG posicionado en absoluto sobre la radiografía.
 * Sincroniza dinámicamente sus dimensiones con <img> mediante ResizeObserver.
 *
 * Cada hallazgo clínico se renderiza con:
 * - <rect> SVG con fill="none" y stroke semántico según severidad clínica
 * - <foreignObject> con etiqueta anatómica en IBM Plex Mono y fondo semitransparente
 * - Soporte para selección, foco e interacción clínica
 */
export const HallazgoBbox = ({
  src,
  alt = 'Fotografía intraoral',
  hallazgos = [],
  selectedHallazgoId = null,
  onSelectHallazgo = null,
  visibleHallazgoIds = null, // Set o Array de IDs visibles (null = todos visibles)
  className = '',
}) => {
  const containerRef = useRef(null);
  const imgRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [hoveredHallazgoId, setHoveredHallazgoId] = useState(null);

  // Sincronización estricta de dimensiones con <img> mediante ResizeObserver
  useLayoutEffect(() => {
    const imgEl = imgRef.current;
    if (!imgEl) return;

    const updateDimensions = () => {
      if (imgEl) {
        const { clientWidth, clientHeight } = imgEl;
        if (clientWidth > 0 && clientHeight > 0) {
          setDimensions({ width: clientWidth, height: clientHeight });
        }
      }
    };

    updateDimensions();

    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        if (entry.target === imgEl) {
          const { width, height } = entry.contentRect;
          if (width > 0 && height > 0) {
            setDimensions({ width, height });
          }
        }
      }
    });

    resizeObserver.observe(imgEl);

    // También reevaluar cuando la imagen termine de cargar
    imgEl.addEventListener('load', updateDimensions);

    return () => {
      resizeObserver.disconnect();
      imgEl.removeEventListener('load', updateDimensions);
    };
  }, [src]);

  // Conversión de coordenadas clínicas normalizadas (0.0 a 1.0) o absolutas a píxeles DOM
  const computePixelCoords = (h) => {
    const { bbox_x, bbox_y, bbox_width, bbox_height } = h;
    if (bbox_x === null || bbox_y === null || bbox_width === null || bbox_height === null) {
      return null;
    }

    const { width: W, height: H } = dimensions;
    if (W === 0 || H === 0) return null;

    // Si los valores son <= 1.0, asumimos coordenadas normalizadas de IA
    const isNormalized = bbox_width <= 1.0 && bbox_height <= 1.0;

    let x = isNormalized ? bbox_x * W : bbox_x;
    let y = isNormalized ? bbox_y * H : bbox_y;
    let w = isNormalized ? bbox_width * W : bbox_width;
    let hg = isNormalized ? bbox_height * H : bbox_height;

    // Si la imagen original tenía dimensiones mayores a la renderizada
    if (!isNormalized && imgRef.current && imgRef.current.naturalWidth > 0) {
      const scaleX = W / imgRef.current.naturalWidth;
      const scaleY = H / imgRef.current.naturalHeight;
      x = bbox_x * scaleX;
      y = bbox_y * scaleY;
      w = bbox_width * scaleX;
      hg = bbox_height * scaleY;
    }

    return { x, y, width: w, height: hg };
  };

  return (
    <div
      ref={containerRef}
      className={`relative inline-block overflow-hidden select-none bg-black rounded-lg border border-slate-300 ${className}`}
    >
      {/* Radiografía base */}
      <img
        ref={imgRef}
        src={src}
        alt={alt}
        className="block max-w-full h-auto object-contain mx-auto"
        draggable={false}
      />

      {/* SVG Overlay absoluto posicionado sobre <img> */}
      {dimensions.width > 0 && dimensions.height > 0 && (
        <svg
          className="absolute inset-0 pointer-events-none"
          width={dimensions.width}
          height={dimensions.height}
          viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}
          style={{ width: `${dimensions.width}px`, height: `${dimensions.height}px` }}
        >
          {hallazgos.map((h, idx) => {
            // Verificar si el hallazgo está visible según toggle individual
            if (visibleHallazgoIds && !visibleHallazgoIds.has(h.id)) {
              return null;
            }

            const coords = computePixelCoords(h);
            if (!coords) return null;

            const isSelected = selectedHallazgoId === h.id;
            const isHovered = hoveredHallazgoId === h.id;
            const severityColor = SEVERIDAD_COLORES[h.severidad] || SEVERIDAD_COLORES.MODERADA;
            const strokeColor = severityColor.stroke;

            // Etiqueta clínica en lenguaje del odontólogo
            const piezaLabel = h.diente_numero ? `P${h.diente_numero}` : `C${h.cuadrante || '?'}`;
            const clinicalLabel = `${piezaLabel} ${formatPatologia(h.tipo_patologia).split(' ')[0]} (${formatConfidence(h.confianza)})`;

            // Posicionamiento de la etiqueta encima del bbox o debajo si está muy pegado arriba
            const labelWidth = Math.max(140, clinicalLabel.length * 7.5);
            const labelHeight = 22;
            const labelX = Math.min(Math.max(2, coords.x), dimensions.width - labelWidth - 4);
            const labelY = coords.y >= labelHeight + 4 ? coords.y - labelHeight - 2 : coords.y + coords.height + 2;

            return (
              <g
                key={h.id || idx}
                className="cursor-pointer pointer-events-auto"
                onClick={() => onSelectHallazgo && onSelectHallazgo(h)}
                onMouseEnter={() => setHoveredHallazgoId(h.id)}
                onMouseLeave={() => setHoveredHallazgoId(null)}
              >
                {/* Rectángulo de delimitación Bounding Box */}
                <rect
                  x={coords.x}
                  y={coords.y}
                  width={coords.width}
                  height={coords.height}
                  fill={isSelected ? `${strokeColor}20` : isHovered ? `${strokeColor}10` : 'none'}
                  stroke={strokeColor}
                  strokeWidth={isSelected ? 2.5 : isHovered ? 2 : 1.5}
                  strokeDasharray={isSelected ? '4 2' : 'none'}
                  rx={2}
                  className="transition-all duration-75"
                />

                {/* Etiqueta HTML con foreignObject (IBM Plex Mono) */}
                <foreignObject
                  x={labelX}
                  y={labelY}
                  width={labelWidth}
                  height={labelHeight}
                  className="overflow-visible"
                >
                  <div
                    xmlns="http://www.w3.org/1999/xhtml"
                    style={{
                      borderColor: strokeColor,
                    }}
                    className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-mono leading-none border shadow-sm transition-all duration-75 ${
                      isSelected
                        ? 'bg-slate-900 text-white font-semibold ring-1 ring-white/50'
                        : isHovered
                        ? 'bg-slate-900/95 text-white'
                        : 'bg-slate-900/85 text-slate-100'
                    }`}
                  >
                    <span
                      className="w-1.5 h-1.5 rounded-full shrink-0"
                      style={{ backgroundColor: strokeColor }}
                    />
                    <span className="truncate">{clinicalLabel}</span>
                  </div>
                </foreignObject>
              </g>
            );
          })}
        </svg>
      )}
    </div>
  );
};
