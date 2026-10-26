# Trazabilidad — Etapa 11 (frontend)

> Una fila por **vista implementada**. Cada fila une el requisito, la ruta de la SPA, los
> endpoints que la alimentan y la evidencia de la Etapa 11. El contrato completo está en
> `docs/api.md`; la paridad visual, en `docs/design-parity.md`; el registro de la puerta, en
> `docs/verification.md` (Etapa 11).

**Alcance:** 4 vistas compartidas de autenticación + 19 de estudiante + 20 de docente + 19
de administrador + 2 vistas nuevas = **64 vistas lógicas**.

## Códigos de evidencia

| Código | Evidencia |
|---|---|
| **A** | Recorrido real de la ruta en navegador (Vite `:5173`) con la cuenta demo del rol y el seed prístino |
| **B** | Smoke contra la API real y contraste del DTO observado con `frontend/src/api/types.ts` |
| **C** | Flujo real de registro → OTP → verificación → `Limitado` → activación → baja; y recuperación OTP → contraseña nueva → login |
| **D** | `npm run typecheck` (3 workspaces) y `npm run build -w frontend` en verde |
| **E** | Estado de error, vacío, `403`/`404` o cuenta `Limitado` comprobado en pantalla |

## Compartidas (4) y vistas nuevas (2)

| # | Vista | Ruta | Requisito | Endpoints | Evidencia |
|---|---|---|---|---|---|
| 1 | Inicio de sesión | `/login` | FR-001, NFR-003 | `POST /auth/login`, `GET /users/me` | A, B, D |
| 2 | Registro | `/registro` | FR-001, FR-024 | `GET /type-doc`, `POST /auth/register` | A, C, E |
| 3 | Verificación OTP | `/verificar` | FR-001 | `POST /auth/verify`, `POST /auth/resend-code` | A, C, E |
| 4 | Recuperación de contraseña | `/recuperar` | FR-001 | `POST /auth/forgot-password`, `POST /auth/reset-password` | A, C, E |
| 5 | Acta del estudiante (nueva) | `/estudiante/acta` | FR-003, US-025, AQ-07 | `GET /acta`, `GET /acta/template`, `POST /acta`, `GET /attachments/:id` | A, B, E |
| 6 | Revisión de actas (nueva) | `/admin/actas` | FR-003, BR-009 | `GET /acta`, `PUT /acta/:id/review` | A, B, E |

## Estudiante (19)

