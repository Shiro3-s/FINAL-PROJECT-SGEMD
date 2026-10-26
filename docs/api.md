# API — SGEMD

Contrato de la API HTTP del MVP. Se amplía en cada etapa; las etapas 1–6 están
implementadas y probadas.

- **Prefijo:** todo cuelga de `/api` en el mismo origen que la SPA (sin CORS).
- **Formato:** JSON `application/json; charset=utf-8`.
- **Autenticación:** cookie `sgemd_session` (`HttpOnly; Secure; SameSite=Strict; Path=/;
  Max-Age=28800`). El token **nunca** viaja en el cuerpo de una respuesta.
- **CSRF:** toda petición que muta (`POST`, `PUT`, `PATCH`, `DELETE`) debe enviar
  `Origin` igual a `APP_ORIGIN` (o `Sec-Fetch-Site: same-origin`). En otro caso:
  `403 ORIGIN_NOT_ALLOWED`. No se envían cabeceras `Access-Control-Allow-*`.
- **Autorización:** el rol y el estado se leen de la fila de `usuarios` en **cada**
  petición; el JWT solo aporta el `id`.

## Envolturas

Éxito con datos:

```json
{ "success": true, "data": { } }
```

Éxito sin datos útiles:

```json
{ "success": true, "message": "Sesión cerrada." }
```

Error:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Revisa los datos enviados.",
    "fields": { "correoInstitucional": "Este correo ya está registrado" }
  }
}
```

`fields` solo aparece en errores de validación y de unicidad. Nunca se devuelve un
stack, una ruta interna ni un valor de configuración.

## Códigos de error

| HTTP | `code` | Cuándo |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Cuerpo inválido, campo desconocido (`.strict()`) o catálogo inexistente |
| 400 | `EMAIL_DOMAIN_NOT_ALLOWED` | El correo no pertenece a un dominio de `correos_dominios_permitidos` |
| 401 | `AUTH_REQUIRED` | Falta la cookie de sesión |
| 401 | `AUTH_INVALID` | Firma inválida, token vencido o usuario con baja lógica |
| 401 | `INVALID_CREDENTIALS` | Correo o contraseña incorrectos (no distingue cuál) |
| 403 | `EMAIL_NOT_VERIFIED` | La cuenta existe y la contraseña es correcta, pero el correo no está verificado |
| 403 | `ACCOUNT_NOT_ACTIVE` | Cuenta `Limitado` o `Inactivo` en un módulo de trabajo (AQ-07) |
| 403 | `ROLE_NOT_ALLOWED` | El rol de la fila no está autorizado para la ruta |
| 403 | `FIELD_NOT_ALLOWED` | El rol puede editar el recurso, pero no ese campo (p. ej. un estudiante cambiando el sector) |
| 403 | `ORIGIN_NOT_ALLOWED` | Mutación con `Origin` ajeno o ausente |
| 404 | `NOT_FOUND` | Recurso inexistente **o fuera de alcance** (un estudiante pidiendo el id de otro) |
| 404 | `ATTACHMENT_FILE_MISSING` | La fila de la evidencia existe, pero el archivo ya no está en el disco |
| 409 | `EMAIL_TAKEN` | Correo institucional ya registrado |
| 409 | `DOCUMENT_TAKEN` | Número de documento ya registrado |
| 409 | `ASSIGNMENT_ALREADY_ACTIVE` | El emprendimiento ya tiene una asignación `activa` (R11) |
| 413 | `PAYLOAD_TOO_LARGE` | El archivo supera `upload_max_mb` (FR-008) |
| 422 | `OTP_INVALID` | Código incorrecto, vencido, ya usado o inexistente |
| 422 | `INVALID_STATE_TRANSITION` | Transición de cuenta no permitida (BR-003, R34) |
| 422 | `SELF_STATE_CHANGE_NOT_ALLOWED` | El administrador intenta cambiar el estado de su propia cuenta |
| 422 | `SELF_DELETE_NOT_ALLOWED` | Intento de baja lógica de la propia cuenta |
| 422 | `INVALID_APPROVAL_STATE` | Aprobar o rechazar un emprendimiento que ya no está `Pendiente` |
| 422 | `PARALLEL_REQUIRED` | El estudiante ya tiene un emprendimiento vigente y el alta no pide autorización de paralelo |
| 422 | `PARALLEL_LIMIT_REACHED` | Se alcanzó `paralelos_maximos` (D5) |
| 422 | `NOT_A_PARALLEL` | El primer emprendimiento del estudiante no puede ser paralelo |
| 422 | `INITIAL_STAGE_NOT_CONFIGURED` | `etapa_inicial` falta en `configuracion_programa` o no existe en el catálogo |
| 422 | `ACTA_NOT_APPROVED` | El emprendimiento no tiene un acta de compromiso `Aprobada` (BR-001) |
| 422 | `ASSIGNMENT_NOT_ACTIVE` | Se intenta editar o dar de baja una asignación que ya está `inactiva` |
| 422 | `MENTOR_NOT_ACTIVE` | El docente destinatario no tiene la cuenta `Activo` |
| 422 | `TEACHER_HOURS_LIMIT_REACHED` | La asignación supera `carga_max_horas` (FR-016, R35) |
| 422 | `TEACHER_ENTREPRENEURSHIP_LIMIT_REACHED` | La asignación supera `max_emprendimientos_docente` (FR-016, R35) |
| 422 | `ACCOUNT_ALREADY_ACTIVE` | Una cuenta `Activo` pide su propio desbloqueo |
| 422 | `ENTREPRENEURSHIP_NOT_APPROVED` | Se pide un paralelo sobre un emprendimiento que no está `Aprobado` |
| 422 | `REQUEST_ALREADY_RESOLVED` | La solicitud ya fue aprobada o rechazada |
| 422 | `REQUEST_TARGET_MISSING` | La cuenta o el emprendimiento de la solicitud ya no existe |
| 422 | `TASK_EVIDENCE_REQUIRED` | Se intenta entregar una tarea sin ninguna evidencia vigente (BR-007) |
| 422 | `INVALID_TASK_TRANSITION` | La acción no corresponde al estado actual de la tarea (T16) |
| 422 | `TASK_NOT_EDITABLE` | Se intenta editar una tarea en revisión o completada |
| 422 | `TASK_EVIDENCE_LOCKED` | Se intenta subir o borrar evidencia de una tarea ya entregada |
| 422 | `ATTACHMENT_LIMIT_REACHED` | La entidad alcanzó `upload_max_files_per_entity` |
| 429 | `OTP_COOLDOWN` | Reenvío antes del cooldown (60 s); incluye `Retry-After` |
| 429 | `OTP_ATTEMPTS_EXCEEDED` | Se agotaron los 5 intentos del código; incluye `Retry-After` |
| 429 | `RATE_LIMITED` | Se superó el límite de peticiones del endpoint; incluye `Retry-After` |
| 500 | `INTERNAL_ERROR` | Fallo no controlado (sin detalles internos) |
| 500 | `CODE_GENERATION_FAILED` | No se pudo generar un código único tras varios intentos |
| 502 | `MAIL_SEND_FAILED` | El transporte de correo falló |

## Autenticación

### `POST /api/auth/register`

Registro público de estudiante. Crea la cuenta en estado `Limitado` con
`verificado = false`, asigna el rol 2 y envía un OTP de 8 dígitos al correo
institucional.

```json
{
  "nombres": "Ana María",
  "apellidos": "Prueba",
  "tipoDocumentoId": 1,
  "numeroDocumento": "1020304050",
  "correoInstitucional": "ana@uniminuto.edu.co",
  "password": "Mínimo8Caracteres",
  "aceptaTratamiento": true
}
```

- Los seis campos y la casilla son obligatorios; un campo extra (`roles_id_roles`,
  `estado`, `verificado`, …) produce `400 VALIDATION_ERROR`.
- `tipoDocumentoId` debe existir en `tipodocumentos` (CC · TI · CE).
- El dominio del correo se valida contra `configuracion_programa`.
- La contraseña se guarda con bcrypt (coste 10) y no se devuelve jamás.

`201`:

```json
{
  "success": true,
  "data": {
    "id": 6,
    "codigo": "483920",
    "nombres": "Ana María",
    "apellidos": "Prueba",
    "correoInstitucional": "ana@uniminuto.edu.co",
    "numeroDocumento": "1020304050",
    "nivelAcademico": null,
    "verificado": false,
    "estado": "Limitado",
    "rol": { "id": 2, "nombre": "Estudiante" },
    "ultimaActividad": null
  }
}
```

### `POST /api/auth/verify`

```json
{ "correoInstitucional": "ana@uniminuto.edu.co", "codigo": "12345678" }
```

Consume el código y marca `verificado = true`. La cuenta **sigue** en `Limitado`
hasta que la coordinación la active. El código es de un solo uso, vence a los
5 minutos y admite 5 intentos; al quinto fallo se quema y responde
`429 OTP_ATTEMPTS_EXCEEDED`.

`200`: `{ "success": true, "message": "Correo verificado. Tu cuenta queda pendiente de activación por la coordinación del programa." }`

### `POST /api/auth/resend-code`

```json
{ "correoInstitucional": "ana@uniminuto.edu.co" }
```

Responde siempre `200`, exista o no la cuenta (no filtra correos). Solo envía si
la cuenta existe y no está verificada. Cooldown de 60 s
(`OTP_RESEND_COOLDOWN_SECONDS`): antes de eso responde `429 OTP_COOLDOWN`.

### `POST /api/auth/login`

```json
{ "correoInstitucional": "ana@uniminuto.edu.co", "password": "Mínimo8Caracteres" }
```

- `401 INVALID_CREDENTIALS` si el correo no existe o la contraseña no coincide
  (mismo código y tiempo de respuesta en ambos casos).
- `403 EMAIL_NOT_VERIFIED` si la contraseña es correcta pero falta verificar.
- `Limitado` e `Inactivo` **sí** pueden iniciar sesión; el bloqueo se aplica por
  endpoint (`ACCOUNT_NOT_ACTIVE`).
- Actualiza `ultima_actividad`.

`200` con `Set-Cookie`:

```
sgemd_session=<jwt>; Max-Age=28800; Path=/; Expires=…; HttpOnly; Secure; SameSite=Strict
```

```json
{ "success": true, "data": { "usuario": { "id": 4, "estado": "Activo", "rol": { "id": 2, "nombre": "Estudiante" } } } }
```

El JWT (HS256) lleva **solo** `{ id, role }` más `iat` y `exp` (8 h).

### `POST /api/auth/logout`

Limpia la cookie (`Expires` en el pasado). No requiere sesión y no invalida el
token en el servidor: el JWT es autocontenido y expira solo.

`200`: `{ "success": true, "message": "Sesión cerrada." }`

### `POST /api/auth/forgot-password`

```json
{ "correoInstitucional": "ana@uniminuto.edu.co" }
```

Responde siempre `200`. Si la cuenta existe, emite un código con
`proposito = 'Recuperación'` y lo envía por correo (mismo TTL, intentos y
cooldown que la verificación).

### `POST /api/auth/reset-password`

```json
{
  "correoInstitucional": "ana@uniminuto.edu.co",
  "codigo": "12345678",
  "password": "NuevaClave123"
}
```

Consume el código, guarda la nueva contraseña (bcrypt) y audita el cambio sin
registrar ninguna contraseña. Un código vencido, usado o incorrecto:
`422 OTP_INVALID`.

`200`: `{ "success": true, "message": "Contraseña actualizada. Ya puedes iniciar sesión." }`

## Usuarios

Todas las rutas de gestión exigen sesión, rol **Admin** (1) y cuenta **`Activo`**. Un
estudiante o un docente reciben `403 ROLE_NOT_ALLOWED`; una cuenta de coordinación
`Limitado` o `Inactivo`, `403 ACCOUNT_NOT_ACTIVE`.

El **estado** y el **rol** no se editan con `PUT`: el estado tiene sus propios endpoints y
el rol es inmutable (P-18). `codigo`, `password` y `verificado` los decide el servidor.

### `GET /api/users/me`

Requiere sesión. Devuelve el usuario de la fila actual, sin contraseña ni hash. Es la
única forma en que la SPA sabe quién es: no lee la cookie.

`200`:

```json
{
  "success": true,
  "data": {
    "id": 4,
    "codigo": "100001",
    "nombres": "Estudiante",
    "apellidos": "Demo Uno",
    "correoInstitucional": "estudiante.demo1@uniminuto.edu.co",
    "numeroDocumento": "900000004",
    "tipoDocumentoId": 1,
    "nivelAcademico": "Pregrado",
    "programaAcademicoId": 1,
    "centroUniversitarioId": 1,
    "municipioId": 1,
    "tipoPoblacionId": 1,
    "tipoUsuarioId": 2,
    "verificado": true,
    "estado": "Activo",
    "rol": { "id": 2, "nombre": "Estudiante" },
    "ultimaActividad": "2026-10-25T23:06:16.000Z"
  }
}
```

Los catálogos se devuelven como **ids** (las columnas del diagrama); los nombres llegan
por los endpoints de catálogos de la Etapa 5.

### `PUT /api/users/me`

Edita el propio perfil. Campos admitidos: `nombres`, `apellidos`, `nivelAcademico`,
`programaAcademicoId`, `centroUniversitarioId`, `municipioId`, `tipoPoblacionId`,
`tipoUsuarioId`. Cualquier otro campo (`correoInstitucional`, `numeroDocumento`,
`tipoDocumentoId`, `rolId`, `estado`, `codigo`) produce `400 VALIDATION_ERROR`. Un objeto
vacío también.

Disponible para cuentas `Limitado`: el perfil está en la matriz de AQ-07 opción A.

`200` con el usuario actualizado (misma forma que `GET /users/me`).

### `GET /api/users`

Listado paginado de todas las cuentas vigentes (las dadas de baja no aparecen).

| Parámetro | Tipo | Default | Notas |
|---|---|---|---|
| `page` | entero ≥ 1 | 1 | |
| `pageSize` | entero 1–100 | 25 | |
| `q` | texto ≤ 100 | — | Busca en nombres, apellidos, correo, código y documento (`ILIKE`) |
| `rol` | 1–4 | — | 1 Admin · 2 Estudiante · 3 Docente · 4 Auditor |
| `estado` | `Limitado` · `Activo` · `Inactivo` | — | |
| `sort` | `codigo` · `nombres` · `apellidos` · `correo` · `estado` · `ultimaActividad` | `apellidos` | Lista blanca: otra columna da `400` |
| `order` | `asc` · `desc` | `asc` | |

Cualquier otro parámetro produce `400 VALIDATION_ERROR` (`.strict()`).

`200`:

```json
{
  "success": true,
  "data": {
    "items": [ { "id": 4, "codigo": "100001", "nombres": "…", "estado": "Activo" } ],
    "total": 42,
    "page": 1,
    "pageSize": 25
  }
}
```

Cada elemento tiene la misma forma que `GET /users/me`.

### `GET /api/users/students` · `GET /api/users/teachers`

Igual que `GET /api/users` pero con el rol fijado en 2 o 3. Si el cliente envía `rol`, se
ignora: el endpoint manda.

### `GET /api/users/:id`

Admin: cualquier cuenta vigente. Cualquier otro rol: **solo su propia fila**; un id ajeno
responde `404 NOT_FOUND` (no 403) para no revelar que existe (NFR-002). `:id` no numérico:
`400 VALIDATION_ERROR`.

### `POST /api/users`

Alta de estudiante o docente por el administrador (FR-011, R33, T06).

```json
{
  "nombres": "Ana María",
  "apellidos": "Prueba",
  "numeroDocumento": "1020304050",
  "correoInstitucional": "ana@uniminuto.edu.co",
  "rolId": 2,
  "tipoDocumentoId": 1,
  "nivelAcademico": "Pregrado",
  "programaAcademicoId": 1,
  "centroUniversitarioId": 1,
  "municipioId": 1,
  "tipoPoblacionId": 1,
  "tipoUsuarioId": 2,
  "estado": "Activo"
}
```

- Obligatorios: `nombres`, `apellidos`, `numeroDocumento`, `correoInstitucional`,
  `rolId`, `tipoDocumentoId`. El resto es opcional (`null` o ausente).
- `rolId` solo admite **2** (Estudiante) o **3** (Docente). Un administrador no se crea
  desde la API.
- `estado` admite `Activo` (default, como el prototipo) o `Limitado`. `Inactivo` solo se
  alcanza después, por transición.
- El **código** lo genera el servidor: `DOC-###` para docentes, 6 dígitos para
  estudiantes. `ADM-###` existe para la coordinación sembrada por seed/operación.
