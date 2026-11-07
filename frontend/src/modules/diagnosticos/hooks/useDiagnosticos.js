import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { diagnosticosApi } from '../../../api/diagnosticos.api';

/**
 * Hook para obtener el detalle de un diagnóstico con sus hallazgos y bounding boxes
 */
export function useDiagnosticoDetail(diagnosticoId) {
  return useQuery({
    queryKey: ['diagnostico', diagnosticoId],
    queryFn: () => diagnosticosApi.obtenerPorId(diagnosticoId),
    enabled: !!diagnosticoId,
    staleTime: 1000 * 60, // 1 minuto
  });
}

/**
 * Hook para validar un diagnóstico sugerido por IA con notas clínicas
 */
export function useValidarDiagnostico() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, odontologo_id, notas }) =>
      diagnosticosApi.validar(id, { odontologo_id, notas }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['diagnostico', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['cola_revision'] });
    },
  });
}

/**
 * Hook para rechazar un diagnóstico con motivo clínico obligatorio
 */
export function useRechazarDiagnostico() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, odontologo_id, motivo }) =>
      diagnosticosApi.rechazar(id, { odontologo_id, motivo }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['diagnostico', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['cola_revision'] });
    },
  });
}
