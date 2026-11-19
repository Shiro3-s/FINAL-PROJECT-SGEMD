import { useState } from 'react';
import type { AttachmentEntity } from '../queries/attachments.ts';
import { useUploadAttachment } from '../queries/attachments.ts';
import { errorMessage } from './States.tsx';
import { useToast } from './Toast.tsx';
import { Dropzone } from './Dropzone.tsx';

interface EvidenceUploaderProps {
  entity: AttachmentEntity;
  entityId: number;
  /** Conteo que devuelve el DTO del padre; es lo único que expone la API. */
  count: number;
  disabled?: boolean;
  note?: string;
}

/**
 * Carga de evidencias de una tarea, seguimiento o asesoría.
 *
 * La API **no lista** los adjuntos de la entidad: el DTO solo trae
 * `evidencias`. Aquí se muestra ese conteo y se permite subir; no se inventa una
 * tabla de archivos con nombres que el servidor no devuelve.
 */
export function EvidenceUploader({
  entity,
  entityId,
  count,
  disabled = false,
  note,
}: EvidenceUploaderProps) {
  const upload = useUploadAttachment();
  const { showToast } = useToast();
  const [progress, setProgress] = useState<number | null>(null);

  return (
    <>
      <p className="ayuda" style={{ marginTop: 0 }}>
        Evidencias cargadas: <b>{count}</b>.{' '}
        {note ??
          'La API no publica la lista de archivos, así que esta vista no ofrece descargas de evidencias anteriores.'}
      </p>
      <Dropzone
        disabled={disabled || upload.isPending}
        progress={progress}
        onFile={(file) => {
          setProgress(0);
          upload.mutate(
            {
              entity,
              id: entityId,
              file,
              onProgress: setProgress,
            },
            {
              onSuccess: () => {
                showToast('Evidencia subida.', 'ok');
                setProgress(null);
              },
              onError: (error) => {
                showToast(errorMessage(error), 'error');
                setProgress(null);
              },
            },
          );
        }}
      />
      {disabled ? (
        <p className="ayuda">La evidencia está congelada mientras el registro no admita cambios.</p>
      ) : null}
    </>
  );
}
