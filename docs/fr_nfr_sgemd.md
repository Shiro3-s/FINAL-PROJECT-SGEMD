# Especificación de Requisitos de Software (SRS) - Sistema de Gestión de Emprendimiento Minuto de Dios (SGEMD)

> **Actualización:** 25 de octubre de 2026 · **trabajo local** (sin rama nueva, sin commit y sin push a GitHub).
> **Motivo:** sincronizar el SRS con las vistas realmente implementadas en el prototipo, con las correcciones C-1…C-7 y adiciones A-1…A-21 de `Config-admin/correcciones-adiciones-requisitos.md`, y con el refactor de los roles administrador, estudiante y docente.
> **Método y evidencia:** [`orquestacion-actualizacion-requisitos-2026-10.md`](./orquestacion-actualizacion-requisitos-2026-10.md) y [`registro-actualizacion-requisitos-2026-10.md`](./registro-actualizacion-requisitos-2026-10.md).
> **Alineación (2026-10-25):** este SRS se contrastó con las **73 pantallas** del prototipo. Cuando un requisito y el prototipo difieren, se corrige el requisito salvo que exista una decisión escrita en contra. Los vacíos del prototipo se registran como pendientes y no se rellenan por invención (ver [`sincronizacion-prototipo-2026-10.md`](./sincronizacion-prototipo-2026-10.md)).
>
> **Nota de alcance:** el prototipo es **estático**. Las operaciones de guardado, descarga, exportación y notificación están **simuladas** en el navegador; no existe backend, API ni base de datos PostgreSQL en este repositorio.

### Leyenda de estado de implementación

| Estado | Significado |
|---|---|
| `Implementado en prototipo (UI)` | La pantalla, el control o el flujo existe y es navegable en `prototype/**` |
| `Parcial en prototipo (UI)` | Parte del requisito existe en la interfaz; falta un flujo, una vista o una validación (se indica cuál) |
| `Simulado en prototipo` | El comportamiento se representa en el navegador (p. ej. `localStorage`), sin persistencia real |
| `Pendiente de backend` | Requisito acordado, sin implementación funcional en este repositorio |
| `Fuera de alcance / Post-MVP` | Reconocido, pero no forma parte del MVP actual |

### Conteos vigentes

| Elemento | Cantidad |
|---|---|
| Requisitos funcionales | 24 (`FR-001` … `FR-024`) |
| Requisitos no funcionales | 9 (`NFR-001` … `NFR-009`) |
| Procesos de negocio | 6 (`BP-001` … `BP-006`) |
| Reglas de negocio | 9 (`BR-001` … `BR-009`) |
| Pantallas del prototipo | 73 (4 globales + 27 estudiante + 23 docente + 19 administrador) |

## 1. Resumen del Proyecto

El Sistema de Gestión de Emprendimiento Minuto de Dios (SGEMD) es una plataforma web orientada a la administración del emprendimiento estudiantil universitario[cite: 7]. El proyecto busca solucionar la ineficiencia, dispersión de datos y cuellos de botella generados por la gestión manual en hojas de cálculo (Excel) dentro del Centro Progresa[cite: 7, 9].

Los usuarios principales son Estudiantes (emprendedores), Docentes/Mentores (asesores) y Administradores (coordinadores)[cite: 7]. Los procesos clave incluyen el registro, la valoración automática del modelo de negocio, el agendamiento controlado de asesorías, el seguimiento del plan de trabajo y la visualización de métricas[cite: 7, 8, 9]. La solución se construirá desde cero utilizando Node.js y React, garantizando seguridad, roles aislados y una interfaz de alta usabilidad[cite: 7, 9].

## 2. Partes Interesadas y Roles de Usuario

| ID | Rol / Parte Interesada | Descripción | Responsabilidades | Necesidades y Objetivos | Referencia |
| -- | ------------------ | ----------- | ---------------- | --------------- | ---------------- |
| R-01 | Administrador (Coordinadora) | Gestiona el sistema, los usuarios, las asignaciones y la configuración del programa[cite: 7]. | **Crear, editar, activar/desactivar y dar de baja lógica** usuarios; aprobar o rechazar emprendimientos (incluido el paralelo); asignar y reasignar docentes; **crear y asignar asesorías directamente**; resolver la bandeja de solicitudes; configurar parámetros del programa; descargar reportes y respaldos[cite: 7, 9]. | Automatizar tabulaciones, mantener el control del agendamiento, ver el estado de los respaldos y operar con trazabilidad[cite: 9]. |[cite: 7, 8, 9] |
| R-02 | Docente / Mentor (Asesor) | Acompaña a uno o varios estudiantes[cite: 7]. | Registrar seguimiento y avances con calificación, crear tareas, **aceptar o reprogramar** las asesorías asignadas, revisar el diagnóstico, recomendar eventos y consultar el expediente[cite: 7, 8]. | Conocer el contexto del emprendimiento (historial) y tener una interfaz simple[cite: 7, 8, 9]. |[cite: 7, 8, 9] |
| R-03 | Estudiante (Emprendedor) | Propietario del emprendimiento[cite: 7]. | Registrarse, diligenciar formularios de valoración, firmar acta de confidencialidad, cumplir tareas y solicitar asesorías[cite: 7, 8, 9]. | Recibir retroalimentación inmediata sobre su modelo de negocio y gestionar sus avances fácilmente[cite: 8, 9]. |[cite: 7, 8, 9] |
| R-04 | Auditor (rol 4) | Rol de **consulta institucional**: revisa información consolidada y exporta reportes, sin intervenir en la operación. | **Consultar** dashboards, expedientes y reportes; **exportar** reportes. **No** edita datos ni accede a información sensible completa. | Verificar el estado del programa y respaldar decisiones con reportes, sin riesgo de alterar la operación. | Decisión AQ-08 (2026-10-25); NFR-002, NFR-007, FR-010, FR-017; US-026. |

## 3. Análisis de Procesos de Negocio

### BP-001: Registro y Diagnóstico Inicial
* **Propósito:** Registrar al estudiante y evaluar el estado de su emprendimiento[cite: 7, 8].
* **Desencadenante:** El estudiante ingresa a la plataforma para crear una cuenta[cite: 7].
* **Actores:** Estudiante, Administrador[cite: 7, 8].
* **Flujo Actual:** El estudiante llena un formulario, el administrador cruza datos manualmente en Excel para generar un diagnóstico y le asigna un docente[cite: 8, 9].
* **Experiencia del Usuario:** El estudiante se registra y verifica su correo[cite: 7]. Tras una reunión de socialización, el administrador le habilita un formulario de caracterización (modelo de negocio, marketing, etc.)[cite: 8, 9]. Al completarlo, el sistema genera el diagnóstico automático y el estudiante firma el acta de confidencialidad[cite: 8, 9].
* **Puntos de Dolor:** Tabulación manual en Excel que consume tiempo y retrasa el feedback[cite: 9].
* **Resultado Deseado:** Diagnóstico automático inmediato y centralización de documentos[cite: 8, 9].
* **Reglas de Negocio:** El estudiante debe verificar su cuenta con un código OTP de 8 dígitos válido por 5 minutos[cite: 7]. La cuenta nace en estado **Limitado** y solo el Administrador la pasa a **Activo** tras la reunión de socialización. La asignación del docente requiere el acta de confidencialidad firmada[cite: 8].
* **Requisitos Relacionados:** FR-001, FR-002, FR-003, FR-013, BR-001, BR-003.
* **Referencia:**[cite: 7, 8, 9].