| # | Vista | Ruta | Requisito | Endpoints | Evidencia |
|---|---|---|---|---|---|
| 7 | Inicio | `/estudiante` | FR-010, FR-022 | `GET /dashboard/student`, `GET /task` | A, B, D |
| 8 | Estado de seguimiento | `/estudiante/estado` | FR-022, FR-002, FR-003 | `GET /dashboard/student`, `GET /task/advance/entrepreneurship/:id` | A, B, E |
| 9 | Mis emprendimientos | `/estudiante/emprendimientos` | FR-012, FR-006 | `GET /entrepreneurship?q=&page=&pageSize=` | A, B, E |
| 10 | Expediente | `/estudiante/emprendimientos/:id` | FR-006, FR-017 | `GET /entrepreneurship/:id`, `GET /task/entrepreneurship/:id`, `GET /tracing/entrepreneurship/:id`, `GET /advice`, `GET /diagnosis/me`, `GET /acta` | A, B, E |
| 11 | Editar emprendimiento | `/estudiante/emprendimientos/:id/editar` | FR-012 | `GET /entrepreneurship/:id`, `PUT /entrepreneurship/:id` | A, B, E |
| 12 | Plan de trabajo | `/estudiante/plan` | FR-022 | `GET /task/entrepreneurship/:id`, `GET /task/advance/entrepreneurship/:id`, `GET /plan-phase` | A, B, E |
| 13 | Mis tareas | `/estudiante/tareas` | FR-023 | `GET /task?q=&estado=&prioridad=&page=` | A, B, E |
| 14 | Detalle de tarea | `/estudiante/tareas/:id` | FR-023, FR-008 | `GET /task/:id`, `POST /attachments/task/:id`, `PUT /task/:id/complete` | A, B, E |
| 15 | Seguimiento | `/estudiante/seguimiento` | FR-006, FR-017 | `GET /tracing/entrepreneurship/:id`, `GET /entrepreneurship` | A, B, E |
| 16 | Detalle de seguimiento | `/estudiante/seguimiento/:id` | FR-006, FR-017 | `GET /tracing/:id` | A, B, E |
| 17 | Asesorías | `/estudiante/asesorias` | FR-004, FR-015 | `GET /advice?q=&grupo=&estado=&page=` | A, B, E |
| 18 | Solicitar asesoría | `/estudiante/asesorias/solicitar` | FR-004, P-1, P-20 | `GET /entrepreneurship`, `POST /requests` | A, B, E |
| 19 | Diagnóstico | `/estudiante/diagnostico` | FR-002, AQ-09 | `GET /diagnosis/form`, `GET /diagnosis/me`, `POST /diagnosis/me`, `GET /characterization/me` | A, B, E |
| 20 | Resultado del diagnóstico | `/estudiante/diagnostico/resultado` | FR-002, AQ-09, P-3, P-35 | `GET /diagnosis/me`, `GET /diagnosis/:id/report` | A, B, E |
| 21 | Eventos | `/estudiante/eventos` | FR-021 | `GET /event?q=&tipo=&estado=&page=` | A, B, E |
| 22 | Detalle de evento | `/estudiante/eventos/:id` | FR-021, P-40 | `GET /event/:id`, `POST/DELETE /event/:id/register`, `GET /event/:id/recommendations` | A, B, E |
| 23 | Notificaciones | `/estudiante/notificaciones` | FR-005, FR-019 | `GET /notifications`, `PUT /notifications/:id/read`, `PUT /notifications/read-all`, `GET /notifications/stream` | A, B, E |
| 24 | Perfil | `/estudiante/perfil` | FR-024, FR-013 | `GET /users/me`, `PUT /users/me`, catálogos | A, B, E |
| 25 | Configuración | `/estudiante/configuracion` | FR-024, P-31 | Sin lectura de datos: enlaces a perfil, contraseña y avisos (claves `notif_*` globales) | A, E |

## Docente (20)

| # | Vista | Ruta | Requisito | Endpoints | Evidencia |
|---|---|---|---|---|---|
| 26 | Inicio | `/docente` | FR-010 | `GET /dashboard/teacher`, `GET /advice` | A, B, D |
| 27 | Emprendimientos asignados | `/docente/emprendimientos` | FR-016, NFR-002 | `GET /entrepreneurship?q=&estado=&page=` | A, B, E |
| 28 | Expediente | `/docente/emprendimientos/:id` | FR-006, FR-017 | `GET /entrepreneurship/:id`, `GET /task/entrepreneurship/:id`, `GET /tracing/entrepreneurship/:id`, `GET /advice`, `GET /diagnosis`, `GET /acta` | A, B, E |
| 29 | Registrar avance | `/docente/avances/nuevo` | FR-006, FR-017 | `GET /entrepreneurship`, `GET /plan-phase`, `POST /tracing` | A, B, E |
| 30 | Detalle de avance | `/docente/avances/:id` | FR-006, FR-008 | `GET /tracing/:id`, `PUT /tracing/:id`, `DELETE /tracing/:id`, `POST /attachments/tracing/:id` | A, B, E |
| 31 | Diagnósticos | `/docente/diagnosticos` | FR-002, NFR-002 | `GET /diagnosis?q=&emprendimientoId=&estado=&page=` | A, B, E |
| 32 | Detalle de diagnóstico | `/docente/diagnosticos/:id` | FR-002, AQ-09, P-2, P-39 | `GET /diagnosis/:id`, `GET /diagnosis/:id/report` | A, B, E |
| 33 | Asesorías | `/docente/asesorias` | FR-004, FR-015 | `GET /advice?q=&grupo=&estado=&page=` | A, B, E |
| 34 | Detalle de asesoría | `/docente/asesorias/:id` | FR-015, FR-008 | `GET /advice/:id`, `POST /advice/:id/accept`, `POST /advice/:id/repropose`, `POST /advice/:id/reject`, `POST /attachments/advice/:id` | A, B, E |
| 35 | Nueva asesoría | `/docente/asesorias/nueva` | FR-004, FR-015 | `GET /entrepreneurship`, `GET /mode`, `GET /date-times`, `POST /advice` | A, B, E |
| 36 | Tareas | `/docente/tareas` | FR-023 | `GET /task?q=&estado=&prioridad=&page=` | A, B, E |
| 37 | Nueva tarea | `/docente/tareas/nueva` | FR-023 | `GET /entrepreneurship`, `GET /plan-phase`, `POST /task` | A, B, E |
| 38 | Detalle de tarea | `/docente/tareas/:id` | FR-023, FR-008 | `GET /task/:id`, `PUT /task/:id/grade`, `PUT /task/:id/return`, `POST /attachments/task/:id` | A, B, E |
| 39 | Devolver tarea | `/docente/tareas/:id/devolver` | FR-023, R19b | `GET /task/:id`, `PUT /task/:id/return` | A, B, E |
| 40 | Eventos | `/docente/eventos` | FR-021 | `GET /event?q=&tipo=&estado=&page=` | A, B, E |
| 41 | Detalle de evento | `/docente/eventos/:id` | FR-021, P-40 | `GET /event/:id`, `GET/POST /event/:id/recommendations` | A, B, E |
| 42 | Perfil | `/docente/perfil` | FR-024 | `GET /users/me`, `PUT /users/me`, catálogos | A, B, E |
| 43 | Cambiar contraseña | `/docente/contrasena` | FR-001 | `POST /auth/forgot-password` → `/recuperar` (D28) | A, E |
| 44 | Configuración | `/docente/configuracion` | FR-024, P-31 | Sin lectura de datos: perfil, seguridad y avisos globales | A, E |
| 45 | Notificaciones | `/docente/notificaciones` | FR-005, FR-019 | `GET /notifications`, `PUT /notifications/:id/read`, `PUT /notifications/read-all`, `GET /notifications/stream` | A, B, E |

