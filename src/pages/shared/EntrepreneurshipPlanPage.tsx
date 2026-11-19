import { Link, useParams } from 'react-router-dom';
import { TAREA_ESTADOS } from '@sgemd/shared';
import { saveDownload } from '../../api/client.ts';
import type { Entrepreneurship, Task } from '../../api/types.ts';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { ProgressBar } from '../../components/ProgressBar.tsx';
import { QueryGate } from '../../components/QueryGate.tsx';
import { EmptyState, LoadingState, errorMessage } from '../../components/States.tsx';
import { formatDate } from '../../lib/format.ts';
import { useEntrepreneurship } from '../../queries/entrepreneurship.ts';
import { useEntrepreneurshipTasks, useTaskAdvance } from '../../queries/tasks.ts';

interface EntrepreneurshipPlanPageProps {
  roleLabel: string;
  /** Prefijo del listado: `/admin/emprendimientos`. */
  listPath: string;
  /** Prefijo de las tareas del rol: `/admin/tareas`. */
  tasksPath: string;
}

/**
 * Plan de trabajo de un emprendimiento visto por la coordinación.
 *
 * No existe un endpoint de «plan»: la vista agrupa las tareas por fase
 * (`GET /task/entrepreneurship/:id`) y lee el avance calculado por el servidor
 * (`GET /task/advance/entrepreneurship/:id`). La descarga se genera en el
 * cliente con esas tareas; no se inventa un archivo que la API no produce.
 */
export function EntrepreneurshipPlanPage({
  roleLabel,
  listPath,
  tasksPath,
}: EntrepreneurshipPlanPageProps) {
  const { id } = useParams();
  const entrepreneurshipId = Number(id);
  const query = useEntrepreneurship(
    Number.isFinite(entrepreneurshipId) ? entrepreneurshipId : null,
  );

  return (
    <>
      <PageHeader
        title="Plan de trabajo"
        sub="Tareas del emprendimiento agrupadas por fase y avance calculado por el servidor."
        crumbs={[
          { label: roleLabel },
          { label: 'Emprendimientos', to: listPath },
          { label: 'Plan de trabajo' },
        ]}
      />
      <QueryGate query={query} loadingLabel="Cargando el plan de trabajo…">
        {(item: Entrepreneurship) => (
          <PlanBoard
            entrepreneurship={item}
            tasksPath={tasksPath}
            listPath={listPath}
          />
        )}
      </QueryGate>
    </>
  );
}