### BP-002: Gestión y Asignación de Asesorías
* **Propósito:** Conectar al estudiante con un mentor y programar sesiones de trabajo[cite: 7, 9].
* **Desencadenante:** El estudiante solicita una asesoría o el administrador la crea y asigna directamente[cite: 7, 9].
* **Actores:** Administrador, Docente, Estudiante[cite: 7, 9].
* **Flujo Actual:** Coordinación manual propensa a errores y cruces de horarios[cite: 9].
* **Experiencia del Usuario:** El Administrador **crea y asigna la asesoría directamente** (emprendimiento, docente, fecha y modalidad) sin flujo de permiso de horario. El Docente **acepta o propone otra fecha** sobre las asesorías que le corresponden. El estudiante consulta la cita y recibe la notificación[cite: 7, 9].
* **Puntos de Dolor:** Agendamiento fantasma si los docentes no actualizan disponibilidad; pérdida de control si los estudiantes agendan libremente[cite: 9].
* **Resultado Deseado:** Un módulo centralizado y restrictivo donde el Administrador controla los cruces de agenda y el docente acepta o propone otra fecha según su disponibilidad[cite: 9].
* **Reglas de Negocio:** No existirá flujo de agendamiento automático ni integración con calendarios externos. El Admin asigna; el docente acepta o reprograma; el estudiante no agenda por su cuenta[cite: 9].
* **Requisitos Relacionados:** FR-004, FR-005, FR-015, FR-019, BR-002.
* **Referencia:**[cite: 7, 9].

### BP-003: Seguimiento y Trazabilidad del Proyecto
* **Propósito:** Mantener el historial de tareas, notas y avances del emprendimiento[cite: 7, 9].
* **Desencadenante:** El docente evalúa avances o crea un plan de trabajo[cite: 7].
* **Actores:** Docente, Estudiante, Administrador[cite: 7].
* **Flujo Actual:** Pérdida de historial cuando un estudiante cambia de asesor[cite: 9].
* **Experiencia del Usuario:** El Docente registra notas y adjunta evidencias (archivos)[cite: 7]. El estudiante ingresa para ver sus tareas, completarlas **con evidencia obligatoria** y visualizar su porcentaje de progreso por fase[cite: 7]. Si un estudiante se inactiva, el sistema alerta al Administrador[cite: 9].
* **Puntos de Dolor:** Pérdida de información histórica y dificultad para identificar estudiantes inactivos[cite: 9].
* **Resultado Deseado:** Un Expediente Central anclado a la idea de negocio, no al docente[cite: 9].
* **Reglas de Negocio:** El historial pertenece al emprendimiento[cite: 9]. El estudiante pasa a **Inactivo** tras **90 días (3 meses)** sin actividad[cite: 9]. La reactivación la hace únicamente el Administrador.
* **Requisitos Relacionados:** FR-006, FR-007, FR-008, FR-017, FR-022, FR-023, BR-005.
* **Referencia:**[cite: 7, 9].

### BP-004: Aprobación de Emprendimientos
* **Propósito:** Autorizar la creación de un emprendimiento y controlar los emprendimientos paralelos de un mismo estudiante.
* **Desencadenante:** El Administrador crea un emprendimiento para un estudiante.
* **Actores:** Administrador, Estudiante.
* **Flujo Actual:** El alta dependía del Administrador; no existía una bandeja única de aprobación.
* **Experiencia del Usuario:** El Administrador registra el emprendimiento; queda en **Pendiente** y lo revisa en la bandeja de solicitudes para **aprobarlo o rechazarlo** con motivo. Si el estudiante ya tiene un emprendimiento activo, la aprobación del segundo se registra como **paralelo autorizado**. *(El prototipo no incluye el alta por el estudiante.)*
* **Puntos de Dolor:** Duplicidad de proyectos y pérdida de control sobre el segundo emprendimiento.
* **Resultado Deseado:** Todo emprendimiento nace con estado y responsable de aprobación trazables.
* **Reglas de Negocio:** Sin aprobación del Administrador el emprendimiento no pasa a **Aprobado**; el rechazo exige motivo y notifica al estudiante.
* **Requisitos Relacionados:** FR-012, FR-014, FR-019, BR-004.
* **Referencia:** `Config-admin/correcciones-adiciones-requisitos.md` (A-2, A-10); `prototype/admin/solicitudes.html`.

### BP-005: Ciclo de Vida de la Cuenta
* **Propósito:** Controlar el acceso del usuario desde el registro hasta la inactividad.
* **Desencadenante:** Registro, reunión de socialización o inactividad prolongada.
* **Actores:** Estudiante, Administrador.
* **Flujo Actual:** El desbloqueo se hacía de forma manual y sin un ciclo de estados explícito.
* **Experiencia del Usuario:** La cuenta nace **Limitado**; el Administrador la **desbloquea** a **Activo**; tras **90 días** sin actividad el sistema la marca **Inactivo**; el Administrador puede **reactivarla**.
* **Puntos de Dolor:** Perfiles bloqueados sin trazabilidad y cuentas inactivas sin tratamiento.
* **Resultado Deseado:** Un único dueño del cambio de estado y un historial de transiciones.
* **Reglas de Negocio:** **Solo el Administrador** cambia el estado de la cuenta. El estudiante no puede autoactivarse ni reactivarse.
* **Requisitos Relacionados:** FR-007, FR-013, BR-003, BR-005.
* **Referencia:** `prototype/admin/usuarios.html`; `docs/historias_usuario.md` §7.

### BP-006: Respaldo y Configuración del Programa
* **Propósito:** Garantizar la contingencia de la información y centralizar los parámetros operativos.
* **Desencadenante:** Cierre de periodo, mantenimiento o cambio de reglas del programa.
* **Actores:** Administrador.
* **Flujo Actual:** Exportaciones dispersas y parámetros repartidos entre pantallas.
* **Experiencia del Usuario:** El Administrador consulta el **estado del respaldo** (último respaldo, tamaño, integridad), exporta la base en CSV/Excel y ajusta parámetros del programa (carga docente, cupos, sedes, notificaciones y bitácora).
* **Puntos de Dolor:** Falta de visibilidad sobre la copia vigente y cambios de configuración sin registro.
* **Resultado Deseado:** Un panel único de respaldos y una configuración centralizada.
* **Reglas de Negocio:** La exportación y el estado del respaldo son visibles solo para el Administrador; todo cambio de configuración queda registrado en la bitácora.
* **Requisitos Relacionados:** FR-018, FR-020, NFR-004, NFR-007.
* **Referencia:** `prototype/admin/respaldos.html`; `prototype/admin/configuracion.html`.

## 4. Requisitos Funcionales

### FR-001: Registro y Verificación de Estudiantes
* **Declaración:** El sistema deberá permitir a los estudiantes registrarse utilizando un correo institucional y verificar su cuenta mediante un código OTP de 8 dígitos enviado por correo[cite: 7].
* **Descripción:** Garantiza que solo usuarios válidos accedan al sistema[cite: 7].
* **Rol Relacionado:** Estudiante[cite: 7].
* **Reglas de Negocio:** El código caduca en 5 minutos y se valida estrictamente en el backend[cite: 7].
* **Prioridad:** Alta[cite: 7].
* **Referencia:**[cite: 7].

### FR-002: Formulario de Valoración y Diagnóstico Automático
* **Declaración:** El sistema deberá proveer un formulario de caracterización (modelo de negocio, marketing, producto, financiero) y calcular automáticamente las métricas para generar un diagnóstico de fortalezas y debilidades[cite: 8, 9].
* **Descripción:** Elimina la tabulación manual y provee feedback inmediato al estudiante y al docente[cite: 8, 9].
* **Rol Relacionado:** Estudiante, Administrador, Docente[cite: 8, 9].
* **Prioridad:** Alta[cite: 8, 9].
* **Referencia:**[cite: 8, 9].

### FR-003: Gestión de Acta de Confidencialidad
* **Declaración:** El sistema deberá permitir a los estudiantes descargar, firmar y subir el acta de compromiso de confidencialidad[cite: 8].
* **Descripción:** Requisito legal previo a la asignación de un mentor[cite: 8].
* **Rol Relacionado:** Estudiante, Administrador[cite: 8].
* **Reglas de Negocio:** Requisito obligatorio para iniciar la asesoría[cite: 8]. El **rechazo del acta exige un motivo obligatorio**; sin motivo no se puede confirmar y el estudiante recibe la notificación (BR-009).
* **Estado de implementación:** `Pendiente de backend`. No existe vista de acta en el prototipo: la carga, la revisión y el rechazo con motivo no están implementados en las 73 pantallas.
* **Prioridad:** Alta[cite: 8].
* **Referencia:**[cite: 8]; AQ-05 (decisión del 2026-10-25).