## Administrador (19)

| # | Vista | Ruta | Requisito | Endpoints | Evidencia |
|---|---|---|---|---|---|
| 46 | Inicio | `/admin` | FR-010 | `GET /dashboard/admin` | A, B, D |
| 47 | Usuarios | `/admin/usuarios` | FR-011, FR-013, FR-024 | `GET /users`, `GET /users/students`, `GET /users/teachers`, catálogos, `POST /users`, `PUT /users/:id`, `PATCH /users/:id/state`, `POST /users/:id/validate`, `POST /users/:id/reactivate`, `DELETE /users/:id` | A, B, C, E |
| 48 | Solicitudes | `/admin/solicitudes` | FR-014, FR-004 | `GET /requests`, `PUT /requests/:id/approve`, `PUT /requests/:id/reject` | A, B, E |
| 49 | Emprendimientos | `/admin/emprendimientos`, `/nuevo`, `/:id/editar` | FR-012 | `GET /entrepreneurship`, `POST /entrepreneurship`, `PUT /entrepreneurship/:id`, `POST /:id/approve`, `POST /:id/reject`, `DELETE /entrepreneurship/:id` | A, B, E |
| 50 | Expediente | `/admin/emprendimientos/:id` | FR-006, FR-017 | `GET /entrepreneurship/:id`, `GET /task/entrepreneurship/:id`, `GET /tracing/entrepreneurship/:id`, `GET /advice`, `GET /diagnosis`, `GET /acta` | A, B, E |
| 51 | Plan de trabajo | `/admin/emprendimientos/:id/plan` | FR-022 | `GET /task/entrepreneurship/:id`, `GET /task/advance/entrepreneurship/:id`, `GET /plan-phase` | A, B, E |
| 52 | Asignaciones | `/admin/asignaciones` | FR-016, BR-001 | `GET /assignments`, `POST /assignments`, `PUT /assignments/:id`, `DELETE /assignments/:id`, `GET /users/teachers`, `GET /entrepreneurship` | A, B, E |
| 53 | Seguimiento | `/admin/seguimiento`, `/nuevo`, `/:id` | FR-006, FR-017 | `GET /entrepreneurship`, `GET /tracing/entrepreneurship/:id`, `GET /tracing/:id`, `POST /tracing`, `PUT /tracing/:id`, `POST /attachments/tracing/:id` | A, B, E |
| 54 | Tablero de seguimiento | `/admin/seguimiento/tablero` | FR-010, FR-022 | `GET /dashboard/admin`, `GET /entrepreneurship` | A, B, E |
| 55 | Tareas | `/admin/tareas`, `/nueva`, `/:id`, `/:id/devolver` | FR-023 | `GET /task`, `POST /task`, `GET /task/:id`, `PUT /task/:id/grade`, `PUT /task/:id/return`, `POST /attachments/task/:id` | A, B, E |
| 56 | Asesorías | `/admin/asesorias`, `/nueva`, `/:id` | FR-004, FR-015 | `GET /advice`, `POST /advice`, `GET /advice/:id`, `POST /advice/:id/accept`, `POST /advice/:id/repropose`, `POST /advice/:id/reject`, `POST /attachments/advice/:id` | A, B, E |
| 57 | Diagnósticos | `/admin/diagnosticos`, `/:id` | FR-002, AQ-09 | `GET /diagnosis`, `GET /diagnosis/:id`, `GET /diagnosis/:id/report` | A, B, E |
| 58 | Eventos | `/admin/eventos`, `/nuevo`, `/:id`, `/:id/editar` | FR-021 | `GET /event`, `POST /event`, `GET /event/:id`, `PUT /event/:id`, `DELETE /event/:id`, `GET/POST /event/:id/recommendations` | A, B, E |
| 59 | Reportes | `/admin/reportes` | FR-009, P-44 | `GET /reports`, `GET /users/teachers`, `GET /reports/:id/export?format=csv\|xlsx\|pdf` | A, B, E |
| 60 | Respaldos | `/admin/respaldos` | FR-018, FR-009, D22 | `GET /backups/panel`, `GET /backups`, `POST /backups`, `POST /backups/:id/verify`, `GET /backups/:id/download`, `GET /backups/export?format=csv\|xlsx` | A, B, E |
| 61 | Notificaciones | `/admin/notificaciones` | FR-005, FR-019 | `GET /notifications`, `PUT /notifications/:id/read`, `PUT /notifications/read-all`, `GET /notifications/stream` | A, B, E |
| 62 | Perfil | `/admin/perfil` | FR-024 | `GET /users/me`, `PUT /users/me`, catálogos | A, B, E |
| 63 | Configuración | `/admin/configuracion` | FR-020, NFR-007 | `GET /settings`, `PUT /settings`, `GET /settings/audit` | A, B, E |
| 64 | Cambiar contraseña | `/admin/perfil` → `/recuperar` | FR-001 | `POST /auth/forgot-password` → `/recuperar` (D28) | A, E |

