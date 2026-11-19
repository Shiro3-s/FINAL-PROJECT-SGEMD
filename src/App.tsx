import { Outlet, Route, Routes } from 'react-router-dom';
import { AppShell } from './components/AppShell.tsx';
import { RequireActive, RequireAuth, RequireRole } from './auth/guards.tsx';
import { HomeRedirect } from './pages/HomeRedirect.tsx';
import { ForbiddenPage } from './pages/ForbiddenPage.tsx';
import { NotFoundPage } from './pages/NotFoundPage.tsx';
import { LoginPage } from './pages/auth/LoginPage.tsx';
import { RecoverPage } from './pages/auth/RecoverPage.tsx';
import { RegisterPage } from './pages/auth/RegisterPage.tsx';
import { VerifyPage } from './pages/auth/VerifyPage.tsx';
import { ActaPage } from './pages/shared/ActaPage.tsx';
import { AccountSettingsPage } from './pages/shared/AccountSettingsPage.tsx';
import { NotificationsPage } from './pages/shared/NotificationsPage.tsx';
import { PasswordPage } from './pages/shared/PasswordPage.tsx';
import { ProfilePage } from './pages/shared/ProfilePage.tsx';
import { StudentAdviceRequestPage } from './pages/estudiante/StudentAdviceRequestPage.tsx';
import { StudentDashboardPage } from './pages/estudiante/StudentDashboardPage.tsx';
import { StudentDiagnosisPage } from './pages/estudiante/StudentDiagnosisPage.tsx';
import { StudentDiagnosisResultPage } from './pages/estudiante/StudentDiagnosisResultPage.tsx';
import { StudentEntrepreneurshipEditPage } from './pages/estudiante/StudentEntrepreneurshipEditPage.tsx';
import { StudentEntrepreneurshipsPage } from './pages/estudiante/StudentEntrepreneurshipsPage.tsx';
import { StudentPlanPage } from './pages/estudiante/StudentPlanPage.tsx';
import { StudentStatePage } from './pages/estudiante/StudentStatePage.tsx';
import {
  StudentAdviceDetailPage,
  StudentAdvicesPage,
  StudentEventDetailPage,
  StudentEventsPage,
  StudentExpedientePage,
  StudentTaskDetailPage,
  StudentTasksPage,
  StudentTracingDetailPage,
  StudentTracingPage,
} from './pages/estudiante/StudentRolePages.tsx';
import { TeacherDashboardPage } from './pages/docente/TeacherDashboardPage.tsx';
import {
  TeacherAdvanceDetailPage,
  TeacherAdvanceFormPage,
  TeacherAdvancesPage,
  TeacherAdviceDetailPage,
  TeacherAdviceFormPage,
  TeacherAdvicesPage,
  TeacherDiagnosesPage,
  TeacherDiagnosisDetailPage,
  TeacherEntrepreneurshipsPage,
  TeacherEventDetailPage,
  TeacherEventsPage,
  TeacherExpedientePage,
  TeacherTaskDetailPage,
  TeacherTaskFormPage,
  TeacherTaskReturnPage,
  TeacherTasksPage,
} from './pages/docente/TeacherRolePages.tsx';
import { AdminDashboardPage } from './pages/admin/AdminDashboardPage.tsx';
import { AdminRequestsPage } from './pages/admin/AdminRequestsPage.tsx';
import { AdminUsersPage } from './pages/admin/AdminUsersPage.tsx';
import { AdminAssignmentsPage } from './pages/admin/AdminAssignmentsPage.tsx';
import { AdminActasPage } from './pages/admin/AdminActasPage.tsx';
import { AdminEntrepreneurshipFormPage } from './pages/admin/AdminEntrepreneurshipFormPage.tsx';
import { AdminTrackingDashboardPage } from './pages/admin/AdminTrackingDashboardPage.tsx';
import { AdminReportsPage } from './pages/admin/AdminReportsPage.tsx';
import { AdminBackupsPage } from './pages/admin/AdminBackupsPage.tsx';
import { AdminSettingsPage } from './pages/admin/AdminSettingsPage.tsx';
import {
  AdminAdviceDetailPage,
  AdminAdviceFormPage,
  AdminAdvicesPage,
  AdminDiagnosesPage,
  AdminDiagnosisDetailPage,
  AdminEntrepreneurshipsPage,
  AdminEventDetailPage,
  AdminEventFormPage,
  AdminEventsPage,
  AdminExpedientePage,
  AdminPlanPage,
  AdminTaskDetailPage,
  AdminTaskFormPage,
  AdminTaskReturnPage,
  AdminTasksPage,
  AdminTrackingDetailPage,
  AdminTrackingFormPage,
  AdminTrackingPage,
} from './pages/admin/AdminRolePages.tsx';