### FR-004: Asignación y Agendamiento Manual
* **Declaración:** El sistema deberá incluir un módulo donde el Administrador **cree y asigne asesorías directamente** (estudiante/emprendimiento, docente, fecha, horario y modalidad), sin flujo de permiso de horario; el **estudiante solicita** asesoría y el **docente acepta o propone otra fecha** sobre las que le corresponden[cite: 7, 9].
* **Descripción:** Mantiene el control administrativo sobre los horarios y elimina la ambigüedad de “quién confirma”[cite: 9].
* **Rol Relacionado:** Administrador, Docente, Estudiante[cite: 9].
* **Reglas de Negocio:** Prohibido el agendamiento libre o automático por parte del estudiante y prohibida la integración con calendarios externos. El Admin asigna; el docente acepta/reprograma[cite: 9].
* **Estado de implementación:** `Implementado en prototipo (UI)` en `admin/asignaciones.html` (asignar/reasignar) y `admin/solicitudes.html` (citas); la aceptación docente está representada en `docente/asesoria-detalle.html` (`Simulado en prototipo`).
* **Prioridad:** Alta[cite: 9].
* **Referencia:**[cite: 7, 9]; `Config-admin/correcciones-adiciones-requisitos.md` C-1, C-2, A-12.

### FR-005: Notificaciones en Tiempo Real
* **Declaración:** El sistema deberá enviar notificaciones en tiempo real a los usuarios cuando se les asigne una tarea o asesoría, cuando cambie el estado de una solicitud o cuando se apruebe/rechace un emprendimiento[cite: 7].
* **Descripción:** Mejora la comunicación y los tiempos de respuesta; cada aviso debe ser **accionable** (abre el objeto referido) y puede marcarse como leído[cite: 7].
* **Rol Relacionado:** Estudiante, Docente, Administrador[cite: 7].
* **Estado de implementación:** `Parcial en prototipo (UI)`. Existen las bandejas de los tres roles con filtros y "marcar como leída", pero **no hay emisión ni canal en tiempo real**: el prototipo no usa WebSocket ni `Socket.io`. La emisión es `Pendiente de backend`.
* **Prioridad:** Media[cite: 7].
* **Referencia:**[cite: 7]; `Config-admin/correcciones-adiciones-requisitos.md` A-8.

### FR-006: Expediente Central del Emprendimiento (Trazabilidad)
* **Declaración:** El sistema deberá anclar todo el historial de diagnósticos, notas de seguimiento, tareas y asesorías directamente a la entidad "Emprendimiento"[cite: 7, 9].
* **Descripción:** Permite que nuevos docentes asignados vean todo el contexto histórico del proyecto sin importar rotaciones de personal[cite: 9].
* **Rol Relacionado:** Docente, Administrador[cite: 9].
* **Prioridad:** Alta[cite: 7, 9].
* **Referencia:**[cite: 7, 9].

### FR-007: Semaforización de Inactividad
* **Declaración:** El sistema deberá cambiar automáticamente el estado de un estudiante a **Inactivo** tras **90 días (3 meses)** continuos sin registrar actividad o avances[cite: 9].
* **Descripción:** Facilita la identificación rápida de deserción para contactar al estudiante[cite: 9].
* **Rol Relacionado:** Administrador[cite: 9].
* **Reglas de Negocio:** El umbral es de **90 días**. La reactivación es manual y exclusiva del Administrador (BR-005)[cite: 9].
* **Estado de implementación:** `Implementado en prototipo (UI)` como estado visible y filtro en `admin/usuarios.html`; el cálculo automático es `Pendiente de backend`.
* **Prioridad:** Media[cite: 9].
* **Referencia:**[cite: 9]; `Config-admin/correcciones-adiciones-requisitos.md` C-3; cierre de AQ-01.

### FR-008: Gestión de Archivos Adjuntos
* **Declaración:** El sistema deberá permitir la subida, almacenamiento y descarga de archivos (PDFs, imágenes) de hasta 500 MB en los módulos de tareas, seguimientos y asesorías[cite: 7].
* **Descripción:** Permite cargar evidencias del trabajo[cite: 7].
* **Rol Relacionado:** Todos[cite: 7].
* **Reglas de Negocio:** El borrado es **lógico y reversible** con confirmación. Al eliminar un emprendimiento o usuario, sus archivos adjuntos se eliminan **en cascada**[cite: 7].
* **Estado de implementación:** `Implementado en prototipo (UI)` el flujo de adjuntar y la exigencia de evidencia; el almacenamiento y la cascada real son `Pendiente de backend`.
* **Prioridad:** Alta[cite: 7].
* **Referencia:**[cite: 7]; `Config-admin/correcciones-adiciones-requisitos.md` A-4.

### FR-009: Exportación de Datos (Backup Local)
* **Declaración:** El sistema deberá incluir un módulo en el perfil del Administrador para exportar la base de datos a formato CSV o Excel con un solo clic[cite: 9].
* **Descripción:** Sirve como plan de contingencia ante caídas del servidor[cite: 9].
* **Rol Relacionado:** Administrador[cite: 9].
* **Prioridad:** Alta[cite: 9].
* **Referencia:**[cite: 9].

### FR-010: Dashboards de Métricas
* **Declaración:** El sistema deberá mostrar métricas derivadas de la base de datos en tiempo real, incluyendo conteos totales (usuarios, emprendimientos), porcentajes de avance de tareas y distribución por etapa[cite: 7, 9].
* **Descripción:** Elimina el procesamiento manual de informes[cite: 9].
* **Rol Relacionado:** Administrador, Docente, Estudiante; **Auditor en solo lectura y exportación** (AQ-08).
* **Prioridad:** Alta[cite: 7, 9].
* **Referencia:**[cite: 7, 9].

### FR-011: CRUD de Usuarios por el Administrador
* **Declaración:** El sistema deberá permitir al Administrador **crear, editar, activar/desactivar y dar de baja lógica** las cuentas de estudiante y docente, asignando el rol en el momento del alta[cite: 7].
* **Descripción:** Reemplaza el alta implícita por registro y concentra la gestión de cuentas en el panel administrativo.
* **Rol Relacionado:** Administrador.
* **Reglas de Negocio:** Toda alta y edición valida campos obligatorios y unicidad (documento, correo). La baja es lógica y reversible, con confirmación. No se elimina el historial del usuario.
* **Estado de implementación:** `Implementado en prototipo (UI)` en `admin/usuarios.html` (alta de estudiante y docente, edición, baja y selector de estado); la persistencia es `Simulado en prototipo`.
* **Prioridad:** Alta.
* **Referencia:** `Config-admin/correcciones-adiciones-requisitos.md` A-1, A-4, A-5, D1.

### FR-012: Aprobación de Emprendimientos y Emprendimiento Paralelo
* **Declaración:** El sistema deberá permitir que el **Administrador cree un emprendimiento** y lo **apruebe o rechace**; el estado inicial será **Pendiente**. El Administrador autorizará el **segundo emprendimiento paralelo** de un mismo estudiante[cite: 8, 9]. *(El prototipo no incluye el alta por el estudiante; ver nota de estado.)*
* **Descripción:** Formaliza el alta de emprendimientos y evita la duplicidad no controlada.
* **Rol Relacionado:** Estudiante, Administrador.
* **Reglas de Negocio:** Sin aprobación no hay paso a **Aprobado**. El rechazo exige motivo y notifica al estudiante. Un segundo emprendimiento requiere autorización expresa de paralelo.
* **Estado de implementación:** `Parcial en prototipo (UI)`. Existe `admin/solicitudes.html` (pestaña Paralelos, aprobar/rechazar) y la lista de emprendimientos del estudiante, pero **no hay formulario de alta ni vista del estado Pendiente**: el prototipo asigna el emprendimiento desde el panel del Administrador. Los estados observados son `Pendiente` · `Aprobado` · `Rechazado`. El **campo de motivo existe**, pero la **obligatoriedad no está validada** en la interfaz: `Pendiente de backend`.
* **Prioridad:** Alta.
* **Referencia:** `Config-admin/correcciones-adiciones-requisitos.md` A-2, A-10, D2.

