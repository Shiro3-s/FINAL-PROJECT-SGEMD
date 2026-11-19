import { useState, type FormEvent } from 'react';
import { RESPALDO_ESTADOS, RESPALDO_TIPOS } from '@sgemd/shared';
import { saveDownload } from '../../api/client.ts';
import type { Backup, BackupPanel } from '../../api/types.ts';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { ListTable } from '../../components/ListTable.tsx';
import { Metric } from '../../components/Metric.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { SearchBox, SelectFilter, Toolbar } from '../../components/Toolbar.tsx';
import { errorMessage } from '../../components/States.tsx';
import { useToast } from '../../components/Toast.tsx';
import { formatDateTime } from '../../lib/format.ts';
import {
  useBackups,
  useBackupPanel,
  useCreateBackup,
  useDownloadBackup,
  useExportDatabase,
  useVerifyBackup,
} from '../../queries/admin.ts';

/**
 * Respaldos del sistema (FR-018, FR-009).
 *
 * `Completo` es volcado + instantánea incremental; `Parcial` solo instantánea.
 * Se muestran los dos tamaños (lógico y añadido) para ver la tendencia. La
 * restauración no forma parte del MVP y no se ofrece: solo crear, verificar,
 * descargar artefactos y exportar la base.
 */
export function AdminBackupsPage() {
  const { showToast } = useToast();
  const [page, setPage] = useState(1);
  const [estado, setEstado] = useState('');
  const [tipo, setTipo] = useState('');
  const [q, setQ] = useState('');
  const [term, setTerm] = useState('');
  const [tipoNuevo, setTipoNuevo] = useState<'Completo' | 'Parcial'>('Completo');

  const panel = useBackupPanel();
  const list = useBackups({ page, pageSize: 25, estado, tipo, q: term });
  const create = useCreateBackup();
  const verify = useVerifyBackup();
  const download = useDownloadBackup();
  const exportDb = useExportDatabase();

  const latest = list.data?.items[0];

  return (
    <>
      <PageHeader
        title="Respaldos"
        sub="Historial de copias de seguridad, integridad y exportación de la base."
        crumbs={[{ label: 'ADMINISTRADOR' }, { label: 'Respaldos' }]}
        actions={
          <div className="fila-acciones">
            <select
              className="filtro"
              aria-label="Tipo de respaldo"
              value={tipoNuevo}
              onChange={(event) => setTipoNuevo(event.target.value as 'Completo' | 'Parcial')}
            >
              {RESPALDO_TIPOS.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
            <Button
              variant="primario"
              icon="bd"
              loading={create.isPending}
              onClick={() =>
                create.mutate(tipoNuevo, {
                  onSuccess: () => showToast('Respaldo ejecutado.', 'ok'),
                  onError: (caught) => showToast(errorMessage(caught), 'error'),
                })
              }
            >
              Crear respaldo
            </Button>
          </div>
        }
      />

      <Callout icon="alerta">
        La restauración no está disponible en el MVP: un respaldo se crea, se verifica y se
        descarga, pero no se restaura desde la interfaz. La exportación de la base es un
        archivo aparte.
      </Callout>

      {panel.data ? <PanelCards panel={panel.data} latest={latest} /> : null}

      <Card flush>
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
            <SearchBox value={q} onChange={setQ} placeholder="Buscar por código o destino" />
          </form>
          <SelectFilter
            label="Estado"
            value={estado}
            onChange={(value) => {
              setEstado(value);
              setPage(1);
            }}
          >
            {RESPALDO_ESTADOS.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </SelectFilter>
          <SelectFilter
            label="Tipo"
            value={tipo}
            onChange={(value) => {
              setTipo(value);
              setPage(1);
            }}
          >
            {RESPALDO_TIPOS.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </SelectFilter>
          <Button variant="secundario" icon="filter" onClick={() => setPage(1)}>
            Aplicar
          </Button>
          <Button
            variant="secundario"
            icon="download"
            loading={exportDb.isPending}
            onClick={() =>
              exportDb.mutate('csv', {
                onSuccess: (file) => {
                  saveDownload(file);
                  showToast('Exportación de la base generada.', 'ok');
                },
                onError: (caught) => showToast(errorMessage(caught), 'error'),
              })
            }
          >
            Exportar base (CSV)
          </Button>
        </Toolbar>

        <ListTable
          query={list}
          caption="Historial de respaldos"
          unit="respaldos"
          emptyTitle="Todavía no hay respaldos"
          emptyText="Ejecuta el primero con el botón «Crear respaldo»."
          onPageChange={setPage}
          rowKey={(item: Backup) => item.id}
          columns={[
            {
              key: 'codigo',
              header: 'Respaldo',
              render: (item) => (
                <div>
                  <b>{item.codigo}</b>
                  <span className="nota-foot" style={{ display: 'block', marginTop: 2 }}>
                    {item.tipo} · {formatDateTime(item.fechaHora)}
                  </span>
                </div>
              ),
            },
            {
              key: 'tamano',
              header: 'Tamaños',
              render: (item) => (
                <div>
                  {item.tamanoLogicoMb === null ? '—' : `${item.tamanoLogicoMb} MB lógicos`}
                  <span className="nota-foot" style={{ display: 'block' }}>
                    {item.tamanoAnadidoMb === null
                      ? '—'
                      : `+${item.tamanoAnadidoMb} MB añadidos`}
                  </span>
                </div>
              ),
            },
            {
              key: 'destino',
              header: 'Destino',
              render: (item) => (
                <div>
                  {item.destino ?? 'Sin destino'}
                  <span className="nota-foot" style={{ display: 'block' }}>
                    {item.retencionDias === null
                      ? 'Sin retención definida'
                      : `Retención ${item.retencionDias} días`}
                  </span>
                </div>
              ),
            },
            {
              key: 'artefactos',
              header: 'Artefactos',
              render: (item) => (
                <div>
                  {item.artefactos.dump ? 'Volcado' : 'Sin volcado'}
                  <span className="nota-foot" style={{ display: 'block' }}>
                    {item.artefactos.snapshot ? 'Instantánea' : 'Sin instantánea'}
                  </span>
                </div>
              ),
            },
            {
              key: 'estado',
              header: 'Estado',
              render: (item) => (
                <div>
                  <Badge state={item.estado === 'Exitosa' ? 'Aprobada' : 'Rechazada'}>
                    {item.estado}
                  </Badge>
                  <span className="nota-foot" style={{ display: 'block', marginTop: 4 }}>
                    {item.ejecutadoPor
                      ? `${item.ejecutadoPor.nombres} ${item.ejecutadoPor.apellidos}`
                      : 'Sin ejecutor registrado'}
                  </span>
                </div>
              ),
            },
            {
              key: 'acc',
              header: '',
              render: (item) => (
                <div className="fila-acciones">
                  {item.estado === 'Exitosa' ? (
                    <>
                      <Button
                        size="sm"
                        variant="secundario"
                        icon="check"
                        loading={verify.isPending}
                        onClick={() =>
                          verify.mutate(item.id, {
                            onSuccess: (result) =>
                              showToast(
                                result.corruptos.length === 0
                                  ? `Integridad correcta: ${result.archivos} archivos.`
                                  : `${result.corruptos.length} archivos corruptos.`,
                                result.corruptos.length === 0 ? 'ok' : 'error',
                              ),
                            onError: (caught) => showToast(errorMessage(caught), 'error'),
                          })
                        }
                      >
                        Verificar
                      </Button>
                      {item.artefactos.dump ? (
                        <Button
                          size="sm"
                          variant="secundario"
                          icon="download"
                          loading={download.isPending}
                          onClick={() =>
                            download.mutate(
                              { id: item.id, part: 'dump' },
                              {
                                onSuccess: (file) => saveDownload(file),
                                onError: (caught) => showToast(errorMessage(caught), 'error'),
                              },
                            )
                          }
                        >
                          Volcado
                        </Button>
                      ) : null}
                      {item.artefactos.snapshot ? (
                        <Button
                          size="sm"
                          variant="secundario"
                          icon="download"
                          loading={download.isPending}
                          onClick={() =>
                            download.mutate(
                              { id: item.id, part: 'storage' },
                              {
                                onSuccess: (file) => saveDownload(file),
                                onError: (caught) => showToast(errorMessage(caught), 'error'),
                              },
                            )
                          }
                        >
                          Evidencias
                        </Button>
                      ) : null}
                    </>
                  ) : (
                    <span className="nota-foot" style={{ margin: 0 }}>
                      Sin artefactos descargables
                    </span>
                  )}
                </div>
              ),
            },
          ]}
        />
      </Card>
    </>
  );
}

function PanelCards({ panel, latest }: { panel: BackupPanel; latest?: Backup }) {
  return (
    <div className="grid g-4 mt-14">
      <Metric
        icon="bd"
        label="Motor"
        value={panel.motor === 'rsync' ? 'rsync' : 'enlaces duros'}
      />
      <Metric icon="calendar" label="Retención" value={panel.retencionDias} unit="días" />
      <Metric icon="carpeta" label="En disco" value={panel.respaldosEnDisco} unit="respaldos" />
      <Card title="Último respaldo" hint={latest ? latest.estado : 'Sin respaldos'}>
        {latest ? (
          <DefinitionList
            items={[
              { term: 'Código', value: latest.codigo },
              { term: 'Fecha', value: formatDateTime(latest.fechaHora) },
              { term: 'Lógico', value: latest.tamanoLogicoMb === null ? '—' : `${latest.tamanoLogicoMb} MB` },
              {
                term: 'Añadido',
                value:
                  latest.tamanoAnadidoMb === null ? '—' : `+${latest.tamanoAnadidoMb} MB`,
              },
              {
                term: 'Checksum',
                value: latest.checksumManifiesto
                  ? `${latest.checksumManifiesto.slice(0, 16)}…`
                  : 'Sin manifiesto',
              },
            ]}
          />
        ) : (
          <p className="ayuda" style={{ margin: 0 }}>
            Ejecuta el primer respaldo para ver su resumen.
          </p>
        )}
      </Card>
    </div>
  );
}
