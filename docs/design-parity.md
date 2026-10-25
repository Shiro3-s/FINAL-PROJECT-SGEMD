# Paridad de diseño — prototipo → React

> Una fila por **vista lógica**. El prototipo es la referencia visual y conductual; la
> aceptación del MVP es API + pruebas, no similitud de píxeles (master §8).
> Estado: `pending` · `ported` · `delta` (diferencia deliberada) · `omitted` (con motivo).
> Fuente de estilos: `prototype/lib_css.py` (valores) y `prototype/DESIGN.md` (intención).
> Última actualización: 2026-10-25.

**Totales:** 4 compartidas + 19 estudiante + 20 docente + 19 admin = **62 vistas lógicas** (73 archivos HTML).

## Compartidas (4)

| Archivo del prototipo | Ruta React | Estado | Notas |
|---|---|---|---|
| `compartido/login.html` | `/login` | pending | Sin chips de cuentas demo; layout a dos columnas con logo real |
| `compartido/registro.html` | `/registro` | pending | 7 campos + checkbox; campos académicos condicionales (FR-024) |
| `compartido/verificar-otp.html` | `/verificar` | pending | OTP de 8 dígitos, reenvío con espera, aviso de 5 min |
| `compartido/recuperar-contrasena.html` | `/recuperar` | pending | Solo solicitud; el reset con token es `/recuperar/:token` (vista nueva) |

## Estudiante (27 archivos → 19 vistas)

| Archivo(s) del prototipo | Ruta React | Estado | Notas |
|---|---|---|---|
| `estudiante/dashboard.html` | `/estudiante` | pending | Emprendimiento propio, etapa, % avance, tareas pendientes/vencidas |
| `estudiante/estado-seguimiento.html` | `/estudiante/estado` | pending | Una barra de progreso por fase |
| `estudiante/emprendimientos.html` | `/estudiante/emprendimientos` | pending | Lista |
| `estudiante/emprendimiento-detalle.html`, `-mochilas.html` | `/estudiante/emprendimientos/:id` | pending | Pestañas resumen, diagnóstico, seguimiento, asesorías, evidencias; el segundo archivo es variante de datos |
| `estudiante/emprendimiento-editar.html` | `/estudiante/emprendimientos/:id/editar` | pending | Solo nombre, descripción y redes |
| `estudiante/plan-trabajo.html` | `/estudiante/plan` | pending | Agrupado por fase; "Descargar plan" |
| `estudiante/tareas.html` | `/estudiante/tareas` | pending | Filtros por estado y prioridad |
| `estudiante/tarea-detalle.html` + `-en-revision` + 3 `-completada-*` | `/estudiante/tareas/:id` | pending | **Conservar la compuerta de evidencia** (FR-023); 5 archivos = 5 estados |
| `estudiante/seguimiento.html` | `/estudiante/seguimiento` | pending | Historial de solo lectura |
| `estudiante/seguimiento-detalle.html` | `/estudiante/seguimiento/:id` | pending | Fecha, autor, estado de revisión, puntaje, retroalimentación |
| `estudiante/asesorias.html` | `/estudiante/asesorias` | pending | Solo lectura; el estudiante nunca agenda |
| `estudiante/solicitar-asesoria.html` | `/estudiante/asesorias/solicitar` | pending | Crea una **solicitud**, no una cita confirmada |
| `estudiante/diagnostico.html` | `/estudiante/diagnostico` | pending | 5 secciones / 22 preguntas; guardar y retomar |
| `estudiante/diagnostico-resultados.html` | `/estudiante/diagnostico/resultado` | pending | 6 dimensiones, 4 bandas, descarga PDF — **sin puntaje mientras AQ-09 esté abierta** |
| `estudiante/eventos.html` | `/estudiante/eventos` | pending | |
| `estudiante/evento-detalle-*.html` (4) | `/estudiante/eventos/:id` | pending | Cuatro tipos; una ruta con contenido por tipo |
| `estudiante/notificaciones.html` | `/estudiante/notificaciones` | pending | Filtros: Todas · Sin leer · Tareas · Asesorías · Seguimiento |
| `estudiante/perfil.html` | `/estudiante/perfil` | pending | |
| `estudiante/configuracion.html` | `/estudiante/configuracion` | pending | Datos personales y académicos condicionales; el programa lo cambia el admin |

## Docente (23 archivos → 20 vistas)

| Archivo(s) del prototipo | Ruta React | Estado | Notas |
|---|---|---|---|
| `docente/dashboard.html` | `/docente` | pending | Estudiantes asignados, % avance, próximas sesiones; tarjetas enlazan a listas prefiltradas `?f=` |
| `docente/emprendimientos.html` | `/docente/emprendimientos` | pending | Solo asignados; alternar tarjetas/tabla; filtros de etapa, sector y evidencia |
| `docente/emprendimiento-expediente.html` | `/docente/emprendimientos/:id` | pending | Pestañas avances, tareas, asesorías, diagnóstico, comentarios |
| `docente/avance-form.html` | `/docente/avances/nuevo` | pending | Página completa: emprendimiento, fase, fecha, descripción, estado de revisión, puntaje 0–100, evidencia |
| `docente/avance-detalle.html` | `/docente/avances/:id` | pending | |
| `docente/diagnostico.html` | `/docente/diagnostico` | pending | Selector de emprendimiento y filtros |
| `docente/diagnostico-revision.html` | `/docente/diagnostico/:id/revision` | pending | Resultado con recomendaciones — **solo lectura hasta resolver P-2** |
| `docente/asesorias.html` | `/docente/asesorias` | pending | Filtro agrupado: Por agendar · **Agendada** (= Programada + Confirmada + En curso) · Completada · Cancelada |
| `docente/asesoria-detalle.html` | `/docente/asesorias/:id` | pending | Acciones: Confirmar y notificar · Proponer otra fecha · Rechazar solicitud |
| `docente/asesoria-form.html` | `/docente/asesorias/nueva` | pending | Agenda para un grupo completo |
| `docente/tareas.html` | `/docente/tareas` | pending | Filtros por estado y prioridad |
| `docente/tarea-form.html` | `/docente/tareas/nueva` | pending | |
| `docente/tarea-detalle.html` | `/docente/tareas/:id` | pending | Calificar 0–100 + retroalimentación + devolver |
| `docente/tarea-devolver.html` | `/docente/tareas/:id/devolver` | pending | Motivo (selector) + observaciones |
| `docente/eventos.html` | `/docente/eventos` | pending | |
| `docente/evento-detalle-*.html` (4) | `/docente/eventos/:id` | pending | Incluye "recomendar" |
| `docente/perfil.html` | `/docente/perfil` | pending | Título/especialidad, ubicación, enlace a contraseña |
| `docente/contrasena.html` | `/docente/contrasena` | pending | Actual, nueva, confirmar |
| `docente/configuracion.html` | `/docente/configuracion` | pending | Preferencias de notificación |
| `docente/notificaciones.html` | `/docente/notificaciones` | pending | Chips por tipo + marcar todo como leído con confirmación |