- La cuenta nace `verificado = true` y con una **contraseña aleatoria inservible**. Se
  envía al correo una invitación con un código de 8 dígitos (`proposito =
  'Recuperación'`) para que el titular establezca su contraseña. El código **no** aparece
  en la respuesta.
- Si el transporte de correo falla, el alta **no se revierte**: la cuenta queda creada y
  el titular puede pedir un código en `POST /auth/forgot-password`.
- El prototipo pide además teléfono, área de conocimiento, sector, emprendimiento y
  etapa; esas columnas no existen en `usuarios` (el emprendimiento es otra entidad,
  Etapa 5). Ver discrepancia #28.

`201` con el usuario creado. `409 EMAIL_TAKEN` / `409 DOCUMENT_TAKEN` si correo o
documento ya existen. `400` si el rol no es 2/3, el dominio no es institucional o un id de
catálogo no existe.

### `PUT /api/users/:id`

Edición por el administrador. Campos admitidos: `nombres`, `apellidos`,
`numeroDocumento`, `correoInstitucional`, `tipoDocumentoId`, `nivelAcademico`,
`programaAcademicoId`, `centroUniversitarioId`, `municipioId`, `tipoPoblacionId`,
`tipoUsuarioId`. Al menos uno. `409` si el correo o el documento chocan con otra cuenta.

`200` con el usuario actualizado. La auditoría guarda solo los campos que cambiaron.

### `DELETE /api/users/:id`

Baja **lógica** (R36, BR-006): marca `fecha_eliminacion`, no borra la fila. La cuenta sale
de todos los listados, `GET /users/:id` pasa a `404` y el login responde
`401 INVALID_CREDENTIALS`. No se puede dar de baja la propia cuenta
(`422 SELF_DELETE_NOT_ALLOWED`).

`200`: `{ "success": true, "message": "Cuenta dada de baja." }`

> Restaurar una cuenta dada de baja no tiene endpoint en el master §13.3 (P-16).

### `POST /api/users/:id/validate`

Activación `Limitado → Activo` (UC-1, BR-003). Solo sobre una cuenta `Limitado`; en
cualquier otro estado, `422 INVALID_STATE_TRANSITION`.

Efectos en una sola transacción: `UPDATE` condicionado al estado leído, fila de auditoría
`Cambio de estado de cuenta` con `{estado}` anterior y nuevo, y notificación `Sistema` al
titular. Después del `COMMIT` se envía el correo de bienvenida (si el transporte falla, se
registra y el cambio se mantiene).

`200` con el usuario en `Activo`.

### `POST /api/users/:id/reactivate`

`Inactivo → Activo` (BR-005). Mismos efectos y misma respuesta que `validate`. Solo sobre
una cuenta `Inactivo`.

### `PATCH /api/users/:id/state`

Selector genérico de `admin/usuarios`.

```json
{ "estado": "Inactivo" }
```

Aplica la misma tabla de transiciones: `Limitado → Activo`, `Inactivo → Activo`,
`Activo → Inactivo`. Todo lo demás, incluido `Activo → Limitado` (que el prototipo ofrece)
y repetir el estado actual, responde `422 INVALID_STATE_TRANSITION`. El administrador no
puede cambiar el estado de su propia cuenta (`422 SELF_STATE_CHANGE_NOT_ALLOWED`).

### `POST /api/users/:id/reject`

Rechazo de la activación (UC-1).

```json
{ "motivo": "La asesoría inicial no se realizó" }
```

El motivo es obligatorio (sin longitud mínima: ningún requisito la fija, AQ-06 sigue
abierta). El diagrama no tiene un estado «Rechazado» para la cuenta, así que **la cuenta
sigue en `Limitado`**; se audita `Rechazo de activación` con el motivo y se notifica al
titular. Solo sobre una cuenta `Limitado`.

`200`: `{ "success": true, "message": "Activación rechazada. Se notificó al titular." }`

## Catálogos

Los 14 catálogos son de **solo lectura**. Todos exigen sesión salvo `GET /api/type-doc`,
que lo necesita el formulario de registro antes de que exista una cuenta. Ninguno exige
cuenta `Activo`: alimentan también la edición del perfil, disponible a una cuenta
`Limitado` (AQ-07 opción A).

