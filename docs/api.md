# API — SGEMD

Contrato de la API HTTP del MVP. Se amplía en cada etapa; las etapas 1–3 están
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
| 403 | `ORIGIN_NOT_ALLOWED` | Mutación con `Origin` ajeno o ausente |
| 404 | `NOT_FOUND` | Ruta inexistente |
| 409 | `EMAIL_TAKEN` | Correo institucional ya registrado |
| 409 | `DOCUMENT_TAKEN` | Número de documento ya registrado |
| 422 | `OTP_INVALID` | Código incorrecto, vencido, ya usado o inexistente |
| 429 | `OTP_COOLDOWN` | Reenvío antes del cooldown (60 s); incluye `Retry-After` |
| 429 | `OTP_ATTEMPTS_EXCEEDED` | Se agotaron los 5 intentos del código; incluye `Retry-After` |
| 429 | `RATE_LIMITED` | Se superó el límite de peticiones del endpoint; incluye `Retry-After` |
| 500 | `INTERNAL_ERROR` | Fallo no controlado (sin detalles internos) |
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

### `GET /api/users/me`

Requiere sesión. Devuelve el usuario de la fila actual, sin contraseña ni hash.
Es la única forma en que la SPA sabe quién es: no lee la cookie.

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
    "nivelAcademico": "Pregrado",
    "verificado": true,
    "estado": "Activo",
    "rol": { "id": 2, "nombre": "Estudiante" },
    "ultimaActividad": "2026-10-25T23:06:16.000Z"
  }
}
```

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
