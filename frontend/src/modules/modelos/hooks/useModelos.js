import { useQuery } from '@tanstack/react-query';
import { modelosApi } from '../../../api/modelos.api';

/**
 * Hook para listar los modelos ML registrados en el sistema
 */
export function useModelosList() {
  return useQuery({
    queryKey: ['modelos'],
    queryFn: () => modelosApi.listar(),
    staleTime: 1000 * 60 * 5, // 5 minutos
  });
}

/**
 * Hook para consultar las métricas de rendimiento en producción de un modelo
 * (CQRS Read Model: rm_estadisticas_modelo)
 */
export function useModeloEstadisticas(modeloId) {
  return useQuery({
    queryKey: ['modelo_estadisticas', modeloId],
    queryFn: () => modelosApi.obtenerEstadisticas(modeloId),
    enabled: !!modeloId,
    staleTime: 1000 * 60 * 2,
  });
}