| Ruta | Tabla | Forma de cada elemento |
|---|---|---|
| `GET /api/roles` | `roles` | `{ id, nombre }` |
| `GET /api/type-doc` | `tipodocumentos` | `{ id, nombre }` — **público** |
| `GET /api/type-users` | `tipousuarios` | `{ id, nombre }` |
| `GET /api/uni-centers` | `centrouniversitarios` | `{ id, nombre }` |
| `GET /api/type-pop` | `tipopoblacion` | `{ id, nombre }` |
| `GET /api/academic-programs` | `programaacademico` | `{ id, nombre }` |
| `GET /api/entrep-stage` | `etapaemprendimiento` | `{ id, nombre }` |
| `GET /api/plan-phase` | `faseplan` | `{ id, nombre }` |
| `GET /api/econo-sector` | `sectoreconomico` | `{ id, nombre }` |
| `GET /api/mode` | `modalidad` | `{ id, nombre }` |
| `GET /api/type-event` | `tipo_evento` | `{ id, nombre }` |
| `GET /api/modules` | `modulos` | `{ id, nombre }` |
| `GET /api/municipalities` | `municipios` | `{ id, nombre, departamento }` — `nombre` es la ciudad |
| `GET /api/date-times` | `fecha_y_horarios` | `{ id, nombre, fecha, horaInicio, horaFin }` — `nombre` es `YYYY-MM-DD HH:MM–HH:MM` |

`200`:

```json
{
  "success": true,
  "data": {
    "items": [ { "id": 1, "nombre": "CC" }, { "id": 2, "nombre": "CE" } ]
  }
}
```

No hay rutas de escritura: cualquier `POST`/`PUT` sobre un catálogo responde `404`.

## Emprendimientos

Módulo de trabajo: todas las rutas exigen sesión **y** cuenta `Activo` (AQ-07 opción A).

| Ruta | Roles | Notas |
|---|---|---|
| `GET /api/entrepreneurship` | Admin, Estudiante, Docente | Admin ve todos; estudiante los propios; docente los de sus `asignaciones` activas |
| `GET /api/entrepreneurship/:id` | Admin, Estudiante, Docente | Fuera de alcance: `404` (NFR-002) |
| `POST /api/entrepreneurship` | Admin | Nace `Pendiente`, `avance = 0`, código `EMP-###` |
| `PUT /api/entrepreneurship/:id` | Admin, estudiante propietario | El estudiante solo nombre, descripción y redes |
| `DELETE /api/entrepreneurship/:id` | Admin | Baja lógica (`fecha_eliminacion`) |
| `POST /api/entrepreneurship/:id/approve` | Admin | Solo desde `Pendiente` |
| `POST /api/entrepreneurship/:id/reject` | Admin | Motivo obligatorio |

Forma de un emprendimiento:

```json
{
  "id": 1,
  "codigo": "EMP-001",
  "nombre": "Sabor y Sabe",
  "descripcion": "Snacks artesanales…",
  "redesSociales": "@saborysabe",
  "estadoAprobacion": "Aprobado",
  "motivoRechazo": null,
  "esParalelo": false,
  "avance": 0,
  "etapa": { "id": 1, "nombre": "FASE 1 - Ideación" },
  "sector": { "id": 1, "nombre": "Alimentos" },
  "centroUniversitario": { "id": 1, "nombre": "Sede Norte" },
  "estudiante": {
    "id": 4,
    "codigo": "100001",
    "nombres": "Estudiante",
    "apellidos": "Demo Uno",
    "correoInstitucional": "estudiante.demo1@uniminuto.edu.co"
  }
}
```

### `GET /api/entrepreneurship`

| Parámetro | Tipo | Default | Notas |
|---|---|---|---|
| `page` | entero ≥ 1 | 1 | |
| `pageSize` | entero 1–100 | 25 | |
| `q` | texto ≤ 100 | — | Nombre o código (`ILIKE`) |
| `estado` | `Pendiente` · `Aprobado` · `Rechazado` | — | |
| `etapaId` | entero > 0 | — | |
| `sectorId` | entero > 0 | — | |
| `estudianteId` | entero > 0 | — | |
| `paralelo` | `true` · `false` | — | |
| `sort` | `codigo` · `nombre` · `estadoAprobacion` · `avance` · `estudiante` | `codigo` | Lista blanca: otra columna da `400` |
| `order` | `asc` · `desc` | `asc` | |

`200`: `{ items, total, page, pageSize }`. Cualquier otro parámetro produce `400`.

### `POST /api/entrepreneurship`

```json
{
  "nombre": "Sabor y Sabe",
  "descripcion": "Snacks artesanales…",
  "redesSociales": "@saborysabe",
  "estudianteId": 4,
  "sectorId": 1,
  "etapaId": 1,
  "centroUniversitarioId": 1,
  "esParalelo": false
}
```

- `estudianteId` debe existir, estar vigente y tener rol Estudiante (`400`).
- `etapaId` es opcional: sin él se usa `configuracion_programa.etapa_inicial`
  (`422 INITIAL_STAGE_NOT_CONFIGURED` si falta o no existe en el catálogo).
- `esParalelo` es la **autorización expresa** de BR-004, no un dato descriptivo:
  - primer emprendimiento + `esParalelo: true` → `422 NOT_A_PARALLEL`;
  - segundo (o posterior) sin `esParalelo` → `422 PARALLEL_REQUIRED`;
  - se alcanzó `paralelos_maximos` → `422 PARALLEL_LIMIT_REACHED`.
  Un emprendimiento `Rechazado` no ocupa cupo.
- `estadoAprobacion`, `motivoRechazo`, `codigo`, `avance` y `usuarioId` no se aceptan
  (`.strict()` → `400`).

`201` con el emprendimiento creado. Audita `Alta de emprendimiento` y notifica al
estudiante.

### `PUT /api/entrepreneurship/:id`

Campos editables: `nombre`, `descripcion`, `redesSociales`, `sectorId`, `etapaId`,
`centroUniversitarioId` (`null` limpia un catálogo). El administrador puede cambiar
todos; el estudiante propietario solo `nombre`, `descripcion` y `redesSociales`; si envía
los otros, `403 FIELD_NOT_ALLOWED`. El propietario no se cambia.

`200` con el emprendimiento actualizado.

### `POST /api/entrepreneurship/:id/approve`

Sin cuerpo. `200` con `estadoAprobacion: "Aprobado"`. Solo desde `Pendiente`
(`422 INVALID_APPROVAL_STATE`). Audita y notifica al estudiante en la misma transacción.

### `POST /api/entrepreneurship/:id/reject`

```json
{ "motivo": "La propuesta no está suficientemente definida" }
```

`motivo` obligatorio (`.strict()` y sin espacios). `200` con `estadoAprobacion:
"Rechazado"` y `motivoRechazo`. Solo desde `Pendiente`.

### `DELETE /api/entrepreneurship/:id`

`200` con `{ "success": true, "message": "Emprendimiento dado de baja." }`. La fila queda
con `fecha_eliminacion` y desaparece de listados y detalles.

## Asignaciones

Módulo de trabajo: todas las rutas exigen sesión **y** cuenta `Activo`. Solo el
administrador escribe (R9); la lectura se filtra por rol (R10).

| Ruta | Roles | Notas |
|---|---|---|
| `GET /api/assignments` | Admin, Docente, Estudiante | Admin todas; docente las suyas; estudiante las suyas |
| `GET /api/assignments/mentor/:id` | Admin, Docente | El docente solo puede consultar su propio id (otro → `404`); un estudiante → `403` |
| `GET /api/assignments/student/:id` | Admin, Docente, Estudiante | El estudiante solo el propio; un docente, solo estudiantes con los que tenga alguna asignación |
| `GET /api/assignments/:id` | Admin, Docente, Estudiante | Fuera de alcance: `404` |
| `POST /api/assignments` | Admin | Exige acta `Aprobada` y respeta los dos topes docentes |
| `PUT /api/assignments/:id` | Admin | Reasigna el mentor y/o ajusta las horas |
| `DELETE /api/assignments/:id` | Admin | Baja lógica: `estado = 'inactiva'` |

Forma de una asignación:

```json
{
  "id": 1,
  "fechaAsignacion": "2026-10-22T15:04:05.000Z",
  "estado": "activa",
  "horasSemanales": 4,
  "mentor": {
    "id": 2,
    "codigo": "DOC-001",
    "nombres": "Carlos",
    "apellidos": "Mendoza",
    "correoInstitucional": "carlos.mendoza@uniminuto.edu.co"
  },
  "estudiante": {
    "id": 4,
    "codigo": "100001",
    "nombres": "Estudiante",
    "apellidos": "Demo Uno",
    "correoInstitucional": "estudiante.demo1@uniminuto.edu.co"
  },
  "emprendimiento": {
    "id": 1,
    "codigo": "EMP-001",
    "nombre": "Sabor y Sabe",
    "estadoAprobacion": "Aprobado"
  }
}
```

### `GET /api/assignments`

| Parámetro | Tipo | Default | Notas |
|---|---|---|---|
| `page` | entero ≥ 1 | 1 | |
| `pageSize` | entero 1–100 | 25 | |
| `q` | texto ≤ 100 | — | Nombre, apellido, código o correo del estudiante; nombre o código del emprendimiento; nombre del docente (`ILIKE`) |
| `estado` | `activa` · `inactiva` | — | |
| `mentorId` | entero > 0 | — | |
| `estudianteId` | entero > 0 | — | |
| `emprendimientoId` | entero > 0 | — | |
| `sort` | `fecha` · `mentor` · `estudiante` · `emprendimiento` · `horas` | `fecha` | Lista blanca: otra columna da `400` |
| `order` | `asc` · `desc` | `desc` | |

`200`: `{ items, total, page, pageSize }`. Cualquier otro parámetro produce `400`.

### `POST /api/assignments`

```json
{
  "mentorId": 2,
  "emprendimientoId": 1,
  "horasSemanales": 4
}
```

- `estudianteId` **no** se envía: se deriva del propietario del emprendimiento.
  Enviarlo produce `400` (`.strict()`).
- `mentorId` debe existir, estar vigente y tener rol Docente (`400`); además debe estar
  `Activo` (`422 MENTOR_NOT_ACTIVE`).
- `emprendimientoId` debe existir y estar vigente (`400`).
- El emprendimiento debe tener al menos un acta `Aprobada` (`422 ACTA_NOT_APPROVED`,
  BR-001). No existe bandera para omitir esta comprobación.
- Si ya hay una asignación `activa` para ese emprendimiento: `409
  ASSIGNMENT_ALREADY_ACTIVE` (R11).
- Topes, sobre las asignaciones activas del mentor:
  - `SUM(horas_semanales) + horasSemanales ≤ carga_max_horas` → si no,
    `422 TEACHER_HOURS_LIMIT_REACHED` con `fields.horasSemanales`;
  - `COUNT(DISTINCT emprendimiento) + 1 ≤ max_emprendimientos_docente` → si no,
    `422 TEACHER_ENTREPRENEURSHIP_LIMIT_REACHED` con `fields.mentorId`.
  Ambos valores se leen de `configuracion_programa` y se comprueban dentro de la
  transacción, bajo un lock por mentor.
