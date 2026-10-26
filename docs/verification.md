# Registro de verificación — SGEMD MVP

> Bitácora **append-only**. Una entrada por puerta de etapa (`MASTER_IMPLEMENTATION_PROMPT.md` §16).
> Cada entrada: fecha, commit, comandos, resultado y, si algo quedó sin verificar, el motivo
> y el ID de decisión que lo bloquea. Una prueba omitida sin ID de decisión es una puerta fallida.

---

## Etapa 0 — Reconocimiento y guardarraíles

- **Fecha:** 2026-10-25
- **Commit:** `c3b611f` (base `b528a61`)
- **Rama:** `feat/mvp-implementation`

### Hecho

- Lectura de las tres fuentes que gobiernan el build: `docs/diagrama-clases.md` v2,
  `prototype/lib_css.py` + `prototype/DESIGN.md` y `MASTER_IMPLEMENTATION_PROMPT.md` v1.3.
- `docs/decisions.md` creado con 16 ADR, D1–D22, AQ-06/07/09/10/12, las 17 discrepancias del
  master y 8 nuevas detectadas al contrastar las fuentes (#18–#25), más los huecos P-1…P-8.
- `docs/design-parity.md` creado con las 62 vistas lógicas en estado `pending`.
- Árbol de trabajo resuelto: rama creada desde el HEAD desacoplado y documentación pendiente
  commiteada en `c3b611f` sin descartar nada (incluye el borrado deliberado de PNG/`.drawio`
  obsoletos que el propio diagrama v2 documenta).

### Verificado

| Comprobación | Resultado |
|---|---|
| `git status --porcelain` tras el commit | 0 archivos pendientes |
| Los 25 criterios de aceptación de `README.md` §13 existen y el mapeo de §7.3 es consistente | OK (discrepancia #14 cerrada) |
| Inventario del prototipo: 73 HTML, cero `fetch`/XHR/WebSocket | Confirmado por inspección |

### Sin verificar

- Aprobación de los requisitos por la Coordinadora (no depende del equipo; master §20).

**Puerta:** superada (sin código de negocio escrito).

---

## Etapa 1 — Esqueleto del repositorio y entorno

- **Fecha:** 2026-10-25
- **Commit:** `78aa8e6` (esqueleto) + `a32ffe7` (cierre de la puerta con Docker)

### Hecho

- Workspaces npm `shared`, `backend`, `frontend` con TypeScript `strict` (`tsconfig.base.json`).
- `shared/src/enums.ts`: todas las cadenas canónicas de §7.2 + las del diagrama v2
  (`NivelAcademico`, `TipoSeguimiento`, `NotificacionTipo`, `CodigoProposito`, `SolicitudTipo`,
  bandas de valoración) y los valores de los 14 catálogos.
- Backend Express 5 con `trust proxy`, `helmet`, `express.json` (1 MB; las evidencias suben por
  streaming), `cookie-parser`, control de origen en mutaciones y envoltura única de errores.
- `GET /api/health` sin autenticación ni datos de negocio.
- Frontend Vite + React 19 + Router + TanStack Query; `tokens.css` copiado literalmente de
  `prototype/lib_css.py`; Inter autoalojada con `@fontsource/inter` (D21).
- `docker-compose.yml` con Caddy, backend y PostgreSQL 17; puertos de backend y base de datos
  **no publicados**; volúmenes `storage/` y `backups/`; init de la BD montado.
- `caddy/Caddyfile`: TLS, `/api` con `flush_interval -1` (SSE), límite de cuerpo
  `PROXY_MAX_BODY_MB`, CSP/HSTS/nosniff, fallback de SPA.
- `Makefile` (`env`, `up`, `down`, `reset-db`, `check`, `typecheck`, `test`, `build`), `.env.example`
  completo y `.gitignore` que excluye secretos, `storage/`, `backups/`, dumps y correo generado.

### Verificado

| Comando | Resultado |
|---|---|
| `npm run typecheck` (3 workspaces) | Pasa sin errores |
| `npm test` (backend, vitest + supertest) | 4/4 pruebas verdes |
| Backend local + `curl http://127.0.0.1:3000/api/health` | `200` · `{"success":true,"data":{"status":"ok","db":"down","uptimeSeconds":6}}` (sin PostgreSQL en el host, como se espera) |
| `npm run build -w frontend` | Construye; 5 pesos de Inter empaquetados; CSS final solo con `#004a93`, `#051533`, `#162644`, `#bbbbbb`, `#ffd300`, `#ffffff` (minificados como `#bbb`/`#fff`) |
| `python3 -c "yaml.safe_load(open('docker-compose.yml'))"` | YAML válido |
| Tags de imagen `caddy:2.10.0-alpine` y `node:22-alpine` | Existen en Docker Hub (HTTP 200) |

### Verificado con la pila en marcha (puerta superada)

| Comprobación | Resultado |
|---|---|
| `docker compose up -d --build` | `caddy`, `backend` y `postgres` arriba; backend y postgres `healthy` |
| `curl -sk https://localhost/api/health` | `200` · `{"success":true,"data":{"status":"ok","db":"up",...}}` **a través de Caddy** |
| `GET /` y `GET /estudiante/tareas` por Caddy | `200` (el fallback de SPA sirve `index.html`) |
| Cabeceras de la SPA | `Content-Security-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options: nosniff` presentes |
| `ss -ltn` en el host | `3000` y `5432` **no escuchan**; solo se publican `80` y `443` |
| `docker compose exec backend pg_dump --version` | `17.11` — se corrigió: `postgresql-client` instalaba la 18 y rompía la regla del master §15 |
| `rsync --version` en el backend | `3.5.0` (prerrequisito de D22) |
| `NODE_ENV` dentro del contenedor | `production` (Compose lo fuerza; `.env` es plantilla de desarrollo) |
| `docker compose down` → `up -d` | Baja limpio y vuelve a levantar; health `200` otra vez |

### Notas de entorno

- El grupo `docker` no estaba activo en la sesión del agente (se añadió después de iniciarla);
  los comandos se ejecutaron con `newgrp docker`. Tras reiniciar sesión funciona directo.
- Plugin: `docker compose` v5.6.1. Daemon 29.9.2.

### Sin verificar (se prueba en la Etapa 12)

- TLS con certificado institucional: se usa la CA interna de Caddy (D15 abierta con TI).
- Límite real de cuerpo de 500 MB y entrega SSE: necesitan el endpoint de subida y el canal
  de notificaciones, que llegan en las etapas 7 y 8.
- Restauración de un respaldo: simulacro de la Etapa 12 (D22).

### Pendiente de decisión

- D15: hostname y certificado fuera de `localhost` (TI).
- D14: credenciales reales de Microsoft 365 / relay (TI).
- D22: disco separado para `backups/` y copia fuera del servidor (TI).

**Puerta:** superada el 2026-10-25 (healthcheck 200 a través de Caddy, puertos internos, `down`/`up` limpio).

---

## Etapa 2 — Esquema y datos iniciales

- **Fecha:** 2026-10-25
- **Commit:** `a95b6cd`

### Hecho

- `database/schema.sql`: las **41 tablas** del diagrama v2 (27 entidades + 14 catálogos),
  con nombres físicos en `snake_case`, claves foráneas, `CHECK` de las cadenas canónicas,
  claves primarias compuestas (`usuarios_has_eventos` y las tres `adjuntos_*`), borrado
  lógico en las siete entidades de BR-006 e índices de las columnas que filtran las pantallas.
- Restricciones que el dibujo no expresa: índice único **parcial** de una sola asignación
  `activa` por emprendimiento (R11); únicos de correo, documento, código de emprendimiento y
  código de respaldo; único `(pregunta, diagnóstico)`; motivo obligatorio al rechazar
  emprendimiento, acta y solicitud, y al devolver una tarea.
- `database/seed.sql`: los 14 catálogos con sus valores canónicos, 18 claves de
  `configuracion_programa`, 5 usuarios ficticios (contraseña `Demo1234` con bcrypt de
  `pgcrypto`), 1 emprendimiento aprobado con acta aprobada y asignación activa, 2 tareas y
  las **22 preguntas** del diagnóstico transcritas de `prototype/estudiante/diagnostico.html`.
- `scripts/check-schema.mjs` (`npm run check:schema`): compara el diagrama con el esquema y
  con `shared/src/enums.ts`. Falla si falta una columna, si sobra una, si el número de tablas
  no es 41 o si un `CHECK` no coincide con su constante.
- `shared/src/enums.ts`: se añaden `TIPOS_MIME_ADJUNTO` y `TIPOS_DATO_CONFIGURACION`.

### Verificado

| Comprobación | Resultado |
|---|---|
| `npm run check:schema` | 27 clases con todas sus columnas · 14 catálogos · 41 tablas · 22 listas `CHECK` coinciden |
| Prueba negativa del verificador (columna borrada, valor de enum cambiado, tabla extra) | Detecta los 5 problemas y sale con código 1 |
| `docker compose down -v && up -d --build` | La inicialización aplica esquema y seed sin errores; los tres servicios quedan `healthy` |
| `information_schema` — tablas base en `public` | **41** |
| Catálogos | roles 4 · tipodocumentos 3 · programaacademico 5 · centrouniversitarios 3 · municipios 3 · tipopoblacion 5 · tipousuarios 4 · etapaemprendimiento 4 · faseplan 4 · sectoreconomico 6 · modalidad 3 · tipo_evento 5 · fecha_y_horarios 2 · modulos 8 |
| `preguntas_diagnostico` | **22** en 5 secciones (5 · 4 · 4 · 4 · 5) |
| Contraseña de las 5 cuentas demo | `crypt('Demo1234', password)` devuelve `true` en todas |
| Expediente de demo | `EMP-001` aprobado · acta `Aprobada` · asignación `activa` de 4 h/semana |
| Integridad referencial (5 uniones) | 0 filas huérfanas |
| Índices clave | `asignaciones_una_activa_por_emprendimiento`, `usuarios_correo_institucional_key`, `usuarios_numero_documento_key` presentes |
| Rechazo sin motivo (`emprendimiento`) | Rechazado por `emprendimiento_rechazo_con_motivo` |
| Segunda asignación activa al mismo emprendimiento | Rechazada por el índice único parcial |
| `GET /api/health` tras recrear la base | `200` con `db: "up"` |
| Datos personales | Solo ficticios (`admin.demo@…`, documento `900000001`…); ninguna fuente real |

### Sin verificar / pendiente

- El banco de preguntas es **provisional**: `tipo` y `origen` no tienen valores canónicos
  (P-9) y el Excel definitivo sigue pendiente (AQ-12).
- `usuarios.codigo` queda sin `UNIQUE` a propósito (P-10); la unicidad se decidirá con la
  Coordinadora y, mientras tanto, la valida el servicio en la Etapa 4.
- Los `CHECK` de `valoracion.dimension`, `auditoria_eventos.accion`, `habilitaciones.estado`,
  `usuarios_has_eventos.estado_asistencia`, `recomendaciones_evento.estado` y
  `preguntas_diagnostico.tipo/origen` **no se crean** hasta tener los valores (P-4, P-8, P-9).
- El usuario de la base de datos es todavía el superusuario del contenedor; se corrige en la
  Etapa 12 (§15).

**Puerta:** superada (41 tablas, catálogos completos, 22 preguntas, integridad y restricciones
comprobadas sobre una base recreada desde cero).

---

## Etapa 3 — Autenticación

- **Fecha:** 2026-10-25
- **Commit:** `705d818`

### Hecho

- `modules/auth`: registro, verificación de correo, reenvío de código, inicio y cierre de
  sesión, solicitud y consumo del código de recuperación. OTP de 8 dígitos guardado como
  HMAC-SHA256 ligado a `correo:proposito:codigo` (D20, D23), TTL 5 min, un solo uso,
  máximo 5 intentos y cooldown de reenvío.
- Sesión: JWT HS256 con **solo** `{ id, role }` y 8 h, en la cookie `sgemd_session`
  (`HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=28800`). El cuerpo del login lleva el
  usuario, nunca el token.
- Middleware: `requireAuth` (relee la fila en cada petición y toma el rol de ella),
  `requireRole`, `requireActiveAccount` (`403 ACCOUNT_NOT_ACTIVE`), `originCheck`
  (mutaciones del mismo origen), `rateLimit` (memoria, por IP) y `validateBody` (zod
  `.strict()`).
- Adaptador de correo con tres transportes: `file` (dev y pruebas, escribe `.eml`),
  `relay` y `oauth2` (XOAUTH2). Solo `file` se ejercita; los otros dos fallan al arrancar
  si faltan las credenciales de TI (D14).
- `GET /api/users/me` y `GET /api/diagnosis/form`. Este último se adelanta **solo** porque
  T03 exige un endpoint restringido real; el módulo de diagnóstico completo es la Etapa 9.
- `policy/accountState.ts` aísla AQ-07: `Limitado` puede ver perfil; los módulos de trabajo
  exigen `Activo`.
- Auditoría en la misma transacción que el cambio (`auditoria_eventos`), sin contraseñas ni
  códigos.
- `docs/api.md` con el contrato de los nueve endpoints y la tabla de códigos de error.
- Banco de pruebas: `docker-compose.test.yml` (proyecto `sgemd-test`, `127.0.0.1:55432`) y
  `globalSetup` que recrea el esquema desde `schema.sql` + `seed.sql` en cada ejecución.

### Verificado

| Comprobación | Resultado |
|---|---|
| `npm test` (PostgreSQL real, 2 archivos) | **36 pruebas en verde** |
| T01 · registro | Cuenta `Limitado` sin verificar, rol 2, bcrypt `$2b$10$`; OTP de 8 dígitos en el correo, HMAC de 64 hex en la fila, vigencia ≈5 min, `usado=false`, `intentos=0`; transporte de correo invocado |
| T01 · duplicados y validación | `409 EMAIL_TAKEN`, `409 DOCUMENT_TAKEN`, `400 EMAIL_DOMAIN_NOT_ALLOWED`, casilla obligatoria y campos desconocidos (`roles_id_roles`, `estado`, `verificado`) rechazados con `400` |
| T01 · OTP | Correcto verifica; incorrecto, vencido y reutilizado dan `422 OTP_INVALID`; al quinto fallo `429 OTP_ATTEMPTS_EXCEEDED` y el código correcto ya no sirve; cooldown `429 OTP_COOLDOWN` con `Retry-After` y reenvío permitido al pasar |
| T01 · no filtración | El OTP y la contraseña no aparecen en el cuerpo de registro, verificación, reenvío ni recuperación |
| T02 · login | Contraseña incorrecta y correo inexistente → `401 INVALID_CREDENTIALS` sin cookie; cuenta sin verificar → `403 EMAIL_NOT_VERIFIED`; éxito con las cuatro banderas y `Max-Age=28800`; cuerpo `{ usuario }` sin token ni hash; JWT con exactamente `{exp, iat, id, role}` y `exp - iat = 28800` |
| T03 · cuenta `Limitado` | `GET /diagnosis/form` → `403 ACCOUNT_NOT_ACTIVE` con el motivo; `GET /users/me` → `200`; una cuenta `Activo` obtiene las 22 preguntas |
| T04 · sesión | Sin cookie `401 AUTH_REQUIRED`; firma alterada y token de otro secreto `401 AUTH_INVALID`; baja lógica invalida la cookie vigente en la petición siguiente; `Inactivo` pasa a `403` en la petición siguiente; el rol se toma de la fila (cambio 2→3 visible sin renovar token); logout devuelve `Expires=Thu, 01 Jan 1970`; `Origin` ajeno `403 ORIGIN_NOT_ALLOWED` |
| T39 · recuperación | El código válido cambia la contraseña una vez, la anterior deja de servir y la nueva entra; el código usado y el vencido dan `422`; la contraseña no cambió tras el fallo; correo desconocido responde `200` sin enviar nada |
| `npm run typecheck` | Los tres workspaces sin errores |
| `npm run check:schema` | Sigue en verde (41 tablas, 22 listas `CHECK`) |
| Recorrido manual a través de Caddy | Login `200` con `Set-Cookie: sgemd_session=…; Max-Age=28800; Path=/; HttpOnly; Secure; SameSite=Strict`; `GET /users/me` `200`; `GET /diagnosis/form` `200` con 22 preguntas para `Activo` y `403 ACCOUNT_NOT_ACTIVE` para `Limitado`; logout limpia la cookie; `Origin` ajeno `403`; un registro real deja el `.eml` con el OTP en el volumen `storage/mail` |

### Defecto encontrado y corregido

El contador de intentos del OTP se incrementaba dentro de la transacción y el `throw`
posterior provocaba `ROLLBACK`: el límite de 5 intentos **nunca se alcanzaba**. T05 lo
detectó. Ahora `consumeOtp` devuelve el resultado y el error se lanza **después** del
`COMMIT`, de modo que el incremento (y el quemado del código) queda guardado.

### Sin verificar / pendiente

- Los transportes `relay` y `oauth2` no se ejercitan: faltan credenciales de TI (D14).
- El cooldown de reenvío (60 s, P-11) y los umbrales de rate limit (P-12) son valores
  iniciales, no requisitos confirmados.
- El consentimiento de tratamiento de datos se exige pero **no se persiste** (P-14); no hay
  columna en el diagrama.
- `POST /auth/register` acepta 6 campos + casilla: el prototipo pide además correo personal,
  celular y teléfono fijo, que el diagrama no tiene (#26).
- El cierre de sesión limpia la cookie pero no revoca el JWT en el servidor (es
  autocontenido y expira a las 8 h), tal como pide el master.

**Puerta:** superada (T01–T05 y T39 en verde; el OTP no aparece en ninguna respuesta; el
código vencido se rechaza; la cookie se emite con las cuatro banderas y el cuerpo no lleva
token).

---

## Etapa 4 — Usuarios, roles y ciclo de vida

- **Fecha:** 2026-10-25
- **Commit:** `267919e`

### Hecho

- `modules/users`: alta administrativa de estudiantes y docentes, lectura de fichas,
  edición por el administrador, edición del propio perfil, baja lógica, listados
  paginados con filtros y las cuatro rutas del ciclo de vida (`validate`, `reactivate`,
  `state`, `reject`).
- `modules/users/repository.ts`: una sola consulta de la fila de `usuarios` (con los ids de
  catálogo) compartida por el middleware de sesión, el login y los casos de uso. El login
  ya no duplica el `SELECT`.
- `services/codes.ts`: `DOC-###` y `ADM-###` secuenciales con `pg_advisory_xact_lock`
  (serializa altas simultáneas del mismo prefijo, porque `usuarios.codigo` no es único) y
  el código estudiantil de 6 dígitos.
- `services/otpCodes.ts`: emisión, cooldown y consumo del código extraídos de
  `auth/service.ts` para reutilizarlos en la invitación de una cuenta nueva.
- `services/email.ts`: transporte, dominio institucional y las cuatro plantillas
  (verificación, recuperación, invitación, bienvenida). `sendMailBestEffort` para los
  correos cuyo hecho de negocio ya está confirmado.
- `services/notify.ts`: escritura de `notificaciones` en la misma transacción que el
  cambio (los endpoints de lectura llegan en la Etapa 8).
- `policy/accountTransitions.ts`: tabla única de transiciones (`Limitado → Activo`,
  `Inactivo → Activo`, `Activo → Inactivo`); el resto, `422 INVALID_STATE_TRANSITION`.
- `middleware/validate.ts`: `validateQuery` + `queryOf`, con `z.coerce` y `.strict()`, para
  que un nombre de columna arbitrario nunca llegue al `ORDER BY`.
- Acciones de auditoría nuevas: `Alta de usuario`, `Edición de usuario`, `Baja lógica de
  usuario`, `Cambio de estado de cuenta`, `Rechazo de activación`.
- `docs/api.md`: sección de usuarios completa (13 rutas, paginación, códigos nuevos).

### Verificado

| Comprobación | Resultado |
|---|---|
| `npm test` (PostgreSQL real, 3 archivos) | **65 pruebas en verde** (36 de la Etapa 3 + 29 de la Etapa 4) |
| T06 · alta | Estudiante con código de 6 dígitos, `verificado = true`, `Activo` por defecto, rol 2, contraseña aleatoria `$2b$10$` que no viaja en la respuesta, auditoría con el actor e invitación con OTP de 8 dígitos; docente con `DOC-003` y `DOC-004` (el seed trae `DOC-001`/`DOC-002`) |
| T06 · unicidad y validación | `409 EMAIL_TAKEN`, `409 DOCUMENT_TAKEN`, `400` para rol fuera de 2/3, dominio no institucional, catálogo inexistente y campos del servidor (`codigo`, `password`, `verificado`) |
| T06 · autorización | Docente y estudiante: `403 ROLE_NOT_ALLOWED` en alta y listado; una cuenta de coordinación `Limitado`: `403 ACCOUNT_NOT_ACTIVE` |
| T13 · transiciones | `Limitado → Activo` por `validate` con auditoría `{estado: "Limitado"} → {estado: "Activo"}`, notificación `Sistema` y correo de bienvenida; `Activo → Inactivo` y `Inactivo → Activo`; `Activo → Limitado`, `Limitado → Inactivo` y repetir el estado dan `422`; `validate`/`reactivate` solo sobre su estado de origen |
| T13 · autoprotección | Un estudiante no cambia su estado ni se valida (`403`); el administrador no cambia el estado de su propia cuenta (`422 SELF_STATE_CHANGE_NOT_ALLOWED`) |
| Rechazo de activación | Sin motivo `400`; con motivo `200`, la cuenta sigue `Limitado`, auditoría con el motivo y notificación al titular; sobre una cuenta ya `Activo`, `422` |
| Baja lógica | `fecha_eliminacion` marcada, `total = 0` en el listado, detalle `404`, login `401 INVALID_CREDENTIALS`, auditoría con el actor; auto-baja `422`; id inexistente `404` |
| Perfil | Un estudiante lee su ficha y la ajena da `404`; `PUT /users/me` cambia nombres y datos académicos y audita solo lo que cambió; correo, documento, tipo de documento, rol, estado y código se rechazan con `400`; el administrador edita a otro y la unicidad da `409` |
| Listados | `pageSize = 2` devuelve 2 elementos, `total` real y páginas sin solaparse; filtros `rol`, `estado` y `q`; `/students` y `/teachers` ignoran el `rol` del cliente; `sort` fuera de la lista blanca, `pageSize = 500` y parámetros desconocidos dan `400` |
| `npm run typecheck` | Los tres workspaces sin errores |
| `npm run check:schema` | Sigue en verde (41 tablas, 22 listas `CHECK`) |
| Recorrido manual a través de Caddy | Alta de estudiante `201` (`Limitado`, código de 6 dígitos) con la invitación en `storage/mail`; alta de docente con `DOC-003`; correo duplicado `409 EMAIL_TAKEN`; listado paginado `200`; `Limitado → Activo` `200`, `Activo → Limitado` `422`, `Activo → Inactivo` `200`, `reactivate` `200`; rechazo sin motivo `400`; un estudiante recibe `403` al intentar cambiar su estado y `400` al enviar `correoInstitucional` en `PUT /users/me`; la auditoría y la notificación quedan escritas; la baja lógica deja el login en `401` |

### Decisiones y huecos registrados

- P-15: el rechazo de activación deja la cuenta en `Limitado` (no existe estado
  «Rechazado» en el diagrama).
- P-16: la restauración de una cuenta dada de baja no tiene endpoint en el master.
- P-17: el alcance de lectura del Auditor queda para el módulo de auditoría.
- P-18: el rol es inmutable en la edición.
- Discrepancias #27 (`Activo → Limitado` del prototipo se rechaza), #28 (campos del alta
  del prototipo que no existen en `usuarios`), #29 (rechazo sin estado de destino) y #30
  (carga y emprendimientos no viven en `usuarios`).
- §5.5: alta verificada con invitación, estado inicial, correo de bienvenida sin reversión,
  notificación transaccional, auto-gestión prohibida y baja lógica sin cascada de archivos
  todavía.

### Sin verificar / pendiente

- El borrado físico de adjuntos al dar de baja un usuario (BR-006) se implementará con el
  módulo de adjuntos: hoy no existen archivos asociados a una cuenta.
- Restaurar una cuenta dada de baja (P-16) y cambiar el rol (P-18) no tienen endpoint.
- Las preferencias `notif_*` no se aplican al escribir; se respetan al construir la bandeja
  (Etapa 8).
- Los criterios de validación del emprendedor siguen abiertos (AQ-06): `reject` solo exige
  el motivo.

**Puerta:** superada (T06 y T13 en verde; un estudiante no puede cambiar su propio estado
ni su rol; la auditoría guarda el valor anterior y el nuevo).

---

## Etapa 5 — Catálogos, emprendimientos y solicitudes

- **Fecha:** 2026-10-25
- **Commit:** `26f3442`

### Hecho

- `modules/catalogs`: los 14 catálogos de solo lectura. `GET /type-doc` es público (lo
  necesita el registro); el resto exige sesión y ninguno exige cuenta `Activo`, porque
  alimentan la edición del propio perfil de una cuenta `Limitado`. `municipalities` y
  `date-times` devuelven la etiqueta compuesta que la interfaz necesita.
- `modules/entrepreneurship`: listado con alcance por rol, detalle, alta administrativa,
  edición con campos por rol, baja lógica, aprobación y rechazo con motivo.
- `modules/requests`: bandeja única de R38 (Desbloqueo, Paralelo, Cita) con contador de
  pendientes por tipo, aprobación que aplica el efecto de dominio una sola vez y rechazo
  con motivo.
- `services/accountLifecycle.ts`: `applyAccountTransition` extraído de `modules/users` para
  que el cambio de estado de la cuenta y la aprobación de un desbloqueo sean el mismo
  camino, con el mismo `SELECT … FOR UPDATE`, la misma auditoría y la misma notificación.
- `services/catalogs.ts`: `assertCatalogIds` compartido por usuarios y emprendimientos
  (tabla y columna son constantes del código, nunca datos de la petición).
- `services/programSettings.ts`: lector de `configuracion_programa` (`etapa_inicial`,
  `paralelos_maximos`) con valor de respaldo si la clave falta o está corrupta.
- `services/codes.ts`: `EMP-###` con el mismo `nextSequential` de `DOC-###`/`ADM-###`;
  `pg_advisory_xact_lock` serializa las altas simultáneas.
- `utils/params.ts`: `parseId` compartido; un `:id` no numérico es `400`, no un `404`
  ambiguo.
- Acciones de auditoría nuevas: `Alta`, `Edición`, `Baja lógica`, `Aprobación` y `Rechazo
  de emprendimiento`; `Solicitud creada`, `Solicitud aprobada` y `Solicitud rechazada`.
- `tests/api.ts`: helpers de sesión compartidos (`loginSession` reenvía la cookie `Secure`
  de forma explícita); `users.test.ts` migrado a ellos.
- `docs/api.md`: secciones de catálogos, emprendimientos y solicitudes, códigos de error
  nuevos y `pageSize` por defecto 25 (master §13.3).

### Verificado

| Comprobación | Resultado |
|---|---|
| `npm test` (PostgreSQL real, 6 archivos) | **95 pruebas en verde** (65 de las etapas 3–4 + 6 de catálogos + 10 de emprendimientos + 14 de solicitudes) |
| Catálogos | `/type-doc` público con CC, CE, TI; los otros 13 responden `401 AUTH_REQUIRED` sin sesión y `200` con sesión; una cuenta `Limitado` los lee; no hay rutas de escritura (`404`); `municipalities` y `date-times` devuelven sus campos compuestos |
| T11 · alta y aprobación | El administrador crea en `Pendiente` con `avance = 0`, `EMP-###` y la etapa inicial de la configuración; auditoría `{Pendiente} → {Aprobado}` con el actor; notificación al estudiante; docente y estudiante reciben `403`; aprobar dos veces o aprobar un rechazado da `422 INVALID_APPROVAL_STATE` |
| T11 · paralelos | Primer emprendimiento con `esParalelo` → `422 NOT_A_PARALLEL`; segundo sin autorización → `422 PARALLEL_REQUIRED`; con autorización → `201`; tercero → `422 PARALLEL_LIMIT_REACHED` (`paralelos_maximos = 1`); un `Rechazado` no ocupa cupo |
| T12 · rechazo | Sin motivo o con espacios → `400` con `fields.motivo`; con motivo → `200`, `motivo_rechazo` persistido, auditoría con el motivo y notificación que lo incluye |
| Edición y alcance | El estudiante propietario cambia nombre, descripción y redes; sector/etapa/sede → `403 FIELD_NOT_ALLOWED`; el propietario, el estado, el motivo, el paralelo, el avance y el código se rechazan con `400`; un emprendimiento ajeno responde `404`; el docente solo ve los asignados; `Limitado` → `403 ACCOUNT_NOT_ACTIVE` |
| T36 · desbloqueo | Una cuenta `Limitado` y otra `Inactivo` piden el desbloqueo (`201`) y la aprobación las deja `Activo` con auditoría `{Limitado} → {Activo}` y notificación `Solicitud`; una cuenta `Activo` recibe `422 ACCOUNT_ALREADY_ACTIVE`; la segunda aprobación da `422 REQUEST_ALREADY_RESOLVED` sin reescribir la auditoría |
| T36 · paralelo y cita | La aprobación de un paralelo pone `es_paralelo = TRUE` una sola vez; una cita se resuelve sin efecto de dominio (`efecto: null`); sin emprendimiento, ajeno o no aprobado → `400`/`422 ENTREPRENEURSHIP_NOT_APPROVED`; un docente no puede pedirlos (`403`) |
| T36 · rechazo y bandeja | Rechazar exige motivo, lo persiste, notifica y no toca la cuenta ni el emprendimiento; el contador `pendientes` desglosa por tipo sobre toda la bandeja; el filtro por tipo no lo altera; estudiante y docente reciben `403 ROLE_NOT_ALLOWED` en toda la bandeja; `:id` no numérico `400`, inexistente `404`, filtro/orden/`pageSize` fuera de rango `400` |
| `npm run typecheck` | Los tres workspaces sin errores |
| `npm run check:schema` | Sigue en verde (41 tablas, 22 listas `CHECK`) |
| Recorrido manual a través de Caddy | Pila recreada desde cero (`down -v` + `up --build`): los 14 catálogos `200`; alta de estudiante y de emprendimiento `201` (`Pendiente`, `avance 0`, etapa inicial); aprobación `200` y doble aprobación `422`; `PARALLEL_REQUIRED`, `PARALLEL_LIMIT_REACHED` y `NOT_A_PARALLEL` según el caso; `FIELD_NOT_ALLOWED` al editar el sector como estudiante; rechazo sin motivo `400` y con motivo `200`; desbloqueo de una cuenta `Limitado` aprobado `200` (cuenta `Activo`, doble aprobación `422`, desbloqueo de una cuenta ya activa `422`); paralelo aprobado deja `esParalelo = true`; cita aprobada sin efecto; bandeja `403` para estudiante; auditorías, notificaciones y correos escritos |

### Decisiones y huecos registrados

- P-19: aprobar una `Cita` no crea la asesoría (faltan columnas y el bloque de agenda); el
  efecto de dominio llega con el módulo de asesorías (Etapa 8).
- P-20: `solicitudes` solo tiene `detalle`; «nuevo emprendimiento», «sector», «docente
  sugerido» y «fecha propuesta» viajan en ese texto libre.
- Discrepancias #31 (el «Tipo» del prototipo no tiene columna ni catálogo), #32 (el
  prototipo edita `avance`; aquí se deriva de las tareas) y #33 («Docente asignado»
  pertenece a `asignaciones`, Etapa 6).
