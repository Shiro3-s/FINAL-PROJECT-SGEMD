import { useState, type FormEvent } from 'react';
import { ACTA_ESTADOS } from '@sgemd/shared';
import { apiDownload, saveDownload } from '../../api/client.ts';
import type { Acta } from '../../api/types.ts';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout } from '../../components/DefinitionList.tsx';
import { ListTable } from '../../components/ListTable.tsx';
import { Modal } from '../../components/Modal.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { ReasonModal } from '../../components/ReasonModal.tsx';
import { errorMessage } from '../../components/States.tsx';
import { useToast } from '../../components/Toast.tsx';
import { SearchBox, SelectFilter, Toolbar } from '../../components/Toolbar.tsx';
import { formatBytes, formatDateTime } from '../../lib/format.ts';
import { useActas, useReviewActa } from '../../queries/acta.ts';

/**
 * Bandeja de actas de compromiso (FR-003, BR-001, BR-009).
 *
 * El acta llega firmada por el estudiante, la coordinación la revisa y la
 * aprobación es la compuerta para crear la asignación de docente
 * (`ACTA_NOT_APPROVED`). Rechazar siempre exige observaciones. La plantilla no
 * está configurada en el servidor (P-36), así que esta vista solo trabaja con el
 * archivo que el estudiante subió.
 */
