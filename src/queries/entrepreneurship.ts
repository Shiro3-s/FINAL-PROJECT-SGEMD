import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiGet, apiSend, withQuery, type QueryParams } from '../api/client.ts';
import type { Entrepreneurship, Paginated } from '../api/types.ts';

/** Emprendimientos (`/entrepreneurship`, §7.5). */

export const entrepreneurshipKeys = {
  all: ['entrepreneurship'] as const,
  list: (filters: QueryParams) => ['entrepreneurship', 'list', filters] as const,
  detail: (id: number) => ['entrepreneurship', 'detail', id] as const,
};

export interface EntrepreneurshipFilters {
  page?: number;
  pageSize?: number;
  q?: string;
  estado?: string;
  etapaId?: number;
  sectorId?: number;
  centroId?: number;
  estudianteId?: number;
  sort?: string;
  order?: string;
}

export function useEntrepreneurships(filters: EntrepreneurshipFilters = {}) {
  const params: QueryParams = {
    page: filters.page ?? 1,
    pageSize: filters.pageSize ?? 25,
    q: filters.q,
    estado: filters.estado,
    etapaId: filters.etapaId,
    sectorId: filters.sectorId,
    centroId: filters.centroId,
    estudianteId: filters.estudianteId,
    sort: filters.sort,
    order: filters.order,
  };
  return useQuery({
    queryKey: entrepreneurshipKeys.list(params),
    queryFn: () => apiGet<Paginated<Entrepreneurship>>(withQuery('/entrepreneurship', params)),
  });
}

export function useEntrepreneurship(id: number | null) {
  return useQuery({
    queryKey: entrepreneurshipKeys.detail(id ?? 0),
    queryFn: () => apiGet<Entrepreneurship>(`/entrepreneurship/${id}`),
    enabled: id !== null && Number.isFinite(id),
  });
}

function useInvalidate() {
  const queryClient = useQueryClient();
  return () => void queryClient.invalidateQueries({ queryKey: entrepreneurshipKeys.all });
}

export function useCreateEntrepreneurship() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      apiSend<Entrepreneurship>('POST', '/entrepreneurship', body),
    onSuccess: invalidate,
  });
}

export function useUpdateEntrepreneurship(id: number) {
  const queryClient = useQueryClient();
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      apiSend<Entrepreneurship>('PUT', `/entrepreneurship/${id}`, body),
    onSuccess: (data) => {
      queryClient.setQueryData(entrepreneurshipKeys.detail(id), data);
      invalidate();
    },
  });
}

export function useApproveEntrepreneurship() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (id: number) =>
      apiSend<Entrepreneurship>('POST', `/entrepreneurship/${id}/approve`),
    onSuccess: invalidate,
  });
}

export function useRejectEntrepreneurship() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: ({ id, motivo }: { id: number; motivo: string }) =>
      apiSend<Entrepreneurship>('POST', `/entrepreneurship/${id}/reject`, { motivo }),
    onSuccess: invalidate,
  });
}

export function useDeleteEntrepreneurship() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (id: number) => apiSend<unknown>('DELETE', `/entrepreneurship/${id}`),
    onSuccess: invalidate,
  });
}
