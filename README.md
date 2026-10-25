# SGEMD — Contexto Maestro para Reconstrucción del MVP

> **Propósito de este documento:** servir como especificación y contexto único **SGEMD (Sistema de Gestión de Emprendimiento Minuto de Dios)** desde cero, de forma limpia.
>
> **Qué es y qué no es:** es un documento de **especificación/contexto**. Describe el comportamiento **correcto esperado** del MVP y qué debe evitarse del proyecto anterior. **No contiene** secretos, contraseñas, tokens, valores de `.env`, ni credenciales reales. **No es** un copiado del código anterior.
>
> El proyecto se construye **DESDE CERO**. No se debe asumir que hay que conservar errores, estructuras innecesarias ni tablas obsoletas del proyecto anterior.

> **Actualización (2026-10-12):** se incorporó el **alcance ampliado** que salió del proceso real de atención (reunión con el área de Emprendimiento) y de las anotaciones del equipo: **validación y activación del emprendedor**, **correo de bienvenida**, **diagnóstico *data-driven* desde Excel**, **caracterización y valoración**, **acta de compromiso y confidencialidad**, **notificaciones** y **rol de auditor** (solo lectura y exportación, AQ-08). El detalle, las reglas nuevas y los puntos por cerrar están en la [§16](#16-fuentes-y-trazabilidad-del-alcance-ampliado). Las secciones [2](#2-roles), [3](#3-funcionalidades-del-mvp), [5](#5-modelo-de-datos), [6](#6-reglas-de-negocio), [7](#7-api), [8](#8-frontend), [11](#11-decisiones-importantes), [12](#12-mvp-mínimo) y [13](#13-criterios-de-aceptación) fueron actualizadas.

> **Actualización (2026-10-25) — trabajo local:** se sincronizaron las secciones [2](#2-roles), [3](#3-funcionalidades-del-mvp), [6](#6-reglas-de-negocio), [8](#8-frontend), [11](#11-decisiones-importantes), [12](#12-mvp-mínimo), [13](#13-criterios-de-aceptación) y [16](#16-fuentes-y-trazabilidad-del-alcance-ampliado) con las vistas verificadas del prototipo: **73 pantallas** (4 globales + 27 estudiante + 23 docente + **19 administrador**), CRUD de usuarios, aprobación de emprendimientos, bandeja de solicitudes, asignación directa de asesorías, respaldos y configuración del programa. **Todo el trabajo es local:** no se creó rama, no se hizo commit y no se publicó en GitHub. El método y la evidencia están en [`docs/orquestacion-actualizacion-requisitos-2026-10.md`](docs/orquestacion-actualizacion-requisitos-2026-10.md), [`docs/registro-actualizacion-requisitos-2026-10.md`](docs/registro-actualizacion-requisitos-2026-10.md) y el dossier [`docs/dossier-decisiones-pendientes-2026-10.md`](docs/dossier-decisiones-pendientes-2026-10.md); las decisiones AQ-08 y AQ-11 ya están cerradas y AQ-06, AQ-07, AQ-09, AQ-10 y AQ-12 quedan para la reunión.
>
> **Alcance del prototipo:** es **estático**. Guardar, descargar, exportar y notificar están **simulados** en el navegador (`localStorage`). **No hay backend, API ni PostgreSQL** en este repositorio.

---

> **Nota sobre el prototipo:** el **prototipo navegable de SGEMD** vive en `prototype/`: **73 pantallas HTML** generadas desde Python, un `index.html` índice para recorrerlas y el pipeline que las genera, audita y publica.
>
> Empieza por **[PROTOTIPO-STITCH.md](PROTOTIPO-STITCH.md)**: qué contiene y cómo usarlo.
>
> Este `README.md` es la especificación general del proyecto. El **refactor UX/UI del Rol Docente** está documentado en **[docs/docente-rol-ux.md](docs/docente-rol-ux.md)** (y en `docs/estructura_de_vistas_sgemd.md` §3.3).

---

## Contenido

1. [Objetivo del proyecto](#1-objetivo-del-proyecto)
2. [Roles](#2-roles)
3. [Funcionalidades del MVP](#3-funcionalidades-del-mvp)
4. [Arquitectura propuesta](#4-arquitectura-propuesta)
5. [Modelo de datos](#5-modelo-de-datos)
6. [Reglas de negocio](#6-reglas-de-negocio)
7. [API](#7-api)
8. [Frontend](#8-frontend)
9. [Autenticación y seguridad](#9-autenticación-y-seguridad)
10. [Problemas del proyecto anterior que NO deben repetirse](#10-problemas-del-proyecto-anterior-que-no-deben-repetirse)
11. [Decisiones importantes](#11-decisiones-importantes)
12. [MVP mínimo](#12-mvp-mínimo)
13. [Criterios de aceptación](#13-criterios-de-aceptación)
14. [Orden recomendado de construcción](#14-orden-recomendado-de-construcción)
15. [Estado final esperado](#15-estado-final-esperado)
16. [Fuentes y trazabilidad del alcance ampliado](#16-fuentes-y-trazabilidad-del-alcance-ampliado)
17. [Reconciliación con el prototipo (2026-10-25)](#17-reconciliación-con-el-prototipo-2026-10-25)

---

## 1. Objetivo del proyecto

### Qué es SGEMD

**SGEMD (Sistema de Gestión de Emprendimiento Minuto de Dios)** es una plataforma web para gestionar de extremo a extremo el emprendimiento estudiantil universitario, utilizando tecnologías modernas como **Node.js** para el backend y **React** para el frontend.

### Para quién está pensado

- **Estudiantes** que tienen (o quieren tener) un emprendimiento.
- **Docentes/Mentores** que acompañan a uno o varios estudiantes.
- **Administradores** que gestionan el sistema, los usuarios y las asignaciones.

### Qué problema resuelve

Centraliza la información que hoy está dispersa: quién emprende, qué tan avanzado está su emprendimiento, qué docente lo orienta, qué seguimiento/acuerdos existen, qué tareas y asesorías se han definido. Elimina la dependencia de hojas de cálculo o seguimiento informal. Permite una correcta recolección de datos alineada con los estándares de investigación y proyectos institucionales de UNIMINUTO.

### Cuál es el objetivo del MVP

Que un estudiante pueda registrarse, tener un emprendimiento, que el administrador le asigne un docente mentor, que el docente registre seguimiento y tareas, y que el estudiante consulte su avance — todo con dashboards alimentados por datos reales de la base de datos. El diseño debe ser totalmente responsive para visualización en computadoras de escritorio y dispositivos móviles.

### Flujo principal del sistema

1. El estudiante se **registra** y **verifica** su correo.
2. El **administrador** crea usuarios y **emprendimientos** (asociados a un estudiante-propietario).
3. El administrador **asigna** un **docente/mentor** a un estudiante (y opcionalmente su emprendimiento) mediante una **asignación**.
4. El docente ve los emprendimientos que **le fueron asignados**, registra **seguimiento** y crea **tareas** y **asesorías** para sus asignados.
5. El estudiante consulta su **emprendimiento, etapas, seguimiento, tareas pendientes y avance**.
6. Todos los roles ven **dashboards** con métricas derivadas de la base de datos (no datos mock).

---

## 2. Roles

Existe **un único campo de rol** en el usuario, con valores:

- `1 = Administrador`
- `2 = Estudiante`
- `3 = Docente/Mentor`
- `4 = Auditor` — **solo lectura y exportación de reportes** (decisión del 2026-10-25). **No edita** datos de ningún módulo ni accede a información sensible completa. Se cubre con NFR-002, NFR-007, FR-010 y FR-017, más la historia **US-026**; **no** se crea un FR nuevo.

> **Nota:** el alcance del rol 4 está **definido**, pero el rol **no existe en el prototipo**: se clasifica `Fuera de alcance / Post-MVP`. El sistema actual opera con **tres** roles funcionales (1–3); implementarlo exige backend y guardas de solo lectura ([§11](#11-decisiones-importantes)).

### Administrador (rol 1)

- **Puede hacer:** gestionar cualquier usuario (**crear, editar, activar/desactivar y dar de baja lógica**), **aprobar o rechazar emprendimientos** (incluido el **paralelo**), crear/editar/eliminar emprendimientos, crear/eliminar/reasignar asignaciones, **crear y asignar asesorías directamente**, resolver la **bandeja de solicitudes** (desbloqueos, paralelos y citas), consultar todos los emprendimientos/seguimientos/tareas/asesorías, dashboard global, **configurar los parámetros del programa** y **exportar/verificar respaldos**. Modifica variables bloqueadas para el estudiante (Mentor asignado, observaciones, sector productivo y etapa).
- **Estados de cuenta:** **Limitado → Activo → Inactivo**. Solo el Administrador desbloquea y reactiva. La inactividad se marca a los **90 días**.
- **Tope de asignación:** no puede confirmar una asignación si el docente ya alcanzó los topes configurados en `admin/configuracion.html`: **12 horas de asesoría por semana** y **12 emprendimientos**. Ambos son parámetros del programa y pueden cambiarse (ver [§6](#6-reglas-de-negocio)).
- **No debería:** crear seguimientos/tareas como si fuera el docente asignado (puede administrarlos pero no "firmarlos"), ni ver credenciales o secretos.

### Docente / Mentor (rol 3)

- **Puede hacer:** ver únicamente los emprendimientos que **le fueron asignados** (vía asignaciones), registrar avances y su evidencia de esos emprendimientos (vista *Registrar avance* y columna *Evidencia*), crear/editar/eliminar tareas y asesorías de sus asignados, **aceptar, rechazar o reprogramar** las asesorías que le corresponden, ver el perfil de sus estudiantes, consultar su dashboard. Revisa el **detalle de cada evento** y lo **recomienda** a estudiantes individuales o a todo un emprendimiento.
- **Capacidades del rol (refactor UX/UI):** registrar **avance con calificación** (puntaje 0–100 + retroalimentación) y **estado de revisión** (Pendiente · En revisión · Calificada · Devuelta); **confirmar o reprogramar** asesorías de sus estudiantes (el estudiante no agenda solo, BR-002); **revisar el diagnóstico y guardar recomendaciones**; **recomendar eventos** por emprendimiento o por estudiante; seguir sus **compromisos en un calendario interactivo**; mantener una **bitácora de comentarios** por emprendimiento; y **gestionar sus notificaciones** (filtro por tipo, marcar como leído).
- **No debería:** ver emprendimientos/estudiantes de otros docentes, modificar el emprendimiento del estudiante, eliminar usuarios ni cambiar roles.
- **Tope de carga:** máximo **12 emprendimientos** y **12 horas semanales** por docente (valores configurables en `admin/configuracion.html`). El prototipo aplica ambos topes; el modelo los almacena en `asignaciones.HorasSemanales` y `configuracion_programa`.

> Detalle del refactor y de las 23 pantallas del rol en **[docs/docente-rol-ux.md](docs/docente-rol-ux.md)**.

### Estudiante (rol 2)

- **Puede hacer:** consultar **sus** emprendimientos, ver su progreso/etapas **por fase**, consultar (solo lectura) el seguimiento de su emprendimiento, consultar y **completar** sus tareas **con evidencia obligatoria**, **solicitar** asesorías (no agendarlas por su cuenta), consultar su dashboard y **descargar su plan de trabajo**. **Permisos de edición de su emprendimiento:** puede editar el Nombre, Descripción, Redes Sociales y, opcionalmente, el plan de trabajo.
- **Vacío del prototipo:** el **alta de emprendimiento por el estudiante no está representada** en las 73 pantallas. La bandeja de aprobación del Admin sí existe, pero no hay formulario de registro del emprendimiento ni vista del estado *Pendiente* (de aprobación). Se documenta como pendiente ([§17.4](#173-vacíos-del-prototipo-que-no-se-inventan)).
- **No debería:** crear seguimientos ni tareas, ver emprendimientos de otros, ni ver datos de otros usuarios.

**Regla general de autorización:** cada endpoint de negocio valida **rol** y **alcance** en **backend** (no solo en la UI). Un docente solo ve lo asignado a él; un estudiante solo lo propio; el admin todo.

---

## 3. Funcionalidades del MVP

Cada módulo describe: quién lo usa, qué puede hacer, qué información maneja y su flujo esperado.

### Login

- **Quién lo usa:** todos.
- **Qué puede hacer:** iniciar sesión con correo + contraseña.
- **Información que maneja:** credenciales, token de sesión.
- **Flujo:** envía credenciales → backend valida (usuario existe, activo, verificado; bcrypt) → genera JWT (8 h) → devuelve `{user, token}` → el frontend guarda el token y navega según el rol.

### Registro

- **Quién lo usa:** público (estudiantes).
- **Qué puede hacer:** crear cuenta con datos personales y correo institucional.
- **Información que maneja:** nombre, correo institucional (único), contraseña (hash bcrypt), datos opcionales.
- **Flujo:** envía datos → backend crea usuario con rol `Estudiante`, `Verificado=0` → genera código de verificación → lo envía por correo → el usuario lo ingresa → backend lo valida y activa la cuenta. Utiliza un flujo de código numérico (OTP) de **8 dígitos** enviado al correo electrónico del estudiante a través de un servicio SMTP genérico. Este código es temporal (caduca en **5 minutos**) y se valida estrictamente en el backend.

### Usuarios y roles

- **Quién lo usa:** admin (gestión completa), el propio usuario (editar su perfil).
- **Qué puede hacer:** listar usuarios, **crear estudiantes y docentes** (`Nuevo estudiante` / `Nuevo docente`), editar, activar/desactivar, **dar de baja lógica**, cambiar estado (Activo · Limitado · Inactivo) y subir avatar.
- **Información que maneja:** todos los datos del usuario. La contraseña **nunca** se devuelve ni se muestra.
- **Flujo:** el admin crea o edita usuarios con rol y estado; el estudiante/docente edita su perfil. La baja es reversible y conserva el historial.
- **Validación:** campos obligatorios, documento y correo únicos; el docente no se repite en la misma asignación ni supera los topes configurados (**12 h/semana** y **12 emprendimientos**).

### Emprendimientos

- **Quién lo usa:** el **admin crea, aprueba y rechaza**; el docente consulta (los asignados). El prototipo **no incluye el alta por el estudiante**.
- **Qué puede hacer:** registrar un emprendimiento con propietario-estudiante desde el panel del Administrador; el estado inicial es **Pendiente**. El Administrador lo **aprueba o rechaza con motivo** y autoriza el **segundo emprendimiento paralelo**. Si un estudiante inicia un nuevo emprendimiento, el anterior no se sobrescribe.
- **Estados observados en el prototipo:** `Pendiente` · `Aprobado` · `Rechazado`, más la marca `EsParalelo`.
- **Información que maneja:** nombre, descripción, tipo, sector productivo, redes sociales (Instagram, WhatsApp, tienda propia), acompañamiento, acta de compromiso, etapa, propietario, fechas y estado de aprobación.
- **Flujo:** el admin crea el registro y revisa en la **bandeja de solicitudes** → aprueba o rechaza → el docente lo ve si tiene asignación; el estudiante lo ve si es el propietario.

### Asignaciones estudiante/docente/emprendimiento

- **Quién lo usa:** admin crea/elimina/reasigna; docente y estudiante consultan las propias.
- **Qué puede hacer:** vincular un docente (mentor) con un estudiante y opcionalmente un emprendimiento.
- **Información que maneja:** mentor, estudiante, emprendimiento, fecha, estado (activa/inactiva) y carga del docente.
- **Flujo:** el admin selecciona docente + estudiante (+ emprendimiento) y crea la asignación, o reasigna desde la tabla; el docente ve los emprendimientos asignados y el estudiante queda bajo su tutoría. La acción está disponible por enlace profundo (`#asignar-docente`).

### Consulta

- **Quién lo usa:** todos.
- **Qué puede hacer:** consultar recursos/entidades según su rol y alcance. Ver detalle de emprendimientos, usuarios, asignaciones. Todos los endpoints de listados implementan paginación desde el inicio.
- **Flujo:** cada consulta se filtra por rol y propiedad en backend.

### Seguimiento

- **Quién lo usa:** docente (crea/consulta/edita/elimina), admin (administra), estudiante (solo lectura).
- **Qué puede hacer:** registrar notas/avances de acompañamiento sobre un emprendimiento y **calificarlos** con puntaje y retroalimentación, asignándoles un estado de revisión.
- **Información que maneja:** descripción de la nota, tipo, **autor** (usuario), **emprendimiento** relacionado, fechas, **estado de revisión** (Pendiente · En revisión · Calificada · Devuelta), **puntaje** y **retroalimentación**.
- **Flujo:** el docente registra una nota/avance sobre un emprendimiento asignado (con puntaje y retroalimentación cuando la califica); el estudiante consulta el historial de su emprendimiento.

### Asesorías

- **Quién lo usa:** estudiante (solicita/consulta), docente (acepta/reprograma/crea/consulta), admin (**crea y asigna directamente**, consulta).
- **Qué puede hacer:** el estudiante **solicita**; el admin **crea y asigna** (emprendimiento, docente, fecha, horario y modalidad); el docente **acepta, rechaza o propone otra fecha**.
- **Información que maneja:** nombre, descripción, fecha, modalidad (Presencial · Virtual · Mixta), horario, lugar o enlace, estado, estudiante, docente.
- **Estados observados en el prototipo:** `Por agendar` · `Programada` · `Confirmada` · `En curso` · `Completada` · `Cancelada`.
- **Flujo:** el estudiante solicita **o** el admin crea la cita → el docente la ve y la acepta/reprograma → ambos consultan la agenda. El sistema envía notificaciones In-App accionables. El estudiante **no agenda por su cuenta** (R22/BR-002).

### Bandeja de solicitudes

- **Quién lo usa:** admin.
- **Qué puede hacer:** ver y resolver en un solo lugar **desbloqueos de cuenta**, **aprobaciones de emprendimiento (incluidos paralelos)** y **citas de asesoría**, con contador de pendientes.
- **Información que maneja:** tipo de solicitud, solicitante, fecha, estado y motivo de rechazo.
- **Flujo:** cada ítem se aprueba o rechaza con confirmación; el rechazo exige motivo y el sistema notifica al solicitante.

### Configuración del programa

- **Quién lo usa:** admin.
- **Qué puede hacer:** ajustar parámetros del programa (carga máxima por docente, emprendimientos máximos, cupos, sedes, etapas y notificaciones) y consultar la **bitácora** de cambios.
- **Información que maneja:** parámetros, valores anteriores/nuevos, autor y fecha.
- **Flujo:** el admin modifica y guarda; el cambio aplica a todo el programa y queda registrado.

### Respaldos y reportes

- **Quién lo usa:** admin.
- **Qué puede hacer:** consultar el **estado del respaldo** (último respaldo, tamaño, historial e integridad), **crear respaldo** y **exportar** la base en CSV/Excel; generar **reportes** institucionales en CSV, PDF o XLSX con filtros.
- **Información que maneja:** fecha y tamaño del respaldo, resultado de integridad, tipo de reporte y periodo.
- **Flujo:** el admin revisa el panel, exporta o genera el reporte; en el prototipo la descarga es simulada.
- **Restauración:** no forma parte de la interfaz del Administrador; es una **operación técnica** (`Fuera de alcance / Post-MVP`, AQ-04).

### Tareas / plan de trabajo

- **Quién lo usa:** docente (crea/edita/elimina/califica), estudiante (consulta y completa), admin (consulta).
- **Qué puede hacer:** crear tareas ligadas a un emprendimiento y a un estudiante, con fecha límite, prioridad y evidencia requerida; **calificarlas** (puntaje + retroalimentación) y **devolverlas** al estudiante.
- **Información que maneja:** título, descripción, fecha límite, estado, prioridad, evidencia requerida, puntaje, retroalimentación, emprendimiento, estudiante, docente.
- **Estados observados en el prototipo:** tarea `Pendiente` · `En curso` · `En revisión` · `Completada` · `Vencida` · `Devuelta`; revisión `Pendiente` · `En revisión` · `Calificada` · `Devuelta`; prioridad `Alta` · `Media` · `Baja`.
- **Flujo:** el docente crea la tarea → el estudiante la ve → la completa → el sistema calcula el avance (% de completadas). El docente puede calificarla (puntaje y retroalimentación) o devolverla al estudiante. El sistema notifica al usuario cuando un docente asigna una nueva tarea o la devuelve; la emisión en tiempo real queda pendiente (el prototipo solo simula la bandeja).

### Gestión de Archivos

El sistema soporta la subida, almacenamiento y descarga de archivos adjuntos (PDFs, imágenes de evidencia) de hasta **500 MB** para tareas, seguimientos y asesorías. Se almacenan localmente en el servidor (organizados en carpetas, con planes de migración a la nube futura para respetar el ciclo de vida de la información). Si se elimina el registro asociado (tarea, asesoría), el archivo se elimina físicamente del servidor.

### Dashboards

- **Quién lo usa:** todos.
- **Qué puede hacer:** mostrar métricas reales derivadas de la base de datos.
- **Información que maneja:** conteos y agregados (total usuarios, emprendimientos, asignaciones, tareas, asesorías, seguimientos; % de avance; distribución por etapa).
- **Flujo:** consulta de métricas por rol, filtradas por alcance.

### Progreso

- **Quién lo usa:** estudiante y docente.
- **Qué puede hacer:** visualizar el avance del emprendimiento por **fase del plan** y el % de tareas completadas.
- **Información que maneja:** fase actual del plan (`faseplan`), % de avance por fase y % de tareas completadas.
- **Fases observadas en el prototipo:** **FASE 1** Ideación y priorización de ideas · **FASE 2** Estructuración y ejecución · **FASE 3** Consolidación del proceso · **FASE 4** Escalamiento.
- **Flujo:** datos calculados a partir de la BD (fase y tareas).

### Eventos

- **Quién lo usa:** admin (crea/edita), usuarios (se registran/consultando).
- **Qué puede hacer:** crear eventos, registrar asistencia de usuarios. Activa para el MVP de eventos. Registrada y digitada manualmente por el Admin o el Docente.
- **Información que maneja:** nombre, descripción, tipo, modalidad, fecha/horario, capacidad, estado, participantes.
- **Flujo:** el admin crea el evento; el usuario se registra; se muestra la lista.

### Validación y activación del emprendedor

- **Quién lo usa:** el emprendedor (estudiante) y el personal administrativo (rol de apoyo, p. ej. la asesora del área de Emprendimiento).
- **Qué puede hacer:** el estudiante completa la información requerida; el administrativo **valida** al emprendedor y **activa** su acceso completo.
- **Información que maneja:** estado de validación/activación del usuario, responsable, fechas y observaciones.
- **Flujo:** inscripción → completar información → **notificación al administrativo** → programación de asesoría → reunión → **validación** → **activación** (habilitación de funcionalidades). El detalle está en la [§16](#16-fuentes-y-trazabilidad-del-alcance-ampliado).
- **Nota:** hasta no ser validado, el usuario opera en modo **limitado** (p. ej. el módulo de Diagnóstico permanece bloqueado). El **alcance exacto del acceso previo** es una [decisión pendiente](#11-decisiones-importantes).
- **Regla de suspensión:** 3 inasistencias a asesorías o 4 meses de incumplimiento → suspensión de 4 meses.

### Correo de bienvenida

- **Quién lo usa:** automático (lo dispara el backend) tras el registro.
- **Qué puede hacer:** enviar un **correo de bienvenida** al estudiante después de registrarse, con las instrucciones del proceso.
- **Flujo:** registro exitoso → el backend envía el correo vía SMTP (mismo canal que la verificación OTP).

### Diagnóstico, Caracterización y Valoración

- **Quién lo usa:** estudiante (diligencia), docente/admin y administrativo (consultan y descargan).
- **Qué puede hacer:** diligenciar el formulario de **caracterización y valoración**; **generar automáticamente** la caracterización y la **valoración/diagnóstico** a partir de las respuestas; consultar un **resumen**, **filtrar** y **descargar** un informe.
- **Información que maneja:** **banco de preguntas** (definido en un archivo **Excel**), respuestas, sector económico, resultados por sección, fortalezas y oportunidades de mejora.
- **Flujo:** el estudiante responde → el sistema genera el diagnóstico y muestra **feedback inmediato** (fortalezas / lo que falta) → el administrativo/docente consulta el resumen y descarga el informe.
- **Regla:** las preguntas **no se hardcodean**; se cargan desde el Excel (fuente única) y el diagnóstico se **deriva** de las respuestas ([§6](#6-reglas-de-negocio)).

### Acta de compromiso y confidencialidad

- **Quién lo usa:** estudiante (descarga, diligencia, firma y sube), administrativo/asesora (revisa y aprueba).
- **Qué puede hacer:** descargar la plantilla, subir el acta firmada y quedar en estado **en revisión**.
- **Información que maneja:** archivo del acta, estado (pendiente/en revisión/aprobada/rechazada), observaciones y fechas.
- **Flujo:** el estudiante descarga, firma y sube → queda **en revisión** → el administrativo aprueba o rechaza. El acta **aprobada** es **precondición para asignar docente** ([§6](#6-reglas-de-negocio)).
- **Vacío del prototipo:** **no existe vista de acta** en las 73 pantallas. `admin/asignaciones.html` exige que el acta de confidencialidad esté aceptada, pero no hay pantalla para descargarla, cargarla ni revisarla; el manejo del botón `ver-acta` es un manejador huérfano. Se documenta como pendiente ([§17.4](#173-vacíos-del-prototipo-que-no-se-inventan)).

### Notificaciones

- **Quién lo usa:** todos (destinatarios); el sistema las emite.
- **Qué puede hacer:** notificar al **personal administrativo** cuando el emprendedor completa el registro/la información, completa el diagnóstico, se crea un emprendimiento o se solicita una asesoría; y notificar al **estudiante** cuando lo validan, cambia el estado del acta, le asignan docente, le recomiendan un evento o le crean tareas/asesorías. Cada aviso es **accionable**: abre el objeto referido.
- **Información que maneja:** destinatario, tipo, mensaje, leída/no leída, fecha y enlace al objeto.
- **Flujo:** un evento dispara la notificación; el usuario la consulta, la abre y la marca como leída (individual o masivamente). El contador de no leídas refleja el estado real.
- **Alcance en el prototipo:** la bandeja existe con filtros **Todas · Sin leer · Tareas · Asesorías · Seguimiento** y preferencias de notificación (correo, sistema y recordatorio de tareas). **No hay emisión en tiempo real**: el envío está simulado y no existe WebSocket ni `Socket.io`.

---

## 4. Arquitectura propuesta

La nueva implementación es **desde cero** y no debe conservar estructuras innecesarias ni errores del proyecto anterior.

> **Diagramas (regenerados el 2026-10-25):** `docs/diagrama-clases.md` (en tres bloques), `docs/diagrama-componentes.md` y `docs/context-diagram.mmd` están alineados con el modelo vigente, el rol auditor, los servicios de solicitudes, configuración, respaldos y auditoría, y los procesos programados. Sus **PNG se regeneraron** desde el mismo Mermaid. Los `.drawio` anteriores siguen siendo **obsoletos**; la fuente de verdad es el archivo Mermaid/Markdown.
>
> **Modelo de datos:** el modelo objetivo es de **41 tablas = 27 de negocio + 14 catálogos**, descritas en la [sección 5](#5-modelo-de-datos). **No se declara un total de relaciones**: el "42" anterior no era trazable a partir de ningún listado. Las relaciones se leen por ficha y se garantizan con claves foráneas.

### Frontend

- Desarrollado utilizando **React** (SPA) con React Router. Totalmente responsive.
- Cliente API central (`api.js`) que agrega el header de autenticación y **maneja 401/403** (limpia token y redirige a login).
- Guardas de ruta (`PrivateRoute`) por rol.
- Sidebars/menús por rol (Admin, Docente, Estudiante).
- Gráficos con la librería disponible (p. ej. recharts), alimentados de datos reales de la API.

### Backend

- Desarrollado utilizando **Node.js** con Express.
- Arquitectura por capas: `routes` → `controllers` → `services` → BD.
- Middlewares: `authenticateToken`, `isAdmin`, `isTeacher`, `isStudent`.
- Consultas parametrizadas (evitar inyección SQL).
- Validación de entrada en cada endpoint.

### API REST

- Todos los endpoints de negocio bajo un prefijo (p. ej. `/segmed`) o `/api`.
- Respuestas JSON consistentes: `{ success, data }` o `{ success, error }`.
- Respuestas de rol/alcance: `401` sin token, `403` sin permiso, `404` no encontrado, `400` error de validación.

### Base de datos

- **PostgreSQL** (17), accedida mediante un pool de conexiones (`pg`).
- Inicialización mediante script SQL montado en la primera creación del contenedor. Sin scripts de migración. La base de datos será 100% limpia sin excepciones ni datos externos.
- Modelo definido en la [sección 5](#5-modelo-de-datos).

### Autenticación

- JWT firmado con secreto de entorno; expiración 8 h.
- Contraseñas con bcrypt (salt 10+).
- Verificación de correo real (código persistido y validado en BD).

### Comunicación frontend/backend

- HTTP/JSON.
- CORS restringido a orígenes permitidos (localhost de dev).
- El token viaja como `Authorization: Bearer <token>`.

### Estructura general de carpetas recomendada

```
SGEMD/
├── backend/
│   ├── src/
│   │   ├── config/            (db.config, mailer, jwt)
│   │   ├── middleware/        (auth.middleware, rol)
│   │   ├── routes/
│   │   ├── controllers/
│   │   ├── services/
│   │   └── app.js
│   ├── .env.example           (placeholders, sin secretos)
│   └── package.json
├── frontend/
│   ├── src/
│   │   ├── api/               (cliente API)
│   │   ├── components/        (UI compartida, layout, sidebars)
│   │   ├── pages/             (Admin/, Estudiante/, Maestro/, auth)
│   │   ├── routes/            (PrivateRoute)
│   │   ├── App.js
│   │   └── main.jsx
│   └── package.json
├── database/
│   ├── schema.sql             (modelo objetivo; sin secretos)
│   └── seed.sql               (opcional)
├── docker-compose.yml         (backend, frontend, postgres; variables de entorno)
├── .gitignore                 (.env, node_modules, __pycache__, *.log, uploads)
└── README.md                  (instalación, despliegue; sin credenciales reales)
```

---

## 5. Modelo de datos

> **Procedencia (2026-10-25):** este modelo se contrastó contra las 73 pantallas de `prototype/`: todo campo, estado y catálogo que muestra la interfaz tiene aquí su tabla o columna. Los vacíos detectados se registran en la [§17](#17-reconciliación-con-el-prototipo-2026-10-25).
>
> **Estado de implementación:** no existe `schema.sql`, ni PostgreSQL, ni migraciones en este repositorio. Esta sección es el **modelo objetivo** para el backend.
>
> **Convenciones:** `snake_case` en columnas nuevas; los nombres heredados en camelCase se conservan cuando ya estaban en uso, para no romper mapeos. Los catálogos son de solo lectura. Las columnas `Estado` usan los valores exactos del prototipo (enumerados en cada ficha).
>
> **Conteo declarado:** **41 tablas = 27 de negocio + 14 catálogos**. Ya **no se declara un total de relaciones**: el "42" anterior no era trazable (el desglose 16+13 suma 29 tablas, no 42 relaciones). Las relaciones se leen por ficha y se garantizan con claves foráneas.

### Catálogos (14, solo lectura)

| Tabla | PK | Valores observados en el prototipo | Propósito |
|---|---|---|---|
| `roles` | `idRoles` | 1=Admin · 2=Estudiante · 3=Docente · 4=Auditor (Post-MVP) | Rol del usuario |
| `tipodocumentos` | `idTipoDocumento` | CC · TI · CE | Tipo de documento |
| `programaacademico` | `idProgramaAcademico` | Ingeniería Industrial, etc. | Programa académico |
| `centrouniversitarios` | `idCentroUniversitarios` | Sede Norte · Sede Centro · Sede Sur | Sede / centro universitario |
| `municipios` | `idMunicipio` | Departamento + ciudad | Residencia |
| `tipopoblacion` | `idTipoPoblacion` | Población vulnerable | Caracterización |
| `tipousuarios` | `idTipoUsuarios` | Estudiante · Egresado · Docente · Administrativo | Tipo de usuario |
| `etapaemprendimiento` | `idEtapaEmprendimiento` | FASE 1 - Ideación · FASE 2 - Prototipo · FASE 3 - Validación · FASE 4 - Formalización | Etapa actual del emprendimiento |
| `faseplan` | `idFasePlan` | FASE 1 Ideación y priorización de ideas · FASE 2 Estructuración y ejecución · FASE 3 Consolidación del proceso · FASE 4 Escalamiento | Fase del plan de trabajo y de los avances |
| `sectoreconomico` | `idSectorEconomico` | Alimentos · Moda · Ambiental · Muebles · Tecnología · Comercio | Sector productivo |
| `modalidad` | `idModalidad` | Presencial · Virtual · Mixta | Modalidad de asesoría o evento |
| `tipo_evento` | `idTipo_evento` | Startup · Capacitación · Asesoría grupal · Showroom · Taller | Tipo de evento |
| `fecha_y_Horarios` | `idFecha_y_Horarios` | fecha · hora inicio · hora fin | Bloque de agenda |
| `modulos` | `idModulos` | Perfil · Emprendimiento · Diagnóstico · Tareas · Asesorías · Seguimiento · Eventos · Reportes | Módulo habilitable por persona |

> **Nota sobre fases:** el prototipo usa dos conceptos distintos. **Etapa** (`etapaemprendimiento`) es el avance global del emprendimiento (4 valores). **Fase del plan** (`faseplan`) es la agrupación de tareas y avances (4 valores). El detalle del emprendimiento usa alias cortos (*Ideación · Ejecución · Crecimiento · Consolidación*); deben normalizarse a `faseplan` en el próximo pase del prototipo (§17.4).

### Entidades de negocio (27)

> Las fichas de esta sección son **23 encabezados** que describen **27 tablas**: la ficha de `adjuntos` agrupa la tabla de adjuntos y sus **tres pivotes** (`adjuntos_tareas`, `adjuntos_seguimientos`, `adjuntos_asesorias`). El conteo 23 + 4 = 27 es el vigente.

#### `usuarios`

- **Propósito:** todas las cuentas (admin, docente, estudiante; auditor post-MVP).
- **Campos:**
  - Identidad: `idUsuarios`, `Codigo` (6 dígitos para estudiante, `DOC-###` para docente, `ADM-###` para admin), `Nombres`, `Apellidos`, `TipoDocumento`, `NumeroDocumento`, `FechaNacimiento`, `Genero`, `EstadoCivil`, `img_perfil`.
  - Contacto: `CorreoInstitucional` (único), `CorreoPersonal`, `Celular`, `Celular2`, `Telefono`, `Direccion`, `Departamento`, `Ciudad`.
  - Académicos: `NivelAcademico` (Pregrado · Posgrado · Egresado), `TipoPosgrado` (Especialización · Maestría · Doctorado), `Semestre`, `Modalidad`, `ProgramaAcademico`, `FechaGrado`, `ProgramaGrado`, `SedeGrado`, `NumeroActaDiploma`.
  - Docente: `AreaConocimiento`, `HorasAsesoriaSemana`, `EmprendimientosAsignados`.
  - Administrativo: `Cargo`, `ZonaHoraria`.
  - Seguridad y estado: `Password` (hash bcrypt, nunca se devuelve), `Verificado` (0/1), **`Estado`** (`Limitado` · `Activo` · `Inactivo`), `UltimaActividad` (base de los 90 días), `FechaCreacion`, `FechaActualizacion`.
- **FKs:** `Roles_idRoles`, `TipoDocumentos_idTipoDocumento`, `ProgramaAcademico_idProgramaAcademico`, `CentroUniversitarios_idCentroUniversitarios`, `Municipios_idMunicipio`, `TipoPoblacion_idTipoPoblacion`, `TipoUsuarios_idTipoUsuarios`.
- **Reglas:** el programa académico y el cargo los modifica el Administrador; el correo institucional no es editable por el usuario; el `Estado` solo lo cambia el Administrador (BR-003).
- **Relaciones:** 1→N emprendimientos (propietario), 1→N asignaciones (como mentor y como estudiante), 1→N seguimientos (autor), 1→N tareas, 1→N asesorías, 1→N notificaciones, 1→N habilitaciones, 1→N comentarios, 1→N adjuntos.

#### `emprendimiento`

- **Propósito:** emprendimiento estudiantil, con su estado de aprobación y su avance.
- **Campos:** `idEmprendimiento`, `Codigo` (`EMP-###`), `Nombre`, `Descripcion`, `TipoEmprendimiento`, `SectorProductivo`, `RedesSociales` (Instagram · WhatsApp · tienda), `Acompanamiento`, **`EstadoAprobacion`** (`Pendiente` · `Aprobado` · `Rechazado`), `MotivoRechazo`, `EsParalelo` (0/1), `Avance` (0–100, derivado de tareas), `ActaCompromiso` (campo heredado; el histórico vive en `actas`), `FechaCreacion`, `FechaActualizacion`.
- **FKs:** `EtapaEmprendimiento_idEtapaEmprendimiento`, `CentroUniversitarios_idCentroUniversitarios` (sede), `Usuarios_idUsuarios` (propietario).
- **Edición (BR-003):** el estudiante solo edita `Nombre`, `Descripcion` y `RedesSociales`; tipo, sector, etapa, acta y estado los administra el Administrador.
- **Relaciones:** Propietario 1→N; Etapa 1→N; Emprendimiento 1→N seguimientos, tareas, diagnósticos, actas, comentarios, recomendaciones; 0..1→N asignaciones; 1→N solicitudes.

#### `asignaciones`

- **Propósito:** vínculo docente ↔ estudiante ↔ emprendimiento.
- **Campos:** `idAsignacion`, `FechaAsignacion`, `Estado` (`activa` · `inactiva`), **`HorasSemanales`** (campo del modal "Horas semanales").
- **FKs:** `Usuarios_idMentor`, `Usuarios_idEstudiante`, `Emprendimiento_idEmprendimiento`.
- **Reglas:** solo el Admin crea, reasigna o desactiva. El docente no puede repetirse en la misma asignación ni superar los topes configurados (**12 h/semana** y **12 emprendimientos**, ambos configurables).
- **Relaciones:** Docente 1→N; Estudiante 1→N; Emprendimiento 0..1→N. Máximo una asignación activa por emprendimiento (R11).

#### `seguimientos`

- **Propósito:** registro de avance o comentario de acompañamiento del docente/admin.
- **Campos:** `idSeguimientos`, `Descripcion`, `TipoSeguimiento` (`Avance de fase` · `Comentario`), **`Fase`** (`faseplan`), **`Puntaje`** (0–100), **`EstadoRevision`** (`Pendiente` · `En revisión` · `Calificada` · `Devuelta`), `FechaCreacion`, `FechaActualizacion`.
- **FKs:** `Emprendimiento_idEmprendimiento` (obligatorio), `Usuarios_idUsuarios` (**autor**), `FasePlan_idFasePlan`.
- **Relaciones:** Emprendimiento 1→N; Autor 1→N; Seguimiento 0..N→N `adjuntos` (evidencia).

#### `tareas`

- **Propósito:** tarea del plan de trabajo, con prioridad, puntos y calificación.
- **Campos:** `idTareas`, `Titulo`, `Descripcion`, `FechaLimite`, **`Prioridad`** (`Alta` · `Media` · `Baja`), **`Puntos`** (máximo), `Estado` (`Pendiente` · `En curso` · `En revisión` · `Completada` · `Vencida` · `Devuelta`), **`PuntajeObtenido`**, **`Retroalimentacion`**, **`EstadoRevision`** (`Pendiente` · `En revisión` · `Calificada` · `Devuelta`), `EvidenciaRequerida` (0/1), **`MotivoDevolucion`**, `ObservacionesDevolucion`, `FechaCompletado`, `FechaCreacion`, `FechaActualizacion`.
- **FKs:** `Emprendimiento_idEmprendimiento`, `Usuarios_idUsuarios` (estudiante asignado), `Usuarios_idDocentes` (docente creador, opcional).
- **Reglas:** solo pasa a `Completada` con al menos una evidencia (BR-007); `Vencida` se deriva de `FechaLimite`; el docente puede calificar o devolver con motivo.
- **Relaciones:** Emprendimiento 1→N; Estudiante 1→N; Docente 1→N; Tarea 0..N→N `adjuntos`.

#### `asesorias`

- **Propósito:** sesión de acompañamiento, solicitada por el estudiante o creada por el Admin.
- **Campos:** `idAsesorias`, **`Tema`**, `Descripcion`, `Fecha_asesoria`, `Comentarios`, **`Estado`** (`Por agendar` · `Programada` · `Confirmada` · `En curso` · `Completada` · `Cancelada`), **`LugarEnlace`**, `Fecha_creacion`, `Fecha_actualizacion`.
- **FKs:** `Emprendimiento_idEmprendimiento` (**obligatoria**, para el expediente), `Usuarios_idUsuarios` (estudiante), `Usuarios_idDocentes` (docente), `Modalidad_idModalidad`, `Fecha_y_Horarios_idFecha_y_Horarios`.
- **Reglas:** el estudiante **solicita** y propone fecha; el Admin **crea y asigna**; el docente **acepta, rechaza o reprograma** (BR-002). El estudiante no agenda por su cuenta.
- **Relaciones:** Emprendimiento 1→N; Estudiante 1→N; Docente 1→N; Modalidad 1→N; Asesoría 0..N→N `adjuntos`.

#### `diagnosticos`

- **Propósito:** encabezado del diagnóstico de un emprendimiento.
- **Campos:** `idDiagnosticos`, `FechaDiagnostico`, `Estado` (`En progreso` · `Enviado` · `Revisado`), **`PuntajeTotal`**, **`UrlInforme`**.
- **FKs:** `Emprendimiento_idEmprendimiento`, `SectorEconomico_idSectorEconomico`.
- **Relaciones:** Emprendimiento 1→N; Diagnóstico 1→N respuestas; Diagnóstico 0..1→N caracterización/valoración.

#### `preguntas_diagnostico`

- **Propósito:** banco de 22 preguntas en 5 secciones (ver §3, Diagnóstico).
- **Campos:** `idPregunta`, `Seccion` (1–5), `Orden`, `Enunciado`, `Tipo` (`Texto` · `Selección` · `Número`), `Opciones`, `Activa`, `Origen` (`Excel` · `Prototipo`).
- **Estado:** el prototipo trae las 22 preguntas fijas; la carga desde Excel sigue pendiente (AQ-12).

#### `respuestas_diagnostico`

- **Campos:** `idRespuesta`, `Valor`, `FechaRespuesta`.
- **FKs:** `Preguntas_idPregunta`, `Diagnosticos_idDiagnosticos`.
- **Relaciones:** Pregunta 1→N; Diagnóstico 1→N.

#### `caracterizacion`

- **Propósito:** resultado estructurado por secciones (insumo del informe).
- **Campos:** `id`, `Seccion`, `Resultado`, `Puntaje`, `Fortalezas`, `Oportunidades`, `Fecha`, `UrlInforme`.
- **FKs:** `Emprendimiento_idEmprendimiento`, `Diagnosticos_idDiagnosticos` (opcional).

#### `valoracion`

- **Propósito:** resultado por dimensión de comportamiento emprendedor.
- **Campos:** `id`, `Dimension` (`Visión` · `Creatividad` · `Resiliencia` · `Liderazgo` · `Trabajo en equipo` · `Capacidad de decisión`), `Puntaje`, `Banda` (`90-100` · `70-89` · `50-69` · `<50`), `Recomendacion`, `Fecha`.
- **FKs:** `Emprendimiento_idEmprendimiento`, `Diagnosticos_idDiagnosticos` (opcional).
- **Estado:** la fórmula que convierte respuestas en puntajes sigue abierta (AQ-09).

#### `actas`

- **Propósito:** acta de compromiso y confidencialidad firmada y su revisión.
- **Campos:** `idActa`, `UrlArchivo`, **`Estado`** (`Pendiente` · `En revisión` · `Aprobada` · `Rechazada`), `Observaciones`, `FechaCarga`, `FechaRevision`.
- **FKs:** `Emprendimiento_idEmprendimiento`, `Usuarios_idRevisor` (opcional).
- **Reglas:** aprobada es precondición de asignación (BR-001); el rechazo exige motivo (BR-009). **No existe vista de acta en el prototipo** (§17.4).

#### `eventos`

- **Propósito:** eventos del programa y su publicación.
- **Campos:** `idEventos`, `Nombre_evento`, `Descripcion_evento`, **`DirigidoA`**, `Capacidad_maxima`, **`Cupo`**, **`Estado`** (`Pendiente` · `Aprobado` · `Rechazado` · `Publicado`), `Requiere_registro`, **`Lugar`**, **`Enlace`**, **`Organizador`**, `Fecha_creacion`, `Fecha_actualizacion`.
- **FKs:** `Tipo_evento_idTipo_evento`, `Modalidad_idModalidad`, `Fecha_y_Horarios_idFecha_y_Horarios`.
- **Relaciones:** Usuario N:N Evento (pivote); Evento 1→N recomendaciones.

#### `usuarios_has_Eventos`

- **Propósito:** inscripción y asistencia.
- **Campos:** `Usuarios_idUsuarios`, `Eventos_idEventos` (PK compuesta), `Estado_asistencia`, `FechaInscripcion`.

#### `codigosverificacion`

- **Propósito:** OTP de verificación de correo.
- **Campos:** `idCodigo`, `CorreoInstitucional`, `Codigo` (8 dígitos), `Expiracion` (5 minutos), `Usado` (0/1), `FechaCreacion`.
- **FKs:** `Usuarios_idUsuarios` (nullable hasta completar la verificación).
- **Nota:** AQ-11 exige el vínculo por `usuario_id`; se conserva el correo para el caso previo a la verificación.

#### `notificaciones`

- **Propósito:** aviso accionable dirigido a un usuario.
- **Campos:** `idNotificaciones`, `Tipo` (`Tarea` · `Asesoría` · `Seguimiento` · `Solicitud` · `Diagnóstico` · `Evento` · `Sistema`), `Mensaje`, **`Url`**, **`TipoObjeto`**, **`ObjetoId`**, `Leida` (0/1), `FechaCreacion`.
- **FKs:** `Usuarios_idUsuarios` (**destinatario**).
- **Reglas:** el contador de no leídas debe reflejar el estado real; marcar como leída no elimina el aviso (FR-019).

#### `habilitaciones`

- **Propósito:** desbloqueo de módulos por persona tras la validación.
- **Campos:** `idHabilitacion`, `Estado` (`habilitado` · `no habilitado`), `Fecha`.
- **FKs:** `Usuarios_idUsuarios`, `Modulos_idModulos`.
- **Estado:** el prototipo no tiene pantalla de habilitaciones; la bandeja de desbloqueo y el estado `Limitado` son la evidencia disponible.

#### `comentarios`

- **Propósito:** bitácora de comentarios del expediente (visible en la pestaña *Comentarios*).
- **Campos:** `idComentario`, `Texto`, `Fecha`.
- **FKs:** `Emprendimiento_idEmprendimiento`, `Usuarios_idUsuarios` (autor).
- **Relaciones:** Emprendimiento 1→N; Autor 1→N.

#### `recomendaciones_evento`

- **Propósito:** recomendación de un evento a un emprendimiento completo o a estudiantes concretos.
- **Campos:** `idRecomendacion`, `Mensaje`, `Estado` (`Enviada` · `Leída`), `Fecha`.
- **FKs:** `Eventos_idEventos`, `Emprendimiento_idEmprendimiento`, `Usuarios_idEstudiante` (opcional si va a todo el grupo), `Usuarios_idDocente` (autor).
- **Reglas:** el docente solo recomienda a sus asignados; la recomendación notifica al estudiante (FR-021).

#### `solicitudes`

- **Propósito:** bandeja única del Administrador (desbloqueos, paralelos y citas).
- **Campos:** `idSolicitud`, `Tipo` (`Desbloqueo` · `Paralelo` · `Cita`), `Detalle`, `Estado` (`Pendiente` · `Aprobada` · `Rechazada`), `MotivoRechazo`, `FechaSolicitud`, `FechaResolucion`.
- **FKs:** `Usuarios_idUsuarios` (solicitante), `Emprendimiento_idEmprendimiento` (opcional), `Usuarios_idResueltoPor` (opcional).
- **Reglas:** toda resolución notifica al solicitante; el rechazo exige motivo y no se confirma con el campo vacío (FR-014).

#### `configuracion_programa`

- **Propósito:** parámetros centralizados del programa (FR-020).
- **Campos:** `idConfiguracion`, `Clave`, `Valor`, `TipoDato`, `Descripcion`, `FechaActualizacion`.
- **FKs:** `Usuarios_idUsuarios` (actualizado por).
- **Claves observadas:** `carga_max_horas` (12), `max_emprendimientos_docente` (12), `sede_por_defecto`, `etapa_inicial`, `fecha_cierre_admisiones`, `cupos_por_sede` (40), `notif_desbloqueo`, `notif_paralelo`, `notif_tarea_vencida`, `notif_resumen_semanal`.

#### `respaldos`

- **Propósito:** historial y estado de las copias de seguridad (FR-018).
- **Campos:** `idRespaldo`, **`Codigo`** (`BKP-YYYYMMDD-HHMM`), **`Tipo`** (`Completo` · `Parcial`), `FechaHora`, **`TamanoMB`**, **`Estado`** (`Exitosa` · `Fallida`), **`Destino`**, `RetencionDias`.
- **FKs:** `Usuarios_idUsuarios` (generado por).
- **Reglas:** la restauración es operación técnica, fuera de la interfaz (AQ-04). Frecuencia observada: diaria 09:00, retención 30 días.

#### `adjuntos` y sus tres pivotes

- **`adjuntos`:** `idAdjunto`, `NombreArchivo`, `RutaArchivo`, `TamanoBytes`, `TipoMime`, `FechaSubida`.
- **FKs:** `Usuarios_idUsuarios` (subido por).
- **Pivotes:** `adjuntos_tareas`, `adjuntos_seguimientos`, `adjuntos_asesorias` (PK compuesta con el adjunto y la entidad).
- **Reglas:** borrado lógico y reversible del registro; **borrado físico en cascada** del archivo (BR-006); el límite de 500 MB es un requisito de backend, no está representado en el prototipo.

#### `auditoria_eventos`

- **Propósito:** trazabilidad de operaciones sensibles (NFR-007).
- **Campos:** `idAuditoria`, `Accion` (`crear` · `editar` · `eliminar` · `aprobar` · `rechazar` · `exportar` · `consultar`), `Entidad`, `EntidadId`, `ValorAnterior` (jsonb), `ValorNuevo` (jsonb), `Fecha`, `Ip`.
- **FKs:** `Usuarios_idUsuarios` (autor).
- **Reglas:** la bitácora visible en `admin/configuracion.html` es su representación de interfaz.

### Cobertura: datos del prototipo que ahora sí tienen tabla o columna

| Elemento visible en el prototipo | Dónde queda modelado |
|---|---|
| Códigos `EMP-###`, `DOC-###`, `912646`, `BKP-…` | `emprendimiento.Codigo`, `usuarios.Codigo`, `respaldos.Codigo` |
| Estado de aprobación del emprendimiento y paralelo | `emprendimiento.EstadoAprobacion`, `EsParalelo`, `solicitudes` |
| Prioridad, puntos, puntaje, retroalimentación y devolución de tareas | `tareas` |
| Puntaje y estado de revisión de avances | `seguimientos` |
| Bitácora de comentarios del expediente | `comentarios` |
| Recomendación de eventos por grupo o estudiante | `recomendaciones_evento` |
| Bandeja de desbloqueos, paralelos y citas | `solicitudes` |
| Parámetros del programa y su bitácora | `configuracion_programa` + `auditoria_eventos` |
| Historial y estado de respaldos | `respaldos` |
| Notificación que abre el objeto referido | `notificaciones.Url`, `TipoObjeto`, `ObjetoId` |
| 6 dimensiones y 4 bandas del diagnóstico | `valoracion` |
| 5 secciones y 22 preguntas del instrumento | `preguntas_diagnostico` + `respuestas_diagnostico` |
| Sedes, cupos y etapa inicial | catálogos + `configuracion_programa` |

### Tablas del proyecto anterior consideradas **obsoletas / no necesarias para el MVP**

- `evaluacioneshabilidades` — evaluación de habilidades no implementada en el flujo principal del MVP.
- `solicitudestutoria` — duplica la funcionalidad de asesorías (la bandeja vigente es `solicitudes`).
- Tablas no relacionadas con el flujo principal deben descartarse en la reconstrucción.

---

## 6. Reglas de negocio

**Registros / usuarios**

- R1: la contraseña siempre se almacena con bcrypt; nunca se devuelve ni se muestra.
- R2: un usuario no verificado (`Verificado=0`) o con `Estado` distinto de `Activo` (es decir, `Limitado` o `Inactivo`) no debe operar los módulos que requieren validación.
- R3: solo el propio usuario o un admin puede ver/editar los datos personales.

**Emprendimientos**

- R4: un estudiante solo consulta sus emprendimientos (`Usuarios_idUsuarios = yo`).
- R5: un docente solo consulta los emprendimientos que le fueron asignados (vía `asignaciones`).
- R6: un admin consulta todos.
- R7: el emprendimiento tiene un propietario estudiante y una etapa.
- R8: crea/edita/elimina emprendimiento el **admin** (el estudiante puede editar ciertos datos, decisión de diseño).

**Asignaciones**

- R9: solo el admin crea/elimina/reasigna asignaciones.
- R10: un docente ve solo sus asignaciones; un estudiante solo las suyas.
- R11: una asignación activa vincula un mentor a un estudiante (y opcionalmente un emprendimiento). Un estudiante debe tener como máximo una asignación **activa** por emprendimiento.

**Seguimiento**

- R12: un seguimiento pertenece a un emprendimiento (`Emprendimiento_idEmprendimiento`).
- R13: un emprendimiento puede tener múltiples seguimientos (cardinalidad 1:N).
- R14: crea seguimiento solo el docente asignado o el admin; el **autor** se registra automáticamente.
- R15: el estudiante puede consultar (lectura) el seguimiento de su emprendimiento.
- R16: editar/eliminar un seguimiento solo el autor o admin.

**Etapas y fases**

- R17: el sistema maneja **dos catálogos de fase distintos** y no deben confundirse:
  1. **Etapa del emprendimiento** (`etapaemprendimiento`): `FASE 1 - Ideación` · `FASE 2 - Prototipo` · `FASE 3 - Validación` · `FASE 4 - Formalización`. Es un catálogo cerrado; el emprendimiento apunta a una etapa y la etapa **no** es un tipo de seguimiento.
  2. **Fase del plan** (`faseplan`): `FASE 1` Ideación y priorización de ideas · `FASE 2` Estructuración y ejecución · `FASE 3` Consolidación del proceso · `FASE 4` Escalamiento. Agrupa tareas y avances.
  - El detalle del emprendimiento usa alias cortos (*Ideación · Ejecución · Crecimiento · Consolidación*) que deben normalizarse a `faseplan`; se registran como deuda del prototipo ([§17.4](#173-vacíos-del-prototipo-que-no-se-inventan)).

**Tareas**

- R18: crea tareas el docente/admin; las completa el estudiante asignado.
- R19: estados de tarea `Pendiente` · `En curso` · `En revisión` · `Completada` · `Vencida` · `Devuelta`; la tarea se auto-marca **Vencida** por fecha límite y pasa a **En revisión** cuando el estudiante la entrega.
- R19b: la tarea tiene **prioridad** (`Alta` · `Media` · `Baja`) y **puntos**; el docente registra **puntaje obtenido** y **retroalimentación**, y el **estado de revisión** es `Pendiente` · `En revisión` · `Calificada` · `Devuelta`.
- R20: estudiante ve sus tareas; docente las de sus asignados; admin todas.
- R21: el avance (% de completadas) es un dato **derivado de BD**, no sintético.

**Asesorías**

- R22: el estudiante **solicita** la asesoría; el **admin puede crearla y asignarla directamente**; el **docente la acepta, la rechaza o propone otra fecha**. El estudiante no agenda por su cuenta. Edita/elimina el autor o el admin.
- R23: consulta filtrada por rol.

**Autorización general**

- R24: todo endpoint de negocio valida autenticación y rol en backend.
- R25: el alcance (propiedad) se valida en backend, no solo en la UI.

**Validación y activación**

- R26: la **validación del emprendedor** por el administrativo es **condición** para habilitar el acceso completo (ver [§16](#16-fuentes-y-trazabilidad-del-alcance-ampliado)).
- R27: solo un usuario autorizado (admin/administrativo) puede validar, activar o rechazar a un emprendedor.
- R28: el **acta de compromiso aprobada** es **precondición** para asignar docente.
- R29: 3 inasistencias a asesorías o 4 meses de incumplimiento → suspensión de 4 meses.

**Diagnóstico**

- R30: las preguntas del diagnóstico provienen del **banco de preguntas** (Excel); **no se hardcodean**.
- R31: el diagnóstico/caracterización/valoración se **deriva** de las respuestas; **no** se digita a mano.

**Notificaciones**

- R32: se notifica al **administrativo** ante registro/información, diagnóstico y solicitud de asesoría; y al **estudiante** ante validación, cambio de estado del acta y creación de tareas/asesorías. Cada notificación es **accionable** y puede marcarse como leída.

**Cuentas y usuarios**

- R33: el **Administrador** es el único que puede **crear, editar y dar de baja lógica** cuentas de estudiante y docente; el alta asigna el rol y el estado inicial.
- R34: los estados de cuenta son **Limitado → Activo → Inactivo**. Solo el Administrador desbloquea (Limitado → Activo) y reactiva (Inactivo → Activo).
- R35: toda alta o edición valida **campos obligatorios**, **documento y correo únicos** y **ambos topes de carga docente**: **12 h de asesoría por semana** y **12 emprendimientos**. Los dos son parámetros del programa (`configuracion_programa`) y pueden cambiarse desde `admin/configuracion.html`; un valor no sustituye al otro.
- R36: la **baja es lógica y reversible**; al eliminar un emprendimiento o usuario, sus **archivos adjuntos se eliminan en cascada**.

**Emprendimientos y solicitudes**

- R37: el emprendimiento nace en **Pendiente** y solo el Administrador lo pasa a **Aprobado** o **Rechazado** (con motivo). El **segundo emprendimiento paralelo** requiere autorización expresa. El **alta la realiza el Administrador**: el prototipo no incluye un formulario de registro de emprendimiento para el estudiante ([§17.4](#173-vacíos-del-prototipo-que-no-se-inventan)).
- R38: la **bandeja de solicitudes** concentra desbloqueos, aprobaciones/paralelos y citas; toda resolución notifica al solicitante y el rechazo exige motivo. **El prototipo no valida que el motivo esté diligenciado** al confirmar un rechazo: es un defecto conocido del prototipo ([§17.3](#172-contradicciones-que-el-prototipo-introduce-y-cómo-se-resuelven)).

**Seguimiento y evidencia**

- R39: una tarea solo pasa a **Completada** si el estudiante adjuntó **al menos un archivo de evidencia**.
- R40: "Registrar avance" y "Revisar diagnóstico" existen para **Administrador y Docente**; es una **duplicidad intencional**, no un defecto. El docente conserva la autoría de su avance.

**Respaldos y configuración**

- R41: solo el Administrador puede **exportar la base**, **crear respaldos**, consultar su **estado/integridad** y modificar la **configuración del programa**; todo cambio de configuración queda en la **bitácora**.

**Avances, comentarios y recomendaciones**

- R42: el **avance** (`seguimientos`) se registra con **fase del plan**, **puntaje 0–100**, **estado de revisión** y **evidencia**; el docente puede dejarlo en `Pendiente`, `En revisión`, `Calificada` o `Devuelta`.
- R43: el **expediente** tiene una **bitácora de comentarios** visible para admin y docente asignado; el autor se registra automáticamente y el estudiante la consulta en solo lectura.
- R44: el **docente recomienda eventos** solo a estudiantes o emprendimientos que tenga asignados; cada recomendación genera una notificación accionable.
- R45: la **prioridad** de una tarea (`Alta` · `Media` · `Baja`) es un campo obligatorio y se usa para ordenar la bandeja del estudiante.

**Bitácora y auditoría**

- R46: toda operación sensible (alta, edición, baja, aprobación, rechazo, exportación) registra **autor, fecha, entidad, valor anterior y valor nuevo** en `auditoria_eventos`. La "bitácora de decisiones" de `admin/configuracion.html` es su representación de interfaz, no una tabla independiente.

---

## 7. API

> Definición de endpoints por módulo. Para cada uno: método, ruta, rol, propósito, entrada y respuesta. No es código completo. Respuestas en JSON `{success, data}` / `{success, error}`. `auth` = requiere `authenticateToken`.

### auth

| Método | Ruta             | Rol     | Propósito                       | Entrada                                      | Respuesta                  |
| ------ | ---------------- | ------- | ------------------------------- | -------------------------------------------- | -------------------------- |
| POST   | `/auth/register` | student | Crear usuario (Estudiante)      | nombre, correo, contraseña, datos opcionales | `{success, user, message}` |
| POST   | `/auth/verify`   | student | Validar código y activar correo | correo, codigo                               | `{success, message}`       |
| POST   | `/auth/login`    | student | Iniciar sesión                  | correo, contraseña                           | `{success, user, token}`   |
| POST   | `/auth/logout`   | auth    | Cerrar sesión                   | —                                            | `{success}`                |

### users

| Método | Ruta                    | Rol                 | Propósito                   |
| ------ | ----------------------- | ------------------- | --------------------------- |
| GET    | `/users/me`             | auth                | Perfil propio               |
| GET    | `/users`                | auth                | Listar usuarios (según rol) |
| GET    | `/users/students`       | auth                | Listar estudiantes          |
| GET    | `/users/teachers`       | auth                | Listar docentes             |
| GET    | `/users/:id`            | auth (propio/admin) | Obtener usuario             |
| PUT    | `/users/:id`            | auth (propio/admin) | Editar perfil               |
| DELETE | `/users/:id`            | admin o propio      | Desactivar (soft)           |
| POST   | `/users/admin`          | admin               | Crear usuario como admin    |
| POST   | `/users/:id/reactivate` | admin               | Reactivar                   |
| POST   | `/users/:id/avatar`     | auth (propio/admin) | Subir avatar                |

### entrepreneurship

| Método | Ruta                    | Rol                   | Propósito                                                   |
| ------ | ----------------------- | --------------------- | ----------------------------------------------------------- |
| GET    | `/entrepreneurship`     | auth (filtra por rol) | Listar (admin todos, docente asignados, estudiante propios) |
| GET    | `/entrepreneurship/:id` | auth (alcance)        | Detalle                                                     |
| POST   | `/entrepreneurship`     | admin                 | Crear                                                       |
| PUT    | `/entrepreneurship/:id` | admin (o propietario) | Editar                                                      |
| DELETE | `/entrepreneurship/:id` | admin                 | Eliminar                                                    |

### assignments

| Método | Ruta                          | Rol               | Propósito                   |
| ------ | ----------------------------- | ----------------- | --------------------------- |
| GET    | `/assignments`                | auth (filtra rol) | Listar asignaciones         |
| GET    | `/assignments/mentor/:id`     | auth              | Asignaciones por docente    |
| GET    | `/assignments/estudiante/:id` | auth              | Asignaciones por estudiante |
| GET    | `/assignments/:id`            | auth              | Detalle                     |
| POST   | `/assignments`                | admin             | Crear asignación            |
| PUT    | `/assignments/:id`            | admin             | Reasignar/actualizar        |
| DELETE | `/assignments/:id`            | admin             | Desactivar                  |

### tracing (seguimiento)

| Método | Ruta                             | Rol                | Propósito                            |
| ------ | -------------------------------- | ------------------ | ------------------------------------ |
| GET    | `/tracing/emprendimiento/:empId` | auth (alcance)     | Historial de un emprendimiento       |
| GET    | `/tracing/:id`                   | auth (alcance)     | Detalle                              |
| POST   | `/tracing`                       | teacher/admin      | Crear seguimiento (autor = req.user) |
| PUT    | `/tracing/:id`                   | auth (autor/admin) | Editar                               |
| DELETE | `/tracing/:id`                   | auth (autor/admin) | Eliminar                             |

### advice (asesorías)

| Método | Ruta          | Rol               | Propósito        |
| ------ | ------------- | ----------------- | ---------------- |
| GET    | `/advice`     | auth (filtra rol) | Listar           |
| GET    | `/advice/:id` | auth (alcance)    | Detalle          |
| POST   | `/advice`     | estudent/teacher  | Crear/solicitar  |
| PUT    | `/advice/:id` | autor/admin       | Editar/confirmar |
| DELETE | `/advice/:id` | autor/admin       | Eliminar         |

### tareas

| Método | Ruta                                    | Rol                        | Propósito                     |
| ------ | --------------------------------------- | -------------------------- | ----------------------------- |
| GET    | `/task`                                 | auth (filtra rol)          | Listar                        |
| GET    | `/task/my-task`                         | auth                       | Tareas del usuario + vencidas |
| GET    | `/task/entrepreneurship/:empId`         | auth                       | Tareas por emprendimiento     |
| GET    | `/task/advance/entrepreneurship/:entId` | auth                       | % avance (derivado)           |
| POST   | `/task`                                 | docente/admin              | Crear                         |
| PUT    | `/task/:id`                             | teacher/admin              | Editar                        |
| PUT    | `/task/:id/completar`                   | auth (estudiante asignado) | Completar                     |
| DELETE | `/task/:id`                             | teacher/admin              | Eliminar                      |

### diagnosis

| Método | Ruta             | Rol           | Propósito                |
| ------ | ---------------- | ------------- | ------------------------ |
| GET    | `/diagnosis`     | auth          | Listar                   |
| GET    | `/diagnosis/me`  | auth          | Diagnósticos del usuario |
| GET    | `/diagnosis/:id` | auth          | Detalle                  |
| POST   | `/diagnosis`     | teacher/admin | Crear                    |
| PUT    | `/diagnosis/:id` | teacher/admin | Editar                   |
| DELETE | `/diagnosis/:id` | teacher/admin | Eliminar                 |
| GET    | `/diagnosis/form`      | auth          | Banco de preguntas (secciones, desde Excel) |
| POST   | `/diagnosis/me`        | student       | Enviar respuestas y generar diagnóstico     |
| GET    | `/diagnosis/:id/report` | auth (alcance) | Informe descargable (PDF)                  |
| GET    | `/characterization/me` | auth          | Caracterización/valoración del emprendedor  |

### validación y activación

| Método | Ruta                     | Rol                    | Propósito                            |
| ------ | ------------------------ | ---------------------- | ------------------------------------ |
| POST   | `/users/:id/validate`    | admin/administrativo   | Validar y **activar** al emprendedor |
| POST   | `/users/:id/reject`      | admin/administrativo   | Rechazar la validación               |
| POST   | `/acta`                  | auth (estudiante)      | Subir el acta firmada                |
| GET    | `/acta/:id`              | auth (alcance)         | Consultar estado del acta            |
| PUT    | `/acta/:id/review`       | admin/administrativo   | Aprobar/rechazar el acta             |

### notificaciones

| Método | Ruta                        | Rol  | Propósito                  |
| ------ | --------------------------- | ---- | -------------------------- |
| GET    | `/notifications`            | auth | Listar notificaciones propias |
| PUT    | `/notifications/:id/read`   | auth | Marcar como leída          |
| PUT    | `/notifications/read-all`   | auth | Marcar todas como leídas   |

### solicitudes (bandeja única)

> Reemplaza la práctica de resolver desbloqueos, paralelos y citas por rutas sueltas. La UI existe en `admin/solicitudes.html`; el backend no.

| Método | Ruta | Rol | Propósito |
| ------ | ---- | --- | --------- |
| GET | `/requests` | admin | Listar por tipo y estado, con contador de pendientes |
| GET | `/requests/:id` | admin | Detalle de la solicitud |
| POST | `/requests` | auth | Crear solicitud (desbloqueo, paralelo o cita) |
| PUT | `/requests/:id/approve` | admin | Aprobar y aplicar el efecto |
| PUT | `/requests/:id/reject` | admin | Rechazar con **motivo obligatorio** |

### configuración del programa

| Método | Ruta | Rol | Propósito |
| ------ | ---- | --- | --------- |
| GET | `/settings` | admin | Leer parámetros (`carga_max_horas`, `max_emprendimientos_docente`, `cupos_por_sede`, sedes, etapa inicial) |
| PUT | `/settings` | admin | Actualizar parámetros; registra autor, valor anterior y valor nuevo |
| GET | `/settings/audit` | admin | Bitácora de cambios de configuración |

### respaldos

| Método | Ruta | Rol | Propósito |
| ------ | ---- | --- | --------- |
| GET | `/backups` | admin | Historial (código, tipo, fecha, tamaño, estado) |
| POST | `/backups` | admin | Solicitar un respaldo |
| GET | `/backups/:id/download` | admin | Descargar la copia |
| GET | `/backups/:id` | admin | Detalle e integridad |

### comentarios y recomendaciones

| Método | Ruta | Rol | Propósito |
| ------ | ---- | --- | --------- |
| GET | `/entrepreneurship/:id/comments` | auth (alcance) | Bitácora de comentarios del expediente |
| POST | `/entrepreneurship/:id/comments` | teacher/admin | Registrar comentario (autor = `req.user`) |
| GET | `/events/:id/recommendations` | auth (alcance) | Recomendaciones del evento |
| POST | `/events/:id/recommendations` | teacher/admin | Recomendar a un estudiante o a todo el emprendimiento |

### dashboard

| Método | Ruta                 | Rol        | Propósito               |
| ------ | -------------------- | ---------- | ----------------------- |
| GET    | `/dashboard/admin`   | admin      | Métricas globales       |
| GET    | `/dashboard/teacher` | docente    | Métricas del docente    |
| GET    | `/dashboard/student` | estudiante | Métricas del estudiante |

### Catálogos (solo lectura; proteger según conveniencia)

| Método | Ruta                                                                                                                                                                                | Propósito        |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| GET    | `/roles`, `/type-doc`, `/type-users`, `/uni-centers`, `/type-pop`, `/municipalities`, `/academic-programs`, `/entrep-stage`, `/plan-phase`, `/econo-sector`, `/mode`, `/type-event`, `/date-times`, `/modules` | Listar los 14 catálogos |

### event (si aplica)

| Método | Ruta                  | Rol  | Propósito             |
| ------ | --------------------- | ---- | --------------------- |
| GET    | `/event`              | auth | Listar eventos        |
| POST   | `/event/:id/register` | auth | Registrarse en evento |
| DELETE | `/event/:id/register` | auth | Desregistrarse        |

### Auditor (rol 4) — solo lectura

> El rol auditor **no existe en el prototipo** (`Fuera de alcance / Post-MVP`). Los endpoints se documentan para cuando se implemente el backend.

| Método | Ruta | Rol | Propósito | Restricción |
| ------ | ---- | --- | --------- | ----------- |
| GET | `/audit/dashboard` | auditor | Consultar métricas agregadas | Solo lectura; sin datos personales completos |
| GET | `/audit/reports` | auditor | Listar reportes disponibles | Solo lectura |
| GET | `/audit/reports/:id/export` | auditor | Exportar un reporte | Exportación; sin edición |
| GET | `/audit/expedientes` | auditor | Consultar expedientes consolidados | Solo lectura; campos sensibles enmascarados |

**Reglas:** ninguna ruta del auditor acepta `POST`, `PUT`, `PATCH` ni `DELETE`. La autorización se valida en backend (NFR-002) y toda consulta o exportación queda registrada (NFR-007).

---

## 8. Frontend

### Administrador

> **19 pantallas** verificadas en `prototype/admin/` y enlazadas desde `prototype/index.html`.

| Pantalla | Información que debe mostrar |
| --- | --- |
| Dashboard | Métricas globales reales: total usuarios (por rol), emprendimientos, asignaciones activas, tareas, asesorías; distribución de emprendimientos por etapa. |
| Usuarios | Dos tablas (estudiantes y docentes) con búsqueda y filtro por estado; **Nuevo estudiante** / **Nuevo docente**; editar, **dar de baja** y cambiar estado (Activo · Limitado · Inactivo). |
| Solicitudes | Bandeja única con pestañas **Desbloqueos · Paralelos · Citas**, contador de pendientes, aprobar/rechazar con confirmación y motivo. |
| Emprendimientos | Lista de todos los emprendimientos con filtros; ver detalle, editar datos/etapa y acceder a la asignación. |
| Expediente del emprendimiento | Vista consolidada por pestañas: avances, asesorías, diagnóstico, comentarios y evidencias; acciones de exportar y abrir plan/seguimiento. |
| Plan de trabajo del emprendimiento | Plan agrupado por fases, con tareas, estado y avance. |
| Asignaciones | Crear/ver/eliminar/reasignar asignaciones (docente + estudiante + emprendimiento); enlace profundo `#asignar-docente`. |
| Seguimiento | Registro y consulta de avances del emprendimiento, con autor, fecha, estado de revisión y evidencia. |
| Tablero de seguimiento | Vista agregada del avance por emprendimiento y fase para el administrador. |
| Tareas | Tareas de todos los emprendimientos con filtros; ver detalle y estado de calificación. |
| Asesorías | Agenda global con filtros por estado, docente y emprendimiento; crear y asignar directamente. |
| Diagnósticos | Banco de preguntas (Excel), resumen del diagnóstico, filtros e **informe descargable**. |
| Eventos | Lista y tablero de eventos con tipo, modalidad, fecha, capacidad y estado. |
| Evento (formulario) | Alta/edición de evento: nombre, descripción, tipo, modalidad, fecha, capacidad y participantes. |
| Reportes | Generación y descarga de reportes institucionales en CSV, PDF o XLSX, con tipo y periodo. |
| Respaldos | Estado del respaldo (último respaldo, tamaño, historial, integridad), crear respaldo y exportar la base. |
| Notificaciones | Bandeja con filtros por tipo, contador de no leídas, abrir el objeto referido y **marcar todo como leído**. |
| Perfil | Datos propios del admin y acceso a cambiar contraseña. |
| Configuración | Parámetros del programa (carga docente, cupos, sedes, etapas, notificaciones), cuenta del administrador y bitácora de cambios. |

### Docente / Mentor

Las acciones del docente son **vistas completas**, no ventanas emergentes (solo *Marcar todo como leído* conserva un diálogo de confirmación).

| Pantalla | Información que debe mostrar |
| --- | --- |
| Dashboard (Inicio) | Panorama de sus asignados: nº estudiantes, emprendimientos asignados, % avance de tareas, próximas asesorías; accesos rápidos que **enlazan** a las vistas de registrar avance, calificar, revisar diagnóstico y **generar asesoría**. Los pendientes enlazan a la lista ya filtrada (`?f=`). |
| Emprendimientos asignados | Solo los emprendimientos en los que es mentor (vía asignaciones), con su etapa, avance, **estado de revisión** y **evidencia**; modelo N:N (un emprendimiento puede tener varios estudiantes), vista Tarjetas/Tabla con filtros de etapa/sector/**evidencia**. Un **selector de estudiante** muestra sus emprendimientos como **pestañas**. |
| Expediente del emprendimiento | Detalle con pestañas Avances · Tareas · Asesorías · Diagnóstico · Comentarios; tarjeta de **estudiantes del grupo** y **bitácora de comentarios** (autor · fecha · texto), con enlaces a las vistas de avance y de asesoría. |
| Detalle del avance | Vista completa de un avance: descripción, **evidencia adjunta**, datos, historial y acciones de edición. |
| Registrar avance | **Vista completa** (formulario-página) con emprendimiento, fase, fecha, descripción, **estado de revisión** (Pendiente · En revisión · Calificada · Devuelta), **puntaje** (0–100) y evidencia. |
| Diagnóstico | **Vista completa** con **selector de emprendimiento** y **filtros por estudiante/proyecto**; el diagnóstico se calcula por **completación de las 4 fases** o por una **serie de tareas clave**; incluye avance por fases. |
| Revisión del diagnóstico | Resultado del diagnóstico con **recomendaciones** del docente, resumen y tabla de pendientes de revisión. |
| Asesorías | **Una sola tabla** con **filtro de estado agrupado** (*Por agendar · Agendada · Completada · Cancelada*) y filtros por **estudiante**/emprendimiento; cada fila abre el **detalle de asesoría**. |
| Detalle de asesoría | Vista completa de la solicitud: datos, agenda, estudiantes agendados y acciones **Confirmar y notificar**, **Proponer otra fecha** y **Rechazar solicitud**. |
| Registrar asesoría | **Vista completa** para agendar por **emprendimiento** (anexa a **todo su grupo**): **tema por defecto** (*FASE 2 - Prototipo: empaque*, *Tarea: …*), **fecha/hora disponible**, modalidad y **descripción de necesidades**. Refleja el flujo del estudiante (BR-002: el estudiante no agenda solo). |
| Tareas | Tareas de sus asignados con filtros por estado/prioridad; **asignar tarea** (`tarea-form.html`) y por fila **ver/calificar** (`tarea-detalle.html`) o **devolver** (`tarea-devolver.html`). |
| Detalle de tarea | Vista completa de la entrega con **evidencia**, calificación (puntaje 0–100), retroalimentación y acción de **devolver**. |
| Devolver tarea | Vista propia con **motivo** (select) y **observaciones** para el estudiante. |
| Mi perfil | Datos propios con **título / especialidad** y **ubicación** (región/rectoría, departamento, ciudad, sede); enlace a **cambiar contraseña** y preferencias de notificación. |
| Cambiar contraseña | Vista propia para actualizar la contraseña institucional (actual, nueva y confirmación). |
| Notificaciones | Avisos con filtro por tipo (chips) y *Marcar todo como leído* con confirmación. |

> Estas 23 pantallas corresponden al refactor UX/UI del rol; detalle y contrato de interacción en **[docs/docente-rol-ux.md](docs/docente-rol-ux.md)** y en `docs/estructura_de_vistas_sgemd.md` §3.3. El módulo **Seguimiento** se eliminó: el registro de avance vive en la vista *Registrar avance* y la columna *Evidencia* de Emprendimientos asignados.

### Estudiante

> **27 archivos** en `prototype/estudiante/` (**18 vistas base** + 4 detalles de evento + 4 variantes de estado de tarea + 1 variante de detalle de emprendimiento).

| Pantalla | Información que debe mostrar |
| --- | --- |
| Dashboard | Su emprendimiento, etapa actual, % de avance de sus tareas, tareas pendientes/vencidas, nº de seguimientos y asesorías; vista previa de tarjetas al pasar el mouse. |
| Estado de seguimiento | Avance general y **una barra con porcentaje por cada fase**, con los requisitos por cumplir. |
| Mi emprendimiento | Listado de sus emprendimientos; cada uno abre su **propia vista de detalle** (Sabor y Sabe y Mochilas Origen incluidas). |
| Detalle del emprendimiento | Ficha por pestañas: resumen, diagnóstico, seguimiento, asesorías y evidencias; descarga del expediente. |
| Editar emprendimiento | Edición de los datos permitidos al estudiante (nombre, descripción, redes sociales). |
| Plan de trabajo | Plan agrupado por fases, con tareas y estado; **Descargar plan**. |
| Tareas | Ver sus tareas, filtrar por estado/prioridad y abrir el detalle. |
| Detalle de tarea | Entrega con evidencia: adjuntar archivo, contador de evidencias y **Marcar como completada** habilitado solo con al menos un archivo. Variantes: completada por clientes/precio/usuarios y en revisión. |
| Seguimiento | Historial (solo lectura) de los avances de su emprendimiento. |
| Detalle de seguimiento | Detalle del avance con fecha, autor, estado de revisión, puntaje y retroalimentación. |
| Asesorías | Consultar sus asesorías y su estado. |
| Solicitar asesoría | Formulario de solicitud (tema, necesidad, disponibilidad); no confirma la cita. |
| Diagnóstico | Ver y diligenciar su diagnóstico. |
| Resultados del diagnóstico | Resultado con fortalezas, oportunidades de mejora y avance por fases. |
| Eventos | Lista de eventos disponibles. |
| Detalle de evento | Ficha del evento (asesoría grupal, capacitación, showroom, startup) con fecha, modalidad y recomendación recibida. |
| Notificaciones | Bandeja con filtros (Todas · Sin leer · Tareas · Asesorías · Seguimiento), contador y **Marcar todas como leídas**. |
| Perfil | Editar sus datos propios. |
| Configuración | Datos personales y **datos académicos condicionales** (Pregrado · Posgrado · Egresado); el programa académico solo lo modifica el Administrador. |

**Componentes compartidos:** Login, Register, PrivateRoute, sidebars por rol, menú de usuario, cliente `api.js`, componentes de UI (tarjetas, tablas, formularios, gráficos).

**Navegación/autorización:** la puerta de entrada esperada es **Login → Dashboard por rol**; `prototype/index.html` queda solo como índice de revisión del prototipo, no como entrada del producto. `PrivateRoute` con `allowedRoles`; redirige a login si no autenticado y a "no autorizado" si el rol no aplica; los menús solo muestran las rutas del rol; sin enlaces muertos.

---

## 9. Autenticación y seguridad

> Solo comportamiento esperado; **sin secretos reales**.

- **JWT:** firmado con un secreto definido en una variable de entorno. Payload con `{ id, Roles_idRoles1 }`.
- **Expiración:** sesión de 8 horas (configurable).
- **Contraseñas:** con bcrypt (salt 10+). Nunca se devuelven.
- **Protección de rutas:** `authenticateToken` en todo endpoint de negocio; `401` sin token, `403` si inválido/expirado.
- **Autorización por rol:** middlewares `isAdmin` / `isTeacher` / `isStudent` usados de forma consistente; `403` si el rol no aplica.
- **Variables de entorno:** secretos y credenciales solo vía variables de entorno (`.env`), cuyo archivo está ignorado por Git. Se provee `.env.example` con placeholders **sin valores reales**.
- **Verificación de correo:** código generado, **almacenado en BD** con expiración, enviado por correo, y **validado en backend** antes de activar la cuenta. Nunca se valida solo en frontend ni se devuelve el código en la respuesta.
- **Manejo seguro de credenciales:** nunca exponer contraseñas, secretos, tokens (más allá del de sesión) ni códigos en respuestas.
- **CORS:** restringido a orígenes permitidos.
- **Validación de entrada:** sanitizar y parametrizar todas las consultas; validar tipos/longitudes/campos requeridos.
- **Manejo de errores:** respuestas JSON consistententes sin exponer stack traces ni datos internos.

---

## 10. Problemas del proyecto anterior que NO deben repetirse

> Documentar para **evitar**; no implementar soluciones en el proyecto actual.

- **Modelos de BD inconsistentes con el código:** p. ej. `tracing.service.js` usaba `Emprendimiento_idEmprendimiento` en una tabla `seguimientos` que no tenía esa columna → la nueva BD debe definir el modelo completo y correcto antes de codificar.
- **Rutas inexistentes / enlaces muertos:** menús con rutas que no existen (404). Verificar que cada ruta del frontend tenga componente y que los menús apunten a rutas reales.
- **Dos capas de autenticación:** coexistían una implementación activa (`users.service`) y otra muerta/no montada (`auth.service`/`auth.controller`) con esquemas de BD distintos. La reconstrucción debe tener **una sola** implementación coherente.
- **Código muerto / duplicado:** `seguimientos.service.js`, `email.service.js`, `auth.service.js` sin uso. No duplicar servicios.
- **Duplicación de modelos de asignación:** coexistían `emprendimiento.Usuarios_idUsuarios` (dueño) y `asignaciones` (mentor), sin conectar. Usar un modelo único.
- **Datos mock donde debería haber datos reales:** cuentas demo que saltan el backend; dashboards con valores inventados. Todo dato de dashboard debe venir de la BD.
- **Problemas de autorización:** muchos endpoints solo exigían autenticación sin validar rol ni alcance; el estudiante podía operar donde no debía. Validar **rol y propiedad** en backend.
- **Verificación de correo insegura:** el código se devolvía en la respuesta y no se validaba en backend; cualquiera podía marcar `Verificado=1`. Implementar validación real en backend con persistencia en BD. No devolver OTPs en respuestas JSON al frontend.
- **Inconsistencias entre roles:** frontend usaba `Rol` numérico y backend `Roles_idRoles1` u objetos de sesión distintos (`UserMenu.jsx` roto). Unificar a un solo campo de rol.
- **Inconsistencias de etapas:** el frontend usaba nombres de etapa distintos a los de BD y el backend referenciaba una columna inexistente (`et.Etapa` en vez de `TipoEtapa`). Unificar catálogo de etapas y columnas.
- **Consultas SQL incompatibles:** joins que usaban columnas inexistentes o nombres mal escritos. Escribir consultas contra el modelo de BD real.
- **Tablas no incluidas en Docker:** `tareas` existía solo en un script aparte y no se montaba en la inicialización. La BD inicial (Docker) debe crear **todas** las tablas necesarias.
- **Errores de tipeo de identificadores:** p. ej. `EtapaEmprimiento` en un componente. Validar nombres de campos/campos en toda la UI.
- **Case-sensitivity:** en PostgreSQL los identificadores no entrecomillados se normalizan a minúsculas. Usar una convención de nombres consistente (snake_case).
- **Secretos en el historial:** `.env` estuvo versionado y sus secretos llegaron a commits. En la reconstrucción **nunca** versionar `.env` ni secretos; usar `.env.example` con placeholders.

---

## 11. Decisiones importantes

### Decisiones ya confirmadas (para el MVP)

- Node.js (backend) + React (frontend) + PostgreSQL con Docker.
- Un único campo de rol (`Roles_idRoles1`): 1=Admin, 2=Estudent, 3=Teacher, 4=Auditor (solo lectura + exportación).
- Autenticación con JWT (8 h) + bcrypt + verificación de correo real en backend.
- Modelo de asignación único (tabla `assignments` mentor↔estudiante↔emprendimiento).
- Emprendimiento con propietario-estudiante (`User_idUsers`) + etapa (`entrepreneurialStage`).
- Seguimiento ligado a un emprendimiento; autor registrado.
- Tareas ligadas a emprendimiento y estudiante; estados y avance derivados de BD.
- **Estados de revisión del docente** (Pendiente · En revisión · Calificada · Devuelta) sobre seguimiento/avances y tareas, con calificación por **puntaje (0–100) + retroalimentación** y posibilidad de **devolver** la tarea al estudiante.
- Dashboards con métricas reales (no mock).
- **El Administrador crea y gestiona usuarios** (alta de estudiante/docente, edición y baja lógica); el autorregistro público sigue existiendo para estudiantes.
- **El Administrador crea el emprendimiento y lo aprueba**; el segundo emprendimiento requiere autorización de **paralelo**. *(El prototipo no incluye el alta por el estudiante: §17.4.)*
- **Estados de cuenta:** Limitado → Activo → Inactivo, con desbloqueo y reactivación **exclusivos del Administrador**.
- **Asesorías:** el Admin crea y asigna directamente; el Docente acepta o reprograma; el estudiante solo solicita (reemplaza el enunciado anterior de R22).
- **Borrado lógico y reversible** con cascada de archivos adjuntos.
- **Evidencia obligatoria** para que el estudiante complete una tarea.
- **Alcance del prototipo:** estático, generado desde Python; guardar/descargar/exportar/notificar son **simulaciones** y no hay backend, API ni PostgreSQL en este repositorio.
- Secretos solo por variables de entorno; `.env` ignorado; `.env.example` sin secretos.
- **Rol auditor (rol 4):** **solo lectura y exportación de reportes**; no edita datos ni accede a información sensible completa. Se cubre con NFR-002, NFR-007, FR-010, FR-017 y **US-026**, sin crear un FR nuevo. Su implementación queda `Fuera de alcance / Post-MVP` (AQ-08).

### Decisiones que todavía deben tomarse (abiertas)

- **Modelo de seguimiento (crítico):**
  - Relación seguimiento → emprendimiento: **obligatoria** (1:N). Confirmar.
  - Relación seguimiento → usuario/docente (autor): **obligatoria** (1:N). Confirmar.
  - Cardinalidad emprendimiento → seguimientos: **1 hacia N**.
  - Quién crea: solo docente asignado/admin (confirmado como recomendado).
  - Quién consulta: docente asignado y estudiante del emprendimiento y admin (lectura para estudiante).
  - Historial: ordenado por fecha, por emprendimiento.
  - Campos a conservar: `description`, `typeMonitoring`, fechas, autor, emprendimiento.
  - **Si se reconstruye desde cero NO hay datos existentes que preservar**, por lo que la tabla se crea con el modelo correcto desde el inicio (esto elimina el problema de migración del proyecto anterior).
- Inclusión del módulo de **eventos** y de **diagnóstico** en el MVP (Confirmado).
- Recuperación de contraseña (Confirmado).
- Módulo de comparativa de emprendimientos (Opcional/Post-MVP).
- **Alcance del rol de auditor (rol 4):** **cerrado (AQ-08)** — solo lectura y exportación de reportes, sin edición ni datos sensibles completos.
- **Validación del emprendedor (AQ-06):** campos obligatorios del registro, criterios de aprobación y **qué funcionalidades están disponibles antes** de la validación (**AQ-07**). **Pendiente de la reunión**; ver el dossier [`docs/dossier-decisiones-pendientes-2026-10.md`](./docs/dossier-decisiones-pendientes-2026-10.md).
- **Diagnóstico (AQ-09):** rúbrica respuestas → fortalezas/oportunidades; formato y contenido del **informe descargable**; filtros necesarios. **Pendiente** (dossier §5).
- **Acta de compromiso (AQ-10):** el **rechazo exige motivo obligatorio** y notifica al estudiante (BR-009, AQ-05). Queda pendiente el **tiempo de revisión** y el efecto completo del rechazo (dossier §6).
- **Restauración de respaldos:** es una **operación técnica**, no una función del Administrador; la UI solo exporta y consulta estado/integridad (`Fuera de alcance / Post-MVP`, AQ-04).
- **Estructura de datos (AQ-11):** **cerrada** con el modelo textual de [§5](#5-modelo-de-datos) (**41 tablas = 27 de negocio + 14 catálogos**). No se declara un total de relaciones. Los diagramas se regeneraron el 2026-10-25 y su fuente es el archivo Mermaid/Markdown, no los binarios.
- **`.py` de correcciones de `context_admin`:** **resuelto (AQ-03)**. El archivo es `Config-admin/correcciones-adiciones-requisitos.md`; la copia usada es idéntica por SHA-256 (`EDCDE30F…836B5872`) y sus 28 ítems están mapeados.
- **Documentos de referencia no disponibles (AQ-12):** `control.pdf` y el **Excel de preguntas** (§16.3). Si no llegan, no se bloquea el cierre ni se inventa su contenido.

---

## 12. MVP mínimo

### P0 — Imprescindible

- Autenticación: registro, login, logout, verificación de correo real en backend (OTP 8 dígitos/5 min), JWT, cierre de rutas por rol.
- Usuarios y roles (admin gestiona usuarios; edición de perfil).
- **Alta, edición y baja lógica de estudiantes y docentes por el Administrador**, con validación de unicidad y **ambos topes de carga docente** (12 h/semana y 12 emprendimientos, configurables).
- **Aprobación de emprendimientos por el Administrador**, incluido el **paralelo**; bandeja única de solicitudes (desbloqueos, paralelos y citas).
- **Ciclo de estados de cuenta** Limitado → Activo → Inactivo, con desbloqueo y reactivación exclusivos del Administrador.
- Emprendimientos: el admin crea y aprueba/rechaza, consulta con alcance, ver detalle y etapa. Historial de emprendimientos. *(El alta por el estudiante no está representada en el prototipo: [§17.4](#173-vacíos-del-prototipo-que-no-se-inventan).)*
- Asignaciones: admin asigna docente a estudiante (+ emprendimiento); docente consulta sus asignados; estudiante su/s mentor/es.
- Seguimiento: docente registra notas sobre un emprendimiento; estudiante consulta historial. Adjuntos (hasta 500MB).
- Tareas: docente crea, estudiante completa **con evidencia obligatoria**, estados y avance derivados de BD. Adjuntos (hasta 500MB).
- Asesorías: estudiante solicita, **admin crea y asigna directamente**, docente acepta/reprograma, ambos consultan. Notificaciones accionables.
- **Respaldos:** exportación de la base y consulta del estado/integridad del backup. **Sin restauración desde la interfaz** (operación técnica).
- Dashboards por rol con métricas reales. Paginación en listas.
- Base de datos inicializada completa (todas las tablas) en Docker. Sin scripts de migración.
- Seguridad: secretos en entorno, `.env` ignorado, validación en backend.
- Validación y activación del emprendedor por el administrativo (desbloqueo). Correo de bienvenida. Notificaciones básicas.

### P1 — Importante

- Diagnóstico de emprendimiento (data-driven desde Excel, con generar resumen e informe descargable).
- Caracterización y valoración del emprendimiento. Feedback inmediato.
- Acta de compromiso y confidencialidad (subida + revisión).
- Eventos (creación y registro de asistencia manual).
- Mejoras de perfil (avatar, datos extendidos: programa y centro educativo ya modelados).
- Plan de trabajo agrupado por etapas.
- **Progreso por fases y descarga del plan** para el estudiante.
- **Configuración del programa** (carga docente, cupos, sedes, etapas, notificaciones) con bitácora.
- **Reportes institucionales** en CSV, PDF o XLSX con filtros.
- **Notificaciones accionables** con contador y marcado masivo como leído.
- **Expediente consolidado** con asesorías, diagnósticos, seguimientos y evidencias; el **log de auditoría** queda para backend.
- **Recomendación de eventos** por el docente a estudiantes o emprendimientos.

### P2 — Opcional / post-MVP

- Comparativa de emprendimientos.
- Evaluación de habilidades (no estaba funcional).
- Notificaciones/push.
- Internacionalización.
- Rol de auditor (alcance definido en AQ-08: solo lectura y exportación de reportes; implementación post-MVP).

---

## 13. Criterios de aceptación

Pruebas funcionales para considerar el MVP terminado:

1. Un estudiante puede **registrarse**, recibir un código OTP de 8 dígitos, verificar su correo y **iniciar sesión**.
2. Un administrador puede **crear** usuarios/docentes, **asignar un emprendimiento a un docente**, y aprobar emprendimientos paralelos.
3. Un docente consulta **solo sus emprendimientos asignados** (no los de otros).
4. Un docente puede **registrar seguimiento** (nota y adjuntos) sobre un emprendimiento asignado.
5. El **estudiante puede consultar** el historial de seguimiento de su emprendimiento (solo lectura).
6. Un docente puede **crear tareas**; un estudiante puede **completar** sus tareas; el estado cambia correctamente.
7. Las **tareas persisten** en BD y sobreviven al reinicio. Los adjuntos se eliminan del servidor si se borra la tarea.
8. Un estudiante puede **solicitar una asesoría**, el **Administrador puede crearla y asignarla directamente** y el **docente aceptarla o reprogramarla**. Se reciben notificaciones accionables.
9. Los **dashboards muestran datos reales** de BD (conteos y % de avance correctos por rol).
10. Un estudiante **no puede** ver ni modificar recursos de otros; un docente **no puede** ver emprendimientos ajenos.
11. El sistema **no expone** credenciales, secretos, ni códigos OTP en ninguna respuesta.
12. La base de datos se **inicializa completa** en un entorno Docker limpio (todas las tablas necesarias). El diseño es totalmente responsive.
13. Un emprendedor con el **registro completo** queda pendiente y **no accede** a las funcionalidades hasta que el administrativo lo **valide y active**.
14. El emprendedor puede **diligenciar el formulario de diagnóstico** (cargado desde Excel), y el sistema **genera** la caracterización/valoración con **feedback inmediato** e **informe descargable**.
15. El emprendedor puede **subir el acta de compromiso** firmada y el administrativo puede **aprobarla/rechazarla**.
16. Se generan **notificaciones** al administrativo (registro, diagnóstico, emprendimiento, asesoría) y al estudiante (validación, acta, tareas/asesorías, evento). Cada notificación abre el objeto referido.
17. El administrador puede **crear, editar y dar de baja lógica** estudiantes y docentes, con validación de documento/correo únicos y **ambos topes de carga docente** (12 h/semana y 12 emprendimientos, configurables).
18. Un emprendimiento queda en **Pendiente** y solo pasa a **Aprobado** por decisión del Administrador; el **paralelo** requiere autorización. *(El alta por el estudiante está pendiente de definición: [§17.4](#173-vacíos-del-prototipo-que-no-se-inventan).)*
19. El estado de la cuenta cambia **solo** por el Administrador: Limitado → Activo (desbloqueo) e Inactivo → Activo (reactivación); a los **90 días** sin actividad se marca Inactivo.
20. El estudiante **no puede completar una tarea sin evidencia** adjunta; el botón permanece deshabilitado hasta que suba al menos un archivo.
21. El administrador puede **exportar la base** y consultar el **estado, historial e integridad** del respaldo; los cambios de **configuración** quedan en la bitácora.
22. La **bandeja de solicitudes** resuelve desbloqueos, paralelos y citas en un solo lugar, con confirmación y notificación al solicitante.
23. El rechazo del **acta de compromiso** exige **motivo obligatorio**; sin motivo no se confirma y el estudiante recibe la notificación (BR-009).
24. El Administrador **no restaura** respaldos desde la interfaz: solo exporta la base/reportes y consulta estado e integridad; la restauración es una operación técnica (AQ-04).
25. El rol **auditor** solo puede **consultar y exportar**; ninguna de sus rutas acepta escritura ni devuelve datos sensibles completos (AQ-08, NFR-002, NFR-007, US-026).

---

## 14. Orden recomendado de construcción

1. **Modelo de datos / Base de datos** — definir y crear el esquema completo correcto (todas las tablas del MVP), con seed inicial y sin secretos.
2. **Backend base (Node.js)** — Express, conexión a BD, manejo de errores, CORS, estructura de carpetas. Configuración de SMTP.
3. **Autenticación** — registro, verificación OTP por correo, login, JWT, logout, middleware de auth y de rol.
4. **Usuarios / roles / módulos** — endpoints y lógica de usuarios, perfil, gestión por admin. Control de vistas por módulo.
5. **Emprendimientos** — CRUD, etapas (catálogo predefinido), estados históricos y validación para emprendimientos paralelos.
6. **Asignaciones** — crear/consultar/desactivar; conectar con emprendimientos y usuarios.
7. **Seguimiento y Adjuntos** — endpoints por emprendimiento, autor, alcance. Subida/borrado de archivos (local, hasta 500MB).
8. **Asesorías y Notificaciones** — solicitud, confirmación, consulta. Alertas en tiempo real (Socket.io).
9. **Tareas** — CRUD, estados, avance, adjuntos.
10. **Eventos y Asistencia** — CRUD de eventos, registro manual de asistencia.
11. **Dashboards** — endpoints de métricas reales por rol. Paginación en todos los listados.
12. **Frontend (React)** — autenticación, layout/sidebars (responsive), páginas por rol, consumo de la API, guardas.
13. **Pruebas** — funcionales de extremo a extremo (criterios de aceptación).
14. **Docker** — contenerización (backend, frontend, PostgreSQL), variables de entorno, inicialización de BD, README.

---

## 15. Estado final esperado

Cuando el MVP esté terminado, el proyecto debe verse así:

- **Un esquema de BD completo y coherente** con el código (sin columnas ni tablas huérfanas u obsoletas en el flujo principal).
- **Backend REST limpio y por capas (Node.js)**, con una sola implementación de autenticación y autorización por rol/alcance en cada endpoint.
- **Frontend React totalmente responsive** con páginas por rol, guardas, menús coherentes y cliente API que maneja sesiones.
- **Seguimiento funcional**: el docente registra notas (con adjuntos) sobre un emprendimiento y el estudiante las consulta; el autor queda registrado.
- **Asignaciones funcionales**: el docente ve "sus" emprendimientos y el estudiante "sus" mentor/emprendimientos.
- **Tareas funcionales** con estados, adjuntos y avance derivados de BD.
- **Dashboards con métricas reales** (sin datos mock ni cuentas demo que salten el backend).
- **Notificaciones en tiempo real** para eventos clave (asesorías, tareas).
- **Seguridad correcta**: secretos solo en entorno, `.env` ignorado, `.env.example` sin valores reales, verificación OTP (8 dígitos/5 min) por correo real, sin credenciales expuestas.
- **Despliegue con Docker** que inicialice la BD completa y limpia, levantando backend + frontend con variables de entorno.

### Distinción final de conceptos

- **REQUISITOS DEL MVP:** lo que "debe" hacer el sistema (secciones 1-3, 6-9, 12).
- **DECISIONES DE DISEÑO:** opciones de arquitectura/modelo ya recomendadas (secciones 4-5, 11 "confirmadas").
- **PROBLEMAS DEL PROYECTO ANTERIOR:** lo que debe evitarse (sección 10).
- **DECISIONES PENDIENTES:** lo que la nueva IA debe consultar antes de implementar (sección 11 "abiertas").

---

## 16. Fuentes y trazabilidad del alcance ampliado

> Esta sección documenta el **alcance ampliado** que salió del proceso real de atención (reunión con el área de Emprendimiento) y de las anotaciones del equipo. Es la referencia para **validar qué falta por implementar** respecto de las secciones actualizadas.

### 16.1 Flujo de registro, validación y activación

1. **Inscripción:** el emprendedor se registra en la plataforma.
2. **Completar información:** diligencia los datos requeridos.
3. **Notificación:** el sistema notifica al administrativo (p. ej. la asesora del área).
4. **Programación de asesoría:** el administrativo se comunica con el emprendedor para acordar la reunión.
5. **Reunión:** se realiza la asesoría.
6. **Validación:** el administrativo verifica y **valida** al emprendedor.
7. **Activación:** aprobado → se **habilitan** las funcionalidades de la plataforma.

- **Acceso previo:** mientras no esté validado, el usuario opera en **modo limitado** (p. ej. Diagnóstico bloqueado).
- **Suspensión:** 3 inasistencias a asesorías o 4 meses de incumplimiento → suspensión de 4 meses.

### 16.2 Puntos por cerrar (bloquean implementación)

> **Estado al 2026-10-25:** AQ-01 … AQ-05 y **AQ-08** están cerradas; **AQ-11** queda cerrada con el modelo textual de [§5](#5-modelo-de-datos) (41 tablas = 27 de negocio + 14 catálogos). Las preguntas que siguen se tratan en el dossier [`docs/dossier-decisiones-pendientes-2026-10.md`](./docs/dossier-decisiones-pendientes-2026-10.md) y **no se deciden por defecto**.

- **AQ-06 — Campos obligatorios y criterios de validación:** 7 campos + casilla en `registro.html`, sin atributos `name`; no hay lista de criterios en el prototipo.
- **AQ-07 — Acceso previo:** contradicción entre `estado-seguimiento.html` (diagnóstico bloqueado) y `emprendimiento-detalle.html` (botón activo).
- **AQ-09 — Rúbrica e informe:** 5 secciones, 22 preguntas, 6 dimensiones y 4 bandas visibles, sin fórmula ni plantilla de informe.
- **AQ-10 — Plazo y efecto del rechazo del acta:** BR-009 fija el motivo obligatorio; falta el plazo y el efecto completo.
- **AQ-12 — Insumos ausentes:** `control.pdf` y el **Excel de preguntas** (§16.3).
- **Diagramas:** regenerados el 2026-10-25 (`docs/diagrama-clases.md`, `docs/diagrama-componentes.md`, `docs/context-diagram.mmd`). Los binarios `.drawio`/`.png` anteriores pueden seguir siendo obsoletos; la fuente es el archivo Mermaid/Markdown.
- **Vacíos del prototipo (no son decisiones, son ausencias):** alta de emprendimiento por el estudiante, vista del acta, rol auditor, validación de motivo obligatorio en rechazos y emisión de notificaciones en tiempo real. Ver [§17.4](#173-vacíos-del-prototipo-que-no-se-inventan).

### 16.3 Documentos de referencia

| Documento | Uso previsto | Estado |
| --------- | ------------ | ------ |
| `control.pdf` | Referencia para el formulario de registro. | ⚠️ **Solicitado (AQ-12); no está en el repositorio** |
| `ficha de carácter y formulación.pdf` | Referencia para caracterización y formulación. | ⚠️ Material local del área (no versionado); falta confirmar equivalencia |
| `Valoración y Diagnóstico.pdf` | Referencia para el diagnóstico y su valoración. | ✅ Material local del área (no versionado) |
| **Archivo Excel de preguntas** | Fuente para estructurar el formulario de diagnóstico. | ⚠️ **Solicitado (AQ-12); pendiente** |

> **Regla AQ-12:** si `control.pdf` o el Excel no llegan antes de la reunión, **no se bloquea** el cierre documental, **no se inventa** su contenido y AQ-06/AQ-09 permanecen abiertas con la evidencia del prototipo.

### 16.4 Documentación de trabajo (local)

> **Importante:** esta actualización se hizo **solo en local**. No se creó rama, no se hizo commit y no se publicó en GitHub.

- **Material local del área (no versionado):** inventario de insumos, flujo real de atención y pendientes del estudiante — se mantienen fuera del repositorio por contener datos personales.
- `docs/orquestacion-actualizacion-requisitos-2026-10.md` — orquestación, protocolo de verificación y criterios de aceptación.
- `docs/registro-actualizacion-requisitos-2026-10.md` — ledger de evidencia, bitácora de vistas, matriz de vacíos, decisiones y preguntas abiertas.
- `docs/dossier-decisiones-pendientes-2026-10.md` — hojas de decisión AQ-06, AQ-07, AQ-09, AQ-10 y AQ-12; anexos de AQ-08 y AQ-11; nota de diagramas.
- `docs/fr_nfr_sgemd.md` — SRS actualizado (24 FR, 9 NFR, 6 BP, 9 BR; AQ-01 … AQ-12).
- `docs/historias_usuario.md` — historias actualizadas (US-011 … US-026).
- `docs/CONSOLIDACION-ANOTACIONES.md` — anotaciones del equipo reorganizadas (diagnóstico, registro/validación, roles, BD, Git).
- `CORRECCIONES-VISTAS-ESTUDIANTE.md` — hallazgos validados del prototipo.
- `Config-admin/correcciones-adiciones-requisitos.md` — correcciones C-1…C-7 y adiciones A-1…A-21 aplicadas.
- `prototype/cambios-a-admin.md`, `prototype/orquestacion-docente-2026.md` — evidencia de los refactors de rol.

### 16.5 Sobre datos sensibles y Git

- Los insumos del área contienen **datos personales** (nombres, cédulas, teléfonos, correos) → aplica la **Ley 1581 de 2012**. **No** versionar estos archivos sin autorización; usar datos ficticios.
- Se propone una **rama de inyección de datos** para centralizar la carga y evitar que cada integrante la introduzca manualmente.
- **Esta entrega no se publica:** el trabajo documental permanece en el equipo local hasta que el responsable decida versionarlo.

### 16.6 Conteos y estado del prototipo

| Elemento | Valor verificado |
|---|---|
| Pantallas totales | **73** |
| Acceso global | 4 |
| Estudiante | 27 archivos (18 vistas base + 9 variantes) |
| Docente | 23 |
| Administrador | **19** (incluye `configuracion.html`) |
| Requisitos | **24 FR · 9 NFR · 6 BP · 9 BR** |
| Historias nuevas | **16** (`US-011` … `US-026`) |
| Preguntas abiertas | **5** (AQ-06, AQ-07, AQ-09, AQ-10, AQ-12) |
| Modelo de datos | **41 tablas = 27 de negocio + 14 catálogos** (sin total de relaciones) |
| Diagramas | **Regenerados el 2026-10-25** (Mermaid/Markdown como fuente) |
| Backend / API / PostgreSQL | **No existen en este repositorio** |
| Guardar / descargar / exportar / notificar | **Simulado en el navegador** |

---

## 17. Reconciliación con el prototipo (2026-10-25)

> **Propósito:** dejar constancia de qué se cambió al alinear la documentación con el prototipo, qué se tomó de él, qué contradicciones se resolvieron y qué vacíos **no** se rellenaron por invención. Este registro evita que un lector nuevo vuelva a leer la documentación anterior como si fuera la vigente.

### 17.1 Qué se tomó del prototipo

- **Estados de cuenta:** `Limitado` · `Activo` · `Inactivo` (antes `Estado 1/0`).
- **Estados de tarea:** `Pendiente` · `En curso` · `En revisión` · `Completada` · `Vencida` · `Devuelta`.
- **Estados de revisión:** `Pendiente` · `En revisión` · `Calificada` · `Devuelta`.
- **Estados de asesoría:** `Por agendar` · `Programada` · `Confirmada` · `En curso` · `Completada` · `Cancelada`.
- **Estados de evento:** `Pendiente` · `Aprobado` · `Rechazado` · `Publicado`.
- **Respaldos:** tipo `Completo` · `Parcial`; estado `Exitosa` · `Fallida`; frecuencia diaria 09:00; retención 30 días.
- **Prioridad:** `Alta` · `Media` · `Baja`.
- **Fases del plan:** Ideación y priorización · Estructuración y ejecución · Consolidación · Escalamiento.
- **Etapas del emprendimiento:** Ideación · Prototipo · Validación · Formalización.
- **Diagnóstico:** 5 secciones, 22 preguntas, 6 dimensiones y 4 bandas.
- **Parámetros:** `carga_max_horas=12`, `max_emprendimientos_docente=12`, `cupos_por_sede=40`, tres sedes (Norte, Centro, Sur).
- **Campos nuevos que el modelo no tenía:** prioridad, puntos, puntaje obtenido, retroalimentación, motivo de devolución, estado de revisión, comentarios, recomendaciones, configuración, respaldos, solicitudes, auditoría y enlace accionable de la notificación.

### 17.2 Contradicciones que el prototipo introduce y cómo se resuelven

| # | Contradicción | Resolución documentada |
|---|---|---|
| 1 | **12 horas** (FR-016) vs **12 emprendimientos** (prototipo) | **No son excluyentes:** el prototipo aplica **ambos** topes y los expone como parámetros. Se modelan `asignaciones.HorasSemanales` + `configuracion_programa.max_emprendimientos_docente`. |
| 2 | **Tres juegos de fases** (R17 anterior, `estado-seguimiento`, detalle del emprendimiento) | Se separan dos conceptos: `etapaemprendimiento` (avance global) y `faseplan` (plan de trabajo). Los alias cortos del detalle quedan como **deuda de normalización** del prototipo. |
| 3 | **Cuenta `Limitado`**: `estado-seguimiento` bloquea el diagnóstico, `emprendimiento-detalle` lo ofrece activo | Se mantiene **AQ-07 abierta**; el modelo soporta ambos comportamientos vía `habilitaciones`. No se decide por defecto. |
| 4 | **Acta**: `admin/asignaciones.html` la exige, pero no hay vista para cargarla | Se mantiene FR-003/BR-001 como **pendientes**; `actas` se modela, pero el flujo no está representado. |
| 5 | **Motivo de rechazo obligatorio** (BR-009) vs confirmación con campo vacío | Se documenta como **defecto del prototipo**; la regla queda vigente en [§6](#6-reglas-de-negocio) (R38). |
| 6 | **Alta de emprendimiento por el estudiante** (FR-012) vs prototipo que no la tiene | Se corrige el rol del estudiante: el alta la hace el Administrador; FR-012 queda como **parcial** hasta que se decida. |
| 7 | **Rol auditor** (R-04, AQ-08) vs catálogo `roles` 1–3 y cero pantallas | Se conserva como `Post-MVP`; el catálogo ya contempla el valor 4 y los diagramas lo incluyen. |
| 8 | **Notificaciones en tiempo real** (NFR, README) vs prototipo sin emisión | Se degrada la expectativa: bandeja simulada; la emisión en tiempo real queda como requisito de backend. |

### 17.3 Vacíos del prototipo que no se inventan

Estos elementos **no existen** en las 73 pantallas. Se documentan como pendientes y no se les asigna comportamiento supuesto:

1. **Alta de emprendimiento por el estudiante** (FR-012): no hay formulario ni vista del estado *Pendiente*.
2. **Vista del acta de compromiso** (FR-003): no hay pantalla de descarga, carga ni revisión.
3. **Rol auditor** (rol 4): definido en requisitos, sin ninguna pantalla.
4. **Validación del motivo obligatorio** en rechazos (FR-014, BR-009): el prototipo confirma con el campo vacío.
5. **Notificaciones en tiempo real** (FR-005): solo bandeja, sin emisión ni WebSocket.
6. **Limpieza en cascada de adjuntos** (BR-006 / NFR): no hay evidencia visual del borrado físico.
7. **Cálculo automático del diagnóstico** (FR-002): 22 preguntas y resultados visibles, sin fórmula ni derivación.
8. **Inactividad automática a 90 días** (FR-007): el estado existe y se filtra, pero no hay proceso que lo calcule.
9. **Restauración de respaldos** (AQ-04): solo creación y descarga simuladas.
10. **Normalización de los alias de fase** en el detalle del emprendimiento.

### 17.4 Documentos sincronizados en este cambio

- `README.md` — §2, §3, §4, §5, §6, §7, §11, §16 y este §17.
- `docs/fr_nfr_sgemd.md` — estados de implementación, FR-012, FR-016, FR-024, conteos y AQ-11.
- `docs/diagrama-clases.md`, `docs/diagrama-componentes.md`, `docs/context-diagram.mmd` — regenerados.
- `docs/estructura_de_vistas_sgemd.md` — §3.2 corregida (se elimina el flujo donde el estudiante agenda asesorías y el dashboard con métricas inventadas).
- `docs/VALIDACION-ALCANCE.md` — 73 pantallas (4 + 27 + 23 + 19).
- `docs/dossier-decisiones-pendientes-2026-10.md` — AQ-11 y evidencia de AQ-06/07/09/10/12.
- `docs/historias_usuario.md` — topes de 12 h y 12 emprendimientos.
- `PROTOTIPO-STITCH.md` — 73 pantallas y reparto 4/27/23/19.
- `prototype/README.md` — nota sobre los scripts de auditoría ausentes.
- `docs/sincronizacion-prototipo-2026-10.md` — registro completo del cambio.

---

_Fin del documento. Autocontenido, sin secretos, diseñado para reconstrucción limpia desde cero._
