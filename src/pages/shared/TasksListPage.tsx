import { useState, type FormEvent } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { PRIORIDADES, TAREA_ESTADOS } from '@sgemd/shared';
import type { Task } from '../../api/types.ts';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { ListTable } from '../../components/ListTable.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { SearchBox, SelectFilter, Toolbar } from '../../components/Toolbar.tsx';
import { formatDate } from '../../lib/format.ts';
import { useTasks } from '../../queries/tasks.ts';

interface TasksListPageProps {
  title: string;
  sub: string;
  roleLabel: string;
  /** Prefijo del rol: `/estudiante`, `/docente`, `/admin`. */
  basePath: string;
  canCreate: boolean;
  /** Filtro inicial de estado, p. ej. `Vencida` desde el tablero. */
  initialEstado?: string;
}

/**
 * Lista de tareas compartida por los tres roles.
 *
 * El alcance lo aplica el servidor; la vista solo cambia las columnas que tienen
 * sentido para quien mira (el estudiante no necesita ver su propio nombre) y el
 * botón de alta, que solo existe para docente y admin.
 */
export function TasksListPage({
  title,
  sub,
  roleLabel,
  basePath,
  canCreate,
  initialEstado,
}: TasksListPageProps) {
  const [params] = useSearchParams();
  const [page, setPage] = useState(1);
  const [q, setQ] = useState(params.get('q') ?? '');
  const [term, setTerm] = useState(params.get('q') ?? '');
  const [estado, setEstado] = useState(params.get('f') ?? initialEstado ?? '');
  const [prioridad, setPrioridad] = useState('');

  const tasks = useTasks({ page, pageSize: 20, q: term, estado, prioridad });

  return (
    <>
      <PageHeader
        title={title}
        sub={sub}
        crumbs={[{ label: roleLabel }, { label: 'Tareas' }]}
        actions={
          canCreate ? (
            <Link className="btn btn-primario" to={`${basePath}/nueva`}>
              Nueva tarea
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
            <SearchBox value={q} onChange={setQ} placeholder="Buscar por título o descripción" />
          </form>
          <SelectFilter
            label="Estado"
            value={estado}
            onChange={(value) => {
              setEstado(value);
              setPage(1);
            }}
          >
            {TAREA_ESTADOS.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </SelectFilter>
          <SelectFilter
            label="Prioridad"
            value={prioridad}
            onChange={(value) => {
              setPrioridad(value);
              setPage(1);
            }}
          >
            {PRIORIDADES.map((item) => (
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
          query={tasks}
          caption="Tareas"
          unit="tareas"
          emptyTitle="No hay tareas con estos filtros"
          emptyText="Cambia el estado o la prioridad, o consulta de nuevo más tarde."
          onPageChange={setPage}
          rowKey={(task: Task) => task.id}
          columns={[
            {
              key: 'titulo',
              header: 'Tarea',
              render: (task) => (
                <div>
                  <Link to={`${basePath}/${task.id}`}>
                    <b>{task.titulo}</b>
                  </Link>
                  <span className="nota-foot" style={{ display: 'block', marginTop: 2 }}>
                    {task.emprendimiento.codigo} · {task.emprendimiento.nombre}
                  </span>
                </div>
              ),
            },
            ...(canCreate
              ? [
                  {
                    key: 'estudiante',
                    header: 'Estudiante',
                    render: (task: Task) => `${task.estudiante.nombres} ${task.estudiante.apellidos}`,
                  },
                ]
              : []),
            {
              key: 'limite',
              header: 'Fecha límite',
              render: (task) =>
                task.fechaLimite ? (
                  <span className={task.vencida ? 'texto-fuerte' : undefined}>
                    {formatDate(task.fechaLimite)}
                  </span>
                ) : (
                  '—'
                ),
            },
            {
              key: 'prioridad',
              header: 'Prioridad',
              render: (task) => <Badge state={task.prioridad}>{task.prioridad}</Badge>,
            },
            {
              key: 'estado',
              header: 'Estado',
              render: (task) => (
                <Badge state={task.vencida && task.estado !== 'Completada' ? 'Vencida' : task.estado}>
                  {task.vencida && task.estado !== 'Completada' ? 'Vencida' : task.estado}
                </Badge>
              ),
            },
            {
              key: 'revision',
              header: 'Revisión',
              render: (task) => <Badge state={task.estadoRevision}>{task.estadoRevision}</Badge>,
            },
            {
              key: 'acc',
              header: '',
              render: (task) => (
                <Link className="btn btn-secundario btn-sm" to={`${basePath}/${task.id}`}>
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
