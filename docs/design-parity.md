# Paridad de diseño — prototipo → React

> Una fila por **vista lógica**. El prototipo es la referencia visual y conductual; la
> aceptación del MVP es API + pruebas, no similitud de píxeles (master §8).
> Estado: `pending` · `ported` · `delta` (diferencia deliberada) · `omitted` (con motivo).
> Fuente de estilos: `prototype/lib_css.py` (valores) y `prototype/DESIGN.md` (intención).
> Última actualización: 2026-10-26.

**Totales:** 62 vistas lógicas del prototipo (73 archivos HTML) **+ 2 vistas nuevas = 64
vistas lógicas implementadas**. Ninguna queda en `pending`: **35 `delta`**, **29 `ported`** y **3
`omitted`**. Las diferencias deliberadas se deben al contrato de la API, a los huecos
registrados en `docs/decisions.md` o a la decisión de no inventar datos.

## Compartidas (4)

| Archivo del prototipo | Ruta React | Estado | Notas |
|---|---|---|---|
| `compartido/login.html` | `/login` | delta | Sin chips de cuentas demo ni «Recordarme»; a dos columnas con el logo real. Enlaza a «Verifica tu cuenta» y a la recuperación |
| `compartido/registro.html` | `/registro` | delta | Solo los 6 campos de `POST /auth/register` + `aceptaTratamiento`; los datos académicos se completan después en el perfil (FR-024). Se omiten correo personal, celular y la segunda casilla del prototipo |
| `compartido/verificar-otp.html` | `/verificar` | delta | OTP de 8 dígitos (no enlace con token), reenvío con espera de 60 s y aviso de 5 min/5 intentos; conserva el correo en el estado de la ruta |
| `compartido/recuperar-contrasena.html` | `/recuperar` | delta | Flujo propio en 3 pasos: correo → código OTP + nueva contraseña → listo. No existe reset por token (`/recuperar/:token` queda omitido) |

## Estudiante (27 archivos → 19 vistas)

| Archivo(s) del prototipo | Ruta React | Estado | Notas |
|---|---|---|---|
| `estudiante/dashboard.html` | `/estudiante` | ported | Emprendimiento propio, etapa, % de avance y tareas pendientes/vencidas desde `GET /dashboard/student` |
| `estudiante/estado-seguimiento.html` | `/estudiante/estado` | delta | Una barra por fase y, además, tarjetas de diagnóstico y acta. El puntaje se declara no disponible (AQ-09) |
| `estudiante/emprendimientos.html` | `/estudiante/emprendimientos` | delta | Lista con búsqueda `?q=` sincronizada con la URL y estado vacío específico; solo el propio y los paralelos autorizados |
| `estudiante/emprendimiento-detalle.html`, `-mochilas.html` | `/estudiante/emprendimientos/:id` | delta | Expediente con pestañas resumen, tareas, seguimiento, diagnóstico, asesorías y acta. Las evidencias se muestran como conteo: la API no lista adjuntos |
| `estudiante/emprendimiento-editar.html` | `/estudiante/emprendimientos/:id/editar` | ported | Solo `nombre`, `descripcion` y `redesSociales`, que es lo que acepta `PUT /entrepreneurship/:id` para el estudiante |
| `estudiante/plan-trabajo.html` | `/estudiante/plan` | delta | Agrupado por fase y con pestañas por emprendimiento. «Descargar plan (CSV)» se genera en el cliente; no hay PDF del plan |
| `estudiante/tareas.html` | `/estudiante/tareas` | ported | Filtros por estado y prioridad, búsqueda y paginación |
| `estudiante/tarea-detalle.html` + `-en-revision` + 3 `-completada-*` | `/estudiante/tareas/:id` | delta | **Conserva la compuerta de evidencia** (FR-023): entregar exige ≥1 archivo. Los 5 estados del prototipo se resuelven con badges, no con rutas; solo se sube y se ve el conteo, sin descargas inventadas |
| `estudiante/seguimiento.html` | `/estudiante/seguimiento` | ported | Historial de solo lectura con filtro por emprendimiento |
| `estudiante/seguimiento-detalle.html` | `/estudiante/seguimiento/:id` | delta | Fecha, autor, estado de revisión, puntaje y retroalimentación; autor puede venir nulo y no se ofrece descarga de evidencias |
| `estudiante/asesorias.html` | `/estudiante/asesorias` | ported | Solo lectura y agrupación de estados; el estudiante no agenda |
| `estudiante/solicitar-asesoria.html` | `/estudiante/asesorias/solicitar` | delta | Crea una **solicitud** `Cita` (`POST /requests`) con fecha y hora preferidas en `detalle` (P-20); el admin fija docente y bloque al aprobar (P-1) |
| `estudiante/diagnostico.html` | `/estudiante/diagnostico` | ported | 5 secciones / 22 preguntas con guardado de borrador y retoma |
| `estudiante/diagnostico-resultados.html` | `/estudiante/diagnostico/resultado` | delta | Respuestas por sección; **sin puntaje, dimensiones ni bandas** mientras AQ-09 esté abierta (P-35) y «Descargar PDF» deshabilitado (P-3) |
| `estudiante/eventos.html` | `/estudiante/eventos` | ported | Agenda institucional con búsqueda, tipo y estado |
| `estudiante/evento-detalle-*.html` (4) | `/estudiante/eventos/:id` | delta | Una ruta con contenido por tipo, inscripción/cancelación y recomendaciones recibidas; no hay control de asistencia (P-40) |
| `estudiante/notificaciones.html` | `/estudiante/notificaciones` | delta | Bandeja con estado de lectura y tipo, y marcar todo como leído. No hay chips separados por módulo; el SSE `notification` invalida la bandeja |
| `estudiante/perfil.html` | `/estudiante/perfil` | ported | Datos de cuenta no editables + datos académicos editables desde `PUT /users/me` |
| `estudiante/configuracion.html` | `/estudiante/configuracion` | delta | Perfil y seguridad; los avisos son claves globales del programa (`notif_*`) y se explican como tales, no como interruptores por usuario (P-31) |

