import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ApiError,
  apiDownload,
  apiGet,
  apiSend,
  apiUpload,
  withQuery,
  type QueryParams,
} from '../api/client.ts';
import type { Acta, Paginated } from '../api/types.ts';

/** Actas (`/acta`, FR-003, BR-001, BR-009). */

export const actaKeys = {
  all: ['acta'] as const,
  list: (filters: QueryParams) => ['acta', 'list', filters] as const,
  detail: (id: number) => ['acta', 'detail', id] as const,
  template: ['acta', 'template'] as const,
};

export interface ActaFilters {
  page?: number;
  pageSize?: number;
  q?: string;
  estado?: string;
  emprendimientoId?: number;
  estudianteId?: number;
  sort?: string;
  order?: string;
}

export function useActas(filters: ActaFilters = {}) {
  const params: QueryParams = {
    page: filters.page ?? 1,
    pageSize: filters.pageSize ?? 25,
    q: filters.q,
    estado: filters.estado,
    emprendimientoId: filters.emprendimientoId,
    estudianteId: filters.estudianteId,
    sort: filters.sort,
    order: filters.order,
  };
  return useQuery({
    queryKey: actaKeys.list(params),
    queryFn: () => apiGet<Paginated<Acta>>(withQuery('/acta', params)),
  });
}

export function useActa(id: number | null) {
  return useQuery({
    queryKey: actaKeys.detail(id ?? 0),
    queryFn: () => apiGet<Acta>(`/acta/${id}`),
    enabled: id !== null && Number.isFinite(id),
  });
}

/**
 * Plantilla del acta. El repositorio no tiene el texto legal: la API responde
 * `404 ACTA_TEMPLATE_NOT_CONFIGURED` y la vista lo declara (P-36). Se devuelve
 * `null` para no tratarlo como error de carga.
 */
export function useActaTemplate(enabled: boolean) {
  return useQuery({
    queryKey: actaKeys.template,
    queryFn: async () => {
      try {
        return await apiDownload('/acta/template', 'acta-sgemd.pdf');
      } catch (error) {
        if (error instanceof ApiError && error.code === 'ACTA_TEMPLATE_NOT_CONFIGURED') return null;
        throw error;
      }
    },
    enabled,
    retry: false,
  });
}

export function useUploadActa() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      file,
      onProgress,
    }: {
      file: File;
      onProgress?: (percent: number) => void;
    }) => apiUpload<Acta>('/acta', file, { onProgress }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: actaKeys.all });
      void queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function useReviewActa() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      decision,
      observaciones,
    }: {
      id: number;
      decision: 'Aprobada' | 'Rechazada';
      observaciones?: string;
    }) =>
      apiSend<Acta>('PUT', `/acta/${id}/review`, {
        estado: decision,
        ...(decision === 'Rechazada' ? { observaciones } : {}),
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: actaKeys.all });
      void queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      void queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
}