### FR-013: Ciclo de Vida y Estado de la Cuenta
* **Declaración:** El sistema deberá manejar los estados de cuenta **Limitado → Activo → Inactivo**. **Solo el Administrador** podrá desbloquear (Limitado → Activo) y reactivar (Inactivo → Activo)[cite: 7, 9].
* **Descripción:** Da un ciclo explícito al acceso del usuario y un único responsable del cambio.
* **Rol Relacionado:** Administrador, Estudiante, Docente.
* **Reglas de Negocio:** El estudiante no puede autoactivarse ni reactivarse. Toda transición queda registrada con responsable y fecha.
* **Estado de implementación:** `Implementado en prototipo (UI)` en `admin/usuarios.html` (selector de estado) y `admin/solicitudes.html` (desbloqueos); `Pendiente de backend` el registro de transiciones.
* **Prioridad:** Alta.
* **Referencia:** `Config-admin/correcciones-adiciones-requisitos.md` A-3, D4; cierre de AQ-02.

### FR-014: Bandeja de Solicitudes Administrativas
* **Declaración:** El sistema deberá ofrecer al Administrador una **bandeja única** para ver y resolver **desbloqueos de cuenta, aprobaciones de emprendimiento (incluidos paralelos) y citas de asesoría**, con contador de pendientes[cite: 9].
* **Descripción:** Evita resolver solicitudes desde pantallas dispersas y da trazabilidad a cada decisión.
* **Rol Relacionado:** Administrador.
* **Reglas de Negocio:** Cada ítem se resuelve con confirmación. El rechazo de emprendimiento o desbloqueo exige motivo. La resolución notifica al solicitante.
* **Estado de implementación:** `Implementado en prototipo (UI)` en `admin/solicitudes.html` (pestañas Desbloqueos, Paralelos, Citas; aprobar/rechazar); `Simulado en prototipo`. El modal **solicita** el motivo, pero **no impide confirmar con el campo vacío**: la validación es `Pendiente de backend`.
* **Prioridad:** Alta.
* **Referencia:** `Config-admin/correcciones-adiciones-requisitos.md` A-13.

### FR-015: Asignación Directa de Asesoría y Aceptación Docente
* **Declaración:** El sistema deberá permitir al Administrador **crear y asignar una asesoría directamente** (emprendimiento, docente, fecha, horario y modalidad) y al Docente **aceptar, rechazar o proponer otra fecha**[cite: 9].
* **Descripción:** Separa la responsabilidad administrativa de la disponibilidad docente y elimina el agendamiento libre del estudiante.
* **Rol Relacionado:** Administrador, Docente, Estudiante.
* **Reglas de Negocio:** El estudiante no agenda por su cuenta. El docente solo gestiona asesorías de sus asignados. Toda asignación notifica a estudiante y docente.
* **Estado de implementación:** `Implementado en prototipo (UI)` en `admin/asignaciones.html` (`#asignar-docente`), `admin/solicitudes.html` y `docente/asesoria-detalle.html`; `Simulado en prototipo`.
* **Prioridad:** Alta.
* **Referencia:** `Config-admin/correcciones-adiciones-requisitos.md` C-1, C-2, A-12.

### FR-016: Validación de Formularios y Unicidad
* **Declaración:** El sistema deberá validar en toda alta y edición los **campos obligatorios**, el **formato** y la **unicidad** de documento y correo, además de **los dos topes de carga docente**: **12 horas de asesoría por semana** y **12 emprendimientos** (ambos configurables)[cite: 9].
* **Descripción:** Evita duplicados y datos incompletos antes de persistir.
* **Rol Relacionado:** Todos.
* **Reglas de Negocio:** Un docente no puede repetirse en la misma asignación ni superar los topes configurados. **Los dos topes son independientes y ambos aplican**: el de horas (`carga_max_horas=12`) y el de emprendimientos (`max_emprendimientos_docente=12`). Los mensajes de error indican el campo afectado.
* **Estado de implementación:** `Implementado en prototipo (UI)` como validación de formulario y mensajes, y como regla de asignación visible en `admin/asignaciones.html` («Un docente puede tener hasta 12 emprendimientos») y en `admin/configuracion.html` (carga máxima y emprendimientos máximos). La unicidad real y el cálculo de los topes son `Pendiente de backend`.
* **Prioridad:** Alta.
* **Referencia:** `Config-admin/correcciones-adiciones-requisitos.md` A-5.

### FR-017: Expediente Consolidado y Trazable
* **Declaración:** El sistema deberá reunir en una sola vista el **expediente del emprendimiento** con **asesorías, diagnósticos, seguimientos, tareas, comentarios y evidencias**, y mantener un **log de auditoría** de los cambios[cite: 9].
* **Descripción:** Garantiza continuidad cuando cambia el docente y permite reconstruir la historia del proyecto.
* **Rol Relacionado:** Administrador, Docente, Estudiante (según alcance); **Auditor en solo lectura y exportación** (AQ-08).
* **Reglas de Negocio:** El expediente pertenece al emprendimiento, no al docente. El estudiante solo consulta el suyo; el docente, los asignados; el admin, todos; el auditor consulta y exporta **sin editar** y con los datos sensibles enmascarados.
* **Estado de implementación:** `Implementado en prototipo (UI)` en `admin/emprendimiento-expediente.html` y `docente/emprendimiento-expediente.html` (pestañas y exportación); el **log de auditoría** es `Pendiente de backend`.
* **Prioridad:** Alta.
* **Referencia:** `Config-admin/correcciones-adiciones-requisitos.md` A-6, A-14.

### FR-018: Panel de Respaldos y Estado de la Copia
* **Declaración:** El sistema deberá permitir al Administrador **exportar la base de datos** (CSV/Excel) y consultar el **estado del respaldo**: último respaldo, tamaño, historial y verificación de integridad[cite: 9].
* **Descripción:** Da visibilidad real sobre la contingencia y complementa el backup automático.
* **Rol Relacionado:** Administrador.
* **Reglas de Negocio:** La exportación y el estado son exclusivos del Administrador. La verificación de integridad debe informar resultado y fecha. La **restauración de la copia no forma parte de la interfaz**: es una operación técnica (`Fuera de alcance / Post-MVP`).
* **Estado de implementación:** `Implementado en prototipo (UI)` en `admin/respaldos.html` (métricas, historial, crear respaldo, exportar); la generación real del archivo es `Simulado en prototipo`. El Administrador **solo exporta**; no restaura desde la UI.
* **Prioridad:** Alta.
* **Referencia:** `Config-admin/correcciones-adiciones-requisitos.md` A-7, A-15.

### FR-019: Notificaciones Accionables
* **Declaración:** El sistema deberá permitir que cada notificación **abra el objeto referido** (asesoría, solicitud, evento, tarea) y que el usuario la marque como leída, individual o masivamente[cite: 7].
* **Descripción:** Convierte el aviso en una acción y reduce el tiempo de respuesta.
* **Rol Relacionado:** Todos.
* **Reglas de Negocio:** El contador de no leídas debe reflejar el estado real. Marcar como leída no elimina el aviso.
* **Estado de implementación:** `Implementado en prototipo (UI)` en `admin/notificaciones.html`, `estudiante/notificaciones.html` y `docente/notificaciones.html` (filtros, contador, marcar todo); `Simulado en prototipo`.
* **Prioridad:** Media.
* **Referencia:** `Config-admin/correcciones-adiciones-requisitos.md` A-8.

### FR-020: Configuración del Programa
* **Declaración:** El sistema deberá ofrecer al Administrador una pantalla de **configuración del programa** con parámetros de carga docente, cupos, sedes, etapas, notificaciones y bitácora de cambios[cite: 9].
* **Descripción:** Centraliza reglas operativas que antes estaban dispersas o implícitas.
* **Rol Relacionado:** Administrador.
* **Reglas de Negocio:** Los cambios aplican a todo el programa y quedan registrados en la bitácora con autor y fecha.
* **Estado de implementación:** `Implementado en prototipo (UI)` en `admin/configuracion.html` (pestañas, parámetros, guardado y bitácora); `Simulado en prototipo`.
* **Prioridad:** Media.
* **Referencia:** `prototype/cambios-a-admin.md`; `prototype/admin/configuracion.html`.