/**
 * Rutas de la SPA.
 *
 * Tres bloques por rol, cada uno con las mismas guardas: sesión (`RequireAuth`),
 * rol (`RequireRole`) y cuenta `Activo` (a través de `Active`). Perfil, acta y
 * notificaciones quedan fuera de la última guarda porque son lo único que puede
 * usar una cuenta `Limitado` o `Inactivo` (AQ-07 opción A).
 *
 * Los segmentos van en español: las notificaciones guardan enlaces profundos con
 * esa forma y cambiarlos rompería los enlaces ya emitidos (`docs/decisions.md`).
 */
export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/registro" element={<RegisterPage />} />
      <Route path="/verificar" element={<VerifyPage />} />
      <Route path="/recuperar" element={<RecoverPage />} />
      <Route path="/" element={<HomeRedirect />} />
      <Route path="/403" element={<ForbiddenPage />} />

      <Route
        element={
          <RequireAuth>
            <AppShell />
          </RequireAuth>
        }
      >
        <Route path="/estudiante">
          <Route element={<Active as="estudiante" />}>
            <Route index element={<StudentDashboardPage />} />
            <Route path="emprendimientos" element={<StudentEntrepreneurshipsPage />} />
            <Route
              path="emprendimientos/:id"
              element={<StudentExpedientePage />}
            />
            <Route
              path="emprendimientos/:id/editar"
              element={<StudentEntrepreneurshipEditPage />}
            />
            <Route path="estado" element={<StudentStatePage />} />
            <Route path="plan" element={<StudentPlanPage />} />
            <Route path="diagnostico" element={<StudentDiagnosisPage />} />
            <Route path="diagnostico/resultado" element={<StudentDiagnosisResultPage />} />
            <Route path="tareas" element={<StudentTasksPage />} />
            <Route path="tareas/:id" element={<StudentTaskDetailPage />} />
            <Route path="seguimiento" element={<StudentTracingPage />} />
            <Route path="seguimiento/:id" element={<StudentTracingDetailPage />} />
            <Route path="asesorias" element={<StudentAdvicesPage />} />
            <Route path="asesorias/solicitar" element={<StudentAdviceRequestPage />} />
            <Route path="asesorias/:id" element={<StudentAdviceDetailPage />} />
            <Route path="eventos" element={<StudentEventsPage />} />
            <Route path="eventos/:id" element={<StudentEventDetailPage />} />
            <Route path="configuracion" element={<AccountSettingsPage />} />
            <Route path="contrasena" element={<PasswordPage />} />
          </Route>
          <Route path="acta" element={<ActaPage />} />
          <Route path="notificaciones" element={<NotificationsPage />} />
          <Route path="perfil" element={<ProfilePage />} />
        </Route>

        <Route path="/docente">
          <Route element={<Active as="docente" />}>
            <Route index element={<TeacherDashboardPage />} />
            <Route path="emprendimientos" element={<TeacherEntrepreneurshipsPage />} />
            <Route path="emprendimientos/:id" element={<TeacherExpedientePage />} />
            <Route path="avances" element={<TeacherAdvancesPage />} />
            <Route path="avances/nuevo" element={<TeacherAdvanceFormPage />} />
            <Route path="avances/:id" element={<TeacherAdvanceDetailPage />} />
            <Route path="tareas" element={<TeacherTasksPage />} />
            <Route path="tareas/nueva" element={<TeacherTaskFormPage />} />
            <Route path="tareas/:id" element={<TeacherTaskDetailPage />} />
            <Route path="tareas/:id/devolver" element={<TeacherTaskReturnPage />} />
            <Route path="diagnosticos" element={<TeacherDiagnosesPage />} />
            <Route path="diagnosticos/:id" element={<TeacherDiagnosisDetailPage />} />
            <Route path="asesorias" element={<TeacherAdvicesPage />} />
            <Route path="asesorias/nueva" element={<TeacherAdviceFormPage />} />
            <Route path="asesorias/:id" element={<TeacherAdviceDetailPage />} />
            <Route path="eventos" element={<TeacherEventsPage />} />
            <Route path="eventos/:id" element={<TeacherEventDetailPage />} />
            <Route path="configuracion" element={<AccountSettingsPage />} />
            <Route path="contrasena" element={<PasswordPage />} />
          </Route>
          <Route path="notificaciones" element={<NotificationsPage />} />
          <Route path="perfil" element={<ProfilePage />} />
        </Route>

        <Route path="/admin">
          <Route element={<Active as="administrador" />}>
            <Route index element={<AdminDashboardPage />} />
            <Route path="solicitudes" element={<AdminRequestsPage />} />
            <Route path="usuarios" element={<AdminUsersPage />} />
            <Route path="asignaciones" element={<AdminAssignmentsPage />} />
            <Route path="actas" element={<AdminActasPage />} />
            <Route path="emprendimientos" element={<AdminEntrepreneurshipsPage />} />
            <Route path="emprendimientos/nuevo" element={<AdminEntrepreneurshipFormPage />} />
            <Route path="emprendimientos/:id" element={<AdminExpedientePage />} />
            <Route
              path="emprendimientos/:id/editar"
              element={<AdminEntrepreneurshipFormPage />}
            />
            <Route path="emprendimientos/:id/plan" element={<AdminPlanPage />} />
            <Route path="diagnosticos" element={<AdminDiagnosesPage />} />
            <Route path="diagnosticos/:id" element={<AdminDiagnosisDetailPage />} />
            <Route path="seguimiento" element={<AdminTrackingPage />} />
            <Route path="seguimiento/tablero" element={<AdminTrackingDashboardPage />} />
            <Route path="seguimiento/nuevo" element={<AdminTrackingFormPage />} />
            <Route path="seguimiento/:id" element={<AdminTrackingDetailPage />} />
            <Route path="tareas" element={<AdminTasksPage />} />
            <Route path="tareas/nueva" element={<AdminTaskFormPage />} />
            <Route path="tareas/:id" element={<AdminTaskDetailPage />} />
            <Route path="tareas/:id/devolver" element={<AdminTaskReturnPage />} />
            <Route path="asesorias" element={<AdminAdvicesPage />} />
            <Route path="asesorias/nueva" element={<AdminAdviceFormPage />} />
            <Route path="asesorias/:id" element={<AdminAdviceDetailPage />} />
            <Route path="eventos" element={<AdminEventsPage />} />
            <Route path="eventos/nuevo" element={<AdminEventFormPage />} />
            <Route path="eventos/:id" element={<AdminEventDetailPage />} />
            <Route path="eventos/:id/editar" element={<AdminEventFormPage />} />
            <Route path="reportes" element={<AdminReportsPage />} />
            <Route path="respaldos" element={<AdminBackupsPage />} />
            <Route path="configuracion" element={<AdminSettingsPage />} />
          </Route>
          <Route path="notificaciones" element={<NotificationsPage />} />
          <Route path="perfil" element={<ProfilePage />} />
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}

/**
 * Guarda de rol + cuenta `Activo`.
 *
 * Se usa como ruta sin `path`: envuelve a las hijas y pinta su `Outlet` solo si
 * el rol coincide y la cuenta está activa. Perfil, acta y notificaciones se
 * declaran fuera de esta guarda a propósito.
 */
function Active({ as }: { as: 'estudiante' | 'docente' | 'administrador' }) {
  return (
    <RequireRole roles={[as]}>
      <RequireActive>
        <Outlet />
      </RequireActive>
    </RequireRole>
  );
}
