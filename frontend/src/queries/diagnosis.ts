import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiGet, apiSend, withQuery, type QueryParams } from '../api/client.ts';
import type {
  Characterization,
  Diagnosis,
  DiagnosisForm,
  Paginated,
} from '../api/types.ts';

/** Diagnóstico (`/diagnosis`, FR-002). Sin rúbrica no hay puntaje (AQ-09). */

export const diagnosisKeys = {
  all: ['diagnosis'] as const,
  form: ['diagnosis', 'form'] as const,
  list: (filters: QueryParams) => ['diagnosis', 'list', filters] as const,
  detail: (id: number) => ['diagnosis', 'detail', id] as const,
  me: (entrepreneurshipId?: number) => ['diagnosis', 'me', entrepreneurshipId ?? null] as const,
  characterization: (entrepreneurshipId?: number) =>
    ['diagnosis', 'characterization', entrepreneurshipId ?? null] as const,
  report: (id: number) => ['diagnosis', 'report', id] as const,
};

export interface DiagnosisFilters {
  page?: number;
  pageSize?: number;
  q?: string;
  estado?: string;
  emprendimientoId?: number;
  estudianteId?: number;
  sort?: string;
  order?: string;
}

export function useDiagnosisForm() {
  return useQuery({
    queryKey: diagnosisKeys.form,
    queryFn: () => apiGet<DiagnosisForm>('/diagnosis/form'),
    staleTime: Number.POSITIVE_INFINITY,
  });
}

export function useDiagnoses(filters: DiagnosisFilters = {}) {
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
    queryKey: diagnosisKeys.list(params),
    queryFn: () => apiGet<Paginated<Diagnosis>>(withQuery('/diagnosis', params)),
  });
}

export function useDiagnosis(id: number | null) {
  return useQuery({
    queryKey: diagnosisKeys.detail(id ?? 0),
    queryFn: () => apiGet<Diagnosis>(`/diagnosis/${id}`),
    enabled: id !== null && Number.isFinite(id),
  });
}

/** Diagnóstico propio. `422 ENTREPRENEURSHIP_REQUIRED` y `404` se manejan en la vista. */
export function useMyDiagnosis(entrepreneurshipId?: number) {
  return useQuery({
    queryKey: diagnosisKeys.me(entrepreneurshipId),
    queryFn: () =>
      apiGet<Diagnosis>(withQuery('/diagnosis/me', { emprendimientoId: entrepreneurshipId })),
    retry: false,
  });
}

export function useMyCharacterization(entrepreneurshipId?: number) {
  return useQuery({
    queryKey: diagnosisKeys.characterization(entrepreneurshipId),
    queryFn: () =>
      apiGet<Characterization>(
        withQuery('/characterization/me', { emprendimientoId: entrepreneurshipId }),
      ),
    retry: false,
  });
}

export interface DiagnosisReportResponse {
  diagnostico: Diagnosis;
  informe: {
    disponible: boolean;
    motivo: string;
    mensaje: string;
    urlInforme: string | null;
    generadoEn: string;
    secciones: {
      numero: number;
      titulo: string;
      puntaje: number | null;
      resultado: string | null;
      fortalezas: string | null;
      oportunidades: string | null;
    }[];
    valoracion: unknown[];
  };
}

export function useDiagnosisReport(id: number | null) {
  return useQuery({
    queryKey: diagnosisKeys.report(id ?? 0),
    queryFn: () => apiGet<DiagnosisReportResponse>(`/diagnosis/${id}/report`),
    enabled: id !== null && Number.isFinite(id),
  });
}

export function useSaveMyDiagnosis() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      emprendimientoId,
      respuestas,
      enviar,
    }: {
      emprendimientoId: number;
      respuestas: { preguntaId: number; valor: string }[];
      enviar: boolean;
    }) =>
      apiSend<Diagnosis>('POST', '/diagnosis/me', {
        emprendimientoId,
        respuestas,
        enviar,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: diagnosisKeys.all });
      void queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}
