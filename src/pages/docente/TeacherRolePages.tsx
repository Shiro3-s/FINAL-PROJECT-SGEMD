import { AdviceDetailPage } from '../shared/AdviceDetailPage.tsx';
import { AdviceFormPage } from '../shared/AdviceFormPage.tsx';
import { AdviceListPage } from '../shared/AdviceListPage.tsx';
import { DiagnosesListPage } from '../shared/DiagnosesListPage.tsx';
import { DiagnosisDetailPage } from '../shared/DiagnosisDetailPage.tsx';
import { EntrepreneurshipsListPage } from '../shared/EntrepreneurshipsListPage.tsx';
import { EventDetailPage } from '../shared/EventDetailPage.tsx';
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
 * Contenedores del rol Docente.
 *
 * Todas las vistas son compartidas con el administrador o con el estudiante:
 * el servidor aplica el alcance de las asignaciones activas y estas funciones
 * solo fijan rutas, etiquetas y las acciones que el rol puede ejecutar. El
 * docente no crea eventos ni emprendimientos; sí registra avances, tareas y
 * asesorías, y califica o devuelve tareas.
 */

const BASE = '/docente';

export function TeacherEntrepreneurshipsPage() {
  return <EntrepreneurshipsListPage roleLabel={ROLE_LABEL.docente} basePath={`${BASE}/emprendimientos`} />;
}

export function TeacherExpedientePage() {
  return (
    <ExpedientePage
      basePath={`${BASE}/emprendimientos`}
      roleLabel={ROLE_LABEL.docente}
      canManage={false}
    />
  );
}

export function TeacherAdvancesPage() {
  return (
    <TracingListPage
      title="Avances"
      sub="Avances de fase y comentarios registrados en tus emprendimientos asignados."
      roleLabel={ROLE_LABEL.docente}
      basePath={`${BASE}/avances`}
      canCreate
    />
  );
}

export function TeacherAdvanceDetailPage() {
  return <TracingDetailPage roleLabel={ROLE_LABEL.docente} basePath={`${BASE}/avances`} />;
}

export function TeacherAdvanceFormPage() {
  return <TracingFormPage />;
}

export function TeacherTasksPage() {
  return (
    <TasksListPage
      title="Tareas"
      sub="Tareas del plan de trabajo de tus emprendimientos. Califica o devuelve las entregas."
      roleLabel={ROLE_LABEL.docente}
      basePath={`${BASE}/tareas`}
      canCreate
    />
  );
}

export function TeacherTaskDetailPage() {
  return (
    <TaskDetailPage
      basePath={`${BASE}/tareas`}
      roleLabel={ROLE_LABEL.docente}
      returnPath={`${BASE}/tareas/:id/devolver`}
    />
  );
}

export function TeacherTaskFormPage() {
  return <TaskFormPage basePath={`${BASE}/tareas`} roleLabel={ROLE_LABEL.docente} />;
}

export function TeacherTaskReturnPage() {
  return <TaskReturnPage basePath={`${BASE}/tareas`} roleLabel={ROLE_LABEL.docente} />;
}

export function TeacherDiagnosesPage() {
  return <DiagnosesListPage roleLabel={ROLE_LABEL.docente} basePath={`${BASE}/diagnosticos`} />;
}

export function TeacherDiagnosisDetailPage() {
  return <DiagnosisDetailPage roleLabel={ROLE_LABEL.docente} basePath={`${BASE}/diagnosticos`} />;
}

export function TeacherAdvicesPage() {
  return (
    <AdviceListPage
      title="Asesorías"
      sub="Sesiones de acompañamiento. Confirma, reprograma o cierra las que tienes asignadas."
      roleLabel={ROLE_LABEL.docente}
      basePath={`${BASE}/asesorias`}
      canCreate
      groupedFilter
    />
  );
}

export function TeacherAdviceDetailPage() {
  return <AdviceDetailPage basePath={`${BASE}/asesorias`} roleLabel={ROLE_LABEL.docente} />;
}

export function TeacherAdviceFormPage() {
  return <AdviceFormPage basePath={`${BASE}/asesorias`} roleLabel={ROLE_LABEL.docente} />;
}

export function TeacherEventsPage() {
  return (
    <EventsListPage roleLabel={ROLE_LABEL.docente} basePath={`${BASE}/eventos`} canCreate={false} />
  );
}

export function TeacherEventDetailPage() {
  return <EventDetailPage roleLabel={ROLE_LABEL.docente} basePath={`${BASE}/eventos`} />;
}
