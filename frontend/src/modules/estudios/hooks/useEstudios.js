import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { estudiosApi } from '../../../api/estudios.api';

/**
 * Hook para listar estudios fotográficos clínicos
 */
export function useEstudiosList(filters = {}) {
  return useQuery({
    queryKey: ['estudios', filters],
    queryFn: () => estudiosApi.listar(filters),
    staleTime: 1000 * 15, // 15 segundos
  });
}

/**
 * Hook para consultar el detalle de un estudio imagenológico
 */
export function useEstudioDetail(estudioId) {
  return useQuery({
    queryKey: ['estudio', estudioId],
    queryFn: () => estudiosApi.obtenerPorId(estudioId),
    enabled: !!estudioId,
    staleTime: 1000 * 30, // 30 segundos
  });
}


/**
 * Hook para crear un nuevo estudio clínico
 */
export function useCrearEstudio() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data) => estudiosApi.crear(data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['estudios'] });
      return data;
    },
  });
}

/**
 * Hook para agregar una imagen a un estudio existente
 */
export function useAgregarImagen(estudioId) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (imagenData) => estudiosApi.agregarImagen(estudioId, imagenData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['estudio', estudioId] });
    },
  });
}

/**
 * Hook para solicitar análisis IA sobre el estudio
 */
export function useSolicitarAnalisis(estudioId) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (modeloMlId) => estudiosApi.solicitarAnalisis(estudioId, modeloMlId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['estudio', estudioId] });
    },
  });
}
