import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiGet, apiSend, withQuery, type QueryParams } from '../api/client.ts';
import type { Paginated, Task } from '../api/types.ts';

/** Tareas (`/task`, §7.7). */

export const taskKeys = {
  all: ['task'] as const,
  list: (filters: QueryParams) => ['task', 'list', filters] as const,
  detail: (id: number) => ['task', 'detail', id] as const,
  byEntrepreneurship: (id: number) => ['task', 'entrepreneurship', id] as const,
  advance: (id: number) => ['task', 'advance', id] as const,
};

export interface TaskFilters {
  page?: number;
  pageSize?: number;
  q?: string;
  estado?: string;
  estadoRevision?: string;
  prioridad?: string;
  emprendimientoId?: number;
  estudianteId?: number;
  fasePlanId?: number;
  sort?: string;
  order?: string;
}

export function useTasks(filters: TaskFilters = {}) {
  const params: QueryParams = {
    page: filters.page ?? 1,
    pageSize: filters.pageSize ?? 25,
    q: filters.q,
    estado: filters.estado,
    estadoRevision: filters.estadoRevision,
    prioridad: filters.prioridad,
    emprendimientoId: filters.emprendimientoId,
    estudianteId: filters.estudianteId,
    fasePlanId: filters.fasePlanId,
    sort: filters.sort,
    order: filters.order,
  };
  return useQuery({
    queryKey: taskKeys.list(params),
    queryFn: () => apiGet<Paginated<Task>>(withQuery('/task', params)),
  });
}

export function useTask(id: number | null) {
  return useQuery({
    queryKey: taskKeys.detail(id ?? 0),
    queryFn: () => apiGet<Task>(`/task/${id}`),
    enabled: id !== null && Number.isFinite(id),
  });
}

export function useEntrepreneurshipTasks(id: number | null) {
  return useQuery({
    queryKey: taskKeys.byEntrepreneurship(id ?? 0),
    queryFn: () => apiGet<Paginated<Task>>(withQuery(`/task/entrepreneurship/${id}`, { pageSize: 100 })),
    enabled: id !== null && Number.isFinite(id),
  });
}

export interface AdvanceByPhase {
  emprendimientoId: number;
  avance: number;
  total: number;
  completadas: number;
  fases: {
    faseId: number | null;
    fase: string | null;
    total: number;
    completadas: number;
    porcentaje: number;
  }[];
}

export function useTaskAdvance(id: number | null) {
  return useQuery({
    queryKey: taskKeys.advance(id ?? 0),
    queryFn: () => apiGet<AdvanceByPhase>(`/task/advance/entrepreneurship/${id}`),
    enabled: id !== null && Number.isFinite(id),
  });
}

function useInvalidate() {
  const queryClient = useQueryClient();
  return () => {
    void queryClient.invalidateQueries({ queryKey: taskKeys.all });
    void queryClient.invalidateQueries({ queryKey: ['entrepreneurship'] });
    void queryClient.invalidateQueries({ queryKey: ['dashboard'] });
  };
}

export function useCreateTask() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (body: Record<string, unknown>) => apiSend<Task>('POST', '/task', body),
    onSuccess: invalidate,
  });
}

export function useUpdateTask(id: number) {
  const queryClient = useQueryClient();
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (body: Record<string, unknown>) => apiSend<Task>('PUT', `/task/${id}`, body),
    onSuccess: (data) => {
      queryClient.setQueryData(taskKeys.detail(id), data);
      invalidate();
    },
  });
}

/** Entrega del estudiante. El servidor exige al menos una evidencia. */
export function useCompleteTask() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (id: number) => apiSend<Task>('PUT', `/task/${id}/complete`),
    onSuccess: invalidate,
  });
}

export function useGradeTask() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: ({
      id,
      puntajeObtenido,
      retroalimentacion,
    }: {
      id: number;
      puntajeObtenido: number;
      retroalimentacion: string;
    }) =>
      apiSend<Task>('PUT', `/task/${id}/grade`, { puntajeObtenido, retroalimentacion }),
    onSuccess: invalidate,
  });
}

export function useReturnTask() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: ({ id, motivo, observaciones }: { id: number; motivo: string; observaciones?: string }) =>
      apiSend<Task>('PUT', `/task/${id}/return`, { motivo, observaciones }),
    onSuccess: invalidate,
  });
}

export function useDeleteTask() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (id: number) => apiSend<unknown>('DELETE', `/task/${id}`),
    onSuccess: invalidate,
  });
}
