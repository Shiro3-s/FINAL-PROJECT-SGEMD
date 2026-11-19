import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiGet, apiSend, withQuery, type QueryParams } from '../api/client.ts';
import type { RequestItem, RequestPage } from '../api/types.ts';

/** Solicitudes (`/requests`, R38). La bandeja es solo del administrador. */

export const requestKeys = {
  all: ['requests'] as const,
  list: (filters: QueryParams) => ['requests', 'list', filters] as const,
  detail: (id: number) => ['requests', 'detail', id] as const,
};

export interface RequestFilters {
  page?: number;
  pageSize?: number;
  tipo?: string;
  estado?: string;
  q?: string;
  sort?: string;
  order?: string;
}

export function useRequests(filters: RequestFilters = {}) {
  const params: QueryParams = {
    page: filters.page ?? 1,
    pageSize: filters.pageSize ?? 25,
    tipo: filters.tipo,
    estado: filters.estado,
    q: filters.q,
    sort: filters.sort,
    order: filters.order,
  };
  return useQuery({
    queryKey: requestKeys.list(params),
    queryFn: () => apiGet<RequestPage>(withQuery('/requests', params)),
  });
}

export function useRequest(id: number | null) {
  return useQuery({
    queryKey: requestKeys.detail(id ?? 0),
    queryFn: () => apiGet<RequestItem>(`/requests/${id}`),
    enabled: id !== null && Number.isFinite(id),
  });
}

function useInvalidate() {
  const queryClient = useQueryClient();
  return () => {
    void queryClient.invalidateQueries({ queryKey: requestKeys.all });
    void queryClient.invalidateQueries({ queryKey: ['users'] });
    void queryClient.invalidateQueries({ queryKey: ['advice'] });
    void queryClient.invalidateQueries({ queryKey: ['entrepreneurship'] });
    void queryClient.invalidateQueries({ queryKey: ['dashboard'] });
  };
}

export function useCreateRequest() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: { tipo: string; detalle: string; emprendimientoId?: number | null }) =>
      apiSend<RequestItem>('POST', '/requests', body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: requestKeys.all });
      void queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
}

export function useApproveRequest() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: ({ id, body }: { id: number; body?: Record<string, unknown> }) =>
      apiSend<RequestItem>('PUT', `/requests/${id}/approve`, body),
    onSuccess: invalidate,
  });
}

export function useRejectRequest() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: ({ id, motivo }: { id: number; motivo: string }) =>
      apiSend<RequestItem>('PUT', `/requests/${id}/reject`, { motivo }),
    onSuccess: invalidate,
  });
}
