# Cambios a Administrador — Refactor UX/UI del Rol Administrador (SGEMD)

> Documento de trabajo. Registra **todo** lo que se hizo sobre el Rol Administrador.
> Estado: **ejecutado**.
> Ámbito: `prototype/admin/**` (19 pantallas), `prototype/index.html` y las vistas
> autorizadas de `prototype/estudiante/` y `prototype/docente/`.
> Fuentes de verdad: `prototype/paginas_admin.py`, `prototype/lib_ui.py`,
> `prototype/paginas_docente.py`, `prototype/paginas_estudiante.py`.
> Regeneración: `python generar.py --rol admin` (desde `prototype/`).

---

## 1. Objetivo

Dejar el panel del administrador como un sistema coherente y navegable: datos
reales en tablas (no textos sueltos), filtros y búsquedas que funcionan, fichas
de detalle por registro, enlaces profundos por `hash`, pantallas de
Configuración y Solicitudes completas, y un flujo de asignación de docente
coherente con el resto del modulo.

---

## 2. Alcance

Las 19 pantallas de `prototype/admin/`:

| # | Archivo | Pantalla |
|---|---|---|
| 1 | `dashboard.html` | Inicio |
| 2 | `usuarios.html` | Gestión de perfiles |
| 3 | `solicitudes.html` | Solicitudes |
| 4 | `emprendimientos.html` | Emprendimientos |
| 5 | `emprendimiento-expediente.html` | Expediente del emprendimiento |
| 6 | `emprendimiento-plan.html` | Plan del emprendimiento |
| 7 | `seguimiento.html` | Seguimiento |
| 8 | `seguimiento-dashboard.html` | Tablero de seguimiento |
| 9 | `tareas.html` | Tareas |
| 10 | `asesorias.html` | Asesorías |
| 11 | `eventos.html` | Eventos |
| 12 | `evento-form.html` | Formulario de evento |
| 13 | `asignaciones.html` | Asignaciones |
| 14 | `diagnosticos.html` | Diagnósticos |
| 15 | `reportes.html` | Reportes |
| 16 | `perfil.html` | Perfil |
| 17 | `notificaciones.html` | Notificaciones |
| 18 | `respaldos.html` | Respaldos |
| 19 | `configuracion.html` | Configuración (**nueva**) |

---

## 3. Estrategia técnica

Todo se aplicó **en el generador**, no sobre el HTML. Editar los `.html`
generados a mano volvería a introducir la desincronización que el proyecto ya
arrastra; el generador es lo que garantiza que `python generar.py` reproduce
exactamente lo que se ve.

Piezas nuevas en `prototype/paginas_admin.py`:

1. **`_tabla_adm()`** — generador de tablas del admin. Una celda puede ser
   `("html", "valor")` cuando lleva markup (p. ej. un `<select>` de estado o un
   `badge`); el resto es texto plano. La tabla genera por sí sola zona
   filtrable (`data-tabla-zona="adm-<id>"`), buscador, filtros por columna,
   paginación, contador de resultados y estados vacíos.
2. **`_tabla_adm_ficha()`** — ficha de detalle en modal, alimentada por los
   `data-*` de la fila (un solo origen de verdad para tabla y ficha).
3. **`ADMIN_JS` / `ADMIN_CSS`** — bundle propio del rol, inyectado por
   `_inyectar()` **después** del bundle del kit, de modo que sus listeners
   `document` se ejecutan después de los de `lib_js` y pueden completar lo que
   el kit deja a medias (ver §5.2).
4. **Deep-links** — `#est-<id>`, `#emp-<código>`, `#doc-<código>`, `#sol-<id>` y
   `#asignar-docente` abren la ficha o el modal correspondiente.
5. **Estados con dato real** — estudiantes, docentes, emprendimientos,
   solicitudes, tareas, asesorías y eventos se modelan como tuplas en el
   generador y se pintan desde ahí; no quedan literales sueltos en el HTML.

Cambios en `prototype/lib_ui.py` (mínimos y solo de API):

- `campo()` **conserva el `name`** en los campos con `bloqueo` (antes se
  perdía); solo el admin usa `bloqueo` + `name`, así que los demás roles no
  cambian de bytes.
