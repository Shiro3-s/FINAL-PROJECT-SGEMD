import { useState } from 'react';
import { Link } from 'react-router-dom';
import type { Tracing } from '../../api/types.ts';
import { Badge } from '../../components/Badge.tsx';
import { Card } from '../../components/Card.tsx';
import { ListTable } from '../../components/ListTable.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { SelectFilter, Toolbar } from '../../components/Toolbar.tsx';
import { formatDate } from '../../lib/format.ts';
import { useEntrepreneurships } from '../../queries/entrepreneurship.ts';
import { useTracings } from '../../queries/tracing.ts';

interface TracingListPageProps {
  title: string;
  sub: string;
  roleLabel: string;
  basePath: string;
  /** Si se conoce el emprendimiento; si no, la vista ofrece un selector. */
  entrepreneurshipId?: number;
  canCreate?: boolean;
}

/**
 * Historial de avances y comentarios.
 *
 * No existe un listado global de seguimientos: la API solo expone los de un
 * emprendimiento (`/tracing/entrepreneurship/:id`). Por eso el administrador ve
 * un selector de expediente y, si no hay ninguno elegido, se usa el primero de
 * su alcance; el estudiante y el docente llegan con el suyo ya resuelto.
 */
export function TracingListPage({
  title,
  sub,
  roleLabel,
  basePath,
  entrepreneurshipId,
  canCreate = false,
}: TracingListPageProps) {
  const entrepreneurships = useEntrepreneurships({ pageSize: 100 });
  const [chosen, setChosen] = useState('');
  const effectiveId =
    entrepreneurshipId ??
    (chosen ? Number(chosen) : (entrepreneurships.data?.items[0]?.id ?? null));
  const tracings = useTracings(effectiveId);

  return (
    <>
      <PageHeader
        title={title}
        sub={sub}
        crumbs={[{ label: roleLabel }, { label: 'Seguimiento' }]}
        actions={
          canCreate ? (
            <Link className="btn btn-primario" to={`${basePath}/nuevo`}>
              Registrar avance
            </Link>
          ) : undefined
        }
      />

      <Card flush>
        {entrepreneurshipId === undefined ? (
          <Toolbar>
            <SelectFilter
              label="Emprendimiento"
              value={chosen}
              onChange={setChosen}
              allLabel="El más reciente de mi alcance"
            >
              {(entrepreneurships.data?.items ?? []).map((item) => (
                <option key={item.id} value={item.id}>
                  {item.codigo} · {item.nombre}
                </option>
              ))}
            </SelectFilter>
          </Toolbar>
        ) : null}

        <ListTable
          query={tracings}
          caption="Seguimientos"
          unit="registros"
          emptyTitle="No hay seguimientos registrados"
          emptyText={
            canCreate
              ? 'Registra el primer avance de fase o comentario del emprendimiento.'
              : 'Cuando el docente registre un avance, aparecerá aquí.'
          }
          onPageChange={() => undefined}
          rowKey={(tracing: Tracing) => tracing.id}
          columns={[
            {
              key: 'fecha',
              header: 'Fecha',
              render: (tracing) => formatDate(tracing.fechaSeguimiento),
            },
            {
              key: 'tipo',
              header: 'Tipo',
              render: (tracing) => (
                <span>
                  <Badge state={tracing.tipo === 'Comentario' ? 'Pendiente' : 'En revisión'}>
                    {tracing.tipo}
                  </Badge>
                </span>
              ),
            },
            {
              key: 'descripcion',
              header: 'Descripción',
              render: (tracing) => (
                <div>
                  <Link to={`${basePath}/${tracing.id}`}>
                    <b>{tracing.descripcion.slice(0, 90)}</b>
                  </Link>
                  <span className="nota-foot" style={{ display: 'block', marginTop: 2 }}>
                    {tracing.emprendimiento.codigo} · {tracing.fase?.nombre ?? 'Sin fase'}
                  </span>
                </div>
              ),
            },
            {
              key: 'autor',
              header: 'Autor',
              render: (tracing) =>
                tracing.autor
                  ? `${tracing.autor.nombres} ${tracing.autor.apellidos}`
                  : 'Autor no disponible',
            },
            {
              key: 'revision',
              header: 'Revisión',
              render: (tracing) => (
                <Badge state={tracing.estadoRevision}>{tracing.estadoRevision}</Badge>
              ),
            },
            {
              key: 'puntaje',
              header: 'Puntaje',
              render: (tracing) => (tracing.puntaje === null ? '—' : String(tracing.puntaje)),
            },
            {
              key: 'evidencias',
              header: 'Evidencias',
              render: (tracing) => String(tracing.evidencias),
            },
            {
              key: 'acc',
              header: '',
              render: (tracing) => (
                <Link className="btn btn-secundario btn-sm" to={`${basePath}/${tracing.id}`}>
                  Ver
                </Link>
              ),
            },
          ]}
        />
      </Card>
    </>
  );
}