- §5.6: alta administrativa, autorización de paralelo, tope, edición por rol, alcance de
  lectura, aprobación/rechazo, catálogos, política de la bandeja, resolución única,
  `pageSize` 25 y aviso a la coordinación.

### Sin verificar / pendiente

- El borrado físico de adjuntos al dar de baja un emprendimiento (BR-006) espera al módulo
  de adjuntos (Etapa 7).
- La asignación de docente, los topes por docente y el acta previa son de la Etapa 6.
- `avance` se calculará con las tareas completadas (R21, Etapa 7); hoy se crea en 0 y no se
  edita.
- El «Tipo» de emprendimiento del prototipo (#31) queda a la espera de la Coordinadora: no
  se creó columna ni catálogo.

**Puerta:** superada (T11, T12 y T36 en verde; un emprendimiento solo se aprueba desde
`Pendiente`; el paralelo exige autorización y respeta el tope; una solicitud se resuelve
una sola vez y siempre notifica).

---

## Etapa 6 — Asignaciones docentes

- **Fecha:** 2026-10-25
- **Commit:** `3b5adfc`

### Hecho

- `modules/assignments`: siete rutas. `POST`, `PUT` y `DELETE` son exclusivos del
  administrador (R9); `GET` se filtra por rol en el servicio (R10), y un detalle fuera de
  alcance responde `404` para no revelar expedientes ajenos.
- El estudiante **no** se envía: se deriva del propietario del emprendimiento. El modal del
  prototipo muestra «Estudiante» y «Emprendimiento» como campos de solo lectura, así que
  aceptar un `estudianteId` permitiría un vínculo incoherente; `.strict()` lo rechaza.
- R11 con doble respaldo: comprobación dentro de la transacción **y** el índice único
  parcial `asignaciones_una_activa_por_emprendimiento`; la violación `23505` se traduce a
  `409 ASSIGNMENT_ALREADY_ACTIVE`.
- Los dos topes de FR-016/R35 se leen de `configuracion_programa` y se comprueban sobre las
  asignaciones **activas** del mentor, dentro de la transacción y bajo
  `pg_advisory_xact_lock` por mentor (en orden ascendente de id para no interbloquear una
  reasignación A→B con otra B→A). Cada tope tiene su código y su campo:
  `422 TEACHER_HOURS_LIMIT_REACHED` (`fields.horasSemanales`) y
  `422 TEACHER_ENTREPRENEURSHIP_LIMIT_REACHED` (`fields.mentorId`).
- BR-001 aplicado desde el primer momento contra `actas`, sin bandera de omisión (§20.5
  #12): se exige al menos un acta `Aprobada` del emprendimiento
  (`422 ACTA_NOT_APPROVED`). Las actas se cargan y revisan en la Etapa 9; hasta entonces se
  usan fixtures.
- El mentor debe existir, estar vigente y tener rol Docente (`400`) y estar `Activo`
  (`422 MENTOR_NOT_ACTIVE`, derivado de AQ-07 opción A).
- La reasignación revalida los topes y el acta del docente **destino**; el anterior libera
  su carga en la misma transacción. La baja es `estado = 'inactiva'` (la tabla no tiene
  `fecha_eliminacion`): libera el cupo del emprendimiento y la carga del docente.
- Acciones de auditoría nuevas: `Alta de asignación`, `Edición de asignación` y `Baja de
  asignación`, con el actor y el antes/después; notificaciones `Sistema` al docente y al
  estudiante en la misma transacción.
- `tests/assignments.test.ts`: 21 pruebas de integración. Se ajustó una aserción frágil de
  `users.test.ts` que esperaba `DOC-003`/`DOC-004` literales: ahora comprueba el formato
  `DOC-\d{3}` y el incremento, porque la suite nueva crea más docentes.

### Verificado

| Comprobación | Resultado |
|---|---|
| `npm test` (PostgreSQL real, 7 archivos) | **116 pruebas en verde** (95 de las etapas 3–5 + 21 de asignaciones) |
| T15 · acta (BR-001) | Sin acta → `422 ACTA_NOT_APPROVED`; con un acta `Pendiente` → igual; un acta `Rechazada` tampoco habilita; tras aprobarla → `201` con `estado: 'activa'` |
| T07 · topes | Doce asignaciones de 1 h → `201`; la decimotercera → `422 TEACHER_HOURS_LIMIT_REACHED`, y la base queda en 12 filas y 12 h; `carga_max_horas = 4` con 4 h ya asignadas rechaza 1 h más con el campo `horasSemanales`; `max_emprendimientos_docente = 2` rechaza el tercer emprendimiento con `fields.mentorId` |
| R11 · unicidad | Una segunda asignación activa del mismo emprendimiento → `409 ASSIGNMENT_ALREADY_ACTIVE`; tras la baja, otra alta → `201` y la fila anterior queda `inactiva`; la baja libera el cupo del docente |
| R9/R10 · autorización | Docente y estudiante reciben `403 ROLE_NOT_ALLOWED` en `POST`, `PUT` y `DELETE`; el docente solo ve sus filas y el estudiante las suyas; el detalle ajeno responde `404`; `/assignments/mentor/:id` da `404` a otro docente y `403` a un estudiante; `/assignments/student/:id` da `404` a un docente sin vínculo con ese estudiante |
| Alta · validaciones | `estudianteId` → `400`; mentor estudiante → `400` con `fields.mentorId`; mentor `Inactivo` → `422 MENTOR_NOT_ACTIVE`; emprendimiento inexistente → `400` con `fields.emprendimientoId`; sin horas y con 0 h → `400` |
| Edición y baja | Reasignar cambia mentor y horas con auditoría del antes/después; el destino en el tope → `422` y la asignación original queda intacta; `estado` en el `PUT` → `400`; una asignación inactiva no se edita ni se vuelve a dar de baja (`422 ASSIGNMENT_NOT_ACTIVE` en ambos casos) |
| Efectos | Auditoría `Alta`, `Edición` y `Baja de asignación` con el actor; dos notificaciones `Sistema` por alta (docente y estudiante) con `tipoObjeto = 'asignaciones'` y URL; la baja avisa a ambos |
| Listado | Filtros por `estado`, `mentorId`, `estudianteId` y `emprendimientoId`; `q` encuentra por correo, código y nombre del emprendimiento; `:id` no numérico `400`; inexistente `404`; `pageSize = 101`, `sort` fuera de la lista blanca y parámetros desconocidos `400` |
| `npm run typecheck` | Los tres workspaces sin errores |
| `npm run check:schema` | Sigue en verde (41 tablas, 22 listas `CHECK`) |
| Recorrido manual a través de Caddy | Pila recreada desde cero (`down -v` + `up --build`): **52 comprobaciones, 52 en el estado esperado**. Incluye las 3 sesiones del seed, la asignación sembrada, `ACTA_NOT_APPROVED` → `201` tras insertar el acta, `409` duplicada, `400` con `estudianteId`, reasignación `200`, `TEACHER_HOURS_LIMIT_REACHED` con el tope bajado a 5, baja `200` → `422`, nueva vinculación `201`, alcance `403`/`404`, filtros, y las filas de auditoría (`Alta`/`Edición`/`Baja`) y las 2 notificaciones |

### Decisiones y huecos registrados

- §5.7: escritura solo del admin, estudiante derivado, unicidad activa, ambos topes, lock
  por mentor, BR-001 sin omisión, mentor `Activo`, edición acotada, reasignación, baja,
  alcance de lectura, rango 1–20 h del formulario, auditoría/avisos y `pageSize` 25.
- P-21: nada exige que el emprendimiento esté `Aprobado` para asignar docente; solo se
  comprueba el acta (BR-001). Se confirma con la Coordinadora si debe ser una segunda
  compuerta.
- P-22: la baja lógica de un emprendimiento o de un usuario no desactiva sus asignaciones:
  la fila sigue `activa`, ocupa el índice y consume el tope del docente. R36 solo menciona
  la cascada de adjuntos; el tratamiento se decide con la Etapa 7.
- P-23: no hay endpoint de reactivación; una fila `inactiva` es histórica y volver a
  vincular exige una asignación nueva.

### Sin verificar / pendiente

- El alta y la revisión de actas (la compuerta de BR-001) llegan con el módulo de actas de
  la Etapa 9; hoy la suite y el recorrido insertan la fila directamente.
- El aviso «Docente asignado» de las vistas de estudiante y docente se pinta en la
  Etapa 11; el contrato ya expone `mentor` en cada asignación.
- La cascada de la baja lógica (P-22) queda abierta hasta la Etapa 7.

**Puerta:** superada (T07 y T15 en verde; ambos topes se aplican bajo transacción y lock;
una sola asignación activa por emprendimiento; la lectura respeta el rol y la escritura es
solo del administrador).

---

## Etapa 7 — Tareas, seguimientos y evidencias

- **Fecha:** 2026-10-25
- **Commit:** `3f457c2`

### Hecho

- `modules/tasks`: ciclo de vida completo. El alta deriva el estudiante del propietario del
  emprendimiento (no se acepta `estudianteId`) y nace `Pendiente` con
  `evidencia_requerida = TRUE`. `PUT` admite `estado: 'En curso'` solo desde `Pendiente`;
  la entrega, la calificación y la devolución tienen rutas propias. `Vencida` se deriva de
  `fecha_limite` en cada lectura y en el filtro, nunca se escribe en la fila.
- `modules/tracing`: avances de fase y comentarios. El autor es la sesión; un
  `Avance de fase` exige `fasePlanId` (`400`) y un `Comentario` no la lleva. Editar y dar
  de baja es del autor o del administrador; un docente ajeno recibe `404`. La fecha del
  avance se guarda a mediodía de Bogotá para no mostrarse como el día anterior.
- `modules/attachments`: subida `multipart/form-data` en streaming con `busboy`,
  descarga con `Content-Disposition` (respaldo ASCII + `filename*=UTF-8''`) y borrado con
  baja lógica de la fila, borrado del pivote y borrado físico del archivo.
- `services/storage.ts`: MIME por **firma del contenido** (JPEG, PNG, PDF), nombre en disco
  `<uuid>.<ext>`, escritura en `*.part` + `rename`, travesía de rutas rechazada con
  `preservePath` y tamaño desde `upload_max_mb`.
- `services/evidence.ts`: los tres pivotes (`tareas`, `seguimientos`, `asesorías`) y la
  cascada de BR-006 al dar de baja un emprendimiento, incluida el acta.
- `services/progress.ts`: `avance = ROUND(100 × Completada / total)` recalculado dentro de
  la transacción y progreso por fase (las cuatro fases siempre presentes).
- BR-007 se aplica en el servidor: `PUT /task/:id/complete` sin evidencia vigente responde
  `422 TASK_EVIDENCE_REQUIRED`; el botón deshabilitado de la interfaz es solo la primera
  capa.
- 11 acciones de auditoría nuevas y avisos `Tarea` / `Seguimiento` al estudiante y a los
  docentes con asignación activa.

### Verificado

| Comprobación | Resultado |
|---|---|
| `npm test` (PostgreSQL real, 10 archivos) | **158 pruebas en verde** (116 de las etapas 3–6 + 42 nuevas) |
| T16 · ciclo de vida | `Pendiente → En curso → En revisión → Completada` con `puntajeObtenido` y `estadoRevision = 'Calificada'`; calificar o devolver antes de tiempo → `422 INVALID_TASK_TRANSITION`; `estado: 'Completada'` en el `PUT` → `400`; una tarea `En revisión` no se edita (`422 TASK_NOT_EDITABLE`); el estudiante no crea, edita, califica ni borra (`403`); otro estudiante recibe `404` al entregar y un docente `404` al calificar sin asignación |
| T17 · BR-007 | Entrega sin evidencia → `422 TASK_EVIDENCE_REQUIRED` y la tarea sigue `Pendiente`; tras subir una imagen → `200`; si se borra la única evidencia, la entrega vuelve a fallar. `evidenciaRequerida`, `estado`, `estadoRevision`, `puntajeObtenido` y `usuariosId` enviados por el cliente → `400` |
| T18 · devolución | Sin motivo → `400`; con motivo y observaciones → `200 Devuelta`, motivo y observaciones guardados, aviso al estudiante y auditoría; un motivo fuera del vocabulario → `400`; tras corregir, la reentrega vuelve a `En revisión` |
| T19 · subida | JPG, PNG y PDF aceptados; PNG declarado como `image/gif` con nombre `.jpg` se guarda como `image/png` (manda el contenido); dos subidas con el mismo nombre original obtienen rutas distintas y sin `.part`; 1,5 MB con `upload_max_mb = 1` → `413 PAYLOAD_TOO_LARGE`; GIF → `400`; `filename="../../etc/passwd.jpg"` → `400`; tercer archivo con tope 2 → `422 ATTACHMENT_LIMIT_REACHED`; sin archivo y entidad `advice` → `400`; sin sesión → `401` |
| T40 · descarga y borrado | `200` con el MIME verificado, `Content-Disposition` con el nombre codificado y `nosniff`; el docente asignado y el admin descargan; otro estudiante y otro docente reciben `404`; el dueño borra (`200`) y el archivo desaparece del disco, la fila queda con `fecha_eliminacion` y se audita; otro estudiante `404`, el docente `403`; con la tarea `En revisión` la subida → `422 TASK_EVIDENCE_LOCKED` y el admin puede retirar la evidencia; archivo ausente en disco → `404 ATTACHMENT_FILE_MISSING` y el borrado sigue siendo idempotente |
| T37 · cascada | `DELETE /entrepreneurship/:id` deja la fila con `fecha_eliminacion`, borra el archivo del disco y conserva la tarea (histórico legible); el adjunto queda con baja lógica |
| Avance (R21) | Dos tareas con una calificada → `avance = 50`, `total = 2`, `completadas = 1`; al dar de baja la pendiente → `avance = 100`; sin tareas → `0`; el endpoint por fase devuelve las cuatro fases y una fila `faseId: null` para las tareas sin fase |
| Vencida | `fechaLimite` pasada → `estado = 'Vencida'` y `vencida = true` en la lectura y en el filtro; la columna guardada sigue `Pendiente`; la entrega funciona igual |
| Alcance | Estudiante solo lo propio (`my-task`); docente solo los emprendimientos con asignación activa; detalle ajeno `404`; admin todo; filtros por estado, prioridad y texto; `sort` y `pageSize` fuera de rango → `400` |
| `npm run typecheck` | Los tres workspaces sin errores |
| `npm run check:schema` | Sigue en verde (41 tablas, 22 listas `CHECK`) |
| Recorrido manual a través de Caddy | Pila recreada desde cero (`down -v` + `up --build`): **96 comprobaciones, 96 en el estado esperado**. Incluye las 5 sesiones del seed (incluida la cuenta `Limitado` bloqueada con `403 ACCOUNT_NOT_ACTIVE`), el ciclo completo de la tarea, `TASK_EVIDENCE_REQUIRED`, `TASK_EVIDENCE_LOCKED`, la calificación, la devolución sin y con motivo, el avance 33 % en la ficha, los seguimientos con su evidencia, la descarga y el borrado, las validaciones de subida (GIF, travesía, sin archivo), la cascada de BR-006 comprobando el archivo en el disco del host, y las 11 acciones de auditoría y los avisos al estudiante |

### Decisiones y huecos registrados

- §5.8: módulo de trabajo y alcance, destinatario de la tarea, evidencia obligatoria,
  ciclo de vida, calificación y devolución, avance, evidencia congelada, subida, límites,
  borrado, cascada, seguimientos y paginación.
- P-24: el diagrama no tiene fecha de entrega; `fechaEnvio` se deriva de la evidencia más
  reciente y «Entregada a tiempo» no se calcula.
- P-25: BR-006 pide borrar los archivos al eliminar un usuario, pero T37 exige conservar el
  histórico legible. La cascada física se aplica solo al emprendimiento; la baja de un
  usuario conserva sus archivos hasta que se confirme.
- P-26: el prototipo ofrece tipo de evidencia, entrega fuera de fecha, asignación al grupo y
  un campo «Puntos» que no aparece en el formulario; no se crean columnas para ello.
- P-27: `advice` se rechaza con `400` hasta que exista el módulo de asesorías de la Etapa 8.
- #34: la tarea se asigna al propietario del emprendimiento; no se inventa un modelo de
  grupos.

### Sin verificar / pendiente

- Las asesorías y sus adjuntos llegan con la Etapa 8; el pivote `adjuntos_asesorias` ya está
  previsto y la cascada de BR-006 lo incluye.
- Las vistas de tareas y seguimientos se pintan en la Etapa 11; el contrato ya devuelve
  `evidencias`, `fechaEnvio`, `fase` y el progreso por fase.
- El enlace de la notificación usa las rutas de la SPA (`/estudiante/tareas/:id`,
  `/docente/tareas/:id`); se valida al construir la navegación.
- La descarga no implementa `Range` ni reanudación: no lo pide ningún requisito.

**Puerta:** superada (T16, T17, T18, T19, T37 y T40 en verde; completar una tarea sin
evidencia es imposible por API; la evidencia se borra del disco al dar de baja la tarea, el
seguimiento o el emprendimiento; el avance se deriva de la base y no del cliente).

---

## Etapa 8 — Asesorías, notificaciones y tiempo real

- **Fecha:** 2026-10-25
- **Commit:** `9d65319`

### Hecho

- `modules/advice`: ciclo completo de la asesoría. El alta exige `emprendimientoId`,
  `docenteId` y `tema`; con bloque nace `Programada` y sin bloque `Por agendar`. El
  estudiante no crea, edita ni confirma (BR-002); el docente solo agenda para sí mismo y
  en sus emprendimientos con asignación activa. La lectura respeta el rol y un id fuera de
  alcance responde `404`.
- Ciclo de vida con rutas propias: `accept` (`Por agendar`/`Programada` → `Confirmada`,
  exige bloque), `repropose` (exige bloque, → `Programada`), `reject` (motivo obligatorio,
  → `Cancelada`) y `PUT` para `En curso`/`Completada`. `Completada` y `Cancelada` son
  finales (`422 ADVICE_NOT_EDITABLE`); el resto de transiciones inválidas responde `422
  INVALID_ADVICE_TRANSITION`.
- T35: el solapamiento se comprueba en la transacción bajo
  `pg_advisory_xact_lock('asesorias:docente:<id>:<fecha>')` y una consulta de intersección
  de horas, excluyendo la propia y las canceladas → `409 ADVICE_SCHEDULE_CONFLICT`. Se
  aplica al crear, confirmar, reprogramar, editar el horario y cambiar de docente.
- El bloque de `fecha_y_horarios` se reutiliza por `(fecha, hora_inicio, hora_fin)` bajo su
  propio advisory lock; `fecha_asesoria` se calcula en `America/Bogota`.
- P-19 cerrado: aprobar una `Cita` exige docente, tema y bloque, y crea la asesoría en
  `Programada` con las mismas reglas del alta. El efecto se aplica una sola vez.
- `modules/notifications`: bandeja propia paginada con filtros `leida`/`tipo` y contador
  `sinLeer` exacto por tipo; marcar una como leída es idempotente y la ajena responde
  `404`; `read-all` devuelve `{ actualizadas, sinLeer }`. Ninguna ruta exige cuenta
  `Activo` (AQ-07 opción A).
- `services/notificationChannel`: SSE con fan-out por usuario, evento `ready`, evento
  `notification` mínimo (id, tipo, contador) y latido cada 25 s. La publicación ocurre
  **después del commit** gracias a `afterCommit` (`AsyncLocalStorage` en `db/pool.ts`).
- `services/notify.ts` respeta `notif_tareas`, `notif_asesorias` y `notif_seguimiento`.
- `advice` es una entidad de adjuntos: escriben el estudiante dueño, el docente asignado y
  el admin; se congela en `Completada`/`Cancelada` (`422 ADVICE_EVIDENCE_LOCKED`), salvo el
  borrado del administrador.
- 6 acciones de auditoría nuevas (`Alta`, `Edición`, `Confirmación`, `Reprogramación`,
  `Cancelación` y `Baja lógica de asesoría`).
- Defecto del seed corregido: los catálogos se siembran con id explícito y el `SERIAL` no
  avanzaba; el seed cierra con `setval(pg_get_serial_sequence(...))` para las 14 tablas.

### Verificado

| Comprobación | Resultado |
|---|---|
| `npm test` (PostgreSQL real, 12 archivos) | **176 pruebas en verde** (158 de las etapas 3–7 + 18 nuevas: 10 de asesorías, 7 de notificaciones y la ampliación de solicitudes) |
| T20 · BR-002 y alcance | El estudiante no crea, edita ni confirma (`403 ROLE_NOT_ALLOWED`); el docente no agenda para otro (`403`); un docente sin asignación recibe `404`; el estudiante solo ve las suyas y el docente solo las que tiene asignadas; la cuenta `Limitado` recibe `403 ACCOUNT_NOT_ACTIVE`; el auditor `403` |
| Ciclo de vida | Alta con y sin bloque (`Programada` / `Por agendar`); `accept` sin horario → `422 ADVICE_NOT_SCHEDULED`; con horario → `Confirmada`; `En curso` y `Completada` solo en orden; editar o rechazar una completada → `422 ADVICE_NOT_EDITABLE`; el docente no cambia de docente (`403 FIELD_NOT_ALLOWED`); `repropose` parcial → `400`; `reject` sin motivo → `400` y con motivo → `Cancelada` |
| T35 · solapamiento | Bloque solapado → `409 ADVICE_SCHEDULE_CONFLICT`; bloque contiguo → `201`; otro docente a la misma hora → `201`; al cancelar, el bloque se libera y se puede reutilizar |
| T36 · Cita (P-19) | Aprobar sin datos → `400` con el campo que falta; con docente y bloque → solicitud `Aprobada` y **una** asesoría `Programada`; la segunda aprobación → `422 REQUEST_ALREADY_RESOLVED` y no crea otra |
| T21 · bandeja | Solo las propias, orden descendente, `total`/`page`/`pageSize`, filtros `leida` y `tipo`, `sinLeer` por tipo; `pageSize` 101, `tipo` inválido, `leida` inválido y `orderBy` → `400`; marcar leída dos veces mantiene el contador; la ajena → `404`; `read-all` es idempotente; sin sesión → `401`; la cuenta `Limitado` lee y marca, pero sigue bloqueada en asesorías |
| T21 · SSE | Dos conexiones reales (`app.listen(0)`): el aviso de A llega a A y **nunca** a B; el frame trae `notificationId`, `tipo` y `unreadCount`, y no el mensaje; una conexión nueva recibe el contador actualizado en `ready`; marcar leída baja el contador de la siguiente conexión |
| Evidencias de asesoría | El estudiante sube y el docente descarga con el MIME verificado; el docente ajeno recibe `404`; al completar, la subida → `422 ADVICE_EVIDENCE_LOCKED`; el admin puede borrar y la evidencia queda dada de baja |
| Baja de asesoría | `DELETE` deja `fecha_eliminacion`, la lectura responde `404` y la fila se conserva; se audita la baja |
| `npm run typecheck` | Los tres workspaces sin errores |
| `npm run check:schema` | Sigue en verde (41 tablas, 22 listas `CHECK`) |
| Recorrido manual a través de Caddy | Pila recreada desde cero (`down -v` + `up --build`): **107 comprobaciones, 107 en el estado esperado**. Incluye las 5 sesiones del seed, BR-002, T35, el ciclo completo, la reprogramación y la cancelación, la reutilización del bloque, el alcance por rol, las evidencias, la baja lógica, la Cita de T36, la bandeja, los dos flujos SSE a través del proxy, las 6 acciones de auditoría y el avance de la secuencia de `fecha_y_horarios` |

### Decisiones y huecos registrados

- §5.9: alcance, BR-002, alta, horario, T35, ciclo de vida, edición, rechazo, baja,
  evidencias, Cita, listado, bandeja, tiempo real, preferencias, auditoría y el ajuste de
  secuencias del seed.
- P-19 y P-27 cerrados.
- P-28: no hay columna de código ni de descripción en `asesorias`; `ASES-###` se deriva.
- P-29: el motivo de cancelación no tiene columna; va en la auditoría y en el aviso.
- P-30: T35 solo cubre al mismo docente el mismo día y no hay índice único.
- P-31: las preferencias de aviso son claves globales, no por usuario.
- P-32: SSE en memoria de una sola instancia; el evento no lleva el cuerpo.
- P-33: la fecha preferida de la cita viaja en `detalle`; la aprobación fija el bloque.
- P-34: los cambios de estado son manuales; no hay «No asistió».
- #35: el prototipo dice «Finalizada» y el estado canónico es `Completada`.
- #36: el formulario pide Estudiante y la API recibe el emprendimiento.
- #37: no se crea catálogo de temas ni columna de descripción.

### Sin verificar / pendiente

- El canal SSE es de una sola instancia; con varias réplicas haría falta un bus compartido
  (P-32, Etapa 12).
- La SPA que consume la bandeja y el flujo llega en la Etapa 11; el contrato ya expone
  `sinLeer`, los filtros y los eventos.
- El aviso por correo de las asesorías no se envía: FR-019 se cumple con la bandeja y el
  tiempo real; el correo se decide con la Coordinadora.
- La exportación de asesorías y la vista de calendario son de la Etapa 11.

**Puerta:** superada (T20, T21, T35 y T36 en verde; el estudiante no puede agendar por API;
el solapamiento del docente se impide en la transacción; un aviso de A nunca llega a la
conexión de B; el evento se publica después del commit).

## Etapa 9 — Diagnóstico, actas y eventos

- **Fecha:** 2026-10-25
- **Commit:** `e6b5e57` (módulos) + `cce68ca` (descarga del acta para la cuenta `Limitado`)

### Hecho

- `modules/diagnosis`: instrumento, borrador y envío. Un emprendimiento tiene **un**
  diagnóstico inicial: el borrador (`En progreso`) se reutiliza en cada guardado y, al
  enviar, las respuestas quedan bloqueadas (`Enviado`). El envío exige las 22 preguntas
  activas; una pregunta inexistente o un valor fuera de las opciones de una selección
  única responde `400` con el índice exacto. `GET /diagnosis`, `GET /diagnosis/:id` y
  `GET /diagnosis/:id/report` usan el alcance del expediente (admin, docente asignado,
  dueño); `GET /characterization/me` devuelve el avance por sección.
- **Sin rúbrica no hay puntaje** (AQ-09): `puntajeTotal` queda `null`, no se escriben filas
  de `valoracion` ni de `caracterizacion`, y cada lectura declara `RUBRIC_NOT_CONFIGURED`.
  El informe se sirve como JSON con las cinco secciones sin puntaje y `urlInforme: null`.
- `modules/acta`: cada carga crea una **versión** en `En revisión`. Una pendiente responde
  `409 ACTA_ALREADY_PENDING`, una aprobada `409 ACTA_ALREADY_APPROVED` y una rechazada se
  puede reemplazar. La revisión es solo del administrador y solo desde `En revisión`
  (`422 ACTA_NOT_REVIEWABLE`); el rechazo exige `observaciones` (BR-009). Se guardan
  revisor y fecha, se audita y se avisa al estudiante con el motivo.
- Ninguna ruta de acta exige cuenta `Activo` (AQ-07 opción A). La descarga del archivo
  (`GET /attachments/:id` con `entidad = acta`) tampoco: se retiró `requireActiveAccount`
  del middleware de lectura y el servicio exige `Activo` solo para las evidencias de
  tareas, seguimientos y asesorías.
- `modules/events`: el administrador crea, edita, publica y da de baja; `estado` acepta
  `Pendiente` y `Publicado` (`Aprobado`/`Rechazado` reservados, P-37). El docente y el
  estudiante solo ven los publicados; un borrador responde `404` también por id. La
  inscripción mueve `cupo` (puestos disponibles) bajo `pg_advisory_xact_lock`, y una
  capacidad menor que las inscripciones responde `422 EVENT_CAPACITY_BELOW_REGISTRATIONS`.
  El docente recomienda solo a sus emprendimientos con asignación activa y a eventos
  publicados; la recomendación nace `Pendiente`, se audita y avisa al estudiante.
- `services/schedule.ts`: el bloque `(fecha, hora_inicio, hora_fin)` de asesorías se
  extrajo a un servicio compartido y lo reutilizan los eventos.
- 10 acciones de auditoría nuevas y `setval` para la secuencia de `eventos` en el seed.

### Verificado

| Comprobación | Resultado |
|---|---|
| `npm test` (PostgreSQL real, 15 archivos) | **201 pruebas en verde** (176 de las etapas 3–8 + 25 nuevas) |
| T25 · instrumento y borrador | Formulario con 22 preguntas en 5 secciones; sin diagnóstico → `404`; el borrador queda `En progreso` con 1 respuesta y se reutiliza (una sola fila); el envío incompleto → `422 DIAGNOSIS_INCOMPLETE`; el envío completo deja `Enviado` con 22 respuestas, `puntajeTotal: null` y `RUBRIC_NOT_CONFIGURED`; un nuevo guardado → `422 DIAGNOSIS_ALREADY_SUBMITTED`; no se escriben `valoracion` ni `caracterizacion`; se audita el envío con el motivo |
| T25 · validaciones | Pregunta inexistente → `400` con `respuestas.0.preguntaId`; valor fuera de opciones → `400` con `respuestas.0.valor`; pregunta repetida y `puntajeTotal` en el cuerpo → `400`; `pageSize` 101, `sort` y `order` fuera de lista → `400` |
| T25 · alcance | El administrador, el docente asignado y el dueño leen el diagnóstico; otro estudiante y otro docente reciben `404`; el docente ajeno ve `total = 0`; una cuenta `Limitado` recibe `403 ACCOUNT_NOT_ACTIVE`; un estudiante sin emprendimiento → `422 ENTREPRENEURSHIP_REQUIRED` |
| T25 · informe y caracterización | `informe.disponible = false`, `motivo = RUBRIC_NOT_CONFIGURED`, cinco secciones con `puntaje` y `resultado` en `null`, `valoracion: []`, `urlInforme: null`; la caracterización suma 22 respuestas repartidas en las cinco secciones |
| T26 · ciclo del acta | Carga → `En revisión` con adjunto PDF; segunda carga → `409 ACTA_ALREADY_PENDING`; rechazo sin motivo → `400`; rechazo con motivo → `Rechazada` con revisor, fecha, aviso y auditoría; revisar dos veces → `422 ACTA_NOT_REVIEWABLE`; la rechazada admite una versión nueva; la aprobada bloquea otra carga con `409 ACTA_ALREADY_APPROVED`; el histórico conserva `Rechazada, Aprobada` |
| T26 · archivo y alcance | La plantilla responde `404 ACTA_TEMPLATE_NOT_CONFIGURED`; el docente recibe `403` en `/acta` y `404` al descargar el archivo; el dueño y el administrador descargan con `Content-Disposition`; un tercero recibe `404`; `DELETE /attachments/:id` sobre el acta → `403 ROLE_NOT_ALLOWED`; el listado propio y el filtro del administrador coinciden |
| T26 · cuenta `Limitado` | Carga su acta, la lista y **descarga el archivo** (`200`, `application/pdf`); una cuenta inactiva no descarga la evidencia de una tarea de su propiedad (`403 ACCOUNT_NOT_ACTIVE`) |
| T27 · CRUD y visibilidad | El administrador crea, lee, edita y da de baja; el estudiante y el docente reciben `403` al escribir; `organizadorId`, horario parcial, horas invertidas y capacidad 0 → `400`; el borrador responde `404` al docente y al estudiante y no aparece en su listado; el publicado sí |
| T27 · inscripción y cupo | La inscripción descuenta `cupo` y devuelve `inscrito: true`; duplicada → `409 EVENT_ALREADY_REGISTERED`; sin puestos → `422 EVENT_FULL`; docente y administrador → `403`; cancelar libera el puesto y una segunda cancelación → `404 EVENT_REGISTRATION_NOT_FOUND`; capacidad menor que las inscripciones → `422 EVENT_CAPACITY_BELOW_REGISTRATIONS`; un evento sin `requiereRegistro` → `422 EVENT_REGISTRATION_NOT_REQUIRED`; sin capacidad, `cupo = null` |
| T27 · recomendaciones | El docente asignado recomienda (`201`, `Pendiente`, estudiante derivado) y el estudiante lo ve; otro estudiante ve `0`; el docente ajeno recibe `404`; estudiante y administrador `403`; un borrador `404`; un `estudianteId` ajeno `400`; se audita y se avisa con tipo `Evento` |
| T27 · baja y auditoría | `DELETE` deja `fecha_eliminacion`, la lectura responde `404` y las inscripciones se conservan; se auditan alta, edición, baja, inscripción, cancelación y recomendación |
| `npm run typecheck` | Los tres workspaces sin errores |
| `npm run check:schema` | Sigue en verde (41 tablas, 22 listas `CHECK`) |
| Recorrido manual a través de Caddy | Pila recreada desde cero (`down -v` + `up --build`): **160 comprobaciones, 160 en el estado esperado**. Incluye las 5 sesiones del seed, el cuestionario completo, el informe sin rúbrica, el ciclo del acta con sus versiones y su archivo, el alta de un tercer estudiante para el cupo, la inscripción y el evento lleno, las recomendaciones, la baja lógica y las 10 acciones de auditoría |

### Decisiones y huecos registrados

- §5.10: alcance y ciclo del diagnóstico, puntaje e informe, revisión docente,
  caracterización, ciclo del acta, cuenta `Limitado`, plantilla, archivo del acta, eventos
  (escritura, visibilidad, cupo, inscripción, recomendaciones), auditoría y seed.
- P-35: sin rúbrica no hay puntaje, ni PDF, ni filas de `valoracion`/`caracterizacion`.
- P-36: la plantilla legal del acta no está en el repositorio; `GET /acta/template` declara
  el hueco con `404 ACTA_TEMPLATE_NOT_CONFIGURED`.
- P-37: `Aprobado`/`Rechazado` de `eventos` quedan reservados; el administrador es el
  organizador y no hay flujo de aprobación.
- P-38: `cupo` es el número de puestos **disponibles**; sin capacidad no hay tope ni lista
  de espera.
- P-39: `Revisado` no es alcanzable; no hay endpoint de revisión del diagnóstico.
- P-40: la recomendación nace `Pendiente` y no hay endpoint para aceptarla, rechazarla ni
  marcar asistencia; el diagrama no define esos valores.
- #38: el prototipo muestra puntaje por dimensión y el requisito no lo permite.
- #39: la revisión docente del prototipo escribe recomendaciones; `valoracion` sigue
  detrás de AQ-09 y la API es de solo lectura.
- #40: el prototipo no tiene vista de acta; se implementa el circuito real y la SPA llega
  en la Etapa 11.

### Sin verificar / pendiente

- El PDF del informe de diagnóstico no se genera (P-3, P-35); `urlInforme` queda `null`.
- La plantilla legal del acta lo aporta la Coordinadora (AQ-12, P-36).
- No hay revisión del diagnóstico ni escritura de recomendaciones docentes hasta que
  AQ-09 defina dimensiones, pesos y fórmula (P-39).
- No hay aceptación/rechazo de recomendaciones ni control de asistencia a eventos: el
  diagrama no define esos flujos (P-9, P-40).
- Las vistas de diagnóstico, acta y eventos se pintan en la Etapa 11; el contrato ya
  devuelve secciones, adjunto, cupo, inscritos e `inscrito`.

**Puerta:** superada (T25, T26 y T27 en verde; sin rúbrica no se inventa puntaje; el acta
solo la revisa el administrador y el rechazo exige motivo; el docente solo recomienda a
sus emprendimientos y el estudiante solo ve eventos publicados).

---

## Etapa 10 — Tableros, reportes, respaldos, configuración y auditoría

- **Fecha:** 2026-10-25
- **Commit:** pendiente de esta etapa

### Hecho

- `modules/settings`: `GET /settings` con las 18 claves de `configuracion_programa`,
  `PUT /settings` por lote y en una transacción, validado por el `tipo_dato` de la fila, y
  `GET /settings/audit` como listado de auditoría del administrador. Solo se auditan las
  claves que cambiaron, con valor anterior y nuevo.
- `modules/reports`: cuatro reportes con una fila por hecho (`seguimiento`, `asesorias`,
  `emprendimientos`, `diagnosticos`). El mismo conjunto de filas alimenta CSV, XLSX
  (`exceljs`) y PDF (`pdfkit`), sin cálculos en el exportador. El periodo se aplica a la
  fecha propia del reporte; `emprendimientos` no lo admite porque la tabla no tiene fecha
  de creación (P-44). Cada exportación se audita.
- `modules/dashboard`: tres tableros, cada uno con **una** consulta agregada
  (`json_build_object`). El alcance se aplica en el SQL: el docente ve sus asignaciones
  activas y el estudiante su emprendimiento más reciente.
- `modules/audit`: módulo del auditor (rol 4) con cuatro `GET` y ninguna escritura. Nombres,
  documentos y correos salen enmascarados en el servidor; cada lectura y cada exportación
  se registran.
- `modules/backups` + `services/backupFiles.ts`: respaldo `Completo` (volcado `pg_dump`
  custom + instantánea incremental + manifiesto con hashes) y `Parcial` (solo volcado). La
  instantánea usa `rsync -a --link-dest` cuando existe y un copiador con `fs.link` cuando
  no (P-45). Código `BKP-YYYYMMDD-HHMM` con sufijo en el mismo minuto y comprobación en
  disco, lock de sesión para el respaldo simultáneo, retención por la `retencion_dias` de
  cada fila, verificación que re-calcula hashes, descarga en streaming del volcado y de la
  instantánea (`tar.gz`) y exportación de la base a ZIP de CSV o a XLSX con una hoja por
  tabla.
- `jobs/`: inactividad a las 06:00, tareas vencidas a las 06:10 y respaldo a las 09:00
  (hora de Bogotá). El planificador revisa cada 30 s, corre cada job una vez al día y no
  recupera corridas perdidas. La inactividad solo toca estudiantes `Activo` con actividad
  medible (P-46) y el aviso de tarea vencida se deduplica por tarea y destinatario.
- `services/masking.ts`, `utils/dates.ts` y `sendDownload()` (nombre ASCII + `filename*`).
- `tests/fixtures/pg_dump`: doble del binario para la suite (P-45); `tests/env.ts` apunta
  `PG_DUMP_BIN` al doble y `RSYNC_BIN` a una ruta inexistente para forzar el copiador.
- 12 acciones de auditoría nuevas: `Cambio de configuración`, `Exportación de reporte`,
  `Consulta de auditoría`, `Exportación de auditoría`, `Alta de respaldo`,
  `Descarga de respaldo`, `Verificación de respaldo`, `Retención de respaldos`,
  `Exportación de base de datos`, `Inactividad automática`,
  `Ejecución del job de inactividad` y `Ejecución del job de tareas vencidas`.

### Verificado

| Comprobación | Resultado |
|---|---|
| `npm test` (PostgreSQL real, 21 archivos) | **285 pruebas en verde** (201 de las etapas 3–9 + 84 nuevas) |
| T23 · configuración | 18 claves con tipo y descripción; el entero no numérico, el menor que uno, el booleano `sí` y el 31 de febrero se rechazan con el índice exacto (`items.0.valor`); la clave desconocida y la repetida responden `400`; un campo de más (`.strict()`) también; el texto se recorta; un guardado sin diferencias devuelve `cambios: 0` y no escribe auditoría; el cambio real deja valor anterior y nuevo; el estudiante y el docente reciben `403` en `/settings` y `/settings/audit` |
| T22 · tableros | Las cifras del administrador coinciden con `COUNT(*)` de la base (usuarios activos, emprendimientos, tareas, alertas sin docente); `avancePorMes` trae seis meses ordenados; el docente solo ve su emprendimiento y un docente sin asignaciones ve ceros; el estudiante sin emprendimiento recibe `null` y `fases: []`; cada rol recibe `403` en el tablero de otro y la cuenta `Limitado`, `403 ACCOUNT_NOT_ACTIVE` |
| T22 · reportes | Catálogo de cuatro con `formatos: [csv, xlsx, pdf]`; CSV con BOM y cabecera en español; XLSX con firma `PK`; PDF con `%PDF-`; el periodo filtra las filas del seguimiento y un rango fuera deja el reporte vacío; `format` ausente o no soportado, reporte inexistente, periodo en `emprendimientos`, rango invertido y `docenteId` que no es docente se rechazan; cada exportación deja su fila de auditoría y el catálogo muestra `ultimaGeneracion` |
| T24 · respaldos | Un `Completo` produce volcado, instantánea y manifiesto, con dos artefactos y tamaños ≥ 1 MB; el segundo se apoya en el primero (`base`), comparte inodo con el archivo sin cambios y su tamaño añadido no supera el lógico; borrar la instantánea anterior no rompe la nueva; un archivo eliminado desaparece del siguiente y sigue en el anterior; `verify` re-calcula hashes y pasa la fila a `Fallida` al corromper un archivo, y un `Fallida` nunca es base del siguiente; un `Parcial` no tiene manifiesto, no se verifica (`422`) ni se descarga su instantánea (`404`); el volcado fallido deja la fila `Fallida` sin tamaños (`500 BACKUP_DUMP_FAILED`); el respaldo simultáneo responde `409 BACKUP_IN_PROGRESS`; la retención borra solo el vencido y nunca el recién creado; la descarga del volcado y del `tar.gz` funciona y se audita; la exportación de base sale como ZIP (`csv`) y como XLSX; ninguna ruta es del estudiante |
| T14 · jobs | La inactividad pasa a `Inactivo` al estudiante con 100 días sin actividad y deja auditoría y aviso; la segunda corrida no afecta a nadie; no toca cuentas recientes, ni `ultima_actividad` nula, ni docentes; respeta el umbral configurado; deja el registro de la corrida. El job de tareas vencidas avisa al estudiante y al mentor una sola vez (la segunda corrida avisa 0) y no toca tareas futuras; el planificador arranca y se detiene de forma idempotente |
| T38 · auditor | El tablero no contiene correos y las cifras son completas; los expedientes muestran `Ana M.` / `Restrepo G.`, documento `******004` y correo `a***@dominio`; la exportación reduce el nombre completo a `Ana G.`; cada lectura y cada exportación deja su fila; el administrador recibe `403` en `/audit/*` y no existe ningún `POST`; la cuenta `Limitado`, `403 ACCOUNT_NOT_ACTIVE` |
| `npm run typecheck` | Los tres workspaces sin errores |
| `npm run check:schema` | Sigue en verde (41 tablas, 22 listas `CHECK`) |
| Recorrido manual a través de Caddy | Pila recreada desde cero: **112 comprobaciones, 112 en el estado esperado**, con `pg_dump` y `rsync` **reales** dentro del contenedor. Incluye los tres tableros contra la base, la configuración con sus validaciones y su bitácora, los tres formatos de reporte, dos respaldos completos con su incremental y su verificación, el parcial, la descarga del volcado (`PGDMP`) y de la instantánea (`1f8b`), la exportación de la base y el auditor con datos enmascarados |
| D19 · espigueo de gráficos | Barras, líneas y dona construidos con `recharts` y con SVG a mano: 585.17 kB / 173.17 kB gzip frente a 223.38 kB / 69.98 kB gzip; decisión y comparación en `docs/decisions.md` §3.1 |

### Decisiones y huecos registrados

- §5.11: configuración por lote y su auditoría, bitácora del administrador, catálogo y
  periodo de los reportes, metadatos por formato, tableros y sus meses, alcance y
  enmascarado del auditor, composición, tamaños, código, integridad, retención y motor de
  los respaldos, exportación de la base, horario y alcance de los jobs y elección de
  gráficos.
- D19: SVG a mano detrás de `components/charts/`, con la comparación de §3.1.
- P-41: la retención de respaldos borra fila y directorio (no hay `fecha_eliminacion`).
- P-42: no hay tabla de ejecuciones de jobs; cada corrida queda en `auditoria_eventos`.
- P-43: los indicadores de cada tablero son los del prototipo; el master no fija la lista.
- P-44: `emprendimientos` rechaza el periodo porque la tabla no tiene fecha de creación.
- P-45: `pg_dump` y `rsync` se configuran por entorno; sin `rsync` la instantánea usa
  `fs.link`.
- P-46: el job de inactividad no marca cuentas con `ultima_actividad` nula.

### Sin verificar / pendiente

- El PDF del informe de diagnóstico sigue sin generarse (P-3, P-35).
- La restauración de un respaldo es un procedimiento manual que se documenta y se ensaya en
  la Etapa 12 (D22); no hay endpoint de restauración.
- La retención por tamaño y la alerta de espacio no están en los requisitos: se proponen a
  la Coordinadora (D22).
- El auditor no existe en la semilla: se habilita por SQL, como lo haría la coordinación.
- Los tableros, reportes, respaldos, configuración y auditoría se pintan en la Etapa 11; el
  contrato ya devuelve todas sus cifras.
- Las gráficas de la SPA se implementan en la Etapa 11 con la decisión D19; esta etapa solo
  fija el motor.

**Puerta:** superada (T22, T23, T24 y T14 en verde; cada cifra de tablero y de reporte traza
a un agregado SQL; un respaldo `Completo` lista sus dos artefactos con tamaños reales y el
segundo se apoya en el primero; el auditor no escribe y ve los datos personales
enmascarados; D19 queda decidida antes de la Etapa 11).

---

## Etapa 11 — Frontend de las 64 vistas

- **Fecha:** 2026-10-26
- **Commit:** pendiente de esta etapa (sin push)
- **Entorno:** Vite 8 en `http://localhost:5173`, backend y PostgreSQL en Docker
  (`docker-compose.yml` + `docker-compose.dev.yml`)

### Hecho

- **Base de la SPA**: tema en `styles/tokens.css` con los seis hex de la paleta, escala
  tipográfica 13–32 px, Inter autoalojada (`@fontsource/inter`) y hojas separadas
  `base`, `layout`, `components`, `lists`, `interactions`, `auth` y `fonts`.
- **Componentes** (26): `Icon` con 50 iconos, `Badge` icono+texto, `Button`, `Card`,
  `PageHeader`, `States` (loading/error/empty), `Toolbar`, `Pagination`, `DataTable`,
  `ListTable`, `FormField`, `Modal`, `Drawer`, `Toast`, `Tabs`, `ProgressBar`, `Metric`,
  `DefinitionList`, `Dropzone`, `EvidenceUploader`, `OtpInput`, `AuthLayout`,
  `ReasonModal`, `QueryGate`, `AppShell` y `NotificationDrawer`.
- **Datos**: `api/client.ts` con `apiGet`/`apiSend`/`apiDownload`/`apiUpload`, DTO de lectura
  en `api/types.ts` alineados con el payload real y consultas TanStack Query por módulo en
  `queries/`. Toda consulta pasa por `QueryGate`; las listas tienen loading, error con
  reintento y vacío propio. El SSE `notification` invalida la bandeja y el contador.
- **Sesión y guardas**: `AuthProvider` resuelve la sesión con `GET /users/me`; `RequireAuth`,
  `RequireRole` y `RequireActive`; la guarda `Active` deja fuera perfil, acta y
  notificaciones (AQ-07 opción A). `HomeRedirect` manda a cada rol a su panel o a
  `/estudiante/perfil` si la cuenta está `Limitado`.
- **Rutas**: públicas `/login`, `/registro`, `/verificar`, `/recuperar`, `/`, `/403`, `*`;
  bloques `/estudiante`, `/docente` y `/admin` con las 64 vistas. Los segmentos van en
  español (D24) y los enlaces profundos de notificación resuelven.
- **Compartidas**: `EntrepreneurshipPlanPage`, `ExpedientePage`, `ActaPage` (nueva),
  `PasswordPage` y `AccountSettingsPage`; listas y detalles compartidos con acciones y
  columnas por rol (`EntrepreneurshipsListPage`, `TasksListPage`, `TaskDetailPage`,
  `AdviceListPage`, `AdviceFormPage`, `TracingListPage`, `TracingFormPage`,
  `EventsListPage`, `EventFormPage`, `DiagnosesListPage`, `DiagnosisDetailPage`).
- **Vistas nuevas**: `/estudiante/acta` (plantilla con hueco P-36, carga, historial y
  reemplazo) y `/admin/actas` (bandeja, filtro, aprobar y rechazar con observaciones).
- **Buscador global**: la barra superior navega a `?q=` del listado principal del rol; los
  listados inicializan y sincronizan el término con la URL.
- **Configuración admin**: 18 claves agrupadas en 5 bloques, etiquetas humanas, guardado por
  lote solo de lo cambiado y bitácora en pestaña aparte.

### Verificado

| Comprobación | Resultado |
|---|---|
| `npm run typecheck` | Shared, backend y frontend sin errores (`strict`, `noUnusedLocals`, `noUnusedParameters`) |
| `npm run build -w frontend` | Build de producción correcto; único aviso, el chunk > 500 kB esperado por el alcance de la SPA |
| Recorrido real de las 64 rutas | Login con los tres roles demo; 19 vistas de estudiante, 20 de docente y 19 de administrador más las compartidas y las dos nuevas, todas en navegador contra la API real |
| Estados de error y vacío | Detalle de asesoría y de seguimiento ajenos/inexistentes, diagnóstico inexistente, listas sin resultados, acta sin plantilla y cuenta `Limitado` muestran su estado propio; ninguna pantalla con `[object Object]`, `undefined` o `NaN` |
| Consola del navegador | Único error: el `401` esperado de `/users/me` antes de iniciar sesión |
| Registro real | Alta de `estudiante.prueba11@uniminuto.edu.co` → `/verificar`; OTP de 8 dígitos leído de `storage/mail/*.eml` → correo verificado y aviso de cuenta pendiente |
| Cuenta `Limitado` | Inicia sesión y aterriza en `/estudiante/perfil`; `/estudiante/tareas` responde con la pantalla «Tu cuenta está limitada» y los enlaces a perfil, acta y notificaciones |
| Recuperación real | Tres pasos con OTP leído del `.eml`; contraseña nueva guardada e inicio de sesión correcto con ella |
| Activación y baja | `POST /users/:id/validate` desde la UI activa la cuenta `Limitado`; la baja lógica la saca de los listados y deja el estado vacío |
| Buscador global `?q=` | Verificado en `/estudiante/emprendimientos`, `/docente/emprendimientos` y `/admin/usuarios`, con aviso «Resultados para «q»» y vacío específico |
| Correcciones de la revisión visual | Badge `Revisión: …` en el detalle de tarea; sin botón «Activar» duplicado cuando la cuenta es `Limitado`; etiquetas humanas en Configuración; valores nulos de respaldos y del actor de auditoría con fallback |
| Estado del entorno | Base recreada con `docker compose down -v` + `up -d postgres backend`: 5 usuarios demo, 1 emprendimiento y 2 tareas del seed; backend con los tres jobs programados; sin datos de prueba |

### Decisiones y huecos registrados

- §5.12 (D23–D38): OTP, rutas en español, adjuntos no listables, seguimiento sin listado
  global, actas del administrador, contraseña por OTP, guarda `Active`, buscador global,
  etiquetas y guardado por lote, entorno de desarrollo, páginas compartidas por rol, DTO a
  mano, solicitud de asesoría, plan CSV y evidencias posteriores al alta, huecos visibles y
  reset de la base de desarrollo.
- AQ-09: el diagnóstico y su resultado se muestran sin puntaje, dimensiones ni bandas.
- P-3/P-35: el PDF del diagnóstico no se genera; el botón queda deshabilitado y explicado.
- P-36: `GET /acta/template` responde `404 ACTA_TEMPLATE_NOT_CONFIGURED`; la vista lo trata
  como hueco y permite subir el archivo firmado.
- P-1: el estudiante no reprograma; solicita una cita nueva con fecha y hora preferidas
  (P-20) y el administrador fija docente y bloque.
- P-40: las recomendaciones de evento quedan `Pendiente` sin transiciones.
- P-44: el reporte de emprendimientos no ofrece periodo.
- P-31: las preferencias de aviso son claves globales del programa, no interruptores por
  usuario.
- P-16: no hay restauración de cuentas dadas de baja.
- D22: no hay restauración de respaldos en la interfaz.

### Sin verificar / pendiente

- No se ejecutó la suite del backend en esta etapa porque no se modificó: siguen vigentes las
  285 pruebas en verde de la Etapa 10.
- El recorrido se hizo con Vite y el proxy `/api`; la puerta final con el build servido por
  Caddy y la suite Playwright corresponden a la Etapa 12.
- No se creó commit ni rama nueva; el trabajo queda en el árbol de trabajo, como se pidió.
- Los datos sintéticos de registro, recuperación y baja se descartaron al recrear la base;
  no viajan a la Etapa 12.

**Puerta:** superada (las 64 rutas existen y se recorrieron con datos reales; typecheck y
build en verde; registro, verificación OTP, recuperación, activación y baja probados de punta
a punta; los huecos AQ-09, P-3, P-36, P-1, P-40, P-44, P-31 y P-16 se muestran explicados y
no simulados; el entorno queda en el seed prístino).
