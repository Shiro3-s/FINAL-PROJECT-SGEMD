import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiGet, apiSend, withQuery, type QueryParams } from '../api/client.ts';
import type { Advice, Paginated } from '../api/types.ts';

/** Asesorías (`/advice`, FR-004, BR-002). */

export const adviceKeys = {
  all: ['advice'] as const,
  list: (filters: QueryParams) => ['advice', 'list', filters] as const,
  detail: (id: number) => ['advice', 'detail', id] as const,
};

export interface AdviceFilters {
  page?: number;
  pageSize?: number;
  estado?: string;
  grupo?: 'Agendada';
  docenteId?: number;
  estudianteId?: number;
  emprendimientoId?: number;
  modalidadId?: number;
  q?: string;
  desde?: string;
  hasta?: string;
  sort?: string;
  order?: string;
}

export function useAdvices(filters: AdviceFilters = {}) {
  const params: QueryParams = {
    page: filters.page ?? 1,
    pageSize: filters.pageSize ?? 25,
    estado: filters.estado,
    grupo: filters.grupo,
    docenteId: filters.docenteId,
    estudianteId: filters.estudianteId,
    emprendimientoId: filters.emprendimientoId,
    modalidadId: filters.modalidadId,
    q: filters.q,
    desde: filters.desde,
    hasta: filters.hasta,
    sort: filters.sort,
    order: filters.order,
  };
  return useQuery({
    queryKey: adviceKeys.list(params),
    queryFn: () => apiGet<Paginated<Advice>>(withQuery('/advice', params)),
  });
}

export function useAdvice(id: number | null) {
  return useQuery({
    queryKey: adviceKeys.detail(id ?? 0),
    queryFn: () => apiGet<Advice>(`/advice/${id}`),
    enabled: id !== null && Number.isFinite(id),
  });
}

function useInvalidate() {
  const queryClient = useQueryClient();
  return () => {
    void queryClient.invalidateQueries({ queryKey: adviceKeys.all });
    void queryClient.invalidateQueries({ queryKey: ['dashboard'] });
  };
}

export function useCreateAdvice() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (body: Record<string, unknown>) => apiSend<Advice>('POST', '/advice', body),
    onSuccess: invalidate,
  });
}

export function useUpdateAdvice(id: number) {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (body: Record<string, unknown>) => apiSend<Advice>('PUT', `/advice/${id}`, body),
    onSuccess: invalidate,
  });
}

export function useAcceptAdvice() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: ({ id, block }: { id: number; block?: Record<string, unknown> }) =>
      apiSend<Advice>('POST', `/advice/${id}/accept`, block),
    onSuccess: invalidate,
  });
}

export function useReproposeAdvice() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: ({ id, block }: { id: number; block: Record<string, unknown> }) =>
      apiSend<Advice>('POST', `/advice/${id}/repropose`, block),
    onSuccess: invalidate,
  });
}

export function useRejectAdvice() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: ({ id, motivo }: { id: number; motivo: string }) =>
      apiSend<Advice>('POST', `/advice/${id}/reject`, { motivo }),
    onSuccess: invalidate,
  });
}

export function useDeleteAdvice() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (id: number) => apiSend<unknown>('DELETE', `/advice/${id}`),
    onSuccess: invalidate,
  });
}