### FR-021: Eventos y Recomendación Docente
* **Declaración:** El sistema deberá permitir al Administrador **crear y editar eventos**, y al Docente **consultar el detalle de cada evento y recomendarlo** a un estudiante o a todo un emprendimiento[cite: 7].
* **Descripción:** Vincula la agenda institucional con el acompañamiento del docente.
* **Rol Relacionado:** Administrador, Docente, Estudiante.
* **Reglas de Negocio:** El docente solo recomienda eventos a sus asignados. La recomendación notifica al estudiante.
* **Estado de implementación:** `Implementado en prototipo (UI)` en `admin/eventos.html`, `admin/evento-form.html` y `docente/evento-detalle-*.html` (recomendar); `Simulado en prototipo`.
* **Prioridad:** Media.
* **Referencia:** `prototype/cambios-a-docente.md`; `prototype/orquestacion-docente-2026.md`.

### FR-022: Progreso por Fases y Descarga del Plan
* **Declaración:** El sistema deberá mostrar al Estudiante el **avance por cada fase** del plan de trabajo, con su porcentaje, y permitir **descargar el plan**[cite: 7, 9].
* **Descripción:** Hace explícito el avance parcial y entrega un artefacto de trabajo al estudiante.
* **Rol Relacionado:** Estudiante.
* **Reglas de Negocio:** El porcentaje se deriva de las tareas completadas por fase; la descarga refleja el plan vigente.
* **Estado de implementación:** `Implementado en prototipo (UI)` en `estudiante/estado-seguimiento.html` y `estudiante/plan-trabajo.html`; la descarga es `Simulado en prototipo`.
* **Prioridad:** Media.
* **Referencia:** `prototype/README.md` §12; `prototype/cambios-a-docente.md`.

### FR-023: Evidencia Obligatoria para Completar una Tarea
* **Declaración:** El sistema deberá exigir al Estudiante **adjuntar al menos un archivo de evidencia** antes de habilitar la acción **Marcar como completada** en una tarea[cite: 7].
* **Descripción:** Asegura que el avance declarado esté respaldado por un entregable.
* **Rol Relacionado:** Estudiante.
* **Reglas de Negocio:** Sin evidencia, la tarea no cambia a **Completada**. La evidencia queda vinculada a la tarea y al expediente.
* **Estado de implementación:** `Implementado en prototipo (UI)` en `estudiante/tarea-detalle.html` (contador de archivos que habilita el botón); `Simulado en prototipo`.
* **Prioridad:** Alta.
* **Referencia:** `prototype/README.md` §12; `estudiante/tarea-detalle.html`.

### FR-024: Datos Académicos Condicionales del Estudiante
* **Declaración:** El sistema deberá adaptar el formulario de datos académicos según el **nivel académico** (Pregrado, Posgrado, Egresado), mostrando solo los campos aplicables al tipo y duración del programa[cite: 7].
* **Descripción:** Evita campos irrelevantes y mejora la calidad del dato académico.
* **Rol Relacionado:** Estudiante, Administrador.
* **Reglas de Negocio:** El programa académico solo lo modifica el Administrador. El semestre depende del tipo de posgrado; para egresado desaparece.
* **Estado de implementación:** `Parcial en prototipo (UI)`. Los campos condicionales por nivel académico existen **solo en `estudiante/configuracion.html`**; el formulario equivalente del Administrador (`admin/usuarios.html`) no los replica. `Simulado en prototipo`.
* **Prioridad:** Media.
* **Referencia:** `prototype/README.md` §12; `estudiante/configuracion.html`.

## 5. Requisitos No Funcionales

### NFR-001: Usabilidad y Simplicidad
* **Categoría:** Usabilidad
* **Declaración:** El sistema deberá tener una interfaz de navegación donde el agendamiento y la subida de archivos requieran un máximo de tres clics desde el panel principal[cite: 9].
* **Descripción:** Asegura la adopción por parte de usuarios no tecnológicos[cite: 9].
* **Condición de Aceptación:** Prueba piloto superada sin necesidad de soporte técnico recurrente[cite: 9].
* **Prioridad:** Alta[cite: 9].
* **Referencia:**[cite: 9].

### NFR-002: Autorización Restringida por Rol y Alcance
* **Categoría:** Seguridad
* **Declaración:** El sistema deberá validar el rol y el alcance (propiedad) en el backend para cada endpoint, asegurando que un docente solo acceda a sus emprendimientos asignados, un estudiante únicamente al suyo y el **auditor** solo a consulta y exportación, sin escritura[cite: 7, 9].
* **Descripción:** Previene la visualización no autorizada de datos cruzados[cite: 7, 9].
* **Condición de Aceptación:** Pruebas de API (HTTP 403) al intentar acceder a IDs no pertenecientes al usuario[cite: 7].
* **Prioridad:** Alta[cite: 7, 9].
* **Referencia:**[cite: 7, 9].

### NFR-003: Seguridad de Credenciales y Autenticación
* **Categoría:** Seguridad
* **Declaración:** El sistema deberá usar JWT (expiración de 8h) para el manejo de sesiones y `bcrypt` para encriptar contraseñas; las credenciales y códigos OTP nunca deben exponerse en respuestas JSON[cite: 7, 9].
* **Descripción:** Mitiga riesgos de interceptación de información y vulnerabilidades previas[cite: 7].
* **Condición de Aceptación:** Análisis de payload de respuestas HTTP[cite: 7].
* **Prioridad:** Alta[cite: 7, 9].
* **Referencia:**[cite: 7, 9].

### NFR-004: Copias de Seguridad Automatizadas
* **Categoría:** Fiabilidad
* **Declaración:** El sistema deberá ejecutar backups automatizados diarios de la base de datos[cite: 9].
* **Descripción:** Garantiza la continuidad del negocio en semanas críticas de evaluación[cite: 9].
* **Condición de Aceptación:** Verificación de archivos de volcado (dump) generados diariamente en el servidor[cite: 9].
* **Prioridad:** Alta[cite: 9].
* **Referencia:**[cite: 9].

### NFR-005: Accesibilidad de la Interfaz
* **Categoría:** Usabilidad / Accesibilidad
* **Declaración:** El sistema deberá usar **formularios nativos con etiqueta asociada**, **estados vacíos explícitos**, **texto alternativo** en iconos y controles, y **foco visible**; los componentes interactivos declararán `aria-label` cuando el texto visible no baste.
* **Descripción:** Permite operar la plataforma con lector de pantalla y teclado, y reduce errores de captura.
* **Condición de Aceptación:** Navegación completa por teclado en login, registro, formularios de alta y bandejas; controles con nombre accesible verificable en el HTML generado.
* **Estado de implementación:** `Implementado en prototipo (UI)` de forma parcial (etiquetas, `aria-label`, `aria-expanded` y foco visible en las vistas revisadas); la auditoría formal es `Pendiente de backend`.
* **Prioridad:** Media.
* **Referencia:** `prototype/admin/usuarios.html`, `prototype/admin/solicitudes.html`, `prototype/lib_ui.py`.

### NFR-006: Consistencia Visual y de Datos
* **Categoría:** Usabilidad / Consistencia
* **Declaración:** El sistema deberá mantener una **paleta y tipografía únicas**, componentes reutilizables y **estados normalizados** (`Limitado`, `Activo`, `Inactivo`, `Pendiente`, `Aprobado`, `Rechazado`) en todas las vistas y roles.
* **Descripción:** Evita que el mismo concepto se muestre con nombres o colores distintos según la pantalla.
* **Condición de Aceptación:** Revisión de badges y filtros en los tres roles; un mismo estado tiene el mismo nombre y tratamiento visual.
* **Estado de implementación:** `Implementado en prototipo (UI)` mediante `lib_css.py` y las convenciones de `README.md` §5.
* **Prioridad:** Media.
* **Referencia:** `prototype/README.md` §5; `prototype/lib_css.py`.