> El administrador comparte `PasswordPage` con los otros roles; la fila 64 documenta el
> acceso desde su perfil, no una ruta adicional.

## Guardas y alcance

| Regla | Implementación | Evidencia |
|---|---|---|
| Sesión obligatoria | `RequireAuth` envuelve `AppShell`; sin sesión, `/login` | A, B |
| Rol correcto | `RequireRole` por bloque (`estudiante`, `docente`, `administrador`); otro rol ve `/403` | A, E |
| Cuenta `Activo` | `Active` = `RequireRole` + `RequireActive` para los módulos de trabajo | A, E |
| `Limitado` solo perfil, acta y notificaciones | Esas tres rutas quedan fuera de `Active`; el resto muestra «Tu cuenta está limitada» | A, C, E |
| Alcance de datos | Los `GET` del backend recortan por rol/propiedad; la SPA no filtra datos que no recibió | B, E |
| Enlaces de notificación | `Notificacion.Url` se usa tal cual; las rutas en español existen (D24) | A, B |

## Cobertura de requisitos de la etapa

| Requisito | Vistas | Estado |
|---|---|---|
| FR-001 registro, OTP y recuperación | 1–4, 43, 64 | Completo con OTP (sin token) |
| FR-002 diagnóstico | 19, 20, 31, 32, 57 | Completo; sin puntaje por AQ-09 |
| FR-003 acta | 5, 6, 8, 10, 50 | Completo; plantilla P-36 |
| FR-004/FR-015 asesorías | 17, 18, 33–35, 48, 56 | Completo; solicitud con preferencia (P-20) |
| FR-005/FR-019 notificaciones | 23, 45, 61 | Completo; SSE invalida la bandeja |
| FR-006/FR-017 expediente | 10, 15, 16, 28, 30, 50, 53 | Completo; sin listado global de seguimiento (D26) |
| FR-008 adjuntos | 14, 30, 34, 38, 53, 55, 56 | Carga y conteo; sin galería (D25) |
| FR-009/FR-018 reportes y respaldos | 59, 60 | Completo; sin restauración (D22) |
| FR-010 tableros | 7, 26, 46, 54 | Completo con agregados reales |
| FR-011/FR-013/FR-024 usuarios | 24, 42, 44, 47, 62 | Completo; sin restauración de cuentas (P-16) |
| FR-012 emprendimientos | 9–11, 49 | Completo; sin alta por estudiante (D4) |
| FR-014 solicitudes | 48 | Completo con motivo obligatorio |
| FR-016 asignaciones | 52 | Completo; acta aprobada y topes |
| FR-020 configuración | 63 | 18 claves; sin sedes inventadas |
| FR-021 eventos | 21, 22, 40, 41, 58 | Completo; recomendaciones sin transición (P-40) |
| FR-022/FR-023 plan y evidencias | 12–14, 36–39, 51, 55 | Completo; CSV en cliente y compuerta de evidencia |
| NFR-005 accesibilidad | Todas | Etiquetas nativas, foco visible, estados vacíos y `aria-label` |
| NFR-006 paleta y escala | Todas | Seis hex y 13–32 px en `styles/tokens.css` |
| NFR-002 alcance | Todas | `404`/`403` verificados en detalles y roles |

