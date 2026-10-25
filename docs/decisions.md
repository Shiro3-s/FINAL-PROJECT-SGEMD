# Decisiones de arquitectura y decisiones pendientes — SGEMD MVP

> Documento vivo. Se revisa en **cada puerta de etapa** (`MASTER_IMPLEMENTATION_PROMPT.md` §16).
> Última actualización: 2026-10-25 · rama `feat/mvp-implementation`.

## 0. Regla de oro

Una **suposición registrada aquí nunca se convierte en requisito confirmado**. Se queda
etiquetada `suposición (decisión pendiente X)` hasta que el propietario responda
(master §20.1). Si un valor no está en las fuentes, no se implementa: se anota.

## 1. Jerarquía de fuentes (arbitraje)

Instrucción del propietario para este build:

| Tema | Fuente que manda | Nota |
|---|---|---|
| Tablas, columnas, FK, enums, nulabilidad, restricciones | `docs/diagrama-clases.md` **v2** | 27 entidades + 14 catálogos, atributo por atributo |
| Estilos, layout, componentes, copy | `prototype/` — **`lib_css.py` para valores**, `DESIGN.md` para intención, los 73 `.html` como referencia | Si `DESIGN.md` y `lib_css.py` discrepan, gana `lib_css.py` |
| Alcance, reglas, API, etapas, tests, seguridad | `MASTER_IMPLEMENTATION_PROMPT.md` **v1.3** | Incluye `CAMBIOS_v1.3.md` (D22) |

