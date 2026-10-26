import { AdviceDetailPage } from '../shared/AdviceDetailPage.tsx';
import { AdviceFormPage } from '../shared/AdviceFormPage.tsx';
import { AdviceListPage } from '../shared/AdviceListPage.tsx';
import { DiagnosesListPage } from '../shared/DiagnosesListPage.tsx';
import { DiagnosisDetailPage } from '../shared/DiagnosisDetailPage.tsx';
import { EntrepreneurshipPlanPage } from '../shared/EntrepreneurshipPlanPage.tsx';
import { EntrepreneurshipsListPage } from '../shared/EntrepreneurshipsListPage.tsx';
import { EventDetailPage } from '../shared/EventDetailPage.tsx';
import { EventFormPage } from '../shared/EventFormPage.tsx';
import { EventsListPage } from '../shared/EventsListPage.tsx';
import { ExpedientePage } from '../shared/ExpedientePage.tsx';
import { TaskDetailPage } from '../shared/TaskDetailPage.tsx';
import { TaskFormPage } from '../shared/TaskFormPage.tsx';
import { TaskReturnPage } from '../shared/TaskReturnPage.tsx';
import { TasksListPage } from '../shared/TasksListPage.tsx';
import { TracingDetailPage } from '../shared/TracingDetailPage.tsx';
import { TracingFormPage } from '../shared/TracingFormPage.tsx';
import { TracingListPage } from '../shared/TracingListPage.tsx';
import { ROLE_LABEL } from '../../navigation/nav.ts';

/**
 * Contenedores del rol Administrador.
 *
 * Casi todo el trabajo institucional reutiliza las vistas compartidas: el
 * alcance lo aplica el servidor y aquí solo se fijan rutas, etiquetas y las
 * acciones que el rol puede ejecutar. Las vistas propias del administrador
 * (asignaciones, actas, reportes, respaldos, configuración y tablero de
 * seguimiento) viven en archivos aparte.
 */

const BASE = '/admin';

export function AdminEntrepreneurshipsPage() {
  return (
    <EntrepreneurshipsListPage
      roleLabel={ROLE_LABEL.administrador}
      basePath={`${BASE}/emprendimientos`}
      canCreate
      canManage
    />
  );
}

export function AdminExpedientePage() {
  return (
    <ExpedientePage
      basePath={`${BASE}/emprendimientos`}
      roleLabel={ROLE_LABEL.administrador}
      canManage
    />
  );
}

export function AdminPlanPage() {
  return (
    <EntrepreneurshipPlanPage
      roleLabel={ROLE_LABEL.administrador}
      listPath={`${BASE}/emprendimientos`}
      tasksPath={`${BASE}/tareas`}
    />
  );
}

/**
 * Seguimiento institucional.
 *
 * La API no expone un listado global de seguimientos: se consultan por
 * emprendimiento y la vista ofrece el selector de expediente. El tablero
 * agregado vive en `/admin/seguimiento/tablero`.
 */
export function AdminTrackingPage() {
  return (
    <TracingListPage
      title="Seguimiento"
      sub="Avances de fase y comentarios registrados en todos los emprendimientos."
      roleLabel={ROLE_LABEL.administrador}
      basePath={`${BASE}/seguimiento`}
      canCreate
    />
  );
}

export function AdminTrackingDetailPage() {
  return (
    <TracingDetailPage roleLabel={ROLE_LABEL.administrador} basePath={`${BASE}/seguimiento`} />
  );
}

export function AdminTrackingFormPage() {
  return <TracingFormPage basePath={`${BASE}/seguimiento`} roleLabel={ROLE_LABEL.administrador} />;
}

export function AdminTasksPage() {
  return (
    <TasksListPage
      title="Tareas"
      sub="Tareas de todos los emprendimientos. La coordinación puede crearlas y devolverlas."
      roleLabel={ROLE_LABEL.administrador}
      basePath={`${BASE}/tareas`}
      canCreate
    />
  );
}

export function AdminTaskDetailPage() {
  return (
    <TaskDetailPage
      basePath={`${BASE}/tareas`}
      roleLabel={ROLE_LABEL.administrador}
      returnPath={`${BASE}/tareas/:id/devolver`}
    />
  );
}

export function AdminTaskFormPage() {
  return <TaskFormPage basePath={`${BASE}/tareas`} roleLabel={ROLE_LABEL.administrador} />;
}

export function AdminTaskReturnPage() {
  return <TaskReturnPage basePath={`${BASE}/tareas`} roleLabel={ROLE_LABEL.administrador} />;
}

export function AdminAdvicesPage() {
  return (
    <AdviceListPage
      title="Asesorías"
      sub="Agenda global de acompañamiento. Crea, confirma o cierra sesiones."
      roleLabel={ROLE_LABEL.administrador}
      basePath={`${BASE}/asesorias`}
      canCreate
      groupedFilter
    />
  );
}

export function AdminAdviceDetailPage() {
  return <AdviceDetailPage basePath={`${BASE}/asesorias`} roleLabel={ROLE_LABEL.administrador} />;
}

export function AdminAdviceFormPage() {
  return <AdviceFormPage basePath={`${BASE}/asesorias`} roleLabel={ROLE_LABEL.administrador} />;
}

export function AdminDiagnosesPage() {
  return (
    <DiagnosesListPage roleLabel={ROLE_LABEL.administrador} basePath={`${BASE}/diagnosticos`} />
  );
}

export function AdminDiagnosisDetailPage() {
  return (
    <DiagnosisDetailPage roleLabel={ROLE_LABEL.administrador} basePath={`${BASE}/diagnosticos`} />
  );
}

export function AdminEventsPage() {
  return <EventsListPage roleLabel={ROLE_LABEL.administrador} basePath={`${BASE}/eventos`} canCreate />;
}

export function AdminEventDetailPage() {
  return <EventDetailPage roleLabel={ROLE_LABEL.administrador} basePath={`${BASE}/eventos`} />;
}

export function AdminEventFormPage() {
  return <EventFormPage />;
}
