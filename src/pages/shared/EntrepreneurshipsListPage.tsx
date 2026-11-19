import { useEffect, useState, type FormEvent } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { EMPRENDIMIENTO_ESTADOS } from '@sgemd/shared';
import type { Entrepreneurship } from '../../api/types.ts';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { ListTable } from '../../components/ListTable.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { ProgressBar } from '../../components/ProgressBar.tsx';
import { ReasonModal } from '../../components/ReasonModal.tsx';
import { SearchBox, SelectFilter, Toolbar } from '../../components/Toolbar.tsx';
import { errorMessage } from '../../components/States.tsx';
import { useToast } from '../../components/Toast.tsx';
import {
  useApproveEntrepreneurship,
  useEntrepreneurships,
  useRejectEntrepreneurship,
} from '../../queries/entrepreneurship.ts';

interface EntrepreneurshipsListPageProps {
  roleLabel: string;
  /** Prefijo del rol: `/docente` o `/admin`. */
  basePath: string;
  /** Solo el administrador da de alta. */
  canCreate?: boolean;
  /** Solo el administrador aprueba o rechaza. */
  canManage?: boolean;
}

/**
 * Listado de emprendimientos compartido por docente y administrador.
 *
 * El alcance lo aplica el servidor: el docente ve los de sus asignaciones
 * activas y el administrador, todos. Las acciones de aprobación solo se pintan
 * para el administrador; el docente entra al expediente.
 */
export function EntrepreneurshipsListPage({
  roleLabel,
  basePath,
  canCreate = false,
  canManage = false,
}: EntrepreneurshipsListPageProps) {
  const [page, setPage] = useState(1);
  /** El buscador global del marco navega aquí con `?q=`; se aplica al listado. */
  const [params] = useSearchParams();
  const urlTerm = params.get('q')?.trim() ?? '';
  const [q, setQ] = useState(urlTerm);
  const [term, setTerm] = useState(urlTerm);
  const [estado, setEstado] = useState('');
  const [rejectId, setRejectId] = useState<number | null>(null);
  const [rejectName, setRejectName] = useState('');

  useEffect(() => {
    if (!urlTerm) return;
    setQ(urlTerm);
    setTerm(urlTerm);
    setPage(1);
  }, [urlTerm]);

  const { showToast } = useToast();
  const approve = useApproveEntrepreneurship();
  const reject = useRejectEntrepreneurship();
  const list = useEntrepreneurships({ page, pageSize: 25, q: term, estado });

  return (
    <>
      <PageHeader
        title={canManage ? 'Emprendimientos' : 'Emprendimientos asignados'}
        sub={
          canManage
            ? 'Todos los emprendimientos del programa, con su estado de aprobación y avance.'
            : 'Los emprendimientos que tienes asignados como mentor.'
        }
        crumbs={[{ label: roleLabel }, { label: 'Emprendimientos' }]}
        actions={
          canCreate ? (
            <Link className="btn btn-primario" to={`${basePath}/nuevo`}>
              Nuevo emprendimiento
            </Link>
          ) : undefined
        }
      />

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
            <SearchBox
              value={q}
              onChange={setQ}
              placeholder="Buscar por nombre, código o estudiante"
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
            {EMPRENDIMIENTO_ESTADOS.map((item) => (
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
          caption="Emprendimientos"
          unit="emprendimientos"
          emptyTitle="No hay emprendimientos para mostrar"
          emptyText={
            canManage
              ? 'Crea el primer emprendimiento o ajusta los filtros.'
              : 'Cuando el administrador te asigne un emprendimiento aparecerá aquí.'
          }
          onPageChange={setPage}
          rowKey={(item: Entrepreneurship) => item.id}
          columns={[
            {
              key: 'nombre',
              header: 'Emprendimiento',
              render: (item) => (
                <div>
                  <Link to={`${basePath}/${item.id}`}>
                    <b>{item.nombre}</b>
                  </Link>
                  <span className="nota-foot" style={{ display: 'block', marginTop: 2 }}>
                    {item.codigo}
                    {item.esParalelo ? ' · Paralelo autorizado' : ''}
                  </span>
                </div>
              ),
            },
            {
              key: 'estudiante',
              header: 'Estudiante',
              render: (item) =>
                `${item.estudiante.nombres} ${item.estudiante.apellidos}`,
            },
            {
              key: 'etapa',
              header: 'Etapa y sector',
              render: (item) => (
                <div>
                  {item.etapa?.nombre ?? 'Sin etapa'}
                  <span className="nota-foot" style={{ display: 'block' }}>
                    {item.sector?.nombre ?? 'Sin sector'}
                  </span>
                </div>
              ),
            },
            {
              key: 'avance',
              header: 'Avance',
              render: (item) => (
                <span>
                  {item.avance}% <ProgressBar value={item.avance} label={`Avance de ${item.nombre}`} />
                </span>
              ),
            },
            {
              key: 'estado',
              header: 'Estado',
              render: (item) => (
                <Badge state={item.estadoAprobacion}>{item.estadoAprobacion}</Badge>
              ),
            },
            {
              key: 'acc',
              header: '',
              render: (item) => (
                <div className="fila-acciones">
                  <Link className="btn btn-secundario btn-sm" to={`${basePath}/${item.id}`}>
                    Expediente
                  </Link>
                  {canManage && item.estadoAprobacion === 'Pendiente' ? (
                    <>
                      <Button
                        size="sm"
                        variant="primario"
                        icon="check"
                        loading={approve.isPending}
                        onClick={() =>
                          approve.mutate(item.id, {
                            onSuccess: () => showToast('Emprendimiento aprobado.', 'ok'),
                            onError: (caught) => showToast(errorMessage(caught), 'error'),
                          })
                        }
                      >
                        Aprobar
                      </Button>
                      <Button
                        size="sm"
                        variant="secundario"
                        icon="x"
                        onClick={() => {
                          setRejectId(item.id);
                          setRejectName(item.nombre);
                        }}
                      >
                        Rechazar
                      </Button>
                    </>
                  ) : null}
                  {canManage ? (
                    <Link
                      className="btn btn-secundario btn-sm"
                      to={`${basePath}/${item.id}/editar`}
                    >
                      Editar
                    </Link>
                  ) : null}
                </div>
              ),
            },
          ]}
        />
      </Card>

      <ReasonModal
        open={rejectId !== null}
        title={`Rechazar ${rejectName}`}
        label="Motivo del rechazo"
        hint="El motivo se guarda y se muestra al estudiante en el expediente."
        confirmLabel="Rechazar"
        loading={reject.isPending}
        onClose={() => setRejectId(null)}
        onSubmit={(motivo) => {
          if (rejectId === null) return;
          reject.mutate(
            { id: rejectId, motivo },
            {
              onSuccess: () => {
                setRejectId(null);
                showToast('Emprendimiento rechazado.', 'ok');
              },
              onError: (caught) => showToast(errorMessage(caught), 'error'),
            },
          );
        }}
      />
    </>
  );
}
