import { Link } from 'react-router-dom';
import { AdviceDetailPage } from '../shared/AdviceDetailPage.tsx';
import { AdviceListPage } from '../shared/AdviceListPage.tsx';
import { EventDetailPage } from '../shared/EventDetailPage.tsx';
import { EventsListPage } from '../shared/EventsListPage.tsx';
import { ExpedientePage } from '../shared/ExpedientePage.tsx';
import { TaskDetailPage } from '../shared/TaskDetailPage.tsx';
import { TasksListPage } from '../shared/TasksListPage.tsx';
import { TracingDetailPage } from '../shared/TracingDetailPage.tsx';
import { TracingListPage } from '../shared/TracingListPage.tsx';
import { EmptyState, ErrorState, LoadingState } from '../../components/States.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { ROLE_LABEL } from '../../navigation/nav.ts';
import { useEntrepreneurships } from '../../queries/entrepreneurship.ts';

/**
 * Contenedores del rol Estudiante.
 *
 * Las vistas de lista y de expediente son compartidas: el alcance de datos lo
 * aplica el servidor y estas funciones solo fijan ruta, etiqueta y acciones
 * permitidas. Así una corrección en la tabla o en los filtros llega a los tres
 * roles a la vez.
 */

export function StudentTasksPage() {
  return (
    <TasksListPage
      title="Mis tareas"
      sub="Compromisos del plan de trabajo. Sube la evidencia antes de marcar una tarea como completada."
      roleLabel={ROLE_LABEL.estudiante}
      basePath="/estudiante/tareas"
      canCreate={false}
    />
  );
}

export function StudentAdvicesPage() {
  return (
    <AdviceListPage
      title="Asesorías"
      sub="Sesiones de acompañamiento agendadas por la coordinación y tu docente."
      roleLabel={ROLE_LABEL.estudiante}
      basePath="/estudiante/asesorias"
      canCreate={false}
    />
  );
}

export function StudentEventsPage() {
  return (
    <EventsListPage
      roleLabel={ROLE_LABEL.estudiante}
      basePath="/estudiante/eventos"
      canCreate={false}
    />
  );
}

export function StudentExpedientePage() {
  return (
    <ExpedientePage
      basePath="/estudiante/emprendimientos"
      roleLabel={ROLE_LABEL.estudiante}
      canManage={false}
    />
  );
}

export function StudentTaskDetailPage() {
  return <TaskDetailPage basePath="/estudiante/tareas" roleLabel={ROLE_LABEL.estudiante} />;
}

export function StudentAdviceDetailPage() {
  return <AdviceDetailPage basePath="/estudiante/asesorias" roleLabel={ROLE_LABEL.estudiante} />;
}

export function StudentEventDetailPage() {
  return <EventDetailPage basePath="/estudiante/eventos" roleLabel={ROLE_LABEL.estudiante} />;
}

export function StudentTracingDetailPage() {
  return <TracingDetailPage basePath="/estudiante/seguimiento" roleLabel={ROLE_LABEL.estudiante} />;
}

/**
 * Seguimiento del estudiante: solo lectura.
 *
 * La API no tiene listado global de seguimientos; se consultan por
 * emprendimiento. Con uno solo se pasa su id y no se pinta selector; con
 * paralelos, `TracingListPage` ofrece el selector de expediente.
 */
export function StudentTracingPage() {
  const entrepreneurships = useEntrepreneurships({ pageSize: 100 });
  const items = entrepreneurships.data?.items ?? [];

  if (entrepreneurships.isPending) {
    return <LoadingState label="Cargando el seguimiento…" />;
  }
  if (entrepreneurships.isError) {
    return <ErrorState error={entrepreneurships.error} />;
  }
  if (items.length === 0) {
    return (
      <>
        <PageHeader
          title="Seguimiento"
          sub="Historial de los acompañamientos registrados por tu docente."
          crumbs={[{ label: ROLE_LABEL.estudiante }, { label: 'Seguimiento' }]}
        />
        <EmptyState
          title="Todavía no hay un emprendimiento registrado"
          text="El seguimiento se registra sobre un emprendimiento. El alta la hace la coordinación (D4)."
          action={
            <Link className="btn btn-primario" to="/estudiante/emprendimientos">
              Mi emprendimiento
            </Link>
          }
        />
      </>
    );
  }

  return (
    <TracingListPage
      title="Seguimiento"
      sub="Historial de los acompañamientos registrados por tu docente. Es de solo lectura."
      roleLabel={ROLE_LABEL.estudiante}
      basePath="/estudiante/seguimiento"
      entrepreneurshipId={items.length > 1 ? undefined : items[0].id}
      canCreate={false}
    />
  );
}
