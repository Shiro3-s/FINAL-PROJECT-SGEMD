import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiDownload, apiSend, apiUpload } from '../api/client.ts';
import type { Attachment } from '../api/types.ts';

/**
 * Evidencias (`/attachments`, FR-008).
 *
 * La API no publica el listado de adjuntos de una tarea, seguimiento o
 * asesoría: el DTO solo trae el conteo (`evidencias`). Por eso aquí solo hay
 * subida, descarga por id (cuando se conoce) y baja. El hueco queda registrado
 * en `docs/decisions.md` y `docs/verification.md`.
 */
export type AttachmentEntity = 'task' | 'tracing' | 'advice';

export function useUploadAttachment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      entity,
      id,
      file,
      onProgress,
    }: {
      entity: AttachmentEntity;
      id: number;
      file: File;
      onProgress?: (percent: number) => void;
    }) => apiUpload<Attachment>(`/attachments/${entity}/${id}`, file, { onProgress }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['task'] });
      void queryClient.invalidateQueries({ queryKey: ['tracing'] });
      void queryClient.invalidateQueries({ queryKey: ['advice'] });
    },
  });
}

export function useDeleteAttachment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => apiSend<unknown>('DELETE', `/attachments/${id}`),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['task'] });
      void queryClient.invalidateQueries({ queryKey: ['tracing'] });
      void queryClient.invalidateQueries({ queryKey: ['advice'] });
    },
  });
}

export function useDownloadAttachment() {
  return useMutation({
    mutationFn: ({ id, filename }: { id: number; filename?: string }) =>
      apiDownload(`/attachments/${id}`, filename ?? 'evidencia'),
  });
}
