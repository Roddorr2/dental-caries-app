import { useQuery } from '@tanstack/react-query';
import { diagnosticosApi } from '../../../api/diagnosticos.api';

/**
 * Hook para consultar la cola de diagnósticos pendientes de revisión
 * (CQRS Read Model: rm_cola_revision)
 *
 * @param {Object} [options]
 * @param {boolean} [options.soloSagundaOpinion=false] - Filtrar casos de confianza BAJA
 * @param {number} [options.limit=20]
 * @param {number} [options.offset=0]
 * @param {boolean} [options.autoRefresh=false]
 */
export function useColaRevision({
  soloSegundaOpinion = false,
  limit = 20,
  offset = 0,
  autoRefresh = false,
} = {}) {
  return useQuery({
    queryKey: ['cola_revision', { soloSegundaOpinion, limit, offset }],
    queryFn: () =>
      diagnosticosApi.obtenerColaRevision({
        solo_segunda_opinion: soloSegundaOpinion,
        limit,
        offset,
      }),
    refetchInterval: autoRefresh ? 5000 : false,
    staleTime: 1000 * 15,
  });
}