- `horasSemanales` es un entero de 1 a 20 (rango del formulario del prototipo).

`201` con la asignación creada. Audita `Alta de asignación` y notifica al docente y al
estudiante en la misma transacción.

### `PUT /api/assignments/:id`

```json
{ "mentorId": 3, "horasSemanales": 6 }
```

Ambos campos son opcionales, pero debe llegar al menos uno (`.strict()`). Solo se edita
una asignación `activa` (`422 ASSIGNMENT_NOT_ACTIVE`). Si cambia el mentor se revalidan
los dos topes del destino y el acta del emprendimiento; el docente anterior libera su
carga. `estudianteId`, `emprendimientoId`, `estado`, `codigo` y `fechaAsignacion` no se
aceptan (`400`).

`200` con la asignación actualizada. Audita `Edición de asignación`.

### `DELETE /api/assignments/:id`

`200` con `{ "success": true, "message": "Asignación dada de baja." }`. La fila queda
`estado = 'inactiva'` (la tabla no tiene `fecha_eliminacion`), libera el cupo del
emprendimiento y la carga del docente. Una segunda baja responde `422
ASSIGNMENT_NOT_ACTIVE`; para volver a vincular se crea una asignación nueva.

## Solicitudes

Bandeja única de R38: desbloqueos de cuenta, autorización de un paralelo y citas de
asesoría.

| Ruta | Roles | Notas |
|---|---|---|
| `POST /api/requests` | Cualquier sesión | El solicitante es siempre la sesión actual |
| `GET /api/requests` | Admin | Bandeja paginada con contador de pendientes |
| `GET /api/requests/:id` | Admin | |
| `PUT /api/requests/:id/approve` | Admin | Aplica el efecto de dominio una sola vez; una `Cita` exige docente y horario |
| `PUT /api/requests/:id/reject` | Admin | Motivo obligatorio, sin efecto de dominio |

Forma de una solicitud:

```json
{
  "id": 1,
  "tipo": "Desbloqueo",
  "detalle": "Cuenta inactiva por 90 días sin acceso",
  "estado": "Pendiente",
  "motivoRechazo": null,
  "fechaSolicitud": "2026-10-25T18:00:00.000Z",
  "fechaResolucion": null,
  "solicitante": {
    "id": 5,
    "codigo": "100002",
    "nombres": "Estudiante",
    "apellidos": "Demo Dos",
    "correoInstitucional": "estudiante.demo2@uniminuto.edu.co"
  },
  "emprendimiento": null,
  "resueltoPor": null
}
```

### `POST /api/requests`

```json
{
  "tipo": "Desbloqueo",
  "detalle": "Cuenta inactiva por 90 días sin acceso",
  "emprendimientoId": null
}
```

- `Desbloqueo`: lo puede pedir una cuenta `Limitado` o `Inactivo` (es el único camino para
  salir de ese estado). Una cuenta `Activo` recibe `422 ACCOUNT_ALREADY_ACTIVE` y no se
  admite `emprendimientoId`.
- `Paralelo` y `Cita`: exigen cuenta `Activo` (`403 ACCOUNT_NOT_ACTIVE`), rol Estudiante
  (`403 ROLE_NOT_ALLOWED`) y un emprendimiento propio vigente (`400` si falta o es ajeno).
  `Paralelo` exige además que esté `Aprobado` (`422 ENTREPRENEURSHIP_NOT_APPROVED`).
- `detalle` es texto libre: el diagrama no tiene columnas para los campos del prototipo
  (P-20). En una `Cita`, la fecha y la hora preferidas viajan ahí; la aprobación fija el
  bloque real y crea la asesoría.

`201` con la solicitud. Audita `Solicitud creada` y notifica a los administradores
`Activo` con la URL de la bandeja.

### `GET /api/requests`

| Parámetro | Tipo | Default | Notas |
|---|---|---|---|
| `page` | entero ≥ 1 | 1 | |
| `pageSize` | entero 1–100 | 25 | |
| `tipo` | `Desbloqueo` · `Paralelo` · `Cita` | — | |
| `estado` | `Pendiente` · `Aprobada` · `Rechazada` | — | |
| `q` | texto ≤ 100 | — | Nombres, apellidos, código, correo o detalle |
| `sort` | `fecha` · `tipo` · `estado` | `fecha` | |
| `order` | `asc` · `desc` | `desc` | |

`200`:

```json
{
  "success": true,
  "data": {
    "items": [ ],
    "total": 3,
    "page": 1,
    "pageSize": 25,
    "pendientes": { "total": 3, "Desbloqueo": 1, "Paralelo": 1, "Cita": 1 }
  }
}
```

`pendientes` cuenta **toda** la bandeja, no el filtro aplicado.

### `PUT /api/requests/:id/approve`

Cuerpo vacío para `Desbloqueo` y `Paralelo`. Para una `Cita`, el cuerpo lleva los datos con
los que nace la asesoría (P-19 cerrado en la Etapa 8):

```json
{
  "docenteId": 2,
  "tema": "Validación de la propuesta de valor",
  "fecha": "2026-12-10",
  "horaInicio": "09:00",
  "horaFin": "10:00",
  "modalidadId": 2,
  "lugarEnlace": "https://meet.example.com/asesoria"
}
```

`docenteId`, `tema`, `fecha`, `horaInicio` y `horaFin` son obligatorios para una `Cita`
(`400 VALIDATION_ERROR` con el campo que falte); `modalidadId` y `lugarEnlace` son
opcionales. Enviar campos de programación en otro tipo de solicitud → `400`.

`200` con la solicitud en `Aprobada`, `fechaResolucion` y `resueltoPor`.

| Tipo | Efecto |
|---|---|
| `Desbloqueo` | `Limitado`/`Inactivo` → `Activo` (si ya estaba `Activo`, solo se resuelve) |
| `Paralelo` | `es_paralelo = TRUE` en el emprendimiento, recalculando `paralelos_maximos` |
| `Cita` | Crea la asesoría en `Programada` con el docente y el bloque elegidos; el docente la confirma después con `accept` |

La asesoría de una `Cita` se crea con las mismas reglas que `POST /api/advice`: docente
vigente y `Activo` (`422 MENTOR_NOT_ACTIVE`), modalidad existente y control de solapamiento
(`409 ADVICE_SCHEDULE_CONFLICT`). Una segunda aprobación responde
`422 REQUEST_ALREADY_RESOLVED`. Si la cuenta o el emprendimiento ya no existen: `422
REQUEST_TARGET_MISSING`. Audita `Solicitud aprobada` con el efecto aplicado (incluida la
asesoría creada) y notifica al solicitante.

### `PUT /api/requests/:id/reject`

```json
{ "motivo": "La cuenta no cumple los requisitos de activación" }
```

`motivo` obligatorio. `200` con `estado: "Rechazada"`, `motivoRechazo`, `fechaResolucion` y
`resueltoPor`. No cambia el estado de la cuenta ni del emprendimiento; audita
`Solicitud rechazada` y notifica al solicitante con el motivo.

## Tareas

Módulo de trabajo: sesión **y** cuenta `Activo`. El administrador y el docente con
asignación activa crean, editan, califican, devuelven y dan de baja; el estudiante lee
las suyas y las entrega. El alcance se resuelve en el servicio: fuera de alcance `404`.

| Ruta | Roles | Notas |
|---|---|---|
| `GET /api/task` | Admin, Docente, Estudiante | Admin todas; docente las de sus emprendimientos asignados; estudiante las suyas |
| `GET /api/task/my-task` | Estudiante | Atajo de las tareas propias; un docente o admin recibe `403` |
| `GET /api/task/entrepreneurship/:id` | Admin, Docente, Estudiante | Exige ver el expediente; si no, `404` |
| `GET /api/task/advance/entrepreneurship/:id` | Admin, Docente, Estudiante | Avance total y por fase (FR-022) |
| `GET /api/task/:id` | Admin, Docente, Estudiante | Fuera de alcance: `404` |
| `POST /api/task` | Admin, Docente | El destinatario es el propietario del emprendimiento |
| `PUT /api/task/:id` | Admin, Docente | Edita la tarea y admite `estado: 'En curso'` desde `Pendiente` |
| `PUT /api/task/:id/complete` | Estudiante destinatario, Admin | Entrega: exige ≥1 evidencia (BR-007) |
| `PUT /api/task/:id/grade` | Admin, Docente | Califica 0–100 desde `En revisión` |
| `PUT /api/task/:id/return` | Admin, Docente | Devuelve con motivo obligatorio (R19b) |
| `DELETE /api/task/:id` | Admin, Docente | Baja lógica + borrado físico de sus evidencias (BR-006) |

Forma de una tarea:

```json
{
  "id": 3,
  "titulo": "Subir evidencia fotográfica",
  "descripcion": "Adjunta las fotos del punto de venta.",
  "fechaLimite": "2026-12-31",
  "prioridad": "Alta",
  "puntos": 100,
  "estado": "Pendiente",
  "vencida": false,
  "puntajeObtenido": null,
  "retroalimentacion": null,
  "estadoRevision": "Pendiente",
  "evidenciaRequerida": true,
  "motivoDevolucion": null,
  "observacionesDevolucion": null,
  "evidencias": 0,
  "fechaEnvio": null,
  "emprendimiento": { "id": 1, "codigo": "EMP-001", "nombre": "Sabor y Sabe" },
  "estudiante": {
    "id": 4,
    "nombres": "Estudiante",
    "apellidos": "Demo Uno",
    "correoInstitucional": "estudiante.demo1@uniminuto.edu.co"
  },
  "creador": { "id": 2, "nombres": "Carlos", "apellidos": "Mendoza" },
  "fase": { "id": 1, "nombre": "FASE 1 Ideación y priorización de ideas" }
}
```

### Ciclo de vida

```
Pendiente ──PUT estado=En curso──► En curso ──complete (≥1 evidencia)──► En revisión
     └──────────────────────────────complete──────────────────────────────┘
En revisión ──grade──► Completada        En revisión ──return + motivo──► Devuelta
Devuelta ──complete (nueva entrega)──► En revisión
```

- `Vencida` **no se almacena**: se deriva de `fechaLimite < hoy` mientras la tarea siga
  `Pendiente` o `En curso`, en cada lectura y en el filtro `estado=Vencida`. Una tarea
  vencida todavía se puede entregar.
