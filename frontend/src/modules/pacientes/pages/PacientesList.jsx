import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePacientesList, useCrearPaciente } from '../hooks/usePacientes';
import { Table } from '../../../shared/components/Table';
import { Button } from '../../../shared/components/Button';
import { Badge } from '../../../shared/components/Badge';
import { Modal } from '../../../shared/components/Modal';
import { PacienteForm } from '../components/PacienteForm';
import { PacienteCard } from '../components/PacienteCard';
import { EmptyState } from '../../../shared/components/EmptyState';
import { usePagination } from '../../../shared/hooks/usePagination';
import { useDebounce } from '../../../shared/hooks/useDebounce';
import { formatDate } from '../../../utils/formatters';
import { SEXO_LABELS } from '../constants';
import { UserPlus, Search, AlertCircle, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';

export const PacientesList = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 250);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const { page, setPage, pageSize } = usePagination(1, 20);

  const {
    data: pacientes = [],
    isLoading,
    isRefetching,
    error,
    refetch,
  } = usePacientesList({
    limit: 100, // Lote para filtrado rápido en cliente
    offset: 0,
  });

  const crearPacienteMutation = useCrearPaciente();

  const handleRetry = () => {
    refetch();
  };

  // Filtrado reactivo en cliente por DNI o Nombres/Apellidos
  const filteredPacientes = useMemo(() => {
    if (!debouncedSearch.trim()) return pacientes;
    const q = debouncedSearch.toLowerCase().trim();
    return pacientes.filter((p) => {
      const full = `${p.nombres} ${p.apellidos}`.toLowerCase();
      return full.includes(q) || (p.dni && p.dni.includes(q));
    });
  }, [pacientes, debouncedSearch]);

  // Paginación sobre el conjunto filtrado
  const paginatedData = useMemo(() => {
    const start = (page - 1) * pageSize;
    return filteredPacientes.slice(start, start + pageSize);
  }, [filteredPacientes, page, pageSize]);

  const handleCreateSubmit = async (formData) => {
    try {
      setErrorMessage(null);
      await crearPacienteMutation.mutateAsync(formData);
      setIsModalOpen(false);
      refetch();
    } catch (err) {
      setErrorMessage(err.message || 'Error al registrar el paciente');
    }
  };

  const columns = [
    {
      header: 'DNI / Identidad',
      accessor: 'dni',
      className: 'w-32',
      render: (p) => (
        <span className="font-mono font-medium text-slate-900">{p.dni}</span>
      ),
    },
    {
      header: 'Paciente (Apellidos, Nombres)',
      accessor: 'apellidos',
      render: (p) => (
        <span className="font-medium text-slate-900">{p.apellidos}, {p.nombres}</span>
      ),
    },
    {
      header: 'Nacimiento / Sexo',
      accessor: 'fecha_nacimiento',
      className: 'w-44',
      render: (p) => (
        <div className="text-xs text-slate-600 font-sans">
          <span>{formatDate(p.fecha_nacimiento)}</span>
          <span className="text-slate-400 ml-1.5">({SEXO_LABELS[p.sexo] || p.sexo})</span>
        </div>
      ),
    },
    {
      header: 'Teléfono',
      accessor: 'telefono',
      className: 'w-36',
      render: (p) => (
        <span className="text-xs text-slate-600 font-sans">{p.telefono || '—'}</span>
      ),
    },
    {
      header: 'Correo Electrónico',
      accessor: 'email',
      render: (p) => (
        <span className="text-xs text-slate-600 truncate block max-w-xs font-sans">{p.email || '—'}</span>
      ),
    },
    {
      header: 'Estado',
      accessor: 'estado',
      className: 'w-24 text-center',
      render: (p) => (
        <Badge
          variant={p.estado === 'ACTIVO' ? 'success' : 'neutral'}
          showDot
          size="sm"
        >
          {p.estado}
        </Badge>
      ),
    },
    {
      header: 'Acciones',
      key: 'actions',
      className: 'w-28 text-right',
      render: (p) => (
        <Button
          size="sm"
          variant="outline"
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/pacientes/${p.id}`);
          }}
          className="text-xs h-7 px-2"
        >
          Ver Ficha
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-4 min-w-0">
      {/* Cabecera de la sección */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-lg font-bold text-slate-900 tracking-tight">
            Gestión de Pacientes
          </h2>
          <p className="text-xs text-slate-500 mt-0.5 font-sans">
            Registro de pacientes y archivo de estudios fotográficos intraorales
          </p>
        </div>

        <Button
          variant="primary"
          icon={UserPlus}
          onClick={() => setIsModalOpen(true)}
          className="w-full sm:w-auto"
        >
          Registrar Paciente
        </Button>
      </div>

      {/* Barra de búsqueda clínica */}
      <div className="bg-white p-2.5 sm:p-3 border border-slate-200 rounded-xl shadow-subtle flex items-center gap-2.5">
        <Search className="w-4 h-4 text-slate-400 shrink-0 ml-1" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setPage(1);
          }}
          placeholder="Buscar por DNI, nombres o apellidos del paciente..."
          className="w-full text-sm bg-transparent border-none focus:outline-none placeholder:text-slate-400 font-sans"
        />
        {searchTerm && (
          <button
            type="button"
            onClick={() => setSearchTerm('')}
            className="text-xs text-slate-400 hover:text-slate-600 px-2 py-0.5 font-sans shrink-0"
          >
            Limpiar
          </button>
        )}
      </div>

      {/* Condicional estricto: Error vs Tabla/Empty State */}
      {error ? (
        <div className="bg-white border border-rose-200 rounded-xl p-6 shadow-subtle flex flex-col items-center justify-center text-center space-y-3">
          <div className="w-10 h-10 rounded-full bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600">
            <AlertCircle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-900">
              No fue posible sincronizar el listado de pacientes
            </h3>
            <p className="text-xs text-slate-500 mt-1 max-w-md font-sans">
              Verifique su conexión de red o contacte al administrador del sistema.
            </p>
          </div>
          <Button
            size="sm"
            variant="secondary"
            icon={RefreshCw}
            onClick={handleRetry}
            isLoading={isRefetching}
            className="mt-1 text-xs border-slate-300 text-slate-700 hover:bg-slate-50"
          >
            Reintentar
          </Button>
        </div>
      ) : (
        <>
          {/* Vista Desktop: Tabla clínica completa */}
          <div className="hidden md:block">
            <Table
              columns={columns}
              data={paginatedData}
              isLoading={isLoading}
              emptyMessage={searchTerm ? 'No se encontraron pacientes' : 'No hay pacientes registrados'}
              emptyDescription={
                searchTerm
                  ? 'No hay coincidencias para el criterio de búsqueda ingresado.'
                  : 'Comience registrando el primer paciente para iniciar la captura de fotografías intraorales.'
              }
              emptyAction={
                searchTerm ? (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setSearchTerm('')}
                    className="text-xs"
                  >
                    Limpiar búsqueda
                  </Button>
                ) : (
                  <Button
                    size="sm"
                    variant="primary"
                    icon={UserPlus}
                    onClick={() => setIsModalOpen(true)}
                    className="text-xs"
                  >
                    Registrar Paciente
                  </Button>
                )
              }
              onRowClick={(p) => navigate(`/pacientes/${p.id}`)}
              pagination={
                filteredPacientes.length > pageSize
                  ? {
                      page,
                      pageSize,
                      total: filteredPacientes.length,
                      onPageChange: (newPage) => setPage(newPage),
                    }
                  : null
              }
            />
          </div>

          {/* Vista Mobile (< md): Lista de tarjetas táctiles responsivas */}
          <div className="md:hidden space-y-3">
            {isLoading ? (
              <div className="bg-white border border-slate-200 rounded-xl p-8 text-center text-xs text-slate-500 font-sans shadow-subtle">
                Cargando pacientes...
              </div>
            ) : paginatedData.length === 0 ? (
              <EmptyState
                title={searchTerm ? 'No se encontraron pacientes' : 'No hay pacientes registrados'}
                description={
                  searchTerm
                    ? 'No hay coincidencias para el criterio de búsqueda ingresado.'
                    : 'Comience registrando el primer paciente para iniciar la captura de fotografías intraorales.'
                }
                action={
                  searchTerm ? (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setSearchTerm('')}
                      className="text-xs w-full"
                    >
                      Limpiar búsqueda
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      variant="primary"
                      icon={UserPlus}
                      onClick={() => setIsModalOpen(true)}
                      className="text-xs w-full"
                    >
                      Registrar Paciente
                    </Button>
                  )
                }
              />
            ) : (
              <>
                <div className="space-y-2.5">
                  {paginatedData.map((paciente) => (
                    <PacienteCard
                      key={paciente.id}
                      paciente={paciente}
                      onSelect={(p) => navigate(`/pacientes/${p.id}`)}
                    />
                  ))}
                </div>

                {/* Paginación Mobile */}
                {filteredPacientes.length > pageSize && (
                  <div className="flex items-center justify-between p-3 bg-white border border-slate-200 rounded-xl shadow-subtle text-xs text-slate-500">
                    <span>
                      Pág. <span className="font-semibold text-slate-800">{page}</span> de <span className="font-semibold text-slate-800">{Math.ceil(filteredPacientes.length / pageSize)}</span>
                    </span>
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        disabled={page <= 1}
                        onClick={() => setPage(page - 1)}
                        className="w-8 h-8 flex items-center justify-center rounded-lg border border-slate-300 bg-white text-slate-600 disabled:opacity-40"
                        aria-label="Página anterior"
                      >
                        <ChevronLeft className="w-4 h-4" />
                      </button>
                      <button
                        type="button"
                        disabled={page >= Math.ceil(filteredPacientes.length / pageSize)}
                        onClick={() => setPage(page + 1)}
                        className="w-8 h-8 flex items-center justify-center rounded-lg border border-slate-300 bg-white text-slate-600 disabled:opacity-40"
                        aria-label="Página siguiente"
                      >
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </>
      )}

      {/* Modal para registrar nuevo paciente */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setErrorMessage(null);
        }}
        title="Registrar Nuevo Paciente"
        subtitle="Identificación oficial e información de contacto clínica"
      >
        {errorMessage && (
          <div className="mb-4 p-3 bg-rose-50 border border-rose-200 rounded-md text-xs text-rose-700 flex items-center gap-2 font-sans">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}
        <PacienteForm
          onSubmit={handleCreateSubmit}
          isLoading={crearPacienteMutation.isPending}
          onCancel={() => {
            setIsModalOpen(false);
            setErrorMessage(null);
          }}
        />
      </Modal>
    </div>
  );
};