- `_item_nav()` acepta un `href` opcional y `_nav_html()` admite un cuarto
  elemento en los hijos de grupo: permite el ítem **Asignar docente** →
  `asignaciones.html#asignar-docente`.
- `NAV["administrador"]` suma ese ítem dentro del grupo *Gestión de perfiles*.

No se tocó `prototype/lib_css.py` ni `prototype/lib_js.py`.

---

## 4. Cambios por pantalla

**Inicio (`dashboard.html`)** — KPIs y series construidos con los datos reales
del modulo (12 emprendimientos, sedes 5/4/3, estados). El conmutador de gráfico
usa `btn-acento` + `aria-pressed` y alterna entre barras y anillo.

**Gestión de perfiles (`usuarios.html`)** — Dos tablas independientes
(estudiantes y docentes) con zona, buscador, filtros, paginación y ficha
propia por fila. El filtro de **Estado** lee el valor vivo del `<select>` de la
celda (no el texto), por eso el `select` se declara como `("html", valor)`.

**Solicitudes (`solicitudes.html`)** — Pestañas por estado (`data-panel`), tabla
por bandeja, ficha de detalle en modal y flujo **Aprobar** heredado del kit.

**Emprendimientos (`emprendimiento-expediente.html`, `emprendimiento-plan.html`)**
— Tablas y expediente con datos reales, ficha por emprendimiento y
deep-link `#emp-EMP-041`.

**Seguimiento (`seguimiento.html`, `seguimiento-dashboard.html`)** — Modal
**Registrar avance** con prefill real (emprendimiento, estudiante, etapa y
avance % de la fila). Requiere los dos arreglos de §5.1 y §5.2.

**Asignaciones (`asignaciones.html`)** — Tabla real de 5 undertakings con
filtros, estado y paginación; acción **Reasignar docente** (modal clonado de
una plantilla oculta) y deep-link `#asignar-docente`, que abre el primer
venture sin docente.

**Configuración (`configuracion.html`, nueva)** — 6 tarjetas de preferencias
(institución, notificaciones, roles, respaldo, etc.) con sus casillas de
verificación y avisos de estado.

**Tareas, Asesorías, Eventos, Diagnósticos, Reportes, Perfil, Notificaciones,
Respaldos** — Tablas y modales alimentados por los datos del generador, con
filtros y fichas coherentes con el resto del modulo.

---

## 5. Correcciones de bugs encontradas durante las pruebas

### 5.1 `lib_ui.campo()` perdía el `name` con `bloqueo`

`campo(..., name="x", bloqueo=...)` descartaba el `name`, así que el formulario
de avance no tenía campos nombrados. Corregido en `lib_ui.py`; solo afecta al
admin (único rol que combina `bloqueo` y `name`).

### 5.2 El kit clona los formularios con `innerHTML`

`plantillaModal()` del kit clona la plantilla con `innerHTML`, lo que **pierde**
el `option` seleccionado y los valores escritos a mano. Como el `ADMIN_JS` se
inyecta después del bundle del kit, su listener `document` (fase de burbujo,
registrado después) repone `emp`, `estu`, `etapa` y `avance` en el clon antes
de que se abra el modal. Verificado: el modal de **Registrar avance** muestra
*EcoPack / Lucía Fernández / FASE 3 - Validación / 84*.

### 5.3 Orden de las tuplas de estado

`_tabla_adm()` documentaba la tupla como `(estado, html)`, pero el código la
leía al revés: el filtro comparaba el `<select>` contra la etiqueta y no
filtraba. Corregido el contrato a `("html", "valor")` y actualizados los dos
puntos de uso (y el `coincide()` del `ADMIN_JS`).

### 5.4 Redacción

Tildes y mayúsculas en *Confirmar asignación*, *La confirmación actualizará…*,
*Aviso de emprendimiento en paralelo*, *Gestión de perfiles*, *decisión*,
*Código* y el aviso de la ficha de solicitud.

### 5.5 `verify.py`: 2 verificaciones que ya fallaban en `HEAD`

`Asignar docente` (en `lib_ui.py`) y `#form-asignar-docente` (en
`paginas_admin.py`) no existían **en el código de `HEAD`**: son deuda
preexistente, no una regresión de este refactor. Se resuelven con el ítem de
navegación y con la plantilla oculta del modal. `python verify.py` → **10/10
OK**.

---