## Docente (23 archivos → 20 vistas)

| Archivo(s) del prototipo | Ruta React | Estado | Notas |
|---|---|---|---|
| `docente/dashboard.html` | `/docente` | ported | Cartera asignada, carga de asesorías, tareas por revisar, agenda, actividad y acciones rápidas |
| `docente/emprendimientos.html` | `/docente/emprendimientos` | delta | Solo asignados, en tabla con búsqueda `?q=` y filtro de estado. Sin alternancia tarjetas/tabla ni filtros de etapa/sector/evidencia |
| `docente/emprendimiento-expediente.html` | `/docente/emprendimientos/:id` | delta | Expediente consolidado con pestañas; el acta es solo lectura y las evidencias se ven como conteo |
| `docente/avance-form.html` | `/docente/avances/nuevo` | delta | Emprendimiento, tipo, fase, fecha, descripción, puntaje y estado; la evidencia se sube desde el detalle después de crear el seguimiento |
| `docente/avance-detalle.html` | `/docente/avances/:id` | ported | Detalle con edición del autor/administrador y carga de evidencias |
| `docente/diagnostico.html` | `/docente/diagnosticos` | delta | Ruta en plural y bandeja compartida con búsqueda, emprendimiento y estado; sin selector previo del prototipo |
| `docente/diagnostico-revision.html` | `/docente/diagnosticos/:id` | delta | Solo lectura, sin recomendaciones ni puntaje: `valoracion` está detrás de AQ-09 (P-2, P-39) |
| `docente/asesorias.html` | `/docente/asesorias` | ported | Filtro agrupado: Por agendar · Agendada · Completada · Cancelada |
| `docente/asesoria-detalle.html` | `/docente/asesorias/:id` | ported | Confirmar y notificar · Proponer otra fecha · Rechazar solicitud, con motivo obligatorio |
| `docente/asesoria-form.html` | `/docente/asesorias/nueva` | delta | Agenda para **un** emprendimiento; el diagrama no tiene asesoría grupal (P-26) y el docente solo agenda para sí mismo |
| `docente/tareas.html` | `/docente/tareas` | ported | Filtros por estado y prioridad, búsqueda y paginación |
| `docente/tarea-form.html` | `/docente/tareas/nueva` | delta | Alta para el propietario del emprendimiento; no hay asignación «a todo el grupo» (P-26) |
| `docente/tarea-detalle.html` | `/docente/tareas/:id` | ported | Calificar 0–100 con retroalimentación y devolver; incluye la compuerta de evidencia |
| `docente/tarea-devolver.html` | `/docente/tareas/:id/devolver` | ported | Motivo (selector) + observaciones |
| `docente/eventos.html` | `/docente/eventos` | ported | Agenda con búsqueda, tipo y estado |
| `docente/evento-detalle-*.html` (4) | `/docente/eventos/:id` | ported | Incluye «Recomendar a un emprendimiento»; la recomendación queda `Pendiente` sin transiciones (P-40) |
| `docente/perfil.html` | `/docente/perfil` | ported | Datos de cuenta, datos editables y enlace al cambio de contraseña |
| `docente/contrasena.html` | `/docente/contrasena` | delta | No pide la contraseña actual: envía un código al correo de la sesión (`POST /auth/forgot-password`) y guía al flujo OTP existente; sin endpoints nuevos |
| `docente/configuracion.html` | `/docente/configuracion` | delta | Perfil y seguridad; las preferencias de aviso son globales y se explican como claves `notif_*` (P-31) |
| `docente/notificaciones.html` | `/docente/notificaciones` | delta | Bandeja compartida con filtros de lectura y tipo, contador y «marcar todo»; el SSE invalida la lista |