- `evidenciaRequerida` es siempre `true` (BR-007, §20.5 #13) y no se acepta del cliente.
- `fechaEnvio` se deriva de la evidencia vigente más reciente: el diagrama no tiene una
  columna de fecha de entrega (P-24).
- El avance del emprendimiento se recalcula en la misma transacción al calificar, al dar
  de baja y al crear una tarea: `ROUND(100 × Completada / total)`, 0 sin tareas (R21).
- Cada transición escribe su acción de auditoría y avisa al estudiante o a los docentes
  con asignación activa.

### `GET /api/task`

| Parámetro | Tipo | Default | Notas |
|---|---|---|---|
| `page` | entero ≥ 1 | 1 | |
| `pageSize` | entero 1–100 | 25 | |
| `q` | texto ≤ 100 | — | Título o descripción (`ILIKE`) |
| `estado` | `Pendiente` · `En curso` · `En revisión` · `Completada` · `Vencida` · `Devuelta` | — | `Vencida` filtra por el estado derivado |
| `estadoRevision` | `Pendiente` · `En revisión` · `Calificada` · `Devuelta` | — | |
| `prioridad` | `Alta` · `Media` · `Baja` | — | |
| `emprendimientoId` | entero > 0 | — | |
| `estudianteId` | entero > 0 | — | |
| `fasePlanId` | entero > 0 | — | |
| `sort` | `limite` · `prioridad` · `estado` · `titulo` | `limite` | Lista blanca: otra columna da `400` |
| `order` | `asc` · `desc` | `asc` | |

`200`: `{ items, total, page, pageSize }`.

### `POST /api/task`

```json
{
  "titulo": "Subir evidencia fotográfica",
  "descripcion": "Adjunta las fotos del punto de venta.",
  "emprendimientoId": 1,
  "fasePlanId": 1,
  "fechaLimite": "2026-12-31",
  "prioridad": "Alta",
  "puntos": 100
}
```

- `emprendimientoId` debe existir y el actor debe ser su mentor activo o el administrador;
  si no, `404`.
- `fasePlanId` debe existir en `faseplan` (`400`).
- `estado`, `estadoRevision`, `puntajeObtenido`, `retroalimentacion`, `motivoDevolucion`,
  `observacionesDevolucion`, `evidenciaRequerida` y `usuariosId` no se aceptan (`400`).
- Nace `Pendiente`, `estadoRevision = 'Pendiente'`, `evidenciaRequerida = true`.

`201` con la tarea. Audita `Alta de tarea`, avisa al estudiante y recalcula el avance.

### `PUT /api/task/:id`

Admite `titulo`, `descripcion`, `fasePlanId`, `fechaLimite`, `prioridad`, `puntos` y
`estado: 'En curso'` (solo desde `Pendiente`, `422 INVALID_TASK_TRANSITION` en otro caso).
Una tarea `En revisión` o `Completada` no se edita (`422 TASK_NOT_EDITABLE`). Los campos
enviados como `null` limpian el valor. Audita `Edición de tarea`.

### `PUT /api/task/:id/complete`

Sin cuerpo. Solo el estudiante destinatario (o el administrador). Se permite desde
`Pendiente`, `En curso` y `Devuelta`; sin al menos una evidencia vigente responde `422
TASK_EVIDENCE_REQUIRED`. Deja `estado = 'En revisión'` y `estadoRevision = 'En revisión'`,
audita `Entrega de tarea` y avisa a los docentes asignados.

### `PUT /api/task/:id/grade`

```json
{ "puntajeObtenido": 85, "retroalimentacion": "Cumple con lo solicitado." }
```

Solo desde `En revisión`. Deja `Completada` / `Calificada`, guarda el puntaje y la
retroalimentación, audita `Calificación de tarea`, avisa al estudiante y recalcula el
avance. Calificar dos veces responde `422 INVALID_TASK_TRANSITION`.

### `PUT /api/task/:id/return`

```json
{ "motivo": "Archivos ilegibles", "observaciones": "La foto está borrosa." }
```

`motivo` es obligatorio y pertenece al vocabulario del prototipo (`Evidencia incompleta`,
`No cumple con lo solicitado`, `Archivos ilegibles`, `Entrega fuera de fecha`,
`Otro motivo`). Solo desde `En revisión`. Deja `Devuelta`, guarda motivo y observaciones,
audita `Devolución de tarea` y avisa al estudiante. La evidencia sigue adjunta para que
pueda corregir y volver a entregar.

### `DELETE /api/task/:id`

`200` con `{ "success": true, "message": "Tarea dada de baja." }`. La fila conserva
`fechaEliminacion` y sus archivos se borran del disco después de confirmar la transacción
(BR-006). Recalcula el avance porque la tarea sale del denominador.

### `GET /api/task/advance/entrepreneurship/:id`

```json
{
  "emprendimientoId": 1,
  "avance": 33,
  "total": 3,
  "completadas": 1,
  "fases": [
    { "faseId": 1, "fase": "FASE 1 …", "total": 1, "completadas": 0, "porcentaje": 0 },
    { "faseId": null, "fase": null, "total": 2, "completadas": 1, "porcentaje": 50 }
  ]
}
```

Las cuatro fases del catálogo aparecen siempre; las tareas sin fase se agrupan en una
fila con `faseId: null`.

## Seguimientos

Registros de avance y comentarios del docente (FR-022). Módulo de trabajo: sesión **y**
cuenta `Activo`. El estudiante solo lee; el docente asignado y el administrador escriben.

| Ruta | Roles | Notas |
|---|---|---|
| `GET /api/tracing/entrepreneurship/:id` | Admin, Docente, Estudiante | Exige ver el expediente; si no, `404` |
| `GET /api/tracing/:id` | Admin, Docente, Estudiante | Fuera de alcance: `404` |
| `POST /api/tracing` | Admin, Docente | El autor es siempre la sesión |
| `PUT /api/tracing/:id` | Autor, Admin | Un docente ajeno recibe `404` |
| `DELETE /api/tracing/:id` | Autor, Admin | Baja lógica + borrado físico de sus evidencias |

```json
{
  "id": 1,
  "descripcion": "Prototipo de empaque listo para 20 unidades.",
  "tipo": "Avance de fase",
  "puntaje": 80,
  "estadoRevision": "Pendiente",
  "fechaSeguimiento": "2026-03-10T17:00:00.000Z",
  "retroalimentacion": null,
  "evidencias": 0,
  "emprendimiento": { "id": 1, "codigo": "EMP-001", "nombre": "Sabor y Sabe" },
  "autor": { "id": 2, "nombres": "Carlos", "apellidos": "Mendoza" },
  "fase": { "id": 2, "nombre": "FASE 2 Estructuración y ejecución" }
}
```

### `POST /api/tracing`

```json
{
  "emprendimientoId": 1,
  "tipoSeguimiento": "Avance de fase",
  "descripcion": "Prototipo de empaque listo para 20 unidades.",
  "fasePlanId": 2,
  "puntaje": 80,
  "estadoRevision": "Pendiente",
  "fechaSeguimiento": "2026-03-10",
  "retroalimentacion": null
}
```

- Un `Avance de fase` exige `fasePlanId` (`400` con `fields.fasePlanId`); un `Comentario`
  no la lleva.
- `puntaje` es 0–100; `fechaSeguimiento` es una fecha `AAAA-MM-DD` y se guarda a mediodía
  de Bogotá para que no se muestre el día anterior.
- `usuariosId` no se acepta: el autor es la sesión.
- `201` con el seguimiento; audita `Alta de seguimiento` y avisa al estudiante.

### `PUT /api/tracing/:id`

Admite `descripcion`, `fasePlanId`, `puntaje`, `estadoRevision`, `fechaSeguimiento` y
`retroalimentacion`. `tipoSeguimiento` y `emprendimientoId` no se editan (`400`). Audita
`Edición de seguimiento`.

### `DELETE /api/tracing/:id`

`200` con `{ "success": true, "message": "Seguimiento dado de baja." }`. La fila conserva
`fechaEliminacion` y sus archivos se borran del disco (BR-006).

## Asesorías

Acompañamiento del docente al emprendimiento (FR-004, FR-015, BR-002). Módulo de trabajo:
sesión **y** cuenta `Activo`.

El estudiante **solicita** (bandeja de solicitudes) y **lee**; nunca crea, edita ni
confirma una sesión. La creación directa es del administrador o del docente asignado, y la
confirmación del docente asignado o del administrador.

| Ruta | Roles | Notas |
|---|---|---|
| `GET /api/advice` | Admin, Docente, Estudiante | Cada rol con su alcance |
| `GET /api/advice/:id` | Admin, Docente, Estudiante | Fuera de alcance: `404` |
| `POST /api/advice` | Admin, Docente | El docente solo para sí mismo y en sus emprendimientos asignados |
| `PUT /api/advice/:id` | Admin, Docente asignado | Contenido, horario y las transiciones del día |
| `POST /api/advice/:id/accept` | Admin, Docente asignado | `Por agendar`/`Programada` → `Confirmada` |
| `POST /api/advice/:id/repropose` | Admin, Docente asignado | Exige horario; deja `Programada` |
| `POST /api/advice/:id/reject` | Admin, Docente asignado | Motivo obligatorio; deja `Cancelada` |
| `DELETE /api/advice/:id` | Admin, Docente asignado | Baja lógica + evidencias (BR-006) |

Forma de una asesoría:

```json
{
  "id": 1,
  "codigo": "ASES-001",
  "tema": "Validación de la propuesta de valor",
  "estado": "Programada",
  "fecha": "2026-12-01",
  "horaInicio": "09:00",
  "horaFin": "10:00",
  "fechaAsesoria": "2026-12-01T14:00:00.000Z",
  "lugarEnlace": "https://meet.example.com/asesoria",
  "modalidad": { "id": 2, "nombre": "Virtual" },
  "emprendimiento": { "id": 1, "codigo": "EMP-001", "nombre": "Sabor y Sabe" },
  "estudiante": {
    "id": 4,
    "nombres": "Estudiante",
    "apellidos": "Demo Uno",
    "correoInstitucional": "estudiante.demo1@uniminuto.edu.co"
  },
  "docente": {
    "id": 2,
    "nombres": "Docente",
    "apellidos": "Demo Uno",
    "correoInstitucional": "docente.demo1@uniminuto.edu.co"
  },
  "evidencias": 0
}
```

`codigo` se deriva del id (`ASES-###`): el diagrama no tiene columna de código (P-28).
`fecha`/`horaInicio`/`horaFin` son el bloque de `fecha_y_horarios`; `fechaAsesoria` es ese
bloque en la zona `America/Bogota`. Sin horario, los cuatro son `null` y el estado es
`Por agendar`.

### `GET /api/advice`

| Parámetro | Tipo | Default | Notas |
|---|---|---|---|
| `page` | entero ≥ 1 | 1 | |
| `pageSize` | entero 1–100 | 25 | |
| `estado` | `Por agendar` · `Programada` · `Confirmada` · `En curso` · `Completada` · `Cancelada` | — | |
| `grupo` | `Agendada` | — | Etiqueta del prototipo: `Programada` + `Confirmada` + `En curso`; no se guarda |
| `docenteId` | entero | — | |
| `estudianteId` | entero | — | |
| `emprendimientoId` | entero | — | |
| `modalidadId` | entero | — | |
| `q` | texto ≤ 100 | — | Tema, emprendimiento, estudiante o docente |
| `desde` · `hasta` | `AAAA-MM-DD` | — | Sobre la fecha del bloque |
| `sort` | `fecha` · `estado` · `tema` · `emprendimiento` · `estudiante` · `docente` | `fecha` | |
| `order` | `asc` · `desc` | `desc` | |

`200` con `{ items, total, page, pageSize }`. El alcance es el de siempre: el administrador
ve todo, el docente solo las que tiene asignadas y el estudiante solo las suyas. Un filtro
por un `docenteId` ajeno no amplía el alcance.

### `POST /api/advice`

```json
{
  "emprendimientoId": 1,
  "docenteId": 2,
  "tema": "Revisión del modelo de negocio",
  "modalidadId": 2,
  "lugarEnlace": "https://meet.example.com/asesoria",
  "fecha": "2026-12-01",
  "horaInicio": "09:00",
  "horaFin": "10:00"
}
```

- `emprendimientoId` y `docenteId` son obligatorios; `tema` también. El horario es todo o
  nada (`400` si falta una de las tres partes o si `horaFin <= horaInicio`).
- Con horario nace `Programada`; sin horario, `Por agendar`.
- El administrador puede agendar cualquier emprendimiento. El docente solo uno con
  asignación activa y con él mismo como docente (`403` si intenta asignar a otro; `404` si
  el emprendimiento no es suyo).
- `docenteId` debe ser un docente vigente con rol Docente (`400`) y cuenta `Activo`
  (`422 MENTOR_NOT_ACTIVE`). `modalidadId` debe existir (`400`).
- Si el docente ya tiene una asesoría que se solapa ese día → `409
  ADVICE_SCHEDULE_CONFLICT` (T35).

`201` con la asesoría. Audita `Alta de asesoría` y avisa al estudiante y al docente.

### `PUT /api/advice/:id`

Edita `tema`, `lugarEnlace`, `modalidadId`, el bloque de horario y `estado`. `docenteId`
solo lo cambia el administrador (`403 FIELD_NOT_ALLOWED` para el docente). El horario se
envía completo o no se envía; si la asesoría estaba `Por agendar` y llega un bloque, pasa a
`Programada`. `estado` solo acepta `En curso` (desde `Confirmada`) y `Completada` (desde
`En curso`); cualquier otra transición → `422 INVALID_ADVICE_TRANSITION`. Una asesoría
`Completada` o `Cancelada` ya no se edita (`422 ADVICE_NOT_EDITABLE`), y una `En curso` no
cambia de horario. Audita `Edición de asesoría`.

### `POST /api/advice/:id/accept`

Cuerpo opcional con el bloque (`fecha`, `horaInicio`, `horaFin`). Confirma una asesoría
`Por agendar` o `Programada`; sin bloque en el cuerpo ni en la fila → `422
ADVICE_NOT_SCHEDULED`. Vuelve a comprobar el solapamiento (`409`). Audita `Confirmación de
asesoría` y avisa al estudiante.

### `POST /api/advice/:id/repropose`

```json
{ "fecha": "2026-12-04", "horaInicio": "14:00", "horaFin": "15:00" }
```

Exige el bloque completo y deja la asesoría en `Programada` desde `Por agendar`,
`Programada` o `Confirmada`. Comprueba el solapamiento (`409`). Audita `Reprogramación de
asesoría` y avisa al estudiante.

### `POST /api/advice/:id/reject`

```json
{ "motivo": "El docente no tiene disponibilidad" }
```

`motivo` obligatorio. Deja `Cancelada` desde `Por agendar`, `Programada` o `Confirmada`; una
sesión `En curso`, `Completada` o ya `Cancelada` responde `422 INVALID_ADVICE_TRANSITION`.
El diagrama no tiene columna de motivo (P-29): se guarda en la auditoría
(`Cancelación de asesoría`) y se envía en el aviso al estudiante.

### `DELETE /api/advice/:id`

`200` con `{ "success": true, "message": "Asesoría dada de baja." }`. Marca
`fechaEliminacion`, da de baja lógica sus evidencias y borra los archivos del disco después
del commit (BR-006). La fila se conserva para el histórico. Audita `Baja lógica de
asesoría` y avisa al estudiante.

### Ciclo de vida

```
Por agendar ──(accept + horario)──► Confirmada ──(PUT estado)──► En curso ──► Completada
     │                                  │
     ├──(repropose)──► Programada ──────┘
     └──(reject)──────────────────────────────────────────────► Cancelada
```

`Completada` y `Cancelada` son finales. El paso a `En curso` es manual: ninguna regla pide
que el reloj cambie el estado, y no existe un estado «No asistió» (P-34).

## Adjuntos

Evidencias de una tarea, un seguimiento o una asesoría (FR-008, BR-006, BR-007). Módulo de
trabajo: sesión **y** cuenta `Activo` (una cuenta `Limitado` o `Inactivo` recibe
`403 ACCOUNT_NOT_ACTIVE`). La única excepción es la **descarga del archivo del acta**, que
se rige por la regla del acta y está disponible para una cuenta `Limitado` (AQ-07
opción A).

| Ruta | Roles | Notas |
|---|---|---|
| `POST /api/attachments/:entity/:id` | Admin, Docente, Estudiante | `entity`: `task`, `tracing` o `advice`; `multipart/form-data`, campo `file` |
| `GET /api/attachments/:id` | Admin, Docente, Estudiante | Descarga con el alcance del padre; el archivo del acta no exige `Activo` |
| `DELETE /api/attachments/:id` | Admin, autor de la evidencia | Baja lógica + borrado físico del archivo |

### `POST /api/attachments/:entity/:id`

- `entity` admite `task`, `tracing` y `advice`; cualquier otro valor —incluido `acta`,
  que solo se lee— responde `400`.
- **Autorización de escritura**: en una tarea, el estudiante destinatario o el
  administrador (el docente califica, no sube evidencia); en un seguimiento, su autor o el
  administrador; en una asesoría, el estudiante dueño, el docente asignado o el
  administrador. Fuera de alcance: `404`; rol sin permiso: `403`.
- Una tarea `En revisión` o `Completada` tiene la evidencia congelada
  (`422 TASK_EVIDENCE_LOCKED`); el administrador puede retirarla.
- Una asesoría `Completada` o `Cancelada` también la tiene congelada
  (`422 ADVICE_EVIDENCE_LOCKED`); el administrador puede retirarla. El límite de archivos
  se cuenta por entidad (`upload_max_files_per_entity`), igual que en tareas y
  seguimientos.
- El MIME se decide por **el contenido** (firma), no por la extensión ni por la cabecera
  declarada; solo JPG/JPEG, PNG y PDF (`400` en otro caso). El nombre en disco es aleatorio
  (`<uuid>.<ext>`) y el original se guarda como metadato. Un nombre con separadores, `..`
  o caracteres de control se rechaza (`400`).
- El archivo se escribe en un `*.part` y se renombra al terminar; ningún `.part` se sirve.
- Tamaño máximo por archivo: `upload_max_mb` (500 por defecto) → `413
  PAYLOAD_TOO_LARGE`. Archivos por entidad: `upload_max_files_per_entity` (5) → `422
  ATTACHMENT_LIMIT_REACHED`. Ambos se leen de `configuracion_programa`.

`201`:

```json
{
  "id": 7,
  "nombreArchivo": "punto-de-venta.jpg",
  "tamanoBytes": 2048,
  "tipoMime": "image/jpeg",
  "fechaSubida": "2026-10-25T18:00:00.000Z",
  "subidoPor": { "id": 4, "nombres": "Estudiante", "apellidos": "Demo Uno" },
  "entidad": "task",
  "entidadId": 3
}
```

Audita `Carga de evidencia`.

### `GET /api/attachments/:id`

Transmite el archivo con `Content-Type` verificado, `Content-Length`,
`Content-Disposition: attachment` (nombre ASCII de respaldo + `filename*=UTF-8''…`),
`Cache-Control: private, no-store` y `X-Content-Type-Options: nosniff`. Si la fila existe
pero el archivo ya no está en el disco: `404 ATTACHMENT_FILE_MISSING`.

La respuesta también cubre el **archivo del acta** (`entidad: "acta"`): lo leen el
administrador y el estudiante dueño; el docente recibe `404`. En ese caso `entidadId` es
el `id` del acta, no el de una tarea o asesoría.

### `DELETE /api/attachments/:id`

`200` con `{ "success": true, "message": "Evidencia eliminada." }`. La fila queda con
`fechaEliminacion`, el pivote se elimina y el archivo se borra del disco (BR-006). Un
archivo ya ausente no impide la baja: el efecto es idempotente. Audita `Baja lógica de
evidencia`. El archivo del acta no se borra por esta ruta: responde `403
ROLE_NOT_ALLOWED` y se reemplaza subiendo una nueva versión en `POST /api/acta`.

## Notificaciones

Bandeja personal y canal en tiempo real (FR-019, T21). **Ninguna** ruta exige cuenta
`Activo`: AQ-07 opción A deja las notificaciones disponibles también para una cuenta
`Limitado`, que es justo la que necesita enterarse de que su desbloqueo fue resuelto.

| Ruta | Roles | Notas |
|---|---|---|
| `GET /api/notifications` | Admin, Docente, Estudiante | Bandeja propia, paginada |
| `PUT /api/notifications/:id/read` | Admin, Docente, Estudiante | Idempotente; la ajena responde `404` |
| `PUT /api/notifications/read-all` | Admin, Docente, Estudiante | Marca todas las propias |
| `GET /api/notifications/stream` | Admin, Docente, Estudiante | SSE (`text/event-stream`) |

Forma de una notificación:

```json
{
  "id": 12,
  "tipo": "Asesoría",
  "mensaje": "Tu asesoría «Revisión del modelo de negocio» fue confirmada.",
  "url": "/estudiante/asesorias",
  "tipoObjeto": "asesoria",
  "objetoId": 3,
  "leida": false,
  "fecha": "2026-10-25T18:00:00.000Z"
}
```

`tipo` es uno de `Tarea`, `Asesoría`, `Seguimiento`, `Solicitud`, `Diagnóstico`, `Evento`
o `Sistema` (P-5). `url`, `tipoObjeto` y `objetoId` son opcionales y pueden ser `null`: son
la pista de navegación de la SPA, no una regla de negocio.

### `GET /api/notifications`

| Parámetro | Tipo | Default | Notas |
|---|---|---|---|
| `page` | entero ≥ 1 | 1 | |
| `pageSize` | entero 1–100 | 25 | |
| `leida` | `true` · `false` | — | Filtra por estado de lectura |
| `tipo` | los 7 valores de `tipo` | — | |

`200` con `{ items, total, page, pageSize, sinLeer }`. El orden es siempre el más reciente
primero (`fecha DESC, id DESC`); no se expone un `ORDER BY` arbitrario (`.strict()` → `400`
si llega `orderBy`).

`sinLeer` es el total de no leídas del usuario **con el filtro de `tipo` aplicado, pero sin
el de `leida`**. Así, al pedir «no leídas» el contador sigue diciendo cuántas hay en total
para ese tipo, y al pedir «leídas» no se vuelve cero.

### `PUT /api/notifications/:id/read`

`200` con la notificación y el `sinLeer` actualizado. Es idempotente: repetir la llamada
devuelve la misma fila y el mismo contador. Una notificación de otro usuario responde
`404 NOT_FOUND` (el `WHERE` incluye al propietario, así que el id ajeno no se revela). La
lectura no se audita.

### `PUT /api/notifications/read-all`

`200` con `{ "actualizadas": 3, "sinLeer": 0 }`. `actualizadas` cuenta solo las que estaban
sin leer; repetir la llamada devuelve `0`.

### `GET /api/notifications/stream`

Canal SSE con `Content-Type: text/event-stream`, `Cache-Control: no-cache, no-transform`,
`Connection: keep-alive` y `X-Accel-Buffering: no`. La respuesta queda abierta hasta que el
cliente cierra; no hay cuerpo JSON.

| Evento | `data` | Cuándo |
|---|---|---|
| `ready` | `{ "unreadCount": 3 }` | Al abrir el flujo |
| `notification` | `{ "notificationId": 12, "tipo": "Asesoría", "unreadCount": 4 }` | Al publicarse un aviso para ese usuario |

- El evento **no** lleva el mensaje, la `url` ni el objeto: solo el id, el tipo y el
  contador. El cliente invalida su bandeja y pide el texto por la API normal.
- Los latidos son comentarios SSE (`: keep-alive`) cada **25 s**; mantienen viva la conexión
  a través de Caddy y permiten descartar clientes muertos sin enviar datos de negocio.
- Cada usuario tiene su propio conjunto de conexiones: un aviso de A nunca se escribe en la
  conexión de B (T21).
- La publicación ocurre **después del commit** de la transacción que crea el aviso, así que
  el cliente nunca recibe un id que todavía no puede leer.
- El canal es en memoria y de **una sola instancia** (P-32). Con varias réplicas haría falta
  un bus compartido (Redis, PostgreSQL `LISTEN/NOTIFY`).

### Preferencias de aviso

`notify()` respeta tres claves de `configuracion_programa`: `notif_tareas`,
`notif_asesorias` y `notif_seguimiento`. Si una vale `false`, no se escribe la fila ni se
publica el evento para ese tipo; los demás tipos no tienen interruptor. Las claves son
globales del programa, no por usuario (P-31).

## Diagnóstico

Caracterización del emprendimiento (FR-002, T25). Es un **módulo de trabajo**: exige
sesión y cuenta `Activo` (`403 ACCOUNT_NOT_ACTIVE`). El estudiante diligencia el suyo; el
administrador y el docente con asignación activa lo leen. Un id fuera de alcance responde
`404`.

| Ruta | Roles | Notas |
|---|---|---|
| `GET /api/diagnosis/form` | Admin, Docente, Estudiante | Banco de preguntas activo |
| `GET /api/diagnosis` | Admin, Docente, Estudiante | Bandeja con el alcance del expediente |
| `GET /api/diagnosis/me` | Estudiante | Diagnóstico de su emprendimiento |
| `POST /api/diagnosis/me` | Estudiante | Guarda borrador o envía |
| `GET /api/diagnosis/:id` | Admin, Docente, Estudiante | Detalle con respuestas |
| `GET /api/diagnosis/:id/report` | Admin, Docente, Estudiante | Informe JSON |
| `GET /api/characterization/me` | Estudiante | Secciones y avance de respuestas |

`GET /api/diagnosis/me` y `GET /api/characterization/me` aceptan `emprendimientoId` para
elegir entre emprendimientos paralelos; sin él se usa el más reciente. Un estudiante sin
emprendimiento vigente recibe `422 ENTREPRENEURSHIP_REQUIRED`; si todavía no guardó nada,
`404 NOT_FOUND`.

### `GET /api/diagnosis/form`

`200` con `{ total, secciones, preguntas }`. Las 22 preguntas activas se agrupan en cinco
secciones (Perfil, Problema, Propuesta de valor, Mercado y Capacidad operativa); cada
pregunta trae `id`, `seccion`, `orden`, `enunciado`, `tipo` y `opciones` (vacío en texto).

### `POST /api/diagnosis/me`

```json
{
  "emprendimientoId": 1,
  "respuestas": [
    { "preguntaId": 1, "valor": "Sabor y Sabe" },
    { "preguntaId": 2, "valor": "Pequeño" }
  ],
  "enviar": false
}
```

- `enviar: false` (o ausente) guarda el borrador: se puede enviar solo una parte y volver
  después. El borrador **reutiliza** el mismo diagnóstico (`En progreso`); no crea filas
  nuevas.
- `enviar: true` exige las 22 preguntas activas. Si falta alguna: `422
  DIAGNOSIS_INCOMPLETE` con el campo `respuestas`. Al enviar, las respuestas quedan
  bloqueadas (`Enviado`); un nuevo guardado responde `422 DIAGNOSIS_ALREADY_SUBMITTED`.
- Una pregunta inexistente o inactiva y un valor fuera de las opciones de una selección
  única responden `400 VALIDATION_ERROR` con el índice exacto (`respuestas.0.preguntaId`).
- `puntajeTotal`, `estado` y `urlInforme` no se aceptan: `.strict()` → `400`.

Forma del diagnóstico:

```json
{
  "id": 1,
  "estado": "En progreso",
  "fechaDiagnostico": "2026-10-25T18:00:00.000Z",
  "puntajeTotal": null,
  "urlInforme": null,
  "emprendimiento": { "id": 1, "codigo": "EMP-001", "nombre": "Sabor y Sabe" },
  "estudiante": { "id": 4, "nombres": "Estudiante", "apellidos": "Demo Uno", "correoInstitucional": "…" },
  "respuestas": [{ "id": 1, "seccion": 1, "orden": 1, "enunciado": "…", "tipo": "Texto", "opciones": [], "valor": "…" }],
  "totalPreguntas": 22,
  "respondidas": 2,
  "puntuacion": {
    "disponible": false,
    "motivo": "RUBRIC_NOT_CONFIGURED",
    "mensaje": "La rúbrica del diagnóstico no está aprobada (AQ-09): se guardan las respuestas, pero no se produce puntaje."
  }
}
```

**Sin rúbrica no hay puntaje.** `rubrica_diagnostico_aprobada` está en `false` y el
repositorio no tiene dimensiones, pesos ni fórmula aprobados (AQ-09). Por eso
`puntajeTotal` es `null`, no se escriben filas de `valoracion` ni de `caracterizacion`, y
la API declara `RUBRIC_NOT_CONFIGURED` en cada lectura. No se inventa un cálculo (P-35).

### `GET /api/diagnosis`

| Parámetro | Tipo | Default | Notas |
|---|---|---|---|
| `page` | entero ≥ 1 | 1 | |
| `pageSize` | entero 1–100 | 25 | |
| `q` | texto ≤ 100 | — | Emprendimiento, estudiante o correo |
| `estado` | `En progreso` · `Enviado` · `Revisado` | — | |
| `emprendimientoId` | entero | — | |
| `estudianteId` | entero | — | No amplía el alcance |
| `sort` | `fecha` · `estado` · `emprendimiento` · `estudiante` | `fecha` | Lista blanca |
| `order` | `asc` · `desc` | `desc` | |

`200` con `{ items, total, page, pageSize }`. El alcance es el del expediente: el
administrador ve todo, el docente solo los emprendimientos con asignación activa y el
estudiante solo los suyos.

### `GET /api/diagnosis/:id/report`

`200` con `{ diagnostico, informe }`. Mientras no haya rúbrica, el informe declara el
hueco y deja las cinco secciones sin puntaje:

```json
{
  "informe": {
    "disponible": false,
    "motivo": "RUBRIC_NOT_CONFIGURED",
    "mensaje": "…",
    "urlInforme": null,
    "generadoEn": "2026-10-25T18:00:00.000Z",
    "secciones": [
      { "numero": 1, "titulo": "Perfil del emprendimiento", "puntaje": null,
        "resultado": null, "fortalezas": null, "oportunidades": null }
    ],
    "valoracion": []
  }
}
```

El PDF no se genera todavía: `urlInforme` queda en `null` (P-3) y el informe se sirve como
JSON para que la SPA pueda mostrarlo.

### `GET /api/characterization/me`

`200` con `{ diagnosticoId, estado, emprendimiento, respondidas, totalPreguntas,
puntuacion, secciones, valoracion }`. Cada sección trae `respondidas`, `total` y los
campos de puntaje en `null`; `valoracion` es `[]`. Es la vista de avance del cuestionario,
no un resultado puntuado.

## Actas

Acta de compromiso y confidencialidad (FR-003, BR-001, BR-009, T26). El estudiante
descarga la plantilla, la firma y la sube; el administrador la revisa. **Ninguna ruta
exige cuenta `Activo`**: AQ-07 opción A deja el acta disponible también para una cuenta
`Limitado`.

| Ruta | Roles | Notas |
|---|---|---|
| `GET /api/acta/template` | Admin, Estudiante | Plantilla para firmar |
| `GET /api/acta` | Admin, Estudiante | Bandeja o actas propias |
| `POST /api/acta` | Estudiante | `multipart/form-data`, campo `file` |
| `GET /api/acta/:id` | Admin, Estudiante | El docente recibe `403` |
| `PUT /api/acta/:id/review` | Admin | Aprobar o rechazar con motivo |

Forma del acta:

```json
{
  "id": 3,
  "estado": "En revisión",
  "observaciones": null,
  "fechaCarga": "2026-10-25T18:00:00.000Z",
  "fechaRevision": null,
  "emprendimiento": { "id": 1, "codigo": "EMP-001", "nombre": "Sabor y Sabe" },
  "estudiante": { "id": 4, "nombres": "Estudiante", "apellidos": "Demo Uno", "correoInstitucional": "…" },
  "revisor": null,
  "adjunto": {
    "id": 8,
    "nombreArchivo": "acta-firmada.pdf",
    "tamanoBytes": 512,
    "tipoMime": "application/pdf",
    "fechaSubida": "2026-10-25T18:00:00.000Z"
  }
}
```

### `GET /api/acta/template`

La plantilla legal del acta **no está en el repositorio** (AQ-12 no la aporta). Servir un
documento inventado sería peor que declarar el hueco, así que responde `404
ACTA_TEMPLATE_NOT_CONFIGURED`. Mientras tanto el estudiante puede subir la que reciba por
otro canal (P-36).

### `POST /api/acta`

`multipart/form-data` con un único archivo en el campo `file` (PDF, JPEG o PNG, MIME
verificado por contenido). Cada carga crea una **versión** del acta en `En revisión`:

- Si la última versión está `En revisión`: `409 ACTA_ALREADY_PENDING`.
- Si está `Aprobada`: `409 ACTA_ALREADY_APPROVED`.
- Si está `Rechazada`: se permite subir una nueva versión.
- Sin emprendimiento vigente: `422 ENTREPRENEURSHIP_REQUIRED`.

El archivo se guarda en `adjuntos` y se enlaza con `actas.adjuntos_id_adjunto`; la carga se
audita como `Carga de acta` y avisa a los administradores.

### `PUT /api/acta/:id/review`

```json
{ "estado": "Rechazada", "observaciones": "La firma no coincide con el documento." }
```

- Solo se revisa un acta `En revisión`; cualquier otro estado responde `422
  ACTA_NOT_REVIEWABLE`.
- `Rechazada` exige `observaciones` (BR-009): sin motivo, `400 VALIDATION_ERROR`.
- Se guardan el revisor y `fechaRevision`; se audita como `Revisión de acta` y se avisa al
  estudiante con el motivo.
- BR-001: una asignación docente exige al menos un acta `Aprobada`; la aprobación es la que
  habilita el mentor.

### Archivo del acta

`GET /api/attachments/:id` transmite el archivo cuando `entidad` es `acta`. Lo leen el
administrador y el estudiante dueño —incluida una cuenta `Limitado`, porque esta ruta no
exige `Activo`—; el docente recibe `404`. **No hay borrado independiente**:
`DELETE /api/attachments/:id` responde `403 ROLE_NOT_ALLOWED` porque el archivo se
reemplaza subiendo una nueva versión desde `POST /api/acta`.

### Listado

`GET /api/acta` acepta `page`, `pageSize` (25), `q`, `estado`, `emprendimientoId`,
`estudianteId`, `sort` (`fecha` · `estado` · `estudiante` · `emprendimiento`) y `order`
(`desc` por defecto). El administrador ve todas; el estudiante, solo las suyas.

## Eventos

Eventos institucionales y recomendaciones (FR-021, T27). El administrador es el
organizador: crea, edita, publica y da de baja. El docente recomienda eventos **solo** a
los emprendimientos que tiene asignados. El estudiante ve los publicados y se inscribe.

| Ruta | Roles | Notas |
|---|---|---|
| `GET /api/event` | Admin, Docente, Estudiante | Listado con alcance |
| `GET /api/event/:id` | Admin, Docente, Estudiante | Borrador oculto para no admin |
| `POST /api/event` | Admin | Alta |
| `PUT /api/event/:id` | Admin | Edición parcial |
| `DELETE /api/event/:id` | Admin | Baja lógica |
| `POST /api/event/:id/register` | Estudiante | Inscripción |
| `DELETE /api/event/:id/register` | Estudiante | Cancelación |
| `GET /api/event/:id/recommendations` | Admin, Docente, Estudiante | Recomendaciones visibles |
| `POST /api/event/:id/recommendations` | Docente | Recomendar a un emprendimiento asignado |

Forma del evento:

```json
{
  "id": 1,
  "nombreEvento": "Startup Minuto de Dios",
  "descripcion": "Jornada de presentación de emprendimientos.",
  "dirigidoA": "Todos los estudiantes",
  "capacidadMaxima": 40,
  "cupo": 40,
  "estado": "Publicado",
  "requiereRegistro": true,
  "lugar": "Auditorio principal",
  "enlace": null,
  "tipoEvento": { "id": 1, "nombre": "Startup" },
  "modalidad": { "id": 1, "nombre": "Presencial" },
  "fecha": "2026-11-05",
  "horaInicio": "09:00",
  "horaFin": "11:00",
  "organizador": { "id": 1, "nombres": "Coordinación", "apellidos": "SGEMD" },
  "inscritos": 0,
  "inscrito": false
}
```

### `GET /api/event`

| Parámetro | Tipo | Default | Notas |
|---|---|---|---|
| `page` | entero ≥ 1 | 1 | |
| `pageSize` | entero 1–100 | 25 | |
| `q` | texto ≤ 100 | — | Nombre, descripción, lugar o dirigido a |
| `estado` | los 4 valores de `EVENTO_ESTADOS` | — | |
| `tipoEventoId` | entero | — | |
| `modalidadId` | entero | — | |
| `desde` / `hasta` | `AAAA-MM-DD` | — | Sobre la fecha del bloque |
| `sort` | `fecha` · `nombre` · `estado` · `cupo` | `fecha` | Lista blanca |
| `order` | `asc` · `desc` | `asc` | |

`200` con `{ items, total, page, pageSize }`. El administrador ve todos los eventos,
publicados o no; el docente y el estudiante **solo** los `Publicado`. Un borrador responde
`404` a quien no es administrador, también por id.

### `POST /api/event`

```json
{
  "nombreEvento": "Taller de costos",
  "descripcion": "…",
  "dirigidoA": "Todos los estudiantes",
  "capacidadMaxima": 30,
  "estado": "Publicado",
  "requiereRegistro": true,
  "lugar": "Aula 204",
  "enlace": null,
  "tipoEventoId": 2,
  "modalidadId": 1,
  "fecha": "2026-12-15",
  "horaInicio": "10:00",
  "horaFin": "12:00"
}
```

- `estado` solo admite `Pendiente` (borrador) y `Publicado`; `Aprobado` y `Rechazado`
  quedan reservados (P-37). El valor por defecto es `Pendiente`.
- El horario es todo o nada: si llega una de las tres partes, faltan las otras → `400`. La
  hora de fin debe ser posterior a la de inicio.
- `capacidadMaxima` es opcional. Sin ella, `cupo` es `null` y no hay tope. Con ella, `cupo`
  nace igual a la capacidad.
- `tipoEventoId` y `modalidadId` se validan contra el catálogo (`400` si no existen).
- Se audita como `Alta de evento`.

### `PUT /api/event/:id`

Edición parcial de los mismos campos. `estado` sigue limitado a `Pendiente`/`Publicado`.
Si se cambia `capacidadMaxima`, `cupo` se recalcula como `capacidad - inscritos`; una
capacidad menor que las inscripciones actuales responde `422
EVENT_CAPACITY_BELOW_REGISTRATIONS`. Un `PUT` sin campos responde `400`. Se audita como
`Edición de evento`.

### `DELETE /api/event/:id`

Baja lógica (`fecha_eliminacion`): el evento desaparece de las lecturas y conserva sus
inscripciones y recomendaciones para el histórico. `200` con `{ "success": true, "message":
"Evento dado de baja." }`. Se audita como `Baja lógica de evento`.

### `POST /api/event/:id/register` y `DELETE /api/event/:id/register`

Solo el estudiante se inscribe. El evento debe estar publicado y `requiereRegistro` debe
ser `true`; en caso contrario: `422 EVENT_REGISTRATION_NOT_REQUIRED`.

- `POST` descuenta un puesto de `cupo` y devuelve el evento con `inscrito: true`. Una
  segunda inscripción responde `409 EVENT_ALREADY_REGISTERED`; sin puestos, `422
  EVENT_FULL`. El descuento ocurre bajo `pg_advisory_xact_lock('evento:cupo:<id>')` para
  que dos estudiantes no tomen el mismo último puesto.
- `DELETE` libera el puesto y devuelve `{ eventoId, inscrito: false, cupo }`. Si no había
  inscripción: `404 EVENT_REGISTRATION_NOT_FOUND`.
- Se auditan como `Inscripción a evento` y `Cancelación de inscripción a evento`.

### Recomendaciones

`POST /api/event/:id/recommendations` es **solo del docente** y exige una asignación
activa al emprendimiento (`404` si no la tiene) y un evento publicado (`404` si es
borrador). El cuerpo es `{ emprendimientoId, estudianteId?, mensaje? }`; si llega
`estudianteId`, debe ser el propietario del emprendimiento (`400`). La recomendación nace
`Pendiente`, se audita como `Recomendación de evento` y avisa al estudiante con tipo
`Evento`.

`GET /api/event/:id/recommendations` devuelve `{ items, total, page, pageSize }` con
`pageSize` 25. El administrador ve todas; el docente, las suyas; el estudiante, las de su
emprendimiento. El estado de la recomendación no se mueve: no hay endpoint para aceptarla,
rechazarla ni marcar asistencia (P-40). Forma de una recomendación:

```json
{
  "id": 1,
  "mensaje": "Te servirá para el modelo de negocio.",
  "estado": "Pendiente",
  "fecha": "2026-10-25T18:00:00.000Z",
  "evento": { "id": 1, "nombreEvento": "Startup Minuto de Dios" },
  "emprendimiento": { "id": 1, "codigo": "EMP-001", "nombre": "Sabor y Sabe" },
  "estudiante": { "id": 4, "nombres": "Estudiante", "apellidos": "Demo Uno" },
  "docente": { "id": 2, "nombres": "Docente", "apellidos": "Demo Uno" }
}
```

## Límites de peticiones

Los umbrales no están fijados por los requisitos (P-12); son valores iniciales
por IP, ajustables en `src/modules/auth/routes.ts`.

| Endpoint | Ventana | Máximo | Clave |
|---|---|---|---|
| `register` | 1 h | 10 | IP |
| `login` | 1 min | 10 | IP + correo |
| `verify` | 1 min | 15 | IP |
| `resend-code` | 1 h | 10 | IP |
| `forgot-password` | 1 h | 10 | IP |
| `reset-password` | 1 h | 10 | IP |

Al agotarse: `429 RATE_LIMITED` con `Retry-After` en segundos.
