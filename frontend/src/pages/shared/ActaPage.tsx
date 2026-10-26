import { useState } from 'react';
import { ApiError, apiDownload, saveDownload } from '../../api/client.ts';
import type { Acta } from '../../api/types.ts';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { Dropzone } from '../../components/Dropzone.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { EmptyState, ErrorState, LoadingState, errorMessage } from '../../components/States.tsx';
import { useToast } from '../../components/Toast.tsx';
import { formatDateTime } from '../../lib/format.ts';
import { useActas, useUploadActa } from '../../queries/acta.ts';

/**
 * Acta de compromiso del estudiante (FR-003, BR-001).
 *
 * La plantilla no está en el repositorio: `GET /acta/template` responde
 * `404 ACTA_TEMPLATE_NOT_CONFIGURED` (P-36). La vista declara ese hueco y deja
 * subir el archivo firmado que la coordinación haya entregado por otro canal.
 * Ninguna ruta del acta exige cuenta `Activo`: también la usa una cuenta
 * `Limitado` (AQ-07 opción A).
 */
export function ActaPage() {
  const { showToast } = useToast();
  const actas = useActas({ page: 1, pageSize: 5 });
  const upload = useUploadActa();
  const [progress, setProgress] = useState<number | null>(null);
  const [templateMissing, setTemplateMissing] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const latest: Acta | null = actas.data?.items[0] ?? null;
  const canUpload = !latest || latest.estado === 'Pendiente' || latest.estado === 'Rechazada';

  const downloadTemplate = async (): Promise<void> => {
    setDownloading(true);
    try {
      const file = await apiDownload('/acta/template', 'acta-sgemd.pdf');
      saveDownload(file);
      setTemplateMissing(false);
    } catch (caught) {
      if (caught instanceof ApiError && caught.code === 'ACTA_TEMPLATE_NOT_CONFIGURED') {
        setTemplateMissing(true);
      } else {
        showToast(errorMessage(caught), 'error');
      }
    } finally {
      setDownloading(false);
    }
  };

  const downloadAttachment = async (id: number, name: string): Promise<void> => {
    try {
      saveDownload(await apiDownload(`/attachments/${id}`, name));
    } catch (caught) {
      showToast(errorMessage(caught), 'error');
    }
  };

  return (
    <>
      <PageHeader
        title="Mi acta de compromiso"
        sub="Descarga la plantilla, fírmala y súbela para que la coordinación la revise."
        crumbs={[{ label: 'ESTUDIANTE' }, { label: 'Acta' }]}
        actions={<Badge state={latest?.estado ?? 'Pendiente'}>{latest?.estado ?? 'Sin cargar'}</Badge>}
      />

      <div className="grid g-2">
        <Card title="Plantilla" hint="FR-003">
          <p className="ayuda" style={{ marginTop: 0 }}>
            La plantilla legal del acta no está configurada en el servidor; cuando lo esté,
            este botón descargará el PDF oficial. Mientras tanto, sube el archivo firmado
            que recibiste de la coordinación.
          </p>
          <div className="fila-acciones">
            <Button variant="secundario" icon="download" loading={downloading} onClick={() => void downloadTemplate()}>
              Descargar plantilla
            </Button>
          </div>
          {templateMissing ? (
            <Callout icon="alerta">
              <b>Plantilla no configurada.</b> El servidor no tiene el texto legal del acta
              (P-36). La carga del archivo firmado sí está disponible; el hueco queda
              registrado en <code>docs/decisions.md</code>.
            </Callout>
          ) : null}
        </Card>

        <Card title="Cargar el acta firmada" hint="PDF o imagen">
          {actas.isPending ? <LoadingState label="Consultando tu acta…" /> : null}
          {actas.isError ? (
            <ErrorState error={actas.error} onRetry={() => void actas.refetch()} />
          ) : null}
          {!actas.isPending && !actas.isError ? (
            canUpload ? (
              <>
                <Dropzone
                  accept=".pdf,.jpg,.jpeg,.png"
                  disabled={upload.isPending}
                  progress={progress}
                  note="PDF, JPG o PNG. Una versión nueva reemplaza la anterior."
                  onFile={(file) => {
                    setProgress(0);
                    upload.mutate(
                      { file, onProgress: setProgress },
                      {
                        onSuccess: () => {
                          showToast('Acta cargada. Queda en revisión.', 'ok');
                          setProgress(null);
                        },
                        onError: (caught) => {
                          showToast(errorMessage(caught), 'error');
                          setProgress(null);
                        },
                      },
                    );
                  }}
                />
                {latest?.estado === 'Rechazada' ? (
                  <Callout icon="alerta">
                    <b>El acta fue rechazada.</b> {latest.observaciones ?? 'Revisa el motivo con la coordinación.'}{' '}
                    Corrige el archivo y vuelve a subirlo.
                  </Callout>
                ) : null}
              </>
            ) : (
              <Callout icon="lock">
                Tu acta está <b>{latest?.estado.toLowerCase()}</b>. Mientras la coordinación
                la revisa no se puede reemplazar.
              </Callout>
            )
          ) : null}
        </Card>
      </div>

      <Card title="Historial de actas" hint="La más reciente primero" flush>
        {actas.isPending ? <LoadingState label="Cargando actas…" /> : null}
        {actas.isError ? (
          <ErrorState error={actas.error} onRetry={() => void actas.refetch()} />
        ) : null}
        {actas.data && actas.data.items.length === 0 ? (
          <EmptyState
            icon="doc"
            title="Todavía no has cargado tu acta"
            text="Sube el archivo firmado para que la coordinación pueda aprobarlo y asignarte un docente."
          />
        ) : null}
        {actas.data && actas.data.items.length > 0 ? (
          <div>
            {actas.data.items.map((acta) => (
              <div className="aviso" key={acta.id}>
                <div style={{ flex: 1 }}>
                  <div className="fila-acciones" style={{ gap: 8, marginBottom: 6 }}>
                    <Badge state={acta.estado}>{acta.estado}</Badge>
                    <span className="nota-foot" style={{ margin: 0 }}>
                      {acta.fechaCarga
                        ? `Radicada ${formatDateTime(acta.fechaCarga)}`
                        : 'Sin radicar'}
                    </span>
                  </div>
                  <DefinitionList
                    items={[
                      { term: 'Emprendimiento', value: acta.emprendimiento.nombre },
                      {
                        term: 'Revisión',
                        value: acta.fechaRevision
                          ? `${formatDateTime(acta.fechaRevision)} · ${acta.revisor ? `${acta.revisor.nombres} ${acta.revisor.apellidos}` : '—'}`
                          : 'Pendiente de revisión',
                      },
                      { term: 'Observaciones', value: acta.observaciones ?? '—' },
                      {
                        term: 'Archivo',
                        value: acta.adjunto ? (
                          <Button
                            size="sm"
                            variant="secundario"
                            icon="download"
                            onClick={() => void downloadAttachment(acta.adjunto!.id, acta.adjunto!.nombreArchivo)}
                          >
                            {acta.adjunto.nombreArchivo}
                          </Button>
                        ) : (
                          '—'
                        ),
                      },
                    ]}
                  />
                </div>
              </div>
            ))}
          </div>
        ) : null}
      </Card>
    </>
  );
}