> **Sin ruta docente de "Seguimiento"**: el módulo se retiró y lo reemplazan "Registrar
> avance" y la columna Evidencia. `prototype/DESIGN.md` línea 53 está obsoleta
> (`docs/decisions.md` #23).

## Administrador (19 archivos → 19 vistas)

| Archivo(s) del prototipo | Ruta React | Estado | Notas |
|---|---|---|---|
| `admin/dashboard.html` | `/admin` | delta | Agregados reales de `GET /dashboard/admin` con gráficos SVG (D19), alertas, agenda, actividad y distribución por sede/sector. No ofrece restaurar respaldos |
| `admin/usuarios.html` | `/admin/usuarios` | delta | Pestañas estudiantes/docentes, búsqueda `?q=`, filtro de estado, alta, edición, baja lógica y `Limitado` → validar. Sin teléfono, área ni horas del prototipo (no existen en `usuarios`); no hay restauración de cuentas (P-16) |
| `admin/solicitudes.html` | `/admin/solicitudes` | ported | Pestañas Desbloqueos · Paralelos · Citas, contador y aprobar/rechazar con **motivo obligatorio** |
| `admin/emprendimientos.html` | `/admin/emprendimientos` | delta | Lista con búsqueda, estado y detalle. Sin «Tipo» (no hay catálogo), sin editar «Avance» (derivado de tareas) y sin «Docente asignado» en el formulario (vive en asignaciones) |
| `admin/emprendimiento-expediente.html` | `/admin/emprendimientos/:id` | delta | Pestañas consolidadas con acciones por rol; la exportación vive en Reportes y no se duplica aquí |
| `admin/emprendimiento-plan.html` | `/admin/emprendimientos/:id/plan` | ported | Plan por fases, compartido con la vista del estudiante y con descarga CSV |
| `admin/asignaciones.html` | `/admin/asignaciones` | ported | Crear, reasignar y retirar; enlace profundo `#asignar-docente`; exige acta aprobada y respeta los topes de 12 emprendimientos y de horas |
| `admin/seguimiento.html` | `/admin/seguimiento` | delta | No hay listado global en la API: se elige un emprendimiento y se ven sus avances. El alta de avance está disponible para el admin |
| `admin/seguimiento-dashboard.html` | `/admin/seguimiento/tablero` | ported | Avance agregado por emprendimiento y fase |
| `admin/tareas.html` | `/admin/tareas` | ported | Todas las tareas, búsqueda, filtros y estado de calificación |
| `admin/asesorias.html` | `/admin/asesorias` | ported | Agenda global; crear y asignar docente directamente |
| `admin/diagnosticos.html` | `/admin/diagnosticos` | delta | Bandeja y detalle de solo lectura. Sin edición del banco de preguntas ni informe PDF: la rúbrica sigue abierta (AQ-09, P-3, P-35) |
| `admin/eventos.html` | `/admin/eventos` | ported | Lista con búsqueda, tipo y estado; los borradores solo los ve el admin |
| `admin/evento-form.html` | `/admin/eventos/nuevo`, `/admin/eventos/:id/editar` | ported | Título, audiencia, descripción, capacidad, fecha, inicio/fin, lugar, enlace y publicación; `Aprobado`/`Rechazado` reservados (P-37) |
| `admin/reportes.html` | `/admin/reportes` | delta | CSV / XLSX / PDF con tipo y periodo; `emprendimientos` no admite periodo porque la tabla no tiene fecha de creación (P-44) |
| `admin/respaldos.html` | `/admin/respaldos` | delta | Último respaldo, tamaños lógico y añadido, historial, integridad, crear respaldo, descargar artefactos y exportar la base. **Sin restauración**: no hay endpoint (D22) |
| `admin/notificaciones.html` | `/admin/notificaciones` | delta | Misma bandeja compartida: filtros de lectura y tipo, contador de no leídas, enlaces profundos y marcar todo |
| `admin/perfil.html` | `/admin/perfil` | ported | Datos propios + acceso al cambio de contraseña por código |
| `admin/configuracion.html` | `/admin/configuracion` | delta | 18 claves en 5 bloques, guardado por lote solo de lo cambiado, etiquetas humanas y bitácora en pestaña aparte. Sin sedes ni «cuenta admin» inventadas |

## Vistas nuevas (ausentes del prototipo)

| Vista | Ruta React | Estado | Requisito |
|---|---|---|---|
| Acta del estudiante | `/estudiante/acta` | ported | FR-003, US-025. Plantilla con hueco P-36 y carga/reemplazo del PDF firmado |
| Revisión de acta (admin) | `/admin/actas` | ported | FR-003, BR-009. Bandeja con filtro y aprobar/rechazar con observaciones; también se ve en el expediente |
| Reset de contraseña con token | `/recuperar/:token` | omitted | El backend no emite token: el reset es OTP de 8 dígitos en `/recuperar` (D20) |
| Habilitaciones por módulo | `/admin/habilitaciones` | omitted | AQ-07 opción A: `Limitado` solo accede a perfil, acta y notificaciones; no se crea un módulo de habilitaciones |
| Auditor (P2) | `/auditor/...` | omitted | P2; el backend expone `/audit/*`, pero la interfaz no se implementa antes de cerrar P0/P1 |

## Deltas visuales conocidos

| Delta | Motivo |
|---|---|
| Chips de cuentas demo del login | No deben existir en producción |
| Pista "Máximo 10 MB" en subidas | Requisito: 500 MB configurable (`upload_max_mb`) |
| Alias de fase del prototipo | Se usa `faseplan` literal |
| Cabecera de tabla/badge 12 px de `DESIGN.md` | `lib_css.py` emite 13 px; T30 prohíbe <13 px |
| Inter desde Google Fonts | Se autoaloja (D21); misma tipografía |
| Puntajes, PDF de diagnóstico y dimensiones | AQ-09 y P-3/P-35: no se inventan |
| Restauración de respaldos y de cuentas | No hay endpoint (D22, P-16) |
| Descarga de evidencias | La API solo publica `evidencias: number`; se muestra el conteo y se permite subir |
| Preferencias de notificación por usuario | Son claves globales del programa (P-31) |
| Selector de tipo de cambio de contraseña | No existe: el cambio siempre confirma con OTP al correo de la sesión |

## Registro de la puerta E11

- **64 rutas** verificadas en navegador con los tres roles demo y una cuenta recién
  registrada; 0 pantallas con `[object Object]`, `undefined` o `NaN`.
- **Estados obligatorios**: cada consulta pasa por `QueryGate` y toda lista tiene loading,
  error con reintento y vacío con texto propio. El único error de consola esperado es el
  `401` de `/users/me` antes de iniciar sesión.
- **Huecos visibles**: AQ-09 en diagnóstico, P-3 en el PDF, P-36 en la plantilla del acta,
  P-1 en la reprogramación del estudiante, P-40 en recomendaciones, P-44 en el reporte de
  emprendimientos y P-31 en las preferencias de aviso.
- La evidencia completa está en `docs/verification.md` (Etapa 11) y el mapa requisito →
  vista → endpoint en `docs/traceability.md`.
