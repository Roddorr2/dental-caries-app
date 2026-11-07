import { useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { inferenciasApi } from '../../../api/inferencias.api';

/**
 * Hook para monitorear el pipeline de inferencia IA con polling cada 2s
 * hasta que el estado sea COMPLETADO o FALLIDO.
 * Al completar, invalida las queries del estudio y de la cola de revisión.
 *
 * @param {string|null} inferenciaId - UUID de la inferencia
 * @param {string|null} estudioId - UUID del estudio asociado para invalidar
 */
export function useInferencia(inferenciaId, estudioId = null) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ['inferencia', inferenciaId],
    queryFn: () => inferenciasApi.obtenerPorId(inferenciaId),
    enabled: !!inferenciaId,
    refetchInterval: (queryState) => {
      const data = queryState.state.data;
      if (!data) return 2000;
      // Detener polling cuando el pipeline termine
      if (data.estado === 'COMPLETADO' || data.estado === 'FALLIDO') {
        return false;
      }
      return 2000; // Polling estricto cada 2 segundos según especificación
    },
    refetchIntervalInBackground: true,
  });

  // Efecto para invalidar el estudio cuando se complete la inferencia
  useEffect(() => {
    if (query.data?.estado === 'COMPLETADO') {
      if (estudioId) {
        queryClient.invalidateQueries({ queryKey: ['estudio', estudioId] });
      }
      queryClient.invalidateQueries({ queryKey: ['cola_revision'] });
    }
  }, [query.data?.estado, estudioId, queryClient]);

  const isCompleted = query.data?.estado === 'COMPLETADO';
  const isFailed = query.data?.estado === 'FALLIDO';
  const isProcessing = query.data?.estado === 'PENDIENTE' || query.data?.estado === 'EN_PROCESO';

  return {
    ...query,
    inferencia: query.data,
    isCompleted,
    isFailed,
    isProcessing,
  };
}
