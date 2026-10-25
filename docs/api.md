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
| 409 | `EMAIL_TAKEN` | Correo institucional ya registrado |
| 409 | `DOCUMENT_TAKEN` | Número de documento ya registrado |
| 409 | `ASSIGNMENT_ALREADY_ACTIVE` | El emprendimiento ya tiene una asignación `activa` (R11) |
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
| `PUT /api/requests/:id/approve` | Admin | Aplica el efecto de dominio una sola vez |
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
  (P-20).

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

Sin cuerpo. `200` con la solicitud en `Aprobada`, `fechaResolucion` y `resueltoPor`.

| Tipo | Efecto |
|---|---|
| `Desbloqueo` | `Limitado`/`Inactivo` → `Activo` (si ya estaba `Activo`, solo se resuelve) |
| `Paralelo` | `es_paralelo = TRUE` en el emprendimiento, recalculando `paralelos_maximos` |
| `Cita` | Ninguno todavía: la asesoría se crea en su módulo (P-19) |

Una segunda aprobación responde `422 REQUEST_ALREADY_RESOLVED`. Si la cuenta o el
emprendimiento ya no existen: `422 REQUEST_TARGET_MISSING`. Audita `Solicitud aprobada`
con el efecto aplicado y notifica al solicitante.

### `PUT /api/requests/:id/reject`

```json
{ "motivo": "La cuenta no cumple los requisitos de activación" }
```

`motivo` obligatorio. `200` con `estado: "Rechazada"`, `motivoRechazo`, `fechaResolucion` y
`resueltoPor`. No cambia el estado de la cuenta ni del emprendimiento; audita
`Solicitud rechazada` y notifica al solicitante con el motivo.

## Diagnóstico

### `GET /api/diagnosis/form`

Requiere sesión **y** cuenta `Activo`; una cuenta `Limitado` o `Inactivo` recibe
`403 ACCOUNT_NOT_ACTIVE`. Devuelve el banco de preguntas activo.

> Implementado en la Etapa 3 únicamente porque T03 exige un endpoint restringido
> real. El resto del módulo (envío, puntaje, informe) llega en la Etapa 9.

`200`:

```json
{
  "success": true,
  "data": {
    "total": 22,
    "preguntas": [
      {
        "id": 1,
        "seccion": 1,
        "orden": 1,
        "enunciado": "…",
        "tipo": "Texto",
        "opciones": []
      }
    ]
  }
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