## 6. Inconsistencias preexistentes (documentadas, no unificadas)

1. **Dominio de correo:** el admin usa `@sgemd.edu.co` y el estudiante
   `@minutodedios.edu.co`. Se dejó como está: unificarlo tocaría dominios de
   ambos roles y sale del alcance de este refactor.
2. **Nombres sin tilde** en algunas bandejas de solicitudes y asesorías
   (*Andres Felipe*, *Lucia Fernandez*). Se comprobó contra la línea base
   (`gen1`) que ya venían así: no es una regresión.
3. **`asignar()` en `paginas_admin.py`** es una vista de asignación antigua que
   no está registrada en el mapa de páginas (tampoco lo estaba en la línea
   base). Se deja el código y se documenta como muerto.
4. **HTML versionado desfasado:** los `.html` de los roles no autorizados del
   repo están desfasados respecto a `lib_css.py` (cambios de CSS ya
   commiteados sin regenerar). Por eso solo se regeneraron los archivos
   autorizados: así el resto queda **byte-idéntico**.

---

## 7. Verificación

- `python generar.py --rol admin` → **19 pantallas** generadas + `index.html`.
- `python verify.py` → **10/10 OK** (incluye los dos checks que fallaban en
  `HEAD`).
- `git status` → solo el conjunto autorizado: 18 `admin/*.html` modificados +
  `admin/configuracion.html` nuevo + 6 `docente/*.html` + 2
  `estudiante/*.html` + `generar.py`, `index.html`, `lib_ui.py` y los tres
  `paginas_*.py`. **Ningún otro rol tocado.**
- Chrome DevTools sobre las 19 pantallas: **0 errores de consola**.
  - `usuarios`: 2 tablas independientes, búsqueda, filtros, paginación, ficha y
    deep-links `#est-912646` / `#est-912655` (saltan de página y resaltan).
  - `asignaciones`: filtros con debounce de 220 ms, estado vacío, modal de
    reasignar con el docente preseleccionado y confirmación que actualiza fila,
    celda, título del botón y muestra *Docente asignado correctamente*.
  - `asignar-docente`: el ítem del menú abre el modal del pendiente (Sofía
    Ramírez / Aromas del Sur / Sin asignar).
  - `solicitudes`: pestañas, ficha de detalle y aprobación desde el kit.
  - `seguimiento`: modal *Registrar avance* con prefill correcto.
  - `emprendimientos`: filtros por sector/etapa/sede y ficha; deep-link
    `#emp-EMP-041` y `#doc-DOC-014` abren la ficha correcta.

---

## 8. Entregables

1. 19 pantallas de `prototype/admin/` regeneradas desde el generador (18
   modificadas + `configuracion.html` nueva). ✅
2. `prototype/cambios-a-admin.md` (este documento). ✅
3. `prototype/index.html` actualizado con *Admin - Configuración*. ✅
4. Deep-links y modal de asignación de docente utilizables por URL. ✅

---

## 9. Rama y commit

- **Base:** `prototype/student` @ `8e71c8c` (el punto de clone; el `reflog` solo
  tiene la entrada `clone`).
- **Rama de trabajo:** `prototype/Admin-Refactor`, creada desde esa base para no
  tocar la rama compartida.
- **Commits (2):**
  1. `prototipo(admin): refactor del rol administrador con datos reales, fichas y deep-links`
     — 33 archivos: `paginas_admin.py`, `lib_ui.py`, `generar.py`,
     `paginas_docente.py`, `paginas_estudiante.py`, `index.html`, las 19
     pantallas de `admin/` (18 modificadas + `configuracion.html` nueva), 6
     pantallas de `docente/` y 2 de `estudiante/`.
  2. `docs(prototipo): documenta el refactor del rol administrador`
     — 3 archivos: `prototype/README.md`,
     `docs/estructura_de_vistas_sgemd.md` y este documento.
- **Fuera del commit:** nada. `git status` antes de commitear listó exactamente
  los 36 archivos del alcance; el resto del repositorio queda **byte-idéntico**
  (las pantallas de los roles no autorizados no se regeneraron, porque el HTML
  versionado de esos roles ya estaba desfasado respecto a `lib_css.py`).
- **Pull request:** de `prototype/Admin-Refactor` hacia `prototype/student`.