### NFR-007: Auditabilidad de Cambios
* **Categoría:** Seguridad / Trazabilidad
* **Declaración:** El sistema deberá registrar **quién** cambió **qué** y **cuándo** en las operaciones sensibles: estados de cuenta, aprobación/rechazo de emprendimientos, asignaciones, configuración del programa, respaldos y **consultas/exportaciones del auditor** (AQ-08).
* **Descripción:** Permite reconstruir decisiones administrativas, responder ante reclamaciones y auditar el uso del rol de solo lectura.
* **Condición de Aceptación:** Toda operación sensible produce un registro con autor, fecha, valor anterior y valor nuevo; toda consulta o exportación del auditor deja rastro de usuario, fecha y objeto.
* **Estado de implementación:** `Pendiente de backend`. El prototipo solo muestra la **bitácora** como vista (`admin/configuracion.html`).
* **Prioridad:** Alta.
* **Referencia:** `Config-admin/correcciones-adiciones-requisitos.md` A-6; `prototype/admin/configuracion.html`.

### NFR-008: Diseño Responsive
* **Categoría:** Usabilidad
* **Declaración:** El sistema deberá adaptar las vistas a escritorio, tableta y móvil, sin pérdida de acciones principales ni tablas inutilizables.
* **Descripción:** El personal administrativo y los estudiantes acceden desde dispositivos distintos.
* **Condición de Aceptación:** Las vistas clave (login, dashboard, listas y formularios) conservan navegación y acciones en los tres tamaños.
* **Estado de implementación:** `Implementado en prototipo (UI)` con puntos de quiebre en `lib_css.py` y en las hojas de cada rol.
* **Prioridad:** Media.
* **Referencia:** `prototype/README.md` §5; `prototype/lib_css.py`.

### NFR-009: Mantenibilidad del Prototipo Generado
* **Categoría:** Mantenibilidad
* **Declaración:** El HTML del prototipo deberá generarse desde Python y **no editarse a mano**; los cambios se harán en `paginas_*.py` y `lib_*.py`, y se regenerarán las pantallas afectadas.
* **Descripción:** Evita divergencias entre vistas y permite reproducir el prototipo de forma determinista.
* **Condición de Aceptación:** `python generar.py --rol <rol>` reproduce las pantallas sin diferencias inesperadas y el repositorio no contiene parches manuales sobre el HTML.
* **Estado de implementación:** `Implementado en prototipo (UI)`; el pipeline es la única fuente de las vistas.
* **Prioridad:** Media.
* **Referencia:** `prototype/README.md` §7–§8; `prototype/generar.py`.

## 6. Reglas de Negocio

### BR-001: Exigencia de Acta para Asignación
* **Regla:** El administrador no puede asignar un docente definitivo al emprendimiento hasta que el estudiante haya diligenciado y firmado el acta de confidencialidad[cite: 8].
* **Descripción:** Proceso de control jurídico del programa[cite: 8].
* **Procesos Afectados:** BP-001, BP-002.
* **Referencia:**[cite: 8].

### BR-002: Gestión Manual de Agenda (Gobernanza Administrativa)
* **Regla:** Se prohíbe la integración con calendarios externos (Google/Outlook) y el agendamiento libre por estudiantes. El **Administrador asigna la asesoría directamente**; el **Docente la acepta o propone otra fecha**; la plataforma aloja toda la lógica y los cruces[cite: 9].
* **Descripción:** Conserva el control restrictivo solicitado por la coordinación y elimina la ambigüedad de “administración o el asesor”[cite: 9].
* **Procesos Afectados:** BP-002.
* **Referencia:**[cite: 9]; `Config-admin/correcciones-adiciones-requisitos.md` C-2, C-6.

### BR-003: Propiedad del Cambio de Estado de Cuenta
* **Regla:** Solo el **Administrador** puede cambiar el estado de una cuenta: **Limitado → Activo** (desbloqueo) e **Inactivo → Activo** (reactivación). El usuario no puede autoactivarse.
* **Descripción:** Evita accesos no autorizados y concentra la responsabilidad.
* **Procesos Afectados:** BP-005.
* **Referencia:** `Config-admin/correcciones-adiciones-requisitos.md` A-3, D4.

### BR-004: Aprobación Previa del Emprendimiento
* **Regla:** Todo emprendimiento nace en **Pendiente** y solo pasa a **Aprobado** por decisión del Administrador. Un segundo emprendimiento requiere autorización de **paralelo**. El rechazo exige motivo.
* **Descripción:** Controla la duplicidad y deja rastro de la decisión.
* **Procesos Afectados:** BP-004.
* **Referencia:** `Config-admin/correcciones-adiciones-requisitos.md` A-2, D2.

### BR-005: Inactividad a los 90 Días
* **Regla:** Un estudiante pasa a **Inactivo** tras **90 días (3 meses)** continuos sin actividad o avances. La reactivación es manual y exclusiva del Administrador.
* **Descripción:** Cierra la ambigüedad de “periodo definido” y alinea el SRS con las historias de usuario.
* **Procesos Afectados:** BP-003, BP-005.
* **Referencia:** `Config-admin/correcciones-adiciones-requisitos.md` C-3; cierre de AQ-01.

### BR-006: Borrado Lógico y Cascada de Adjuntos
* **Regla:** Eliminar, desactivar u ocultar son **bajas lógicas reversibles** con confirmación. Al eliminar un emprendimiento o usuario, sus **archivos adjuntos** se eliminan en cascada.
* **Descripción:** Protege la trazabilidad y evita archivos huérfanos.
* **Procesos Afectados:** BP-003, BP-004.
* **Referencia:** `Config-admin/correcciones-adiciones-requisitos.md` A-4, D3; FR-008.

### BR-007: Evidencia Obligatoria en Tareas
* **Regla:** Una tarea solo puede pasar a **Completada** si el estudiante adjuntó al menos un archivo de evidencia.
* **Descripción:** Asegura que el avance declarado esté respaldado.
* **Procesos Afectados:** BP-003.
* **Referencia:** `prototype/estudiante/tarea-detalle.html`; FR-023.

### BR-008: Duplicidad Intencional de Vistas de Avance y Diagnóstico
* **Regla:** “Registrar avance” y “Revisar diagnóstico” existen tanto para el **Administrador** como para el **Docente**. Es una decisión de diseño, no un defecto.
* **Descripción:** El admin puede administrar el acompañamiento sin suplantar la firma del docente; el docente conserva la autoría de su avance.
* **Procesos Afectados:** BP-003.
* **Referencia:** `Config-admin/correcciones-adiciones-requisitos.md` A-19, D5.

### BR-009: Motivo Obligatorio en el Rechazo del Acta
* **Regla:** El rechazo del acta de compromiso exige un **motivo obligatorio**; sin motivo no se puede confirmar el rechazo. La decisión notifica al estudiante y queda registrada.
* **Descripción:** Evita rechazos sin justificación y unifica el criterio ya aplicado en la bandeja de solicitudes.
* **Procesos Afectados:** BP-001.
* **Referencia:** AQ-05 (decisión del 2026-10-25); FR-003, FR-014.
* **Estado de implementación:** `Pendiente de backend`. No existe vista de acta en el prototipo y el modal de rechazo de la bandeja no valida el campo vacío.

## 7. Experiencia de Usuario y Recorrido (User Journey)

**Flujo de Ingreso y Diagnóstico (Estudiante)**
1. **Inicio:** El estudiante se registra en la web e introduce el OTP recibido por correo[cite: 7].
2. **Acción Administrativa:** El Administrador, tras una charla, le habilita secciones de la plataforma[cite: 8].
3. **Caracterización:** El estudiante accede a su perfil y llena el formulario de valoración (preguntas de negocio)[cite: 8, 9].
4. **Respuesta del Sistema:** El sistema procesa los datos y presenta un diagnóstico gráfico (fortalezas y debilidades) sin tabulación manual[cite: 8, 9].
5. **Documentación:** El estudiante descarga, firma y sube el acta de confidencialidad[cite: 8].
6. **Resultado:** El Administrador ve los requisitos cumplidos y asocia el emprendimiento a un Docente en el módulo de Asignaciones[cite: 7, 8]. A partir de ahí, el estudiante visualiza a su mentor y las tareas del plan de trabajo[cite: 7].

## 8. Matriz de Trazabilidad