> **Sin ruta docente de "Seguimiento"**: el módulo se retiró y lo reemplazan "Registrar
> avance" y la columna Evidencia. `prototype/DESIGN.md` línea 53 está obsoleta
> (`docs/decisions.md` #23).

## Administrador (19 archivos → 19 vistas)

| Archivo(s) del prototipo | Ruta React | Estado | Notas |
|---|---|---|---|
| `admin/dashboard.html` | `/admin` | pending | Agregados reales: usuarios por rol, emprendimientos, asignaciones activas, tareas, sesiones, distribución por etapa |
| `admin/usuarios.html` | `/admin/usuarios` | pending | Dos tablas (estudiantes, docentes), búsqueda, filtro de estado, alta, edición, baja lógica, selector `Activo · Limitado · Inactivo` |
| `admin/solicitudes.html` | `/admin/solicitudes` | pending | Pestañas Desbloqueos · Paralelos · Citas; contador; aprobar/rechazar con **motivo obligatorio** |
| `admin/emprendimientos.html` | `/admin/emprendimientos` | pending | Filtros, detalle, edición de etapa, ir a asignación |
| `admin/emprendimiento-expediente.html` | `/admin/emprendimientos/:id` | pending | Pestañas consolidadas + exportar |
| `admin/emprendimiento-plan.html` | `/admin/emprendimientos/:id/plan` | pending | Plan por fases |
| `admin/asignaciones.html` | `/admin/asignaciones` | pending | Crear/retirar/reasignar; enlace profundo `#asignar-docente`; tope de 12 emprendimientos |
| `admin/seguimiento.html` | `/admin/seguimiento` | pending | Avances con autor, fecha, estado de revisión, evidencia |
| `admin/seguimiento-dashboard.html` | `/admin/seguimiento/tablero` | pending | Avance agregado por emprendimiento y fase |
| `admin/tareas.html` | `/admin/tareas` | pending | Todas las tareas, filtros, estado de calificación |
| `admin/asesorias.html` | `/admin/asesorias` | pending | Agenda global; crear y asignar directamente |
| `admin/diagnosticos.html` | `/admin/diagnosticos` | pending | Banco de preguntas, resumen, filtros, informe descargable |
| `admin/eventos.html` | `/admin/eventos` | pending | Lista/tablero |
| `admin/evento-form.html` | `/admin/eventos/nuevo`, `/admin/eventos/:id/editar` | pending | Título, audiencia, descripción, capacidad, fecha, inicio/fin, lugar, enlace |
| `admin/reportes.html` | `/admin/reportes` | pending | CSV / PDF / XLSX con tipo y periodo |
| `admin/respaldos.html` | `/admin/respaldos` | pending | Último respaldo, tamaño **lógico y añadido**, historial, integridad, crear respaldo, exportar BD. **Sin restauración** |
| `admin/notificaciones.html` | `/admin/notificaciones` | pending | Filtros, contador de no leídas, enlaces profundos, marcar todo |
| `admin/perfil.html` | `/admin/perfil` | pending | Datos propios + contraseña |
| `admin/configuracion.html` | `/admin/configuracion` | pending | Parámetros, cuenta admin, bitácora de cambios |

## Vistas nuevas (ausentes del prototipo)

| Vista | Ruta React | Estado | Requisito |
|---|---|---|---|
| Acta del estudiante | `/estudiante/acta` | pending | FR-003, US-025 |
| Revisión de acta (admin) | `/admin/actas` o pestaña en el expediente | pending | FR-003, BR-009 |
| Reset de contraseña con token | `/recuperar/:token` | pending | FR-001, T39 |
| Habilitaciones por módulo | `/admin/habilitaciones` | pending | Solo si AQ-07 lo exige |
| Auditor (P2) | `/auditor/...` | omitted | P2; no se implementa antes de cerrar P0/P1 |

## Deltas visuales conocidos (a confirmar al portar)

| Delta | Motivo |
|---|---|
| Chips de cuentas demo del login | No deben existir en producción |
| Pista "Máximo 10 MB" en subidas | Requisito: 500 MB configurable |
| Alias de fase del prototipo | Se usa `faseplan` literal |
| Cabecera de tabla/badge 12 px de `DESIGN.md` | `lib_css.py` emite 13 px; T30 prohíbe <13 px |
| Inter desde Google Fonts | Se autoaloja (D21); misma tipografía |