## Huecos y decisiones que afectan la traza

| Hueco / decisión | Efecto en la SPA | Vista |
|---|---|---|
| AQ-09, P-35 | Sin puntaje, dimensiones ni bandas del diagnóstico | 8, 10, 19, 20, 32, 50, 57 |
| P-3 | PDF del diagnóstico deshabilitado y explicado | 20, 32, 57 |
| P-36 | `404 ACTA_TEMPLATE_NOT_CONFIGURED` se muestra como hueco; se puede subir el archivo | 5, 6, 8, 10, 50 |
| P-1, P-20 | El estudiante solicita cita con fecha/hora preferidas; no reprograma | 18 |
| P-40 | Recomendaciones `Pendiente` sin aceptar/rechazar ni asistencia | 22, 41, 58 |
| P-44 | Reporte de emprendimientos sin periodo | 59 |
| P-31 | Preferencias de aviso globales, no por usuario | 25, 44 |
| P-16 | Sin restauración de cuentas dadas de baja | 47 |
| D22 | Sin restauración de respaldos | 60 |
| D25 | Adjuntos: conteo y carga, sin descargas inventadas | 14, 30, 34, 38, 53, 55, 56 |
| D26 | Seguimiento admin por emprendimiento, sin listado global | 53 |
| D4 | El estudiante no da de alta emprendimientos | 9, 49 |
| P-7 | Sin avatar | 24, 42, 62 |
| AQ-07 | Sin módulo de habilitaciones; `Limitado` usa perfil, acta y notificaciones | 5, 24, 42, 62, 23/45/61 |
| P2 | Sin interfaz de auditor; el backend expone `/audit/*` | — |

## Verificación

- Recorrido completo: **64/64 rutas** con los tres roles, más una cuenta registrada en vivo.
- `npm run typecheck`: shared, backend y frontend sin errores.
- `npm run build -w frontend`: build correcto (aviso de chunk > 500 kB).
- Estados: loading, error con reintento y vacío en todas las listas; `403`/`404` y cuenta
  `Limitado` con pantalla propia.
- Flujos auth reales: registro → OTP → verificación → `Limitado` → activación → baja;
  recuperación → OTP → contraseña nueva → login.
- Entorno final: base recreada desde cero con las 5 cuentas demo y los datos del seed; sin
  datos de prueba.
- El detalle de cada comprobación está en `docs/verification.md`, sección «Etapa 11».
