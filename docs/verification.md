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
- **Commit:** _pendiente de commitear al cerrar la entrada_

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

### Sin verificar — **puerta no superada**

La puerta de la Etapa 1 exige `docker compose up` con `/api/health` en 200 **a través de Caddy**.
No se pudo ejecutar:

```
systemctl is-enabled docker → disabled
systemctl is-active docker  → inactive
docker compose             → plugin no instalado
usuario                    → no pertenece al grupo docker
```

- **Bloqueo:** entorno local. Se necesita `sudo systemctl enable --now docker`, el plugin
  `docker-compose` y agregar al usuario al grupo `docker` (o `sudo` para cada comando).
- **No se avanza a la Etapa 2** hasta verificar la puerta (master §16).
- **Tampoco verificado:** TLS interno de Caddy, límite de cuerpo real, entrega SSE y
  `pg_dump`/`rsync` dentro de la imagen del backend (dependen de Docker).

### Pendiente de decisión

- D15: hostname y certificado fuera de `localhost` (TI).
- D14: credenciales reales de Microsoft 365 / relay (TI).
- D22: disco separado para `backups/` y copia fuera del servidor (TI).