| Source ID | Necesidad del Usuario / Hallazgo | Proceso Relacionado | ID Requisito(s) | Tipo | Estado |
| --------- | ----------------------------- | ------------------------ | ----------------- | ---------------- | ------ |
|[cite: 7] | Verificación segura por correo OTP 8 dígitos | BP-001 | FR-001 | FR | Confirmado |
|[cite: 8, 9] | Eliminar tabulación manual de diagnóstico | BP-001 | FR-002 | FR | Confirmado |
|[cite: 8] | Subir acta de confidencialidad antes de asignar | BP-001 | FR-003, BR-001 | FR, BR | Confirmado |
|[cite: 9] | Control manual administrativo de agenda (sin calendarios externos) | BP-002 | FR-004, BR-002 | FR, BR | Confirmado |
|[cite: 7] | Notificaciones al recibir tareas o confirmar citas | BP-002, BP-003 | FR-005 | FR | Confirmado |
|[cite: 9] | Historial ligado a la idea de negocio (no al docente) | BP-003 | FR-006 | FR | Confirmado |
|[cite: 9] | Alertas por inactividad del estudiante | BP-003, BP-005 | FR-007, BR-005 | FR, BR | Confirmado |
|[cite: 7] | Subida de evidencias de hasta 500MB | BP-003 | FR-008 | FR | Confirmado |
|[cite: 9] | Descarga de Excel/CSV como contingencia local | BP-003, BP-006 | FR-009, FR-018 | FR | Confirmado |
|[cite: 9] | Máximo 3 clics para acciones principales | N/A | NFR-001 | NFR | Confirmado |
|[cite: 7, 9] | Seguridad de roles y JWT estricta | N/A | NFR-002, NFR-003 | NFR | Confirmado |
| A-1, D1 | El Admin crea y gestiona cuentas | BP-001, BP-005 | FR-011, FR-016 | FR | Confirmado |
| A-2, D2 | Estudiante crea; Admin aprueba, incluido el paralelo | BP-004 | FR-012, BR-004 | FR, BR | Confirmado |
| A-3, D4 | Ciclo Limitado → Activo → Inactivo con dueño único | BP-005 | FR-013, BR-003 | FR, BR | Confirmado |
| A-13 | Bandeja única de solicitudes | BP-004, BP-005 | FR-014 | FR | Confirmado |
| C-1, C-2, A-12 | Admin asigna asesoría; docente acepta | BP-002 | FR-015, BR-002 | FR, BR | Confirmado |
| A-5 | Validación, unicidad y tope de carga | BP-001, BP-004 | FR-016 | FR | Confirmado |
| A-6, A-14 | Expediente consolidado y trazable | BP-003 | FR-017, NFR-007 | FR, NFR | Confirmado |
| A-7, A-15 | Panel de respaldos con estado | BP-006 | FR-018, NFR-004 | FR, NFR | Confirmado |
| A-8 | Notificaciones accionables | BP-002, BP-004 | FR-019 | FR | Confirmado |
| AQ-05 | Acta: motivo obligatorio de rechazo | BP-001 | FR-003, BR-009 | FR, BR | Confirmado |
| AQ-08 | Auditor: solo lectura y exportación, sin edición ni datos sensibles completos | N/A | NFR-002, NFR-007, FR-010, FR-017 | NFR, FR | Confirmado (Post-MVP) |
| AQ-11 | Estructura definitiva según el modelo textual (41 tablas = 27 de negocio + 14 catálogos) | N/A | FR-017, NFR-007 | FR, NFR | Confirmado |
| Config. del programa | Parámetros centralizados y bitácora | BP-006 | FR-020 | FR | Confirmado |
| Docente | Eventos y recomendación | BP-003 | FR-021 | FR | Confirmado |
| Estudiante | Progreso por fases y descarga del plan | BP-003 | FR-022 | FR | Confirmado |
| Estudiante | Evidencia obligatoria para completar tarea | BP-003 | FR-023, BR-007 | FR, BR | Confirmado |
| Estudiante | Datos académicos condicionales | BP-001 | FR-024 | FR | Confirmado |
| Auditoría UI/UX | Accesibilidad de formularios y controles | N/A | NFR-005 | NFR | Confirmado |
| Auditoría UI/UX | Consistencia visual y de estados | N/A | NFR-006 | NFR | Confirmado |
| Prototipo | Responsive en escritorio, tableta y móvil | N/A | NFR-008 | NFR | Confirmado |
| Prototipo | HTML generado, no editado a mano | N/A | NFR-009 | NFR | Confirmado |

## 9. Ambigüedades, Suposiciones y Preguntas Abiertas

| ID | Tipo | Descripción | Requisito Relacionado | Impacto | Recomendación |
| -- | ---- | ----------- | ---------------------- | ------ | ------------------------- |
| AQ-01 | **Cerrada** | **Tiempo exacto para semaforización:** se fijó en **90 días (3 meses)** continuos sin actividad, alineado con `historias_usuario.md` §7 y con la evidencia del prototipo. | FR-007, BR-005 | Medio | Cerrada el 2026-10-25. Sin acción pendiente. |
| AQ-02 | **Cerrada** | **Habilitación de plataforma:** la cuenta nace **Limitado** y el Administrador la pasa a **Activo** tras la reunión; el cambio es manual y exclusivo del Admin. | FR-013, BR-003 | Alto | Cerrada el 2026-10-25. Sin acción pendiente. |
| AQ-03 | **Cerrada** | **Archivo de correcciones:** el documento existe; la copia usada en `Config-admin/correcciones-adiciones-requisitos.md` es idéntica por **SHA-256** (`EDCDE30F…836B5872`) a las otras copias del equipo. Sus **28 ítems** (C-1…C-7 y A-1…A-21) están mapeados. | FR-011 … FR-024 | Medio | Cerrada el 2026-10-25. Sin acción pendiente. |
| AQ-04 | **Cerrada** | **Restauración de respaldos:** es una **operación técnica**, no una función del Administrador. El Admin solo **exporta la base/reportes** y consulta estado e integridad. Se clasifica `Fuera de alcance / Post-MVP`. | FR-018, NFR-004 | Medio | Cerrada el 2026-10-25. Sin acción pendiente. |
| AQ-05 | **Cerrada** | **Motivo obligatorio de rechazo:** el rechazo del **acta de compromiso** exige motivo, igual que en la bandeja; sin motivo no se confirma y se notifica al estudiante (BR-009). | FR-003, FR-012, FR-014 | Bajo | Cerrada el 2026-10-25. La validación en la interfaz queda `Pendiente de backend`. |
| AQ-06 | **Abierta** | **Campos obligatorios y criterios de validación:** el registro tiene 7 campos obligatorios + casilla, sin atributos `name`; no existe lista de criterios del emprendedor en el prototipo. | FR-016 | Alto | Dossier §3. Decidir en reunión; no se asume por defecto. |
| AQ-07 | **Abierta** | **Acceso previo:** contradicción entre `estado-seguimiento.html` (diagnóstico bloqueado en cuenta `Limitado`) y `emprendimiento-detalle.html` (botón activo). | FR-013 | Alto | Dossier §4. Decidir en reunión. |
| AQ-08 | **Cerrada** | **Rol auditor:** solo lectura y exportación de reportes; sin edición ni datos sensibles completos. Se cubre con NFR-002, NFR-007, FR-010 y FR-017; **sin FR nuevo**. | NFR-002, NFR-007, FR-010, FR-017 | Medio | Cerrada el 2026-10-25. Implementación `Fuera de alcance / Post-MVP`; US-026. |
| AQ-09 | **Abierta** | **Rúbrica e informe:** 5 secciones, 22 preguntas, 6 dimensiones y 4 bandas visibles, sin fórmula ni plantilla del informe. | FR-002 | Alto | Dossier §5. Decidir en reunión. |
| AQ-10 | **Abierta** | **Plazo y efecto del rechazo del acta:** BR-009 fija el motivo obligatorio; faltan el plazo de revisión y el efecto completo. | FR-003, BR-009 | Medio | Dossier §6. Decidir en reunión. |
| AQ-11 | **Cerrada** | **Estructura definitiva:** se toma del **modelo textual** de `README.md` §5, reconciliado con el prototipo: **41 tablas = 27 de negocio + 14 catálogos**. No se declara total de relaciones (el "42" anterior no era trazable). `adjuntos` y sus pivotes ya tienen ficha; `auditoria_eventos`, `solicitudes`, `configuracion_programa`, `respaldos`, `comentarios` y `recomendaciones_evento` quedan modeladas. | FR-017, NFR-007 | Medio | Cerrada el 2026-10-25. Diagramas regenerados el 2026-10-25. |
| AQ-12 | **Abierta** | **Insumos ausentes:** `control.pdf` y el Excel de preguntas fueron solicitados; no están en el repositorio. | FR-002, FR-016 | Medio | Dossier §8. Si no llegan, no se bloquea ni se inventa contenido. |