Consecuencia práctica: donde `README.md` §5 y el diagrama v2 no coinciden en columnas,
**manda el diagrama** y la diferencia queda registrada como discrepancia (§6, #18), no
como columna añadida por iniciativa propia.

---

## 2. ADR de stack

| ID | Decisión | Estado | Justificación | Alternativa rechazada |
|---|---|---|---|---|
| ADR-01 | React SPA + React Router | Adoptada | 62 vistas con layout compartido y rutas con guarda | Plantillas server-side, Next.js |
| ADR-02 | Vite | Adoptada | Tooling estándar para SPA React | Create React App |
| ADR-03 | Node + Express + TypeScript, capas `routes → controllers → services` | Adoptada | Stack declarado por el equipo; capa HTTP fina, servicios testeables | NestJS, Django/Spring |
| ADR-04 | PostgreSQL 17 + `pg` pool | Adoptada | 41 tablas relacionales, agenda transaccional | MongoDB, SQLite |
| ADR-05 | Un único `schema.sql` montado en el init del contenedor | Adoptada (D16) | No hay datos que migrar; la BD se recrea | Migraciones numeradas (se reevalúan antes del primer dato real) |
| ADR-06 | JWT 8 h en cookie `sgemd_session` `HttpOnly; Secure; SameSite=Strict` + bcrypt | Adoptada (D15) | Quita el token del alcance de XSS; el estado del usuario se relee por petición | JWT en `localStorage`, sesión en servidor |
| ADR-07 | Caddy como reverse proxy (TLS, estáticos, `/api`, límites) | Adoptada (D15) | Un solo origen ⇒ cookie `SameSite=Strict` y sin CORS | nginx, exponer Node directo |
| ADR-08 | TypeScript `strict` + `zod` en el workspace `shared/` | Adoptada (D17) | Los enums y DTO son la superficie de fallo; tipos por `z.infer` | JavaScript plano |
| ADR-09 | TanStack Query para estado de servidor | Adoptada (D18) | 62 vistas paginadas con estados de carga/error/vacío e invalidación | `useEffect` a mano, Redux/Zustand |
| ADR-10 | SSE para notificaciones | Adoptada (D2) | Canal unidireccional que encaja con Express y la cookie | Polling, Socket.io |
| ADR-11 | Inter autoalojada con `@fontsource/inter` | Adoptada (D21) | Ley 1581/2012: sin peticiones a terceros con IP del usuario | Google Fonts |
| ADR-12 | Reportes con `exceljs` + (`pdfkit` \| `pdfmake`) | Adoptada (D6) | XLSX/CSV y PDF sin navegador headless | Puppeteer |
| ADR-13 | Storage en filesystem local + metadatos en BD; evidencias dentro del respaldo `Completo` | Adoptada (D13, D22) | Evidencia ≤500 MB, sin cuentas cloud | S3/MinIO, blobs en Postgres |
| ADR-14 | Docker Compose (Caddy, backend, postgres, build del frontend) | Adoptada | Inicialización limpia y reproducible | Kubernetes, PaaS |
| ADR-15 | Mail: Microsoft 365 OAuth2 o relay SMTP institucional, seleccionado por `MAIL_TRANSPORT`; transporte de archivo en dev/tests | Adoptada (D14) | La casilla es Outlook/M365 y el SMTP con contraseña se está retirando | SMTP genérico con usuario/clave, API de terceros |
| ADR-16 | Respaldos de evidencia por **instantánea incremental** (`rsync --link-dest`) | Adoptada (D22) | Copia completa y navegable; lo no modificado son hard links y no ocupa disco | Tar completo diario (v1.2), descartado |

**Pinning**: solo PostgreSQL 17 está fijado por el repositorio. El resto se fija a la versión
LTS/estable al instalar, con lockfile commiteado, y se anota abajo (§7).

---

## 3. Decisiones del propietario (D15–D22)

| ID | Decisión | Consecuencia | Abierto |
|---|---|---|---|
| D15 | JWT 8 h en cookie `HttpOnly; Secure; SameSite=Strict`; el middleware relee el usuario en cada petición; Caddy termina TLS | Un solo origen, sin CORS, sin token en JS | Hostname y certificado fuera de localhost (TI). Logout y reset de contraseña no revocan un JWT ya emitido |
| D16 | `schema.sql` único, sin migraciones | La BD se recrea mientras no haya datos reales | Reevaluar antes del primer despliegue con datos |
| D17 | TypeScript `strict` en backend y frontend; tipos derivados de `zod` en `shared/` | Enums una sola vez en `shared/src/enums.ts`; script los contrasta con los `CHECK` | — |
| D18 | TanStack Query para todo dato de servidor | Redux/Zustand quedan descartados para estado de servidor | — |
| D19 | `recharts` vs SVG a mano: se decide en la Etapa 10 tras construir los tres gráficos de las dos formas | Los gráficos viven detrás de una interfaz única hasta entonces | Elección final en Etapa 10 |
| D20 | **No decidida por el propietario.** Default: OTP como HMAC-SHA256 con `OTP_HMAC_SECRET` | Cambiar el esquema es un cambio local en el servicio `auth` | Confirmar D20 |
| D21 | Inter autoalojada; sin Google Fonts en ejecución | Verificado por T30 | — |
| D22 | Evidencias en instantáneas incrementales; `backups/` en disco distinto de `storage/`; procedimiento manual de restauración y simulacro en Etapa 12 | Reemplaza el tar completo de v1.2 | Disco separado y copia fuera del servidor (TI; preservar enlaces con `rsync -aH`). Retención por tamaño y alerta de espacio: no están en requisitos, se proponen a la Coordinadora |

---

## 4. Defaults importantes (D1–D14)

| ID | Pregunta | Default adoptado | Reversión |
|---|---|---|---|
| D1 | Límite de subida: 500 MB (FR-008) vs "10 MB" del prototipo | **500 MB**, `configuracion_programa.upload_max_mb`; el texto del prototipo es defecto (§8 #2) | Baja (config) |
| D1b | Archivos por entidad: el JS del prototipo limita a 5, ningún requisito lo fija | `upload_max_files_per_entity`, default 5 | Baja (config) |
| D2 | Tiempo real | **SSE** detrás de `NotificationChannel`; Caddy sin buffering | Media (un adaptador) |
| D3 | Dominio de correo | `uniminuto.edu` y `uniminuto.edu.co` desde una lista en configuración; sin regla dominio→rol hasta que el propietario la declare | Baja (config) |
| D4 | Alta de emprendimiento por el estudiante | Solo admin en el MVP; el estudiante edita nombre, descripción y redes | Media |
| D5 | Tope de paralelos | Un activo + como máximo un paralelo pendiente/aprobado | Baja (config) |
| D6 | Librería XLSX/PDF | `exceljs` + (`pdfkit` \| `pdfmake`); la elección se hace en Etapa 10 | Baja |
| D7 | Retención de respaldos | `backup_retention_days`, default 30 | Baja (config) |
| D8 | Copy e iconografía de notificaciones | Copy del prototipo y estilo de iconos de la paleta | Baja |
| D9 | Retención y filtros de auditoría | Tabla append-only; lista paginada; sin purga en el MVP | Baja |
| D10 | Volumen del seed | Solo lo que necesita una demo; nunca datos reales | Baja |
| D11 | Deltas visuales al portar | Se registran en `docs/design-parity.md`; no se "mejora" en silencio | — |
| D12 | Enmascarado del auditor | Enmascarar documento y contacto; exponer agregados y metadatos del expediente | Baja (serializador) |
| D13 | Alcance del respaldo | `Completo` = dump + instantánea de evidencias (D22); `Parcial` = solo dump | Media |
| D14 | Proveedor de correo | OAuth2 (Nodemailer XOAUTH2) o relay institucional según `MAIL_TRANSPORT`; archivo en dev/tests | Baja (env) |

---

## 5. Decisiones pendientes

### 5.1 Bloqueantes para su funcionalidad

| ID | Pregunta | Qué bloquea | Comportamiento interino |
|---|---|---|---|
| AQ-07 | ¿Qué puede hacer una cuenta `Limitado`? | La matriz de autorización del espacio del estudiante | Matriz como tabla en `policy/accountState.ts`; default opción **A** del dossier (perfil + acta + notificaciones). Diagnóstico y alta de emprendimiento no habilitados para `Limitado` |
| AQ-06 | ¿Qué campos y criterios validan la activación del emprendedor? | Checklist de activación y reglas de unicidad | 7 campos del prototipo + checkbox + documento/correo únicos; checklist detrás de una clave de configuración |
| AQ-09 | Rúbrica del diagnóstico: pesos por dimensión, regla de fortalezas/oportunidades, formato del informe | Cualquier puntaje | Instrumento, almacenamiento y reporte sin puntaje; respuesta explícita "rúbrica no configurada" |
| AQ-12 | Faltan `control.pdf` y el Excel de preguntas | Banco y rúbrica definitivos | 22 preguntas transcritas de `prototype/estudiante/diagnostico.html` con `Origen='Prototipo'`, seed marcado provisional |

### 5.2 No bloqueantes

| ID | Pregunta | Manejo |
|---|---|---|
| AQ-10 | Plazo de revisión del acta (5 días hábiles) y efecto pleno del rechazo | Rechazo con motivo obligatorio + notificación; sin plazo/recordatorio |
| AQ-06 residual | Campos extra de caracterización en el registro | No se implementan; viven en "Configuración" |

### 5.3 Huecos del diagrama de clases (documento v2, "Pendientes de confirmar")

| # | Hueco | Comportamiento interino | Bloquea |
|---|---|---|---|
| P-1 | Dónde se guarda la **fecha reprogramada** de una asesoría (no hay columna) | `accept` y `reject` funcionan; `repropose` responde `422` con código `REPROPOSE_NOT_CONFIGURED` | Cerrar Etapa 8 |
| P-2 | Quién **revisó** el diagnóstico y su recomendación (no hay columnas) | La revisión docente muestra el resultado en solo lectura, sin escritura | Nada (Etapa 9 parcial) |
| P-3 | `Diagnosticos.UrlInforme`: ¿se genera al vuelo o se guarda? | Se genera al vuelo con `GET /diagnosis/:id/report`; la columna queda nula | Nada |
| P-4 | `Valoracion.Dimension` (6 valores) y `AuditoriaEventos.Accion` (lista de acciones) | Columna creada sin `CHECK` de dimensión; tabla `valoracion` vacía. Acciones: lista mínima documentada en `shared/src/enums.ts` | AQ-09 para dimensión |
| P-5 | `Notificaciones.Tipo` no figura en el master §7.2 | Se usan los 7 valores del diagrama como `CHECK`, marcado como **inferido** | Nada |
| P-6 | `CodigosVerificacion.Proposito` es nuevo (el master tiene T39 pero ninguna tabla de tokens) | Se implementa con `Verificación` · `Recuperación`, marcado como **inferido** | Nada |
| P-7 | El diagrama v2 no tiene columna para la **imagen de perfil**, pero el master §13.3 declara `POST /users/:id/avatar` | El endpoint queda **diferido**; no se inventa la columna. Alternativa a decidir: reutilizar `adjuntos` con un tipo de uso | Cerrar el perfil P1 |
| P-8 | `Habilitaciones.Estado` es `enum` en el diagrama, pero la tabla de enumeraciones no lista sus valores | Columna creada **sin `CHECK`** y tabla vacía; los valores llegan con AQ-07 | Nada (Etapa 3/4) |
| P-9 | Cuatro columnas son `enum` en el diagrama y **no** tienen lista canónica: `PreguntasDiagnostico.Tipo`, `PreguntasDiagnostico.Origen`, `UsuariosHasEventos.Estado_asistencia` y `RecomendacionesEvento.Estado` | `Tipo` y `Origen` se siembran con valores **provisionales** (`Texto` · `Texto largo` · `Selección única`; `Prototipo`) y quedan sin `CHECK`; las otras dos no tienen `CHECK` y sus tablas permanecen vacías | Nada (Etapa 9 para el banco definitivo) |
| P-10 | `Usuarios.Codigo` no se declara único en el diagrama y ningún requisito lo exige; el prototipo usa `EMP-###`, `DOC-###` y el código estudiantil | No se crea `UNIQUE`. El servicio de usuarios validará duplicados al crear (Etapa 4) y se confirma con la Coordinadora si debe ser único por rol | Nada |
| P-11 | El master §15 exige **cooldown de reenvío** del OTP pero no fija los segundos | **60 s**, configurable con `OTP_RESEND_COOLDOWN_SECONDS`; antes responde `429 OTP_COOLDOWN` con `Retry-After` | Nada (valor de producto a confirmar) |
| P-12 | El master §15 exige límites en login, registro, OTP y recuperación, pero **no fija umbrales** | Valores iniciales por IP en `src/modules/auth/routes.ts` (registro 10/h, login 10/min por IP+correo, verificación 15/min, reenvío/recuperación 10/h). Se revisan con el uso real | Nada (ajustable en código) |
| P-13 | `CodigosVerificacion` no tiene columna de **fecha de creación**, así que no se puede medir el cooldown directamente | Se deriva de `expiracion - vigencia` (5 min): `creado ≈ expiracion - 5 min`. Si se confirma el hueco, se añade `fecha_creacion` en la Etapa 12 | Nada |
| P-14 | El prototipo exige la casilla de **autorización de tratamiento de datos**, pero el diagrama no tiene columna para el consentimiento ni su fecha | Se valida como obligatoria (`aceptaTratamiento: true`) y **no se persiste**. Se propone `usuarios.fecha_consentimiento` para la Etapa 12, previa confirmación | Nada (cumplimiento Ley 1581 a revisar) |

| P-15 | `POST /users/:id/reject` está en el master §13.3, pero el diagrama **no tiene un estado «Rechazado»** para la cuenta y AQ-06 (criterios de validación) sigue abierta | El rechazo **deja la cuenta en `Limitado`**, exige motivo, lo guarda en la auditoría y notifica al titular. No se inventa un estado ni se borra la cuenta | Nada (AQ-06 para los criterios) |
| P-16 | R36 dice que la baja es «lógica y **reversible**», pero el master §13.3 no declara ningún endpoint para restaurar una cuenta dada de baja | La baja solo marca `fecha_eliminacion`; la fila y sus datos siguen ahí. La restauración se hará con un endpoint propio cuando se confirme (Etapa 12) | Nada |
| P-17 | NFR-002 describe al **Auditor** como «solo lectura», pero §13.3 no le asigna ningún endpoint de usuarios y AQ-08 sigue pendiente | Se deniega por defecto: los listados y la gestión de cuentas son solo del Admin. El alcance del Auditor se fija con el módulo de auditoría | Nada (Etapa 11) |
| P-18 | «CRUD de usuarios» podría incluir cambiar el **rol**, pero ninguna regla lo pide y el cambio afecta asignaciones, topes docentes y auditoría | El rol es **inmutable** en `PUT /users/:id` (`.strict()` → `400`). Cambiar el rol exigirá una operación dedicada con su propia validación | Nada |
| P-19 | El prototipo resuelve una solicitud de **Cita** con «Docente sugerido», «Fecha propuesta» y «Motivo», pero `solicitudes` no tiene esas columnas y `asesorias` exige un docente y un bloque de `fecha_y_horarios` | Aprobar una `Cita` **no crea la asesoría**: solo resuelve la solicitud (efecto `null` en la auditoría). La coordinación registra la asesoría en su módulo (Etapa 8) | Cerrar Etapa 8 |
| P-20 | `solicitudes` solo tiene `detalle` (texto libre): no hay columnas para «Emprendimiento actual», «Nuevo emprendimiento», «Sector», «Docente sugerido» ni «Fecha propuesta» del prototipo | Todo lo que no es `tipo` + `emprendimientoId` viaja en `detalle`. No se inventan columnas; si la Coordinadora necesita filtrar por esos datos, se añaden en una etapa posterior | Nada (diseño de la bandeja) |
### 5.4 Inferencias de esta etapa que no son huecos del diagrama

| Elemento | Qué se infirió | Dónde queda |
|---|---|---|
| `ConfiguracionPrograma.TipoDato` | El diagrama lo declara `string`; se fijan cuatro valores (`int`, `bool`, `text`, `date`) para tipar el valor en la interfaz | `TIPOS_DATO_CONFIGURACION` en `shared/src/enums.ts`; `CHECK` en el esquema |
| `Adjuntos.TipoMime` | Lista blanca de MIME del master §15 (JPG/JPEG, PNG, PDF); `jpg` y `jpeg` comparten `image/jpeg` | `TIPOS_MIME_ADJUNTO` en `shared/src/enums.ts` |
| Motivo obligatorio | `CHECK` en `emprendimiento` (BR-004), `actas` (BR-009), `solicitudes` (bandeja única) y `tareas` (R19b), además de la validación del servicio | `database/schema.sql` |

### 5.5 Decisiones tomadas en la Etapa 4

| Tema | Decisión | Motivo |
|---|---|---|
| Alta administrativa | La cuenta nace **`verificado = true`**, con una contraseña aleatoria inservible y una invitación por correo con un código de `Recuperación` para que el titular fije su contraseña | La coordinación ya conoce el correo institucional y la invitación va a esa misma dirección; exigir el OTP de registro dejaría la cuenta inutilizable |
| Estado inicial | `Activo` por defecto; `Limitado` es optativo en el alta; `Inactivo` no se ofrece al crear | Es lo que hace el prototipo (`form-nuevo-docente` / `form-nuevo-estudiante`) y el ciclo de vida no empieza en `Inactivo` |
| Correo de bienvenida | Se envía al pasar a `Activo`; si el transporte falla, se registra y **no** se revierte el cambio | El hecho de negocio es el cambio de estado, no el correo |
| Notificación de estado | Se escribe en la **misma transacción** que el cambio y la auditoría | Nunca hay un cambio sin rastro ni un aviso de algo que no ocurrió |
| Auto-gestión | Nadie cambia el estado ni da de baja su propia cuenta | Con un único administrador activo, el autodesplazamiento dejaría el sistema sin quien lo revierta |
| Rol | Inmutable en la edición (P-18) | Cambiarlo altera asignaciones, topes y semántica de la auditoría |
| Baja lógica | Solo marca `fecha_eliminacion`; no borra adjuntos porque todavía no existen (Etapa 6/7) | BR-006 pide el borrado físico de adjuntos; se implementará con el módulo de adjuntos |

### 5.6 Decisiones tomadas en la Etapa 5

| Tema | Decisión | Motivo |
|---|---|---|
| Alta de emprendimiento | Solo el administrador (`POST /entrepreneurship`); nace `Pendiente`, `avance = 0`, código `EMP-###` y la etapa de `configuracion_programa.etapa_inicial` | R37 y D4: el prototipo no tiene formulario de registro para el estudiante; el avance se deriva de las tareas (R21), nunca lo envía el cliente |
| Autorización de paralelo | `esParalelo` es la **autorización expresa** de BR-004, no un dato descriptivo: sin ella, un segundo emprendimiento vigente responde `422 PARALLEL_REQUIRED`; el primero no puede ser paralelo (`422 NOT_A_PARALLEL`) | El prototipo la resuelve con un botón de la bandeja, no con un campo del formulario |
| Tope de paralelos | `paralelos_maximos` (=1, D5) cuenta solo los no rechazados; al alcanzarlo: `422 PARALLEL_LIMIT_REACHED` | Un `Rechazado` se conserva con su motivo pero no ocupa cupo |
| Edición | El administrador cambia nombre, descripción, redes, sector, etapa y sede; el estudiante propietario solo nombre, descripción y redes (`403 FIELD_NOT_ALLOWED` para el resto) | Master §13.2; el propietario, el estado, el motivo, el paralelo y el avance no se editan por esta vía (`.strict()` → `400`) |
| Lectura | Admin: todos; estudiante: los propios; docente: los que tiene con `asignaciones.estado = 'activa'`; fuera de alcance: `404` | R4, R5, R25 y NFR-002: no se revela la existencia de un expediente ajeno |
| Aprobación y rechazo | Solo desde `Pendiente` (`422 INVALID_APPROVAL_STATE`); el rechazo exige motivo y lo guarda en `motivo_rechazo`; auditoría y notificación en la misma transacción | BR-004, T11, T12. El `UPDATE … WHERE estado = 'Pendiente'` impide aplicar la decisión dos veces |
| Catálogos | 13 exigen sesión; `GET /type-doc` es público porque lo necesita el registro. Ninguno exige cuenta `Activo` | Alimentan también la edición del perfil, que AQ-07 opción A deja disponible a una cuenta `Limitado` |
| Bandeja de solicitudes | `POST /requests` solo exige sesión: una cuenta `Limitado` o `Inactivo` debe poder pedir su desbloqueo. `Paralelo` y `Cita` exigen `Activo`, rol Estudiante y un emprendimiento propio vigente (`Paralelo`, además, `Aprobado`) | La política de cuenta no puede impedir el único camino para salir de `Limitado` |
| Resolución | Cada aprobación aplica su efecto **una sola vez** (`SELECT … FOR UPDATE` + `UPDATE … WHERE estado = 'Pendiente'` → `422 REQUEST_ALREADY_RESOLVED`): Desbloqueo → `Activo`; Paralelo → `es_paralelo = TRUE` con recuento del tope; Cita → sin efecto de dominio (P-19) | T36: nunca una solicitud aprobada sin efecto ni un efecto duplicado |
| Rechazo de solicitudes | Exige motivo, no aplica ningún efecto de dominio y notifica al solicitante | R38 |
| Paginación | `pageSize` por defecto **25** (máximo 100) en todos los listados, también en `GET /users` | Master §13.3 |
| Aviso a la coordinación | Crear una solicitud notifica a todos los administradores `Activo` con la URL de la bandeja | El contador de pendientes es la señal; no hay otro canal en el MVP |


---

## 6. Discrepancias verificadas

### 6.1 Registradas por el master (§20.5)

| # | Discrepancia | Resolución en este build |
|---|---|---|
| 1 | El prototipo rechaza con motivo vacío (`admin/solicitudes.html`) | Motivo obligatorio en la API (T12) |
| 2 | Pista de subida "10 MB" vs 500 MB | 500 MB configurable |
| 3 | Porcentajes de diagnóstico sin fórmula | Bloqueado por AQ-09; sin puntaje |
| 4 | `emprendimiento-detalle` permite diagnóstico y `estado-seguimiento` lo bloquea | Bloqueado por AQ-07; un solo módulo de política |
| 5 | Sin pantallas de acta, auditor ni alta de emprendimiento por el estudiante | Acta P1; auditor P2; alta diferida (D4) |
| 6 | Alias de fase "Ideación · Ejecución · Crecimiento · Consolidación" vs `faseplan` | Se usa `faseplan` literal (§7.2) |
| 7 | `admin/usuarios.html` dice que el admin solo cambia el estado de acceso | Gana FR-011: CRUD completo |
| 8 | Dominios de correo inconsistentes | D3: `uniminuto.edu` / `uniminuto.edu.co`; mapeo por rol sin definir |
| 9 | `prototype/DESIGN.md` lista un módulo docente "Seguimiento" | Obsoleto: "Registrar avance" + columna Evidencia (ver #23) |
| 10 | 12 scripts de auditoría citados en `prototype/README.md` que no existen | No se afirma que corrieron; se escriben pruebas reales |
| 11 | Erratas de la tabla de API de `README.md` §7 (`estudent`, `autor/admin`) | Se resuelven con la matriz de §13.3 y se documentan en `docs/api.md` |
| 12 | Flujos P0 dependen de capacidades P1 (acta para asignar; auditoría y notificaciones para los tests de ciclo de vida) | Servicio de auditoría y `notify()` desde la Etapa 4; tabla `actas` y fixtures en la Etapa 6 |
| 13 | BR-006 llama "reversible" al borrado pero borra archivos físicamente; `EvidenciaRequerida` existe aunque BR-007 es incondicional | Suposición: desactivar/ocultar es reversible; el borrado confirmado es lógico en la fila e irreversible para archivos (el diálogo lo dice); `evidencia_requerida` siempre verdadero |
| 14 | Los AC de la §19.1 original contradecían el mapeo AC→test de §7.3 | §19.1 derivada de §7.3; verificada contra `README.md` §13 en la Etapa 0 (25 AC confirmados) |
| 15 | Nombres de recurso mezclan singular y plural (`/task`, `/event`, `/assignments`, `/requests`) | Se conservan por trazabilidad a `README.md` §7; segmentos en inglés; lista final en `docs/api.md` |
| 16 | `schema.sql` único (D16) choca con resoluciones de AQ que cambian tablas cuando ya haya datos | Se mantiene por decisión del propietario; solo recreación hasta el primer dato real |
| 17 | BR-006 borra evidencias del disco pero los respaldos `Completo` las conservan hasta la retención | **Resuelto por retención documentada, no por purga** (ver §6.2) |

### 6.2 Detalle de la #17 (CAMBIOS_v1.3, bloque B)

1. Los respaldos son inmutables; no se reescribe nada.
2. Por los hard links, un archivo borrado desaparece del disco cuando expira la última
   instantánea que lo contiene: como máximo `backup_retention_days` (30 por defecto) después
   del borrado.
3. El diálogo de confirmación de BR-006 lo dice, con el **valor vigente** de la configuración.
4. El texto de tratamiento de datos del registro debe mencionar las copias de respaldo; lo
   redacta la institución (pendiente, no lo inventa este proyecto).
5. Descargas y exportaciones de respaldos quedan en `auditoria_eventos`.
6. El procedimiento de restauración exige reaplicar los borrados registrados en la auditoría
   posteriores a la fecha del respaldo.

### 6.3 Nuevas, detectadas en la Etapa 0 al contrastar las tres fuentes

| # | Discrepancia | Resolución |
|---|---|---|
| 18 | `README.md` §5 lista en `usuarios` columnas que el diagrama v2 no tiene (`img_perfil`, `correo_personal`, `celular`, `fecha_nacimiento`, `genero`, `estado_civil`, `tipo_posgrado`, `semestre`, `fecha_grado`, `area_conocimiento`, `horas_asesoria_semana`, `cargo`, `zona_horaria`, …) | **Manda el diagrama**: no se crean. Consecuencia: `POST /users/:id/avatar` (master §13.3) queda **diferido** hasta que se decida dónde vive la imagen; el "perfil extendido" P1 se limita a lo que el diagrama soporta. Registrar como pendiente P-7 |
| 19 | Master §13.2 da `actas.UrlArchivo`; el diagrama v2 lo sustituye por `actas.adjuntos_id_adjunto` (cambio #11) | **Manda el diagrama**: un solo camino para MIME, borrado y respaldo |
| 20 | `DESIGN.md` §3.3/§3.4 dice cabecera de tabla y badge de **12 px**; `lib_css.py` emite **13 px** | **Manda `lib_css.py`**: 13 px (coincide con §10.2 y T30, que prohíben <13 px) |
| 21 | `DESIGN.md` §3.1: botón con `padding 0 18px`; master §10.5 dice `0 16px` | **Manda `lib_css.py`**: `0 18px` |
| 22 | `DESIGN.md` escribe `rgba(4,74,147,…)`; el token real de `#004a93` es `rgba(0,74,147,…)` | **Manda el token**: `rgba(0,74,147,…)` (la variante de `DESIGN.md` es una errata) |
| 23 | `DESIGN.md` línea 53 incluye "Seguimiento" en el sidebar docente; no existe `docente/seguimiento.html` entre las 73 pantallas | **Mandan las pantallas**: el módulo docente es "Registrar avance" + columna Evidencia |
| 24 | El prototipo carga Inter desde Google Fonts (`lib_ui.py`); D21 exige autoalojarla | Misma tipografía, distinto medio de entrega; se autoaloja con `@fontsource/inter` |
| 25 | `docs/diagrama-clases.md` v2 dice "si este documento y el master discrepan, manda el master"; la instrucción del propietario para este build es lo contrario en tablas | Se aplica la instrucción del propietario (tablas = diagrama) y se registra aquí. Toda diferencia restante se resuelve caso por caso en las tablas #18–#19 |
| 26 | El prototipo (`compartido/registro.html`) y AQ-06 hablan de **7 campos + casilla**: nombres, apellidos, tipo y número de documento, **correo personal**, correo institucional, **celular** (obligatorios) y **teléfono fijo** (opcional). El diagrama v2 no tiene columnas para correo personal, celular ni teléfono fijo | **Manda el diagrama**: `POST /auth/register` acepta 6 campos (los cinco primeros más la contraseña) + la casilla. Los tres datos de contacto que no existen no se inventan ni se piden; si la Coordinadora los necesita, se añaden columnas en una etapa posterior y se actualiza AQ-06 |
| 27 | El selector de estado de `admin/usuarios.html` ofrece **`Activo → Limitado`** (y `Limitado → Inactivo`), pero FR-013 y BR-003 solo definen `Limitado → Activo`, `Inactivo → Activo` y `Activo → Inactivo` | **Mandan los requisitos**: la tabla de `policy/accountTransitions.ts` rechaza esas transiciones con `422 INVALID_STATE_TRANSITION`; el selector de la SPA solo ofrecerá las válidas |
| 28 | Los formularios de alta de `admin/usuarios.html` piden **teléfono**, **área de conocimiento**, **horas de asesoría por semana** (docente) y **sector, emprendimiento y etapa** (estudiante). `usuarios` no tiene esas columnas; los topes docentes son claves de `configuracion_programa` y el emprendimiento es otra entidad | **Manda el diagrama**: `POST /users` crea la cuenta con los campos de `usuarios`. El emprendimiento se crea en la Etapa 5; teléfono, área y horas no se inventan (ver #18 y #26) |
| 29 | `POST /users/:id/reject` (master §13.3) no tiene estado de destino en el diagrama: no existe «Rechazado» para la cuenta | Se mantiene `Limitado`, con motivo obligatorio auditado y notificación (P-15). El alta rechazada no se borra |
| 30 | El prototipo muestra el estado del docente en la tabla de usuarios junto a «Carga semanal» y «Emprendimientos», pero esas dos columnas no existen en `usuarios` | El listado devuelve la cuenta; los topes y el conteo de emprendimientos se calculan en la Etapa 6 (asignaciones), no se guardan en la fila |
| 31 | `admin/emprendimientos.html` pide un **«Tipo»** (`Comercio`, `Moda`, `Industrial`, `Alimentos`, `Artesanal`) distinto de «Sector» (`sectoreconomico`: Alimentos, Moda, Ambiental, Muebles, Tecnología, Comercio). El diagrama v2 no tiene columna ni catálogo para ese «Tipo» | **Manda el diagrama**: no se crea columna ni catálogo y el formulario no pide «Tipo». Se registra como decisión pendiente para la Coordinadora (¿es `modalidad`? ¿un catálogo nuevo?) |
| 32 | El formulario de `admin/emprendimientos.html` deja **editar «Avance (%)»** y lo guarda, pero R21 define el avance como derivado de las tareas completadas | **Mandan los requisitos**: `avance` no se acepta en `POST` ni en `PUT` (`.strict()` → `400`); se calculará en la Etapa 7 |
| 33 | El formulario de `admin/emprendimientos.html` incluye **«Docente asignado»**, pero el mentor vive en `asignaciones` (con horas, estado y fecha), no en `emprendimiento` | El campo pertenece al módulo de asignaciones (Etapa 6): se asigna después de aprobar y con el acta aprobada (BR-001). El formulario de emprendimiento no lo pide |

---

## 7. Versiones fijadas

Instaladas con `--save-exact`; el lockfile está commiteado.

| Componente | Versión | Nota |
|---|---|---|
| PostgreSQL | 17 | Fijada por el repositorio (`postgres:17`) |
| Node (Docker) | `node:22-alpine` | Tag mayor verificado en Docker Hub; fijar digest exacto antes de producción |
| Node (local, verificado) | v26.12.1 | `engines: >=22` |
| Caddy | `caddy:2.10.0-alpine` | Tag exacto verificado en Docker Hub |
| TypeScript | 7.0.2 | Raíz del workspace |
| Express | 5.3.0 | |
| zod | 4.6.7 | |
| pg | 8.23.1 | |
| pino | 10.4.0 | |
| dotenv | 18.0.9 | |
| helmet | 8.3.0 | |
| cookie-parser | 1.4.7 | |
| React / React DOM | 19.3.1 | |
| react-router-dom | 7.18.4 | |
| @tanstack/react-query | 5.104.5 | |
| vite | 8.3.5 | |
| @vitejs/plugin-react | 6.1.2 | |
| @fontsource/inter | 5.3.0 | |
| vitest | 5.0.5 | |
| supertest | 7.3.1 | |
| tsx | 4.23.15 | |

Desviación menor respecto a §14: hay **un solo** `.env.example` en la raíz (no
`backend/.env.example`), porque Compose lo consume con `env_file` y el backend lo carga
desde la raíz. Una sola plantilla evita duplicar variables.

---

## 8. Registro de la Etapa 0

| Aspecto | Resultado |
|---|---|
| Commit base | `b528a61` (HEAD desacoplado) |
| Rama creada | `feat/mvp-implementation` |
| Documentación pendiente | Commiteada en `c3b611f` sin descartar nada (incluye borrado de PNG/`.drawio` obsoletos) |
| AC verificados | 25 criterios de `README.md` §13 leídos; mapeo de §7.3 consistente |
| Estado del prototipo | Confirmado: 73 HTML, cero `fetch`/XHR/WebSocket, sesión en `localStorage`, sin atributos `name` |
| Bloqueo de entorno | `docker` desactivado, sin plugin `compose`, usuario fuera del grupo `docker` → la puerta de la Etapa 1 no se puede verificar hasta que TI/el usuario lo habiliten |
