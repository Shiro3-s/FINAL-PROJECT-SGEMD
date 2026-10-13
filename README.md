# SGEMD — Contexto Maestro para Reconstrucción del MVP

> **Propósito de este documento:** servir como especificación y contexto único **SGEMD (Sistema de Gestión de Emprendimiento Minuto de Dios)** desde cero, de forma limpia.
>
> **Qué es y qué no es:** es un documento de **especificación/contexto**. Describe el comportamiento **correcto esperado** del MVP y qué debe evitarse del proyecto anterior. **No contiene** secretos, contraseñas, tokens, valores de `.env`, ni credenciales reales. **No es** un copiado del código anterior.
>
> El proyecto se construye **DESDE CERO**. No se debe asumir que hay que conservar errores, estructuras innecesarias ni tablas obsoletas del proyecto anterior.

> **Actualización (2026-10-12):** se incorporó el **alcance ampliado** que salió del proceso real de atención (reunión con el área de Emprendimiento) y de las anotaciones del equipo: **validación y activación del emprendedor**, **correo de bienvenida**, **diagnóstico *data-driven* desde Excel**, **caracterización y valoración**, **acta de compromiso y confidencialidad**, **notificaciones** y **rol de auditor (propuesto)**. El detalle, las reglas nuevas y los puntos por cerrar están en la [§16](#16-fuentes-y-trazabilidad-del-alcance-ampliado). Las secciones [2](#2-roles), [3](#3-funcionalidades-del-mvp), [5](#5-modelo-de-datos), [6](#6-reglas-de-negocio), [7](#7-api), [8](#8-frontend), [11](#11-decisiones-importantes), [12](#12-mvp-mínimo) y [13](#13-criterios-de-aceptación) fueron actualizadas.

---

> **Nota sobre esta rama:** si estás viendo esto en la rama `prototype/stitch`, aquí además del documento de especificación vive el **prototipo navegable de SGEMD**: 54 pantallas HTML generadas desde Python (51 ya publicadas en Stitch), un `index.html` índice para recorrerlas y el pipeline en Python que las genera, audita y publica.
>
> Empieza por **[PROTOTIPO-STITCH.md](PROTOTIPO-STITCH.md)**: qué contiene la rama y cómo usarla.
>
> Este `README.md` es la especificación general del proyecto y se mantiene idéntico al de `main`.

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
- `4 = Auditor` — **propuesto por el equipo, pendiente de definir** (ver [§16](#16-fuentes-y-trazabilidad-del-alcance-ampliado)). Su alcance, permisos y qué información puede consultar **aún no están cerrados**.

> **Nota:** mientras el alcance del rol de auditor no se defina, el sistema opera con **tres** roles funcionales (1–3). No implementar el rol 4 hasta cerrar su alcance ([§11](#11-decisiones-importantes)).

### Administrador (rol 1)

- **Puede hacer:** gestionar cualquier usuario (crear, editar, activar/desactivar, cambiar rol), crear/editar/eliminar emprendimientos, crear/eliminar/reasignar asignaciones, consultar todos los emprendimientos/seguimientos/tareas/asesorías, dashboard global. Modifica variables bloqueadas para el estudiante (Mentor asignado, observaciones, sector productivo y etapa). Aprueba la creación de emprendimientos paralelos para un estudiante.
- **No debería:** crear seguimientos/tareas como si fuera el docente asignado (puede administrarlos pero no "firmarlos"), ni ver credenciales o secretos.

### Docente / Mentor (rol 3)

- **Puede hacer:** ver únicamente los emprendimientos que **le fueron asignados** (vía asignaciones), registrar seguimiento (crear/editar/eliminar notas) de esos emprendimientos, crear/editar/eliminar tareas y asesorías de sus asignados, ver el perfil de sus estudiantes, consultar su dashboard. Registra asistencias a eventos manualmente en la plataforma.
- **No debería:** ver emprendimientos/estudiantes de otros docentes, modificar el emprendimiento del estudiante, eliminar usuarios ni cambiar roles.

### Estudiante (rol 2)

- **Puede hacer:** consultar **sus** emprendimientos, ver su progreso/etapas, consultar (solo lectura) el seguimiento de su emprendimiento, consultar y **completar** sus tareas, solicitar/consultar asesorías, consultar su dashboard. **Permisos de edición de su emprendimiento:** Puede editar el Nombre, Descripción, Redes Sociales y, opcionalmente, el plan de trabajo.
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
- **Qué puede hacer:** listar usuarios, crear (public o admin), editar, activar/desactivar, cambiar rol, subir avatar.
- **Información que maneja:** todos los datos del usuario. La contraseña **nunca** se devuelve ni se muestra.
- **Flujo:** el admin crea o edita usuarios con rol; el estudiante/docente edita su perfil.

### Emprendimientos

- **Quién lo usa:** admin crea/edita; docente consulta (los asignados); estudiante consulta (los suyos).
- **Qué puede hacer:** crear emprendimiento con propietario-estudiante, consultar (con alcance por rol), editar, ver detalle y etapa. Si un estudiante inicia un nuevo emprendimiento, el anterior no se sobrescribe (se mantiene la trazabilidad a menos que se desee borrar). Se pueden manejar emprendimientos en paralelo, pero el registro de un segundo emprendimiento requiere **aprobación explícita del Administrador**.
- **Información que maneja:** nombre, descripción, tipo, sector productivo, redes sociales, acompañamiento, acta de compromiso, etapa, propietario, fechas.
- **Flujo:** admin crea el emprendimiento y lo asocia a un estudiante; el docente lo ve si tiene asignación; el estudiante lo ve si es el propietario.

### Asignaciones estudiante/docente/emprendimiento

- **Quién lo usa:** admin crea/elimina/reasigna; docente y estudiante consultan las propias.
- **Qué puede hacer:** vincular un docente (mentor) con un estudiante y opcionalmente un emprendimiento.
- **Información que maneja:** mentor, estudiante, emprendimiento, fecha, estado (activa/inactiva).
- **Flujo:** el admin selecciona docente + estudiante (+ emprendimiento) y crea la asignación; desde entonces el docente ve los emprendimientos asignados y el estudiante queda bajo su tutoría.

### Consulta

- **Quién lo usa:** todos.
- **Qué puede hacer:** consultar recursos/entidades según su rol y alcance. Ver detalle de emprendimientos, usuarios, asignaciones. Todos los endpoints de listados implementan paginación desde el inicio.
- **Flujo:** cada consulta se filtra por rol y propiedad en backend.

### Seguimiento

- **Quién lo usa:** docente (crea/consulta/edita/elimina), admin (administra), estudiante (solo lectura).
- **Qué puede hacer:** registrar notas/anotaciones de acompañamiento sobre un emprendimiento.
- **Información que maneja:** descripción de la nota, tipo, **autor** (usuario), **emprendimiento** relacionado, fechas.
- **Flujo:** el docente registra una nota sobre un emprendimiento asignado; el estudiante consulta el historial de su emprendimiento.

### Asesorías

- **Quién lo usa:** estudiante (solicita/consulta), docente (confirma/crea/consulta), admin (consulta).
- **Qué puede hacer:** solicitar una asesoría, programar (fecha/horario/modalidad), confirmar.
- **Información que maneja:** nombre, descripción, fecha, modalidad, horario, estado (pendiente/confirmada), estudiante, docente.
- **Flujo:** el estudiante solicita; el docente la ve y confirma; ambos consultan la agenda. El sistema envía notificaciones en tiempo real a los usuarios cuando un docente confirma una asesoría.

### Tareas / plan de trabajo

- **Quién lo usa:** docente (crea/edita/elimina), estudiante (consulta y completa), admin (consulta).
- **Qué puede hacer:** crear tareas ligadas a un emprendimiento y a un estudiante, con fecha límite y estado.
- **Información que maneja:** título, descripción, fecha límite, estado (pendiente/completada/vencida), emprendimiento, estudiante, docente.
- **Flujo:** el docente crea la tarea → el estudiante la ve → la completa → el sistema calcula el avance (% de completadas). El sistema envía notificaciones en tiempo real a los usuarios cuando un docente asigna una nueva tarea.

### Gestión de Archivos

El sistema soporta la subida, almacenamiento y descarga de archivos adjuntos (PDFs, imágenes de evidencia) de hasta **500 MB** para tareas, seguimientos y asesorías. Se almacenan localmente en el servidor (organizados en carpetas, con planes de migración a la nube futura para respetar el ciclo de vida de la información). Si se elimina el registro asociado (tarea, asesoría), el archivo se elimina físicamente del servidor.

### Dashboards

- **Quién lo usa:** todos.
- **Qué puede hacer:** mostrar métricas reales derivadas de la base de datos.
- **Información que maneja:** conteos y agregados (total usuarios, emprendimientos, asignaciones, tareas, asesorías, seguimientos; % de avance; distribución por etapa).
- **Flujo:** consulta de métricas por rol, filtradas por alcance.

### Progreso

- **Quién lo usa:** estudiante y docente.
- **Qué puede hacer:** visualizar el avance del emprendimiento (etapa actual) y de las tareas.
- **Información que maneja:** etapa del emprendimiento, % de tareas completadas.
- **Flujo:** datos calculados a partir de la BD (etapa y tareas).

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

### Notificaciones

- **Quién lo usa:** todos (destinatarios); el sistema las emite.
- **Qué puede hacer:** notificar al **personal administrativo** cuando el emprendedor completa el registro/la información, completa el diagnóstico o solicita una asesoría; y notificar al **estudiante** cuando lo validan, cambia el estado del acta, le asignan docente o le crean tareas/asesorías.
- **Información que maneja:** destinatario, tipo, mensaje, leída/no leída, fecha.
- **Flujo:** un evento dispara la notificación; el usuario la consulta y la marca como leída. (Complementa las notificaciones en tiempo real de [Asesorías](#asesorías) y [Tareas](#tareas--plan-de-trabajo).)

---

## 4. Arquitectura propuesta

La nueva implementación es **desde cero** y no debe conservar estructuras innecesarias ni errores del proyecto anterior.

> **Diagrama de componentes:** se agregó el diagrama de componentes del proyecto en `docs/diagrama-componentes.drawio`, que refleja la arquitectura propuesta (Cliente/Navegador → Backend Node.js + Express → Persistencia/Infraestructura).
>
> **Diagrama de clases:** en `docs/diagrama-clases.md` (fuente Mermaid), `.png` y `.drawio` editable. Muestra la estructura interna del dominio: 20 clases con atributos, visibilidad, métodos y multiplicidades, y 31 relaciones, derivadas del modelo de datos de la [sección 5](#5-modelo-de-datos). Incluye trazabilidad requisito → clase y la revisión crítica contra los FR/NFR.
>
> **Modelo de datos:** el modelo objetivo es de **29 tablas y 42 relaciones** (16 de negocio con comportamiento + 13 catálogos de lectura), descritas en la [sección 5](#5-modelo-de-datos) y corregidas con `docs/diagrama-clases.md`.

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

> Diseño **conceptual** objetivo. No es una réplica del `schema.sql` anterior. No implementar la BD todavía; solo usar como guía. No incluir secretos ni datos sensibles en los scripts.
>
> **Convenciones del modelo:** la versión corregida aplica **snake_case** a todas las columnas, vincula `codigosverificacion` por `usuario_id`, modela los módulos como `habilitaciones` por persona y agrega `adjuntos` con sus tres tablas pivote.

### Catalogos (referenciados por claves foráneas)

| Tabla                  | PK                     | Propósito                                                             | Cardinalidad              |
| ---------------------- | ---------------------- | --------------------------------------------------------------------- | ------------------------- |
| `roles`                | idRoles                | Rol: 1=Admin, 2=Estudiante, 3=Docente                                 | 1 → N usuarios            |
| `tipodocumentos`       | idTipoDocumento        | Tipo de documento                                                     | 1 → N usuarios            |
| `programaacademico`    | idProgramaAcademico    | Programa académico                                                    | 1 → N usuarios            |
| `centrouniversitarios` | idCentroUniversitarios | Centro/campus universitario                                           | 1 → N usuarios            |
| `municipios`           | idMunicipio            | Municipio                                                             | 1 → N usuarios            |
| `tipopoblacion`        | idTipoPoblacion        | Población vulnerable                                                  | 1 → N usuarios            |
| `tipousuarios`         | idTipoUsuarios         | Estudiante/Egresado/Docente/Administrativo                            | 1 → N usuarios            |
| `etapaemprendimiento`  | idEtapaEmprendimiento  | Etapa del emprendimiento (`TipoEtapa`)                                | 1 → N emprendimientos     |
| `sectoreconomico`      | idSectorEconomico      | Sector económico                                                      | 1 → N diagnósticos        |
| `modalidad`            | idModalidad            | Presencial/Distancia                                                  | 1 → N asesorías/eventos   |
| `tipo_evento`          | idTipo_evento          | Tipo de evento                                                        | 1 → N eventos             |
| `fecha_y_Horarios`     | idFecha_y_Horarios     | Bloque de fecha/hora                                                  | 1 → N asesorías / eventos |
| `modulos`              | idModulos              | Controla qué partes de la plataforma están disponibles para cada rol. | 1 → N usuarios (opcional) |

### Entidades de negocio

#### `usuarios`

- **Propósito:** todos los usuarios del sistema (admin, docente, estudiante).
- **Campos importantes:** idUsuarios, Nombre, CorreoInstitucional (único), CorreoPersonal, Password (hash bcrypt — nunca se devuelve), Verificado (0/1), Estado (1 activo / 0 desactivado), Celular, Telefono, Direccion, Genero, EstadoCivil, FechaNacimiento, Semestre, Modalidad, img_perfil, FechaCreacion, FechaActualizacion.
- **Fks:** Roles_idRoles1 → roles, TipoDocumentos_idTipoDocumento → tipodocumentos, ProgramaAcademico_idProgramaAcademico → programaacademico, CentroUniversitarios_idCentroUniversitarios → centrouniversitarios, Municipios_idMunicipio → municipios, TipoPoblacion_idTipoPoblacion → tipopoblacion, TipoUsuarios_idTipoUsuarios → tipousuarios, Modulos_idModulos (opcional) → modulos.
- **Relaciones:** un usuario (estudiante) puede ser propietario de N emprendimientos; puede participar como mentor o estudiante en N asignaciones; puede ser autor de N seguimientos; puede tener N tareas; puede solicitar N asesorías.

#### `emprendimiento`

- **Propósito:** representa el emprendimiento del estudiante. El **Tipo de Emprendimiento** se maneja a través de un catálogo ya creado en BD.
- **Campos importantes:** idEmprendimiento, Nombre, Descripcion, TipoEmprendimiento, SectorProductivo, RedesSociales, Acompanamiento, ActaCompromiso, FechaCreacion, FechaActualizacion.
- **Fks:** EtapaEmprendimiento_idEtapaEmprendimiento → etapaemprendimiento; Usuarios_idUsuarios → usuarios (**propietario** estudiante).
- **Relaciones/cardinalidades:** Propietario (usuarios) **1 → N** emprendimiento; Etapa **1 → N** emprendimiento; Emprendimiento **1 → N** seguimientos; Emprendimiento **1 → N** tareas; Emprendimiento **1 → N** diagnósticos; Emprendimiento **0..1 → N** asignaciones.

#### `asignaciones`

- **Propósito:** vincula un docente (mentor) con un estudiante y opcionalmente un emprendimiento.
- **Campos importantes:** idAsignacion, FechaAsignacion, Estado (activa/inactiva).
- **Fks:** Usuarios_idMentor → usuarios; Usuarios_idEstudiante → usuarios; Emprendimiento_idEmprendimiento (opcional) → emprendimiento.
- **Relaciones/cardinalidades:** Docente **1 → N** asignaciones; Estudiante **1 → N** asignaciones; Emprendimiento **0..1 → N** asignaciones. Aplica el modelo correcto de relación docente↔emprendimiento (no duplicar con columnas en emprendimiento).

#### `seguimientos`

- **Propósito:** nota/anotación de acompañamiento sobre un emprendimiento. No se deben incluir los campos vestigiales `histproal` ni `SeguimientoCol`.
- **Campos importantes:** idSeguimientos, Descripcion, TipoSeguimiento, FechaCreacion, FechaActualizacion.
- **Fks:** Emprendimiento_idEmprendimiento → emprendimiento (**obligatorio**); Usuarios_idUsuarios → usuarios (**autor**).
- **Relaciones/cardinalidades:** Emprendimiento **1 → N** seguimientos; Usuario (autor) **1 → N** seguimientos.

#### `tareas`

- **Propósito:** tarea/plan de trabajo asociado a un emprendimiento y a un estudiante.
- **Campos importantes:** idTareas, Titulo, Descripcion, FechaLimite, Estado (pendiente/completada/vencida), FechaCreacion, FechaActualizacion.
- **Fks:** Emprendimiento_idEmprendimiento → emprendimiento; Usuario_idUsuarios → usuarios (estudiante asignado); Docentes_idDocentes (opcional) → usuarios.
- **Relaciones/cardinalidades:** Emprendimiento **1 → N** tareas; Estudiante **1 → N** tareas; Docente **1 → N** tareas.

#### `asesorias`

- **Propósito:** sesión de acompañamiento entre estudiante y docente.
- **Campos importantes:** idAsesorias, Nombre_de_asesoria, Descripcion, Fecha_asesoria, Comentarios, confirmacion (pendiente/confirmada), Fecha_creacion, Fecha_actualizacion.
- **Fks:** Usuarios_idUsuarios → usuarios (estudiante solicitante); Docentes_idDocentes (opcional) → usuarios; Modalidad_idModalidad → modalidad; Fecha_y_Horarios_idFecha_y_Horarios → fecha_y_Horarios.
- **Relaciones/cardinalidades:** Estudiante **1 → N** asesorías; Docente **1 → N** asesorías; Modalidad **1 → N** asesorías.

#### `diagnosticos` (encabezado), `preguntas_diagnostico` y `respuestas_diagnostico`

- **Propósito:** el diagnóstico deja de ser una única tabla "en desarrollo" con campos sueltos y pasa a ser **data-driven**:
  - `diagnosticos`: **encabezado** del diagnóstico (emprendimiento, sector, fecha, estado, url del informe generado).
  - `preguntas_diagnostico`: **banco de preguntas** cargado desde un archivo **Excel** (sección, orden, enunciado, tipo, opciones, activa).
  - `respuestas_diagnostico`: **respuestas** del emprendedor, con FK a la pregunta y al encabezado.
- **Campos importantes:** `diagnosticos` (idDiagnosticos, FechaDiagnostico, Estado, UrlInforme); `preguntas_diagnostico` (idPregunta, Seccion, Orden, Enunciado, Tipo, Opciones, Activa); `respuestas_diagnostico` (idRespuesta, Valor, FechaRespuesta).
- **Fks:** `diagnosticos.Emprendimiento_idEmprendimiento` → emprendimiento; `diagnosticos.SectorEconomico_idSectorEconomico` → sectoreconomico; `respuestas_diagnostico.Preguntas_idPregunta` → preguntas_diagnostico; `respuestas_diagnostico.Diagnosticos_idDiagnosticos` → diagnosticos.
- **Relaciones:** Emprendimiento **1 → N** diagnósticos (encabezados); Diagnóstico **1 → N** respuestas; Pregunta **1 → N** respuestas.

> Esto resuelve el hallazgo del equipo: *"la definición actual del diagnóstico no está bien estructurada ni relacionada con los demás componentes"*. La matriz de indicadores se sustituye por **preguntas + respuestas** ([§6](#6-reglas-de-negocio), [§16](#16-fuentes-y-trazabilidad-del-alcance-ampliado)).

#### `eventos` y `usuarios_has_Eventos`

- **Propósito:** eventos académicos/culturales y registro de participación.
- **`eventos` campos:** idEventos, Nombre_evento, Descripcion_evento, Capacidad_maxima, Estado, Requiere_registro, Fecha_creacion, Fecha_actualizacion. **Fks:** Tipo_evento_idTipo_evento → tipo_evento; Modalidad_idModalidad → modalidad; Fecha_y_Horarios_idFecha_y_Horarios → fecha_y_Horarios.
- **`usuarios_has_Eventos`:** tabla pivote con PK compuesta (Usuarios_idUsuarios, Eventos_idEventos), campo Estado_asistencia, FKs a usuarios y eventos. Cardinalidad Usuario **N : N** Evento.

#### `codigosverificacion`

- **Propósito:** almacenar los códigos de verificación de correo para validarlos de forma segura.
- **Campos:** idCodigo, CorreoInstitucional, Codigo, Expiracion, Usado (0/1).
- **Relaciones:** varios códigos pueden corresponder a un usuario (por correo). Es la base del flujo REAL de verificación.

#### `caracterizacion` / `valoracion` (resultado del formulario)

- **Propósito:** almacenar el **resultado estructurado por secciones** generado a partir de las respuestas del formulario (caracterización + valoración), con soporte para el **informe descargable**.
- **Campos:** id, Seccion, Resultado, Puntaje, Fortalezas, Oportunidades, Fecha, UrlInforme.
- **Fks:** Emprendimiento_idEmprendimiento → emprendimiento; Diagnosticos_idDiagnosticos (opcional) → diagnosticos.
- **Relaciones:** Emprendimiento **1 → N** caracterizaciones/valoraciones; Diagnóstico **0..1 → N** resultados.

#### `actas` (acta de compromiso y confidencialidad)

- **Propósito:** almacenar el acta firmada y su **estado de revisión**. Complementa el campo `emprendimiento.ActaCompromiso`.
- **Campos:** idActa, UrlArchivo, Estado (pendiente/en revisión/aprobada/rechazada), Observaciones, FechaCarga, FechaRevision.
- **Fks:** Emprendimiento_idEmprendimiento → emprendimiento; Usuarios_idRevisor (opcional) → usuarios.
- **Relaciones:** Emprendimiento **1 → N** actas (histórico); Usuario (revisor) **1 → N** actas revisadas.

#### `notificaciones`

- **Propósito:** avisos dirigidos a usuarios/admin (registro, diagnóstico, asesoría, validación, tareas).
- **Campos:** idNotificaciones, Tipo, Mensaje, Leida (0/1), FechaCreacion.
- **Fks:** Usuarios_idUsuarios → usuarios (**destinatario**).
- **Relaciones:** Usuario **1 → N** notificaciones.

#### `habilitaciones` (desbloqueo de módulos por persona)

- **Propósito:** controlar **qué partes de la plataforma** están habilitadas para cada usuario; es la base del "desbloqueo" tras la validación. (Ya referenciado en la nota del [§5](#5-modelo-de-datos): los módulos se modelan como `habilitaciones` por persona.)
- **Campos:** idHabilitacion, Estado (habilitado/no), Fecha.
- **Fks:** Usuarios_idUsuarios → usuarios; Modulos_idModulos → modulos.
- **Relaciones:** Usuario **1 → N** habilitaciones; Módulo **1 → N** habilitaciones.

### Tablas del proyecto anterior consideradas **obsoletas / no necesarias para el MVP**

- `evaluacioneshabilidades` — evaluación de habilidades no implementada en el flujo principal del MVP.
- `solicitudestutoria` — duplica la funcionalidad de asesorías.
- Tablas no relacionadas con el flujo principal deben descartarse en la reconstrucción.

---

## 6. Reglas de negocio

**Registros / usuarios**

- R1: la contraseña siempre se almacena con bcrypt; nunca se devuelve ni se muestra.
- R2: un usuario no verificado (`Verificado=0`) y desactivado (`Estado=0`) no debe operar.
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

**Etapas**

- R17: las etapas del emprendimiento son un catálogo cerrado:
  1. Análisis y Definición de Requerimientos
  2. Planeación y Diseño Arquitectónico
  3. Desarrollo e Implementación Funcional
  4. Evaluación y Validación de Impacto
     El emprendimiento apunta a una etapa. La etapa **no** es un tipo de seguimiento.

**Tareas**

- R18: crea tareas el docente/admin; las completa el estudiante asignado.
- R19: estados `pendiente/completada/vencida`; se auto-marca vencida por fecha límite.
- R20: estudiante ve sus tareas; docente las de sus asignados; admin todas.
- R21: el avance (% de completadas) es un dato **derivado de BD**, no sintético.

**Asesorías**

- R22: solicita el estudiante; confirma el docente; edita/elimina el autor o admin.
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

- R32: se notifica al **administrativo** ante registro/información, diagnóstico y solicitud de asesoría; y al **estudiante** ante validación, cambio de estado del acta y creación de tareas/asesorías.

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

### dashboard

| Método | Ruta                 | Rol        | Propósito               |
| ------ | -------------------- | ---------- | ----------------------- |
| GET    | `/dashboard/admin`   | admin      | Métricas globales       |
| GET    | `/dashboard/teacher` | docente    | Métricas del docente    |
| GET    | `/dashboard/student` | estudiante | Métricas del estudiante |

### Catálogos (solo lectura; proteger según conveniencia)

| Método | Ruta                                                                                                                                                                                | Propósito        |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| GET    | `/roles`, `/type-doc`, `/type-users`, `/uni-centers`, `/type-pop`, `/municipalities`, `/academic-programs`, `/entrep-stage`, `/econo-sector`, `/mode`, `/type-event`, `/date-times` | Listar catálogos |

### event (si aplica)

| Método | Ruta                  | Rol  | Propósito             |
| ------ | --------------------- | ---- | --------------------- |
| GET    | `/event`              | auth | Listar eventos        |
| POST   | `/event/:id/register` | auth | Registrarse en evento |
| DELETE | `/event/:id/register` | auth | Desregistrarse        |

---

## 8. Frontend

### Administrador

| Pantalla                                 | Información que debe mostrar                                                                                                                             |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Dashboard                                | Métricas globales reales: total usuarios (por rol), emprendimientos, asignaciones activas, tareas, asesorías; distribución de emprendimientos por etapa. |
| Gestión de usuarios                      | Lista/tabla de usuarios, crear/editar/activar/desactivar/cambiar rol, ver perfil.                                                                        |
| Gestión de docentes                      | Lista de docentes y sus asignaciones.                                                                                                                    |
| Gestión de emprendimientos               | Lista de todos los emprendimientos, ver detalle, crear, editar etapa/datos.                                                                              |
| Asignaciones                             | Crear/ver/eliminar/reasignar asignaciones (docente + estudiante + emprendimiento).                                                                       |
| Validación de emprendedores              | Validar/activar o rechazar emprendedores; revisar y aprobar el **acta de compromiso**.                                                                    |
| Gestión de diagnóstico                   | Banco de preguntas (Excel), resumen del diagnóstico, filtros e **informe descargable**.                                                                    |
| Gradar/s see Aspirante (plan de trabajo) | Plan de trabajo por emprendimiento (opcional).                                                                                                           |
| Perfil                                   | Datos propios del admin.                                                                                                                                 |

### Docente / Mentor

| Pantalla                  | Información que debe mostrar                                                                                                 |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Dashboard                 | Métricas de sus asignados: nº estudiantes, emprendimientos asignados, % avance de tareas, nº asesorías/notas de seguimiento. |
| Emprendimientos asignados | Solo los emprendimientos en los que es mentor (vía asignaciones), con su etapa y datos.                                      |
| Seguimiento               | Crear/ver/editar/eliminar notas del emprendimiento seleccionado.                                                             |
| Asesorías                 | Ver/solicitar/confirmar asesorías de sus estudiantes.                                                                        |
| Tareas                    | Crear/editar tareas de sus asignados; ver estados y avance.                                                                  |
| Diagnóstico               | Ver/crear diagnóstico del emprendimiento (según alcance).                                                                    |
| Perfil                    | Datos propios.                                                                                                               |

### Estudiante

| Pantalla                 | Información que debe mostrar                                                                                      |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| Dashboard                | Su emprendimiento, etapa actual, % avance de sus tareas, tareas pendientes/vencidas, nº seguimientos y asesorías. |
| Mi emprendimiento        | Detalle del emprendimiento propio + etapa.                                                                        |
| Seguimiento              | Historial (solo lectura) del seguimiento de su emprendimiento.                                                    |
| Asesorías                | Solicitar y consultar sus asesorías.                                                                              |
| Tareas / plan de trabajo | Ver sus tareas y marcarlas como completadas.                                                                      |
| Progreso                 | Etapa actual y avance de tareas.                                                                                  |
| Diagnóstico              | Ver su diagnóstico.                                                                                               |
| Caracterización/valoración | Diligenciar el formulario (por secciones) y ver el **feedback inmediato** (fortalezas / lo que falta).           |
| Acta de compromiso       | Descargar la plantilla, subir el acta firmada y consultar su **estado de revisión**.                              |
| Notificaciones           | Ver sus avisos (validación, acta, tareas, asesorías) y marcarlos como leídos.                                     |
| Perfil                   | Editar sus datos propios.                                                                                         |

**Componentes compartidos:** Login, Register, PrivateRoute, sidebars por rol, menú de usuario, cliente `api.js`, componentes de UI (tarjetas, tablas, formularios, gráficos).

**Navegación/autorización:** `PrivateRoute` con `allowedRoles`; redirige a login si no autenticado y a "no autorizado" si el rol no aplica; los menús solo muestran las rutas del rol; sin enlaces muertos.

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
- Un único campo de rol (`Roles_idRoles1`): 1=Admin, 2=Estudent, 3=Teacher.
- Autenticación con JWT (8 h) + bcrypt + verificación de correo real en backend.
- Modelo de asignación único (tabla `assignments` mentor↔estudiante↔emprendimiento).
- Emprendimiento con propietario-estudiante (`User_idUsers`) + etapa (`entrepreneurialStage`).
- Seguimiento ligado a un emprendimiento; autor registrado.
- Tareas ligadas a emprendimiento y estudiante; estados y avance derivados de BD.
- Dashboards con métricas reales (no mock).
- Secretos solo por variables de entorno; `.env` ignorado; `.env.example` sin secretos.

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
- **Alcance del rol de auditor (rol 4):** permisos y qué información consulta. **Pendiente** (§16).
- **Validación del emprendedor:** campos obligatorios del registro, criterios de aprobación y **qué funcionalidades están disponibles antes** de la validación. **Pendiente** (§16).
- **Diagnóstico:** rúbrica respuestas → fortalezas/oportunidades; formato y contenido del **informe descargable**; filtros necesarios. **Pendiente** (§16).
- **Acta de compromiso:** tiempo de revisión y qué ocurre si se rechaza. **Pendiente** (§16).
- **Documentos de referencia no disponibles:** `control.pdf` y el **Excel de preguntas** (§16).

---

## 12. MVP mínimo

### P0 — Imprescindible

- Autenticación: registro, login, logout, verificación de correo real en backend (OTP 8 dígitos/5 min), JWT, cierre de rutas por rol.
- Usuarios y roles (admin gestiona usuarios; edición de perfil).
- Emprendimientos: crear (admin), consultar con alcance, ver detalle y etapa. Historial de emprendimientos.
- Asignaciones: admin asigna docente a estudiante (+ emprendimiento); docente consulta sus asignados; estudiante su/s mentor/es.
- Seguimiento: docente registra notas sobre un emprendimiento; estudiante consulta historial. Adjuntos (hasta 500MB).
- Tareas: docente crea, estudiante completa, estados y avance derivados de BD. Adjuntos (hasta 500MB).
- Asesorías: estudiante solicita, docente confirma, ambos consultan. Notificaciones en tiempo real.
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

### P2 — Opcional / post-MVP

- Comparativa de emprendimientos.
- Evaluación de habilidades (no estaba funcional).
- Notificaciones/push.
- Internacionalización.
- Rol de auditor (una vez definido su alcance).

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
8. Un estudiante puede **solicitar una asesoría** y el docente **confirmarla**. Se reciben notificaciones en tiempo real.
9. Los **dashboards muestran datos reales** de BD (conteos y % de avance correctos por rol).
10. Un estudiante **no puede** ver ni modificar recursos de otros; un docente **no puede** ver emprendimientos ajenos.
11. El sistema **no expone** credenciales, secretos, ni códigos OTP en ninguna respuesta.
12. La base de datos se **inicializa completa** en un entorno Docker limpio (todas las tablas necesarias). El diseño es totalmente responsive.
13. Un emprendedor con el **registro completo** queda pendiente y **no accede** a las funcionalidades hasta que el administrativo lo **valide y active**.
14. El emprendedor puede **diligenciar el formulario de diagnóstico** (cargado desde Excel), y el sistema **genera** la caracterización/valoración con **feedback inmediato** e **informe descargable**.
15. El emprendedor puede **subir el acta de compromiso** firmada y el administrativo puede **aprobarla/rechazarla**.
16. Se generan **notificaciones** al administrativo (registro, diagnóstico, asesoría) y al estudiante (validación, acta, tareas/asesorías).

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

- **Campos obligatorios** del registro y **criterios de validación** del emprendedor.
- **Funcionalidades disponibles antes** de la validación.
- **Permisos** del rol de **auditor** (rol 4).
- **Rúbrica** del diagnóstico (respuestas → fortalezas/oportunidades) y **formato del informe descargable**.
- **Tiempo de revisión** del acta y qué pasa si se rechaza.
- **Estructura definitiva** de las tablas y relaciones ([§5](#5-modelo-de-datos)).

### 16.3 Documentos de referencia

| Documento | Uso previsto | Estado |
| --------- | ------------ | ------ |
| `control.pdf` | Referencia para el formulario de registro. | ⚠️ No está en el repositorio |
| `ficha de carácter y formulación.pdf` | Referencia para caracterización y formulación. | ⚠️ Material local del área (no versionado); falta confirmar equivalencia |
| `Valoración y Diagnóstico.pdf` | Referencia para el diagnóstico y su valoración. | ✅ Material local del área (no versionado) |
| **Archivo Excel de preguntas** | Fuente para estructurar el formulario de diagnóstico. | ⚠️ Pendiente |

### 16.4 Documentación de trabajo (esta rama)

- **Material local del área (no versionado):** inventario de insumos, flujo real de atención y pendientes del estudiante — se mantienen fuera del repositorio por contener datos personales.
- `docs/CONSOLIDACION-ANOTACIONES.md` — anotaciones del equipo reorganizadas (diagnóstico, registro/validación, roles, BD, Git).
- `CORRECCIONES-VISTAS-ESTUDIANTE.md` — hallazgos validados del prototipo.

### 16.5 Sobre datos sensibles y Git

- Los insumos del área contienen **datos personales** (nombres, cédulas, teléfonos, correos) → aplica la **Ley 1581 de 2012**. **No** versionar estos archivos sin autorización; usar datos ficticios.
- Se propone una **rama de inyección de datos** para centralizar la carga y evitar que cada integrante la introduzca manualmente.

---

_Fin del documento. Autocontenido, sin secretos, diseñado para reconstrucción limpia desde cero._