## 10. Revisión de Calidad de Requisitos

* **Correctitud y Consistencia:** Se alinearon los requerimientos conflictivos de los calendarios. Aunque en el "MOMENT 1" se sugirió integración con Google Calendar[cite: 9], el "MOMENT 2" dictaminó explícitamente que todo vivirá dentro de la plataforma sin integraciones externas[cite: 9]. La matriz refleja la decisión final. También se resolvió la contradicción de **quién confirma la asesoría**: el Admin asigna directamente y el docente acepta o reprograma (FR-004, FR-015, BR-002).
* **Trazabilidad con el prototipo:** cada requisito nuevo se contrastó con la vista del rol antes de documentarse (`admin/usuarios.html`, `admin/solicitudes.html`, `admin/asignaciones.html`, `admin/respaldos.html`, `admin/configuracion.html`, `estudiante/tarea-detalle.html`, entre otras). El detalle está en el registro de ejecución.
* **Separación de Responsabilidades:** Se separaron estrictamente las reglas funcionales de negocio (como el diagnóstico) de los requisitos técnicos estructurales (JWT, Node.js, aislamientos por API)[cite: 7, 9].
* **Límite de alcance:** se distingue de forma explícita entre lo implementado en el prototipo, lo simulado en el navegador y lo pendiente de backend. Ningún requisito se declara terminado por el hecho de tener pantalla.
* **Recomendación:** Definir en la etapa de planeación de Sprints los campos exactos del formulario de caracterización (Modelo de Negocio, Marketing, etc.) mencionados cualitativamente por la coordinadora[cite: 8]. Estado al 2026-10-25: **AQ-01 … AQ-05 y AQ-08 cerradas**; **AQ-11 cerrada** con el modelo textual. **AQ-06, AQ-07, AQ-09, AQ-10 y AQ-12 siguen abiertas** y se tratan en `docs/dossier-decisiones-pendientes-2026-10.md`; no se deciden por defecto.

## 11. Resumen Ejecutivo de Requisitos

El proyecto SGEMD incluye **24 requisitos funcionales** y **9 requisitos no funcionales** (`FR-001` … `FR-024`, `NFR-001` … `NFR-009`), distribuidos en **6 procesos de negocio** y **9 reglas de negocio**. Las áreas funcionales más críticas incluyen el diagnóstico automático de emprendimientos para ahorrar cargas administrativas (BP-001), la aprobación controlada de emprendimientos (BP-004) y la consolidación de un expediente central e intransferible para los proyectos (BP-003)[cite: 8, 9].

Los requisitos de mayor prioridad se enfocan en la seguridad del control de datos (exportaciones a Excel, roles estrictos validados en el backend, firmas confidenciales), en la gobernanza de cuentas (estados Limitado/Activo/Inactivo con dueño único) y en la asignación controlada de asesorías (Admin asigna, docente acepta)[cite: 7, 8, 9]. El principal riesgo a mitigar es la fricción en la usabilidad, por lo que el sistema exige un límite de tres clics para tareas básicas como adjuntar archivos y agendar, además de formularios accesibles y consistentes[cite: 9].

El prototipo actual cubre **73 pantallas** (4 globales, 27 de estudiante, 23 de docente y 19 de administrador) y permite validar la mayor parte de los flujos de interfaz. No sustituye la implementación: guardar, descargar, exportar y notificar son simulaciones.

**Estado de las preguntas abiertas:** cerradas **AQ-01 … AQ-05**, **AQ-08** (rol auditor: solo lectura y exportación, sin FR nuevo) y **AQ-11** (modelo textual de 41 tablas = 27 de negocio + 14 catálogos, sin total de relaciones). Abiertas: **AQ-06** (campos y criterios), **AQ-07** (acceso previo), **AQ-09** (rúbrica e informe), **AQ-10** (plazo y efecto del acta) y **AQ-12** (insumos). El detalle está en el dossier de decisiones. Los diagramas se regeneraron el 2026-10-25 y su fuente es el archivo Mermaid/Markdown (`docs/diagrama-clases.md`, `docs/diagrama-componentes.md`, `docs/context-diagram.mmd`).

## 12. Control de Cambios

| Fecha | Cambio | IDs afectados | Evidencia |
|---|---|---|---|
| 2026-10-25 | Encabezado de actualización, leyenda de estado y conteos vigentes | — | `prototype/index.html` (73 enlaces) |
| 2026-10-25 | Corrección de asignación de asesorías | FR-004, BR-002 | `admin/asignaciones.html`, `admin/solicitudes.html`, `docente/asesoria-detalle.html`; C-1, C-2, C-6 |
| 2026-10-25 | Cierre de inactividad en 90 días | FR-007, BR-005, AQ-01 | `historias_usuario.md` §7; C-3 |
| 2026-10-25 | Ciclo de estados de cuenta y desbloqueo | FR-013, BR-003, AQ-02 | `admin/usuarios.html`; A-3, D4 |
| 2026-10-25 | Borrado lógico y cascada de adjuntos | FR-008, BR-006 | A-4, D3 |
| 2026-10-25 | Nuevos requisitos funcionales | FR-011 … FR-024 | Vistas de los tres roles; A-1 … A-21 |
| 2026-10-25 | Nuevos requisitos no funcionales | NFR-005 … NFR-009 | `lib_ui.py`, `lib_css.py`, `paginas_*.py` |
| 2026-10-25 | Nuevos procesos de negocio | BP-004, BP-005, BP-006 | `admin/solicitudes.html`, `admin/usuarios.html`, `admin/respaldos.html` |
| 2026-10-25 | Nuevas reglas de negocio | BR-003 … BR-009 | Correcciones y vistas verificadas |
| 2026-10-25 | Matriz de trazabilidad ampliada | FR-011 … FR-024, NFR-005 … NFR-009 | Este documento, §8 |
| 2026-10-25 | Ambigüedades y bloqueos | AQ-01 … AQ-12 | Registro de ejecución; dossier de decisiones |
| 2026-10-25 | Cierre de AQ-03: archivo de correcciones localizado e idéntico por hash | AQ-03 | `Config-admin/correcciones-adiciones-requisitos.md` (SHA-256 `EDCDE30F…836B5872`) |
| 2026-10-25 | Cierre de AQ-04: restauración fuera de la UI (operación técnica) | FR-018, AQ-04 | `admin/respaldos.html`; decisión del usuario |
| 2026-10-25 | Cierre de AQ-05: motivo obligatorio en el rechazo del acta | BR-009, FR-003, FR-014, AQ-05 | `admin/solicitudes.html` (modal de motivo); decisión del usuario |
| 2026-10-25 | Cierre de AQ-08: rol auditor de solo lectura y exportación, sin FR nuevo | R-04, NFR-002, NFR-007, FR-010, FR-017, AQ-08 | Decisión del usuario; `docs/dossier-decisiones-pendientes-2026-10.md` §9 |
| 2026-10-25 | Cierre de AQ-11: estructura definitiva según el modelo textual | AQ-11, FR-017, NFR-007 | `README.md` §5 (41 tablas = 27 + 14); dossier §7 |
| 2026-10-25 | Apertura registrada de los pendientes de reunión | AQ-06, AQ-07, AQ-09, AQ-10, AQ-12 | `docs/dossier-decisiones-pendientes-2026-10.md` |

**Requisitos reemplazados (no eliminados):** el enunciado anterior de FR-004 (“el Administrador aprueba/gestiona los cruces”) se conserva en el historial de este control y queda **reemplazado** por la redacción vigente. El enunciado anterior de FR-007 (“periodo de tiempo definido”) queda **reemplazado** por 90 días. Ningún ID se renumeró.