export function AdminActasPage() {
  const [page, setPage] = useState(1);
  const [estado, setEstado] = useState('');
  const [q, setQ] = useState('');
  const [term, setTerm] = useState('');
  const [approving, setApproving] = useState<Acta | null>(null);
  const [rejecting, setRejecting] = useState<Acta | null>(null);

  const { showToast } = useToast();
  const list = useActas({ page, pageSize: 25, estado, q: term });
  const review = useReviewActa();

  const download = async (acta: Acta): Promise<void> => {
    if (!acta.adjunto) return;
    try {
      saveDownload(
        await apiDownload(`/attachments/${acta.adjunto.id}`, acta.adjunto.nombreArchivo),
      );
    } catch (caught) {
      showToast(errorMessage(caught), 'error');
    }
  };

  return (
    <>
      <PageHeader
        title="Actas de estudiantes"
        sub="Revisión del acta de compromiso firmada. La aprobación habilita la asignación de docente."
        crumbs={[{ label: 'ADMINISTRADOR' }, { label: 'Actas de estudiantes' }]}
      />

      <Callout icon="escudo">
        La plantilla legal del acta no está configurada en el servidor (P-36). El estudiante
        sube el PDF firmado y aquí se aprueba o se rechaza con observaciones.
      </Callout>

      <Card flush className="mt-14">
        <Toolbar>
          <form
            className="crece"
            role="search"
            onSubmit={(event: FormEvent<HTMLFormElement>) => {
              event.preventDefault();
              setTerm(q.trim());
              setPage(1);
            }}
          >
            <SearchBox
              value={q}
              onChange={setQ}
              placeholder="Buscar por estudiante, código o emprendimiento"
            />
          </form>
          <SelectFilter
            label="Estado"
            value={estado}
            onChange={(value) => {
              setEstado(value);
              setPage(1);
            }}
          >
            {ACTA_ESTADOS.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </SelectFilter>
          <Button variant="secundario" icon="filter" onClick={() => setPage(1)}>
            Aplicar
          </Button>
        </Toolbar>

        <ListTable
          query={list}
          caption="Actas"
          unit="actas"
          emptyTitle="No hay actas en esta bandeja"
          emptyText="Cuando un estudiante suba su acta firmada aparecerá aquí."
          onPageChange={setPage}
          rowKey={(acta: Acta) => acta.id}
          columns={[
            {
              key: 'estudiante',
              header: 'Estudiante',
              render: (acta) => (
                <div>
                  <b>
                    {acta.estudiante.nombres} {acta.estudiante.apellidos}
                  </b>
                  <span className="nota-foot" style={{ display: 'block', marginTop: 2 }}>
                    {acta.estudiante.codigo}
                  </span>
                </div>
              ),
            },
            {
              key: 'emprendimiento',
              header: 'Emprendimiento',
              render: (acta) => (
                <div>
                  {acta.emprendimiento.nombre}
                  <span className="nota-foot" style={{ display: 'block' }}>
                    {acta.emprendimiento.codigo}
                  </span>
                </div>
              ),
            },
            {
              key: 'carga',
              header: 'Cargada',
              render: (acta) => formatDateTime(acta.fechaCarga),
            },
            {
              key: 'adjunto',
              header: 'Archivo',
              render: (acta) =>
                acta.adjunto ? (
                  <div>
                    <b>{acta.adjunto.nombreArchivo}</b>
                    <span className="nota-foot" style={{ display: 'block' }}>
                      {formatBytes(acta.adjunto.tamanoBytes)}
                    </span>
                  </div>
                ) : (
                  'Sin archivo'
                ),
            },
            {
              key: 'estado',
              header: 'Estado',
              render: (acta) => (
                <div>
                  <Badge state={acta.estado}>{acta.estado}</Badge>
                  {acta.revisor ? (
                    <span className="nota-foot" style={{ display: 'block', marginTop: 4 }}>
                      {acta.revisor.nombres} {acta.revisor.apellidos}
                      {acta.fechaRevision ? ` · ${formatDateTime(acta.fechaRevision)}` : ''}
                    </span>
                  ) : null}
                  {acta.observaciones ? (
                    <span className="nota-foot" style={{ display: 'block', marginTop: 4 }}>
                      {acta.observaciones}
                    </span>
                  ) : null}
                </div>
              ),
            },
            {
              key: 'acc',
              header: '',
              render: (acta) => (
                <div className="fila-acciones">
                  {acta.adjunto ? (
                    <Button
                      size="sm"
                      variant="secundario"
                      icon="download"
                      onClick={() => void download(acta)}
                    >
                      Ver archivo
                    </Button>
                  ) : null}
                  {acta.estado === 'Pendiente' ? (
                    <>
                      <Button
                        size="sm"
                        variant="primario"
                        icon="check"
                        onClick={() => setApproving(acta)}
                      >
                        Aprobar
                      </Button>
                      <Button
                        size="sm"
                        variant="secundario"
                        icon="x"
                        onClick={() => setRejecting(acta)}
                      >
                        Rechazar
                      </Button>
                    </>
                  ) : (
                    <span className="nota-foot" style={{ margin: 0 }}>
                      Revisada
                    </span>
                  )}
                </div>
              ),
            },
          ]}
        />
      </Card>

      <Modal
        open={approving !== null}
        title="Aprobar el acta"
        onClose={() => setApproving(null)}
        footer={
          <>
            <Button variant="secundario" onClick={() => setApproving(null)}>
              Cancelar
            </Button>
            <Button
              variant="primario"
              icon="check"
              loading={review.isPending}
              onClick={() => {
                if (!approving) return;
                review.mutate(
                  { id: approving.id, decision: 'Aprobada' },
                  {
                    onSuccess: () => {
                      setApproving(null);
                      showToast('Acta aprobada. Ya se puede asignar docente.', 'ok');
                    },
                    onError: (caught) => showToast(errorMessage(caught), 'error'),
                  },
                );
              }}
            >
              Aprobar acta
            </Button>
          </>
        }
      >
        <p style={{ marginTop: 0 }}>
          Al aprobar el acta de{' '}
          <b>
            {approving?.estudiante.nombres} {approving?.estudiante.apellidos}
          </b>{' '}
          queda habilitada la asignación de docente para{' '}
          <b>{approving?.emprendimiento.nombre}</b> (BR-009).
        </p>
      </Modal>

      <ReasonModal
        open={rejecting !== null}
        title="Rechazar el acta"
        label="Observaciones"
        hint="El estudiante verá este motivo y podrá subir una versión corregida."
        confirmLabel="Rechazar"
        loading={review.isPending}
        onClose={() => setRejecting(null)}
        onSubmit={(observaciones) => {
          if (!rejecting) return;
          review.mutate(
            { id: rejecting.id, decision: 'Rechazada', observaciones },
            {
              onSuccess: () => {
                setRejecting(null);
                showToast('Acta rechazada con observaciones.', 'ok');
              },
              onError: (caught) => showToast(errorMessage(caught), 'error'),
            },
          );
        }}
      />
    </>
  );
}
