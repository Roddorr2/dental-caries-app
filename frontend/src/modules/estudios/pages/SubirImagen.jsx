import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useEstudioDetail, useAgregarImagen, useSolicitarAnalisis } from '../hooks/useEstudios';
import { ImagenUploader } from '../components/ImagenUploader';
import { Button } from '../../../shared/components/Button';
import { Badge } from '../../../shared/components/Badge';
import { Loader } from '../../../shared/components/Loader';
import { formatDate, formatEstadoPipeline } from '../../../utils/formatters';
import { TIPO_EXAMEN_LABELS } from '../constants';
import { ArrowLeft, Sparkles, CheckCircle2, AlertCircle, Image as ImageIcon } from 'lucide-react';

export const SubirImagen = () => {
  const { id: estudioId } = useParams();
  const navigate = useNavigate();

  const { data: estudio, isLoading: isLoadingEstudio, refetch } = useEstudioDetail(estudioId);
  const agregarImagenMutation = useAgregarImagen(estudioId);
  const solicitarAnalisisMutation = useSolicitarAnalisis(estudioId);

  const [successMessage, setSuccessMessage] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  const handleUploadImage = async (imagenPayload) => {
    try {
      setErrorMessage(null);
      await agregarImagenMutation.mutateAsync({
        tipo_vista: imagenPayload.tipo_vista,
        formato: imagenPayload.formato,
        ruta_almacenamiento: imagenPayload.ruta_almacenamiento,
        nombre_archivo: imagenPayload.nombre_archivo,
        hash_sha256: imagenPayload.hash_sha256,
        calidad_suficiente: imagenPayload.calidad_suficiente,
        nitidez: imagenPayload.nitidez,
        iluminacion: imagenPayload.iluminacion,
      });

      setSuccessMessage('Fotografía intraoral registrada correctamente con hash SHA-256 verificado.');
      refetch();
    } catch (err) {
      setErrorMessage(err.message || 'Error al agregar la fotografía al estudio.');
    }
  };

  const handleTriggerAnalisis = async () => {
    try {
      setErrorMessage(null);
      // Ejecución directa del motor CDSS de producción (best.pt)
      const res = await solicitarAnalisisMutation.mutateAsync();
      const inferenciaId = res?.inferencia_id || res?.id;
      // Redirigir al detalle del estudio para monitorear pipeline inline
      navigate(`/estudios/${estudioId}?inferencia_id=${inferenciaId}`);
    } catch (err) {
      setErrorMessage(err.message || 'Error al solicitar el análisis clínico con CDSS.');
    }
  };


  if (isLoadingEstudio) {
    return <Loader size="lg" message="Cargando estudio..." className="py-20" />;
  }

  const imagenes = estudio?.imagenes || [];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Navegación */}
      <button
        type="button"
        onClick={() => navigate(`/estudios/${estudioId}`)}
        className="inline-flex items-center gap-1.5 text-xs font-mono text-slate-500 hover:text-slate-900 transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Ir a Vista de Detalle del Estudio</span>
      </button>

      {/* Cabecera del Estudio */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 shadow-subtle flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-base font-bold text-slate-900 tracking-tight">
              {TIPO_EXAMEN_LABELS[estudio?.tipo_examen] || estudio?.tipo_examen}
            </h2>
            <Badge variant="neutral" size="sm" showDot>
              {formatEstadoPipeline(estudio?.estado_procesamiento)}
            </Badge>
          </div>
          <p className="text-xs font-mono text-slate-500 mt-1">
            Estudio #{estudioId?.slice(0, 8)} · Fecha: {formatDate(estudio?.created_at, true)}
          </p>
        </div>

        {/* Trigger de análisis clínico directo con CDSS */}
        {imagenes.length > 0 && (
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 w-full sm:w-auto">
            <div className="text-right hidden sm:block">
              <span className="text-[10px] uppercase font-mono text-emerald-600 font-semibold block tracking-wider">
                ● CDSS Calibrado
              </span>
              <span className="text-[11px] text-slate-500 font-mono">
                Detector Oficial (OMS CPO-D)
              </span>
            </div>
            <Button
              variant="primary"
              icon={Sparkles}
              onClick={handleTriggerAnalisis}
              isLoading={solicitarAnalisisMutation.isPending}
              className="w-full sm:w-auto shadow-sm"
            >
              Analizar con CDSS
            </Button>
          </div>
        )}
      </div>

      {successMessage && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded text-xs text-emerald-800 flex items-center gap-2 font-mono">
          <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
          <span>{successMessage}</span>
        </div>
      )}

      {errorMessage && (
        <div className="p-3 bg-rose-50 border border-rose-200 rounded text-xs text-rose-800 flex items-center gap-2 font-mono">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Uploader con SHA-256 */}
      <ImagenUploader
        onUpload={handleUploadImage}
        isLoading={agregarImagenMutation.isPending}
      />

      {/* Lista de imágenes adjuntas en este estudio */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-subtle space-y-4">
        <h4 className="text-sm font-semibold text-slate-900 tracking-tight">
          Imágenes Registradas en el Estudio ({imagenes.length})
        </h4>

        {imagenes.length === 0 ? (
          <p className="text-xs text-slate-400 font-sans py-4 text-center">
            Aún no se han agregado fotografías a este estudio clínico.
          </p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {imagenes.map((img) => (
              <div
                key={img.id}
                className="border border-slate-200 rounded p-3 bg-slate-50 space-y-2 text-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-800 truncate">
                    {img.nombre_archivo}
                  </span>
                  <Badge variant="neutral" size="sm">
                    {img.tipo_vista}
                  </Badge>
                </div>
                <div className="flex items-center justify-between text-slate-500 font-mono text-[11px]">
                  <span>{img.formato.toUpperCase()}</span>
                  <span>{formatDate(img.created_at)}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
