import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiGet, apiSend, withQuery, type QueryParams } from '../api/client.ts';
import type { Assignment, Paginated } from '../api/types.ts';

/** Asignaciones mentor → emprendimiento (`/assignments`, §7.6). */

export const assignmentKeys = {
  all: ['assignments'] as const,
  list: (filters: QueryParams) => ['assignments', 'list', filters] as const,
  detail: (id: number) => ['assignments', 'detail', id] as const,
};

export interface AssignmentFilters {
  page?: number;
  pageSize?: number;
  q?: string;
  estado?: string;
  mentorId?: number;
  estudianteId?: number;
  emprendimientoId?: number;
  sort?: string;
  order?: string;
}

export function useAssignments(filters: AssignmentFilters = {}) {
  const params: QueryParams = {
    page: filters.page ?? 1,
    pageSize: filters.pageSize ?? 25,
    q: filters.q,
    estado: filters.estado,
    mentorId: filters.mentorId,
    estudianteId: filters.estudianteId,
    emprendimientoId: filters.emprendimientoId,
    sort: filters.sort,
    order: filters.order,
  };
  return useQuery({
    queryKey: assignmentKeys.list(params),
    queryFn: () => apiGet<Paginated<Assignment>>(withQuery('/assignments', params)),
  });
}

export function useAssignment(id: number | null) {
  return useQuery({
    queryKey: assignmentKeys.detail(id ?? 0),
    queryFn: () => apiGet<Assignment>(`/assignments/${id}`),
    enabled: id !== null && Number.isFinite(id),
  });
}

function useInvalidate() {
  const queryClient = useQueryClient();
  return () => {
    void queryClient.invalidateQueries({ queryKey: assignmentKeys.all });
    void queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    void queryClient.invalidateQueries({ queryKey: ['entrepreneurship'] });
  };
}

export function useCreateAssignment() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (body: { mentorId: number; emprendimientoId: number; horasSemanales: number }) =>
      apiSend<Assignment>('POST', '/assignments', body),
    onSuccess: invalidate,
  });
}

export function useUpdateAssignment(id: number) {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (body: { mentorId?: number; horasSemanales?: number }) =>
      apiSend<Assignment>('PUT', `/assignments/${id}`, body),
    onSuccess: invalidate,
  });
}

export function useDeleteAssignment() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (id: number) => apiSend<unknown>('DELETE', `/assignments/${id}`),
    onSuccess: invalidate,
  });
}
