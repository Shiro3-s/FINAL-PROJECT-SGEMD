import { useState } from 'react';
import { Link } from 'react-router-dom';
import { TAREA_ESTADOS } from '@sgemd/shared';
import { saveDownload } from '../../api/client.ts';
import type { Task } from '../../api/types.ts';
import { Badge } from '../../components/Badge.tsx';
import { Button } from '../../components/Button.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { ProgressBar } from '../../components/ProgressBar.tsx';
import { EmptyState, LoadingState, errorMessage } from '../../components/States.tsx';
import { Tabs, TabPanel } from '../../components/Tabs.tsx';
import { formatDate } from '../../lib/format.ts';
import { useEntrepreneurships } from '../../queries/entrepreneurship.ts';
import { useEntrepreneurshipTasks, useTaskAdvance } from '../../queries/tasks.ts';

/**
 * Plan de trabajo del estudiante.
 *
 * No existe un endpoint de «plan»: el plan es la vista de las tareas agrupadas
 * por fase (`GET /task/entrepreneurship/:id`) más el avance por fase
 * (`GET /task/advance/entrepreneurship/:id`), que ya calcula el servidor. La
 * descarga se genera en el cliente con esas tareas: no inventa un archivo que la
 * API no produce.
 */
export function StudentPlanPage() {
  const entrepreneurships = useEntrepreneurships({ pageSize: 100 });
  const items = entrepreneurships.data?.items ?? [];
  const [chosen, setChosen] = useState<number | null>(null);
  const selectedId = chosen ?? items[0]?.id ?? null;

  if (entrepreneurships.isPending) {
    return <LoadingState label="Cargando tu plan de trabajo…" />;
  }
  if (entrepreneurships.isError) {
    return <EmptyState title="No fue posible cargar tu plan" text={errorMessage(entrepreneurships.error)} />;
  }
  if (items.length === 0) {
    return (
      <>
        <PageHeader
          title="Plan de trabajo"
          sub="Las cuatro fases del programa y tu avance por emprendimiento."
          crumbs={[{ label: 'ESTUDIANTE' }, { label: 'Plan de trabajo' }]}
        />
        <Card title="Todavía no hay un emprendimiento registrado">
          <Callout icon="bombilla">
            El alta del emprendimiento la hace la coordinación del programa (D4). Cuando
            exista, aquí verás el plan que construya tu docente.
          </Callout>
          <div className="fila-acciones">
            <Link className="btn btn-primario" to="/estudiante/emprendimientos">
              Mi emprendimiento
            </Link>
            <Link className="btn btn-secundario" to="/estudiante/acta">
              Cargar mi acta
            </Link>
          </div>
        </Card>
      </>
    );
  }

  return (
    <>
      <PageHeader
        title="Plan de trabajo"
        sub="Las cuatro fases del programa y tu avance por emprendimiento."
        crumbs={[{ label: 'ESTUDIANTE' }, { label: 'Plan de trabajo' }]}
        actions={<PlanDownload entrepreneurshipId={selectedId} />}
      />

      <Callout icon="escudo">
        El plan de trabajo lo construye el docente que tienes asignado; tú solo puedes
        consultar su avance y completar las tareas.
      </Callout>

      <div className="mt-14">
        <Tabs
          label="Emprendimientos"
          active={String(selectedId)}
          onChange={(value) => setChosen(Number(value))}
          items={items.map((item) => ({ id: String(item.id), label: item.nombre }))}
        />
        {items.map((item) => (
          <TabPanel key={item.id} id={String(item.id)} active={String(selectedId)}>
            <PlanBoard entrepreneurshipId={item.id} nombre={item.nombre} />
          </TabPanel>
        ))}
      </div>
    </>
  );
}

/**
 * El botón de descarga vive en la cabecera, donde el prototipo lo ubica, pero
 * necesita las tareas del emprendimiento activo. Se suscribe a la misma consulta
 * que el tablero (TanStack Query la comparte por clave) y no crea una segunda.
 */
function PlanDownload({ entrepreneurshipId }: { entrepreneurshipId: number | null }) {
  const tasks = useEntrepreneurshipTasks(entrepreneurshipId);

  const download = (): void => {
    const rows = tasks.data?.items ?? [];
    const header = ['Título', 'Fase', 'Prioridad', 'Estado', 'Fecha límite', 'Puntos', 'Puntaje', 'Evidencias'];
    const lines = rows.map((task: Task) => [
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
      filename: `plan-de-trabajo-${entrepreneurshipId ?? 'emprendimiento'}.csv`,
    });
  };

  return (
    <Button
      variant="secundario"
      icon="download"
      disabled={!tasks.data || tasks.data.items.length === 0}
      onClick={download}
    >
      Descargar plan (CSV)
    </Button>
  );
}

function PlanBoard({ entrepreneurshipId, nombre }: { entrepreneurshipId: number; nombre: string }) {
  const tasks = useEntrepreneurshipTasks(entrepreneurshipId);
  const advance = useTaskAdvance(entrepreneurshipId);

  if (tasks.isPending) return <LoadingState label="Cargando las tareas del plan…" />;
  if (tasks.isError) {
    return <EmptyState title="No fue posible cargar el plan" text={errorMessage(tasks.error)} />;
  }

  const items = tasks.data?.items ?? [];
  const phases = advance.data?.fases ?? [];
  const counts = TAREA_ESTADOS.map((estado) => ({
    estado,
    total: items.filter((task) => task.estado === estado).length,
  }));

  return (
    <div className="grid g-2-1 mt-14">
      <div className="grid">
        {phases.length === 0 && items.length === 0 ? (
          <Card title="Sin tareas todavía">
            <p className="ayuda" style={{ marginTop: 0 }}>
              Tu docente aún no ha asignado tareas a {nombre}. Cuando lo haga, aparecerán
              agrupadas por fase.
            </p>
          </Card>
        ) : null}

        {(phases.length > 0 ? phases : [{ faseId: null, fase: 'Sin fase', total: items.length, completadas: 0, porcentaje: 0 }]).map(
          (phase) => {
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
                        to={`/estudiante/tareas/${task.id}`}
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
          },
        )}
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
      </div>
    </div>
  );
}