function PlanBoard({
  entrepreneurship,
  tasksPath,
  listPath,
}: {
  entrepreneurship: Entrepreneurship;
  tasksPath: string;
  listPath: string;
}) {
  const tasks = useEntrepreneurshipTasks(entrepreneurship.id);
  const advance = useTaskAdvance(entrepreneurship.id);

  if (tasks.isPending) return <LoadingState label="Cargando las tareas del plan…" />;
  if (tasks.isError) {
    return <EmptyState title="No fue posible cargar el plan" text={errorMessage(tasks.error)} />;
  }

  const items = tasks.data?.items ?? [];
  const phases = advance.data?.fases ?? [];
  const groups =
    phases.length > 0
      ? phases
      : [{ faseId: null, fase: 'Sin fase', total: items.length, completadas: 0, porcentaje: 0 }];
  const counts = TAREA_ESTADOS.map((estado) => ({
    estado,
    total: items.filter((task) => task.estado === estado).length,
  }));

  const download = (): void => {
    const header = [
      'Título',
      'Fase',
      'Prioridad',
      'Estado',
      'Fecha límite',
      'Puntos',
      'Puntaje',
      'Evidencias',
    ];
    const lines = items.map((task: Task) => [
      task.titulo,
      task.fase?.nombre ?? 'Sin fase',
      task.prioridad,
      task.estado,
      task.fechaLimite ?? '',
      String(task.puntos),
      task.puntajeObtenido === null ? '' : String(task.puntajeObtenido),
      String(task.evidencias),
    ]);
    const csv = [header, ...lines]
      .map((row) => row.map((cell) => `"${cell.replaceAll('"', '""')}"`).join(','))
      .join('\r\n');
    saveDownload({
      blob: new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8' }),
      filename: `plan-${entrepreneurship.codigo || entrepreneurship.id}.csv`,
    });
  };

  return (
    <>
      <Callout icon="bombilla">
        <b>{entrepreneurship.nombre}</b> ({entrepreneurship.codigo}) ·{' '}
        {entrepreneurship.estudiante.nombres} {entrepreneurship.estudiante.apellidos}. El
        plan lo construye el docente asignado; la coordinación puede consultarlo y ajustar
        tareas.
      </Callout>

      <div className="fila-acciones mt-14" style={{ justifyContent: 'flex-end' }}>
        <Link className="btn btn-secundario" to={`${listPath}/${entrepreneurship.id}`}>
          Volver al expediente
        </Link>
        <Button
          variant="secundario"
          icon="download"
          disabled={items.length === 0}
          onClick={download}
        >
          Descargar plan (CSV)
        </Button>
      </div>

      <div className="grid g-2-1 mt-14">
        <div className="grid">
          {groups.map((phase) => {
            const propias = items.filter(
              (task) => (task.fase?.nombre ?? null) === (phase.fase ?? null),
            );
            return (
              <Card
                key={`${phase.faseId ?? 'sin-fase'}`}
                title={
                  <span className="fila-acciones" style={{ gap: 8 }}>
                    <Badge state={phase.porcentaje === 100 ? 'Completada' : 'Pendiente'}>
                      {phase.fase ?? 'Sin fase'}
                    </Badge>
                    <span className="nota-foot" style={{ margin: 0 }}>
                      {phase.porcentaje}%
                    </span>
                  </span>
                }
                hint={`${phase.completadas} de ${phase.total} tareas completadas`}
              >
                {propias.length === 0 ? (
                  <p className="ayuda" style={{ margin: 0 }}>
                    Aún no hay tareas asignadas en esta fase.
                  </p>
                ) : (
                  <div>
                    {propias.map((task) => (
                      <Link
                        className="aviso"
                        key={task.id}
                        to={`${tasksPath}/${task.id}`}
                        style={{ textDecoration: 'none' }}
                      >
                        <div style={{ flex: 1 }}>
                          <b>{task.titulo}</b>
                          <span className="nota-foot" style={{ display: 'block', marginTop: 4 }}>
                            Fecha límite {formatDate(task.fechaLimite)} · {task.evidencias}{' '}
                            evidencias
                          </span>
                        </div>
                        <Badge state={task.estado}>{task.estado}</Badge>
                      </Link>
                    ))}
                  </div>
                )}
              </Card>
            );
          })}
        </div>

        <div className="grid">
          <Card title="Avance general">
            <p style={{ fontSize: 28, fontWeight: 700, margin: '0 0 8px' }}>
              {advance.data?.avance ?? 0}%
            </p>
            <ProgressBar value={advance.data?.avance ?? 0} label="Avance general del plan" />
            <p className="ayuda" style={{ marginBottom: 0 }}>
              {advance.data
                ? `${advance.data.completadas} de ${advance.data.total} tareas completadas.`
                : 'Calculando el avance…'}
            </p>
          </Card>

          <Card title="Tareas por estado" hint="Distribución del plan">
            <DefinitionList
              items={counts.map(({ estado, total }) => ({
                term: estado,
                value: String(total),
              }))}
            />
          </Card>

          <Card title="Datos del emprendimiento">
            <DefinitionList
              items={[
                { term: 'Etapa', value: entrepreneurship.etapa?.nombre ?? 'Sin etapa' },
                { term: 'Sector', value: entrepreneurship.sector?.nombre ?? 'Sin sector' },
                {
                  term: 'Centro',
                  value: entrepreneurship.centroUniversitario?.nombre ?? 'Sin centro',
                },
                {
                  term: 'Estado',
                  value: entrepreneurship.estadoAprobacion,
                },
              ]}
            />
          </Card>
        </div>
      </div>
    </>
  );
}
