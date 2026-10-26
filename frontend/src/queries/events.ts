import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiGet, apiSend, withQuery, type QueryParams } from '../api/client.ts';
import type { EventItem, EventRecommendation, Paginated } from '../api/types.ts';

/** Eventos y recomendaciones (`/event`, FR-021). */

export const eventKeys = {
  all: ['event'] as const,
  list: (filters: QueryParams) => ['event', 'list', filters] as const,
  detail: (id: number) => ['event', 'detail', id] as const,
  recommendations: (id: number) => ['event', 'recommendations', id] as const,
};

export interface EventFilters {
  page?: number;
  pageSize?: number;
  q?: string;
  estado?: string;
  tipoEventoId?: number;
  modalidadId?: number;
  desde?: string;
  hasta?: string;
  sort?: string;
  order?: string;
}

export function useEvents(filters: EventFilters = {}) {
  const params: QueryParams = {
    page: filters.page ?? 1,
    pageSize: filters.pageSize ?? 25,
    q: filters.q,
    estado: filters.estado,
    tipoEventoId: filters.tipoEventoId,
    modalidadId: filters.modalidadId,
    desde: filters.desde,
    hasta: filters.hasta,
    sort: filters.sort,
    order: filters.order,
  };
  return useQuery({
    queryKey: eventKeys.list(params),
    queryFn: () => apiGet<Paginated<EventItem>>(withQuery('/event', params)),
  });
}

export function useEvent(id: number | null) {
  return useQuery({
    queryKey: eventKeys.detail(id ?? 0),
    queryFn: () => apiGet<EventItem>(`/event/${id}`),
    enabled: id !== null && Number.isFinite(id),
  });
}

export function useEventRecommendations(id: number | null) {
  return useQuery({
    queryKey: eventKeys.recommendations(id ?? 0),
    queryFn: () =>
      apiGet<Paginated<EventRecommendation>>(
        withQuery(`/event/${id}/recommendations`, { pageSize: 100 }),
      ),
    enabled: id !== null && Number.isFinite(id),
  });
}

function useInvalidate() {
  const queryClient = useQueryClient();
  return () => void queryClient.invalidateQueries({ queryKey: eventKeys.all });
}

export function useCreateEvent() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (body: Record<string, unknown>) => apiSend<EventItem>('POST', '/event', body),
    onSuccess: invalidate,
  });
}

export function useUpdateEvent(id: number) {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (body: Record<string, unknown>) => apiSend<EventItem>('PUT', `/event/${id}`, body),
    onSuccess: invalidate,
  });
}

export function useDeleteEvent() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (id: number) => apiSend<unknown>('DELETE', `/event/${id}`),
    onSuccess: invalidate,
  });
}

export function useRegisterEvent() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (id: number) => apiSend<EventItem>('POST', `/event/${id}/register`),
    onSuccess: invalidate,
  });
}

export function useUnregisterEvent() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (id: number) => apiSend<unknown>('DELETE', `/event/${id}/register`),
    onSuccess: invalidate,
  });
}

export function useRecommendEvent() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: ({
      id,
      emprendimientoId,
      mensaje,
    }: {
      id: number;
      emprendimientoId: number;
      mensaje?: string;
    }) =>
      apiSend<EventRecommendation>('POST', `/event/${id}/recommendations`, {
        emprendimientoId,
        mensaje,
      }),
    onSuccess: invalidate,
  });
}
