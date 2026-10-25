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
