import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiGet, apiSend, withQuery } from '../api/client.ts';
import type { Paginated, Tracing } from '../api/types.ts';

/** Seguimientos (`/tracing`, FR-022). No hay listado global: cuelgan del expediente. */

export const tracingKeys = {
  all: ['tracing'] as const,
  byEntrepreneurship: (id: number) => ['tracing', 'entrepreneurship', id] as const,
  detail: (id: number) => ['tracing', 'detail', id] as const,
};

export function useTracings(entrepreneurshipId: number | null) {
  return useQuery({
    queryKey: tracingKeys.byEntrepreneurship(entrepreneurshipId ?? 0),
    queryFn: () =>
      apiGet<Paginated<Tracing>>(
        withQuery(`/tracing/entrepreneurship/${entrepreneurshipId}`, { pageSize: 100 }),
      ),
    enabled: entrepreneurshipId !== null && Number.isFinite(entrepreneurshipId),
  });
}

export function useTracing(id: number | null) {
  return useQuery({
    queryKey: tracingKeys.detail(id ?? 0),
    queryFn: () => apiGet<Tracing>(`/tracing/${id}`),
    enabled: id !== null && Number.isFinite(id),
  });
}

function useInvalidate() {
  const queryClient = useQueryClient();
  return () => {
    void queryClient.invalidateQueries({ queryKey: tracingKeys.all });
    void queryClient.invalidateQueries({ queryKey: ['dashboard'] });
  };
}

export function useCreateTracing() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (body: Record<string, unknown>) => apiSend<Tracing>('POST', '/tracing', body),
    onSuccess: invalidate,
  });
}

export function useUpdateTracing(id: number) {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (body: Record<string, unknown>) => apiSend<Tracing>('PUT', `/tracing/${id}`, body),
    onSuccess: invalidate,
  });
}

export function useDeleteTracing() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (id: number) => apiSend<unknown>('DELETE', `/tracing/${id}`),
    onSuccess: invalidate,
  });
}
