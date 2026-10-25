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
- **Commit:** _pendiente de commitear al cerrar la entrada_

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
