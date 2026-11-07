import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { pacientesApi } from '../../../api/pacientes.api';

/**
 * Hook para listar pacientes con paginación
 */
export function usePacientesList({ limit = 50, offset = 0 } = {}) {
  return useQuery({
    queryKey: ['pacientes', { limit, offset }],
    queryFn: () => pacientesApi.listar({ limit, offset }),
    staleTime: 1000 * 60 * 2, // 2 minutos
  });
}

/**
 * Hook para obtener el perfil de un paciente por su ID
 */
export function usePacienteDetail(pacienteId) {
  return useQuery({
    queryKey: ['paciente', pacienteId],
    queryFn: () => pacientesApi.obtenerPorId(pacienteId),
    enabled: !!pacienteId,
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook de mutación para registrar un nuevo paciente
 */
export function useCrearPaciente() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data) => pacientesApi.registrar(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pacientes'] });
    },
  });
}
