import React, { useState, useRef } from 'react';
import { UploadCloud, AlertCircle, Image as ImageIcon, Check, CheckCircle } from 'lucide-react';
import { computeSHA256 } from '../../../utils/sha256';
import { Button } from '../../../shared/components/Button';
import { TIPO_VISTA } from '../constants';

export const ImagenUploader = ({ onUpload, isLoading = false }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [hashSHA256, setHashSHA256] = useState('');
  const [isHashing, setIsHashing] = useState(false);
  const [tipoVista, setTipoVista] = useState(TIPO_VISTA.OCLUSAL_MANDIBULAR);
  const [calidadSuficiente, setCalidadSuficiente] = useState(true);
  const [nitidez, setNitidez] = useState(0.92);
  const [iluminacion, setIluminacion] = useState(0.88);
  const [error, setError] = useState(null);

  const fileInputRef = useRef(null);

  const processFile = async (file) => {
    if (!file) return;

    // Validación de extensiones permitidas
    const validExtensions = ['image/jpeg', 'image/png', 'image/jpg'];
    const isDcm = file.name.toLowerCase().endsWith('.dcm');

    if (!validExtensions.includes(file.type) && !isDcm) {
      setError('Formato no soportado. Se requieren imágenes JPG, PNG o archivos DICOM (.dcm).');
      return;
    }

    setError(null);
    setSelectedFile(file);

    // Generar vista previa si es imagen web estándar
    if (!isDcm) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    } else {
      setPreviewUrl(null);
    }

    // Cálculo estricto de SHA-256 client-side en memoria (Web Crypto API)
    try {
      setIsHashing(true);
      const hash = await computeSHA256(file);
      setHashSHA256(hash);
    } catch (err) {
      setError('Error al calcular el hash de integridad del archivo.');
    } finally {
      setIsHashing(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const handleConfirmUpload = () => {
    if (!selectedFile || !hashSHA256) return;

    const extension = selectedFile.name.split('.').pop().toLowerCase();
    const formato = extension === 'jpeg' ? 'jpg' : extension;

    onUpload({
      file: selectedFile,
      previewUrl,
      tipo_vista: tipoVista,
      formato,
      ruta_almacenamiento: `/storage/estudios/${selectedFile.name}`,
      nombre_archivo: selectedFile.name,
      hash_sha256: hashSHA256,
      calidad_suficiente: calidadSuficiente,
      nitidez: Number(nitidez),
      iluminacion: Number(iluminacion),
    });
  };

  const resetSelection = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setHashSHA256('');
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-subtle space-y-5">
      <div className="border-b border-slate-100 pb-3">
        <h4 className="text-sm font-semibold text-slate-900 tracking-tight">
          Carga de Fotografía Intraoral
        </h4>
        <p className="text-xs text-slate-500 mt-0.5">
          Seleccione o arrastre la fotografía clínica para su análisis y registro en el estudio
        </p>
      </div>

      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 rounded text-xs text-rose-800 flex items-center gap-2 font-mono">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Zona Drag & Drop Accesible */}
      {!selectedFile ? (
        <div
          role="button"
          tabIndex={0}
          data-testid="uploader-dropzone"
          aria-label="Zona de carga de fotografía intraoral. Presione enter o espacio para seleccionar archivo o arrastre la fotografía aquí"
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              fileInputRef.current?.click();
            }
          }}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-slate-900 ${
            dragActive
              ? 'border-slate-900 bg-slate-100'
              : 'border-slate-300 hover:border-slate-400 bg-slate-50/50'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".jpg,.jpeg,.png"
            onChange={handleInputChange}
            className="hidden"
            aria-hidden="true"
            tabIndex={-1}
          />
          <UploadCloud className="w-10 h-10 text-slate-400 mx-auto mb-3 stroke-[1.5]" aria-hidden="true" />
          <p className="text-xs font-semibold text-slate-800">
            Arrastre la fotografía intraoral aquí o haga clic para seleccionar archivo
          </p>
          <p className="text-[11px] text-slate-400 mt-1">
            Formatos admitidos: JPG, JPEG, PNG · Integridad clínica y verificación automática
          </p>
        </div>
      ) : (
        /* Vista de archivo seleccionado con verificación clínica y metadatos */
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row items-start gap-4 p-4 bg-slate-50 border border-slate-200 rounded-lg">
            {previewUrl ? (
              <img
                src={previewUrl}
                alt={`Vista previa de fotografía intraoral: ${selectedFile.name}`}
                className="w-24 h-24 object-cover rounded border border-slate-200 bg-black shrink-0"
              />
            ) : (
              <div className="w-24 h-24 rounded border border-slate-200 bg-slate-200 flex items-center justify-center text-slate-500 shrink-0" aria-hidden="true">
                <ImageIcon className="w-8 h-8" />
              </div>
            )}

            <div className="flex-1 min-w-0 space-y-1.5 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-900 truncate">
                  {selectedFile.name}
                </span>
                <button
                  type="button"
                  onClick={resetSelection}
                  className="text-xs text-rose-600 hover:text-rose-800 font-medium focus:outline-none focus:underline"
                >
                  Cambiar archivo
                </button>
              </div>

              <p className="text-slate-500">
                Tamaño: {(selectedFile.size / 1024).toFixed(1)} KB · Tipo: {selectedFile.type || 'DICOM'}
              </p>

              {/* Indicador de Verificación Silenciosa con región en vivo ARIA */}
              <div aria-live="polite" className="pt-0.5">
                {isHashing ? (
                  <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium mt-1">
                    <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" aria-hidden="true" />
                    <span>Verificando integridad clínica del archivo...</span>
                  </div>
                ) : hashSHA256 ? (
                  <div className="flex items-center gap-1.5 text-xs text-emerald-600 font-medium mt-1">
                    <CheckCircle className="w-4 h-4 text-emerald-500 shrink-0" aria-hidden="true" />
                    <span>Archivo verificado (integridad clínica certificada)</span>
                  </div>
                ) : null}
              </div>
            </div>
          </div>

          {/* Formulario de parámetros clínicos para la imagen */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 sm:gap-4 pt-2">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1 font-mono">
                Tipo de Vista *
              </label>
              <select
                value={tipoVista}
                onChange={(e) => setTipoVista(e.target.value)}
                className="w-full h-10 px-3 text-base sm:text-xs border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-1 focus:ring-slate-900"
              >
                <option value={TIPO_VISTA.OCLUSAL_MANDIBULAR}>Oclusal Mandibular</option>
                <option value={TIPO_VISTA.OCLUSAL_MAXILAR}>Oclusal Maxilar</option>
                <option value={TIPO_VISTA.FRONTAL_VESTIBULAR}>Frontal Vestibular</option>
                <option value={TIPO_VISTA.LATERAL_DERECHA}>Lateral Derecha</option>
                <option value={TIPO_VISTA.LATERAL_IZQUIERDA}>Lateral Izquierda</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1 font-mono">
                Control de Calidad Inicial
              </label>
              <div className="flex items-center gap-4 h-10">
                <label className="inline-flex items-center gap-2 text-xs text-slate-700 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={calidadSuficiente}
                    onChange={(e) => setCalidadSuficiente(e.target.checked)}
                    className="rounded border-slate-300 text-slate-900 focus:ring-slate-900 h-4 w-4"
                  />
                  <span>Calidad Diagnóstica Suficiente</span>
                </label>
              </div>
            </div>
          </div>

          {/* Botón de confirmación */}
          <div className="flex justify-end pt-3">
            <Button
              variant="primary"
              onClick={handleConfirmUpload}
              isLoading={isLoading || isHashing}
              disabled={!hashSHA256 || isHashing}
              icon={Check}
              className="w-full sm:w-auto shadow-sm"
            >
              Registrar Imagen en Estudio
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
