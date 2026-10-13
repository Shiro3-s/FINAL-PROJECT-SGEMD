# Rol Docente — Refactor UX/UI (SGEMD)

Documentación de los cambios aplicados al **Rol Docente** del prototipo SGEMD:
qué se refactorizó, qué componentes nuevos existen, cuál es el flujo actualizado y
qué consideraciones técnicas hay que tener en cuenta antes de regenerar.

- **Alcance:** las **17** pantallas de `prototype/docente/` (9 tras el primer refactor;
  ver §10 para el tercer refactor que las lleva a 17). No se tocaron `admin/`,
  `estudiante/`, `compartido/` ni las librerías `lib_*` (salvo `NAV`/`MIGAS` en
  `lib_ui.py`, ver sección 8).
- **Origen de los cambios:** portados al generador `prototype/paginas_docente.py`
  (ver sección *Consideraciones técnicas*), luego regenerados con `generar.py`.

---

## 1. Inventario de pantallas

| # | Archivo | Pantalla |
|---|---|---|
| 21 | `dashboard.html` | Inicio |
| 22 | `asesorias.html` | Mis asesorías |
| 23 | `asesoria-detalle.html` | Detalle de asesoría |
| 24 | `asesoria-form.html` | Registrar asesoría |
| 25 | `emprendimientos.html` | Emprendimientos asignados |
| 26 | `emprendimiento-expediente.html` | Expediente del emprendimiento |
| 27 | `avance-detalle.html` | Detalle del avance |
| 28 | `avance-form.html` | Registrar avance |
| 29 | `diagnostico.html` | Diagnóstico |
| 30 | `diagnostico-revision.html` | Revisión del diagnóstico |
| 31 | `tareas.html` | Tareas asignadas |
| 32 | `tarea-detalle.html` | Detalle de tarea |
| 33 | `tarea-devolver.html` | Devolver tarea |
| 34 | `tarea-form.html` | Asignar tarea |
| 35 | `perfil.html` | Mi perfil |
| 36 | `contrasena.html` | Cambiar contraseña |
| 37 | `notificaciones.html` | Notificaciones |

---

## 2. Mejoras transversales

> **Nota (2026):** los puntos 2 y 3 de esta sección describen la primera iteración,
> en la que varias acciones abrían **modales**. El **tercer refactor** (§10) las
> convirtió en **vistas completas**; hoy solo *Marcar todo como leído* conserva un
> diálogo de confirmación.

1. **Filtros funcionales.** Los `<select class="filtro">` ahora filtran de verdad:
   cada zona filtrable lleva `<div data-tabla-zona>` alrededor de `toolbar` +
   tabla, los selects llevan `data-filtro` + `data-filtro-col`, el option "Todos…"
   tiene `value=""` y existe un `<span data-resultados aria-live="polite">` con el
   contador (p. ej. "2 resultados").
2. **Acciones reales** en lugar de toasts sueltos: calificar, asignar tarea,
   registrar avance y generar asesoría abren modal; confirmar/reprogramar asesoría
   abren modal; devolver tarea y marcar todo como leído piden confirmación.
3. **Jerarquía y navegación:** tabs en Expediente (Avances · Tareas · Asesorías ·
   Diagnóstico · Comentarios) y en Emprendimientos (Tarjetas / Tabla); tarjeta de
   acciones rápidas en el Inicio; **menú lateral agrupado con acordeón** igual que el
   rol Estudiante.
4. **Estados de revisión** con `badge`: Pendiente · En revisión · Calificada ·
   Devuelta. La columna **Evidencia** de Emprendimientos usa *Con evidencia* /
   *Sin evidencia*.
5. **Enlaces a lista filtrada:** las listas filtrables aceptan `?f=<valor>` (ver
   sección 5).

---

## 3. Componentes nuevos

| Componente | Dónde | Descripción |
|---|---|---|
| Modal de calificación | Expediente, Tareas, Inicio | Puntaje (number 0–100, `required`), Resultado (Aprobada / Devuelta / En revisión) y retroalimentación (`textarea`). |
| Modal de asignación de tarea | Tareas, Inicio | Título, Emprendimiento, Prioridad, Fecha límite, Evidencia requerida e Instrucciones. |
| Modal de asesoría | Asesorías, asesoría-form | Confirmación y reprogramación: Fecha, Hora, Modalidad, Lugar + resumen. |
| Modal de generación de asesoría | Inicio, Asesorías, Expediente | Genera una asesoría para **un estudiante** o para **un proyecto completo** (anexa a todo el grupo); Fecha, Hora, Modalidad, Lugar. |
| Modal de registro de avance | Inicio, Expediente | Emprendimiento, Fase, Fecha, Descripción, Puntaje, Estado de revisión, Evidencia y comentario. |
| Bitácora de comentarios | Expediente | Lista `.comentario` (autor · fecha · texto) + `textarea` con `placeholder` y botón `data-accion="publicar-comentario"`.
| Tabs | Expediente, Emprendimientos | Reutiliza el sistema de `lib_js` (`data-panel`, `data-panel-nombre`, `aria-selected`). |
| Contador de resultados | zonas filtrables | `<span data-resultados aria-live="polite">`. |
| Chips de notificación | Notificaciones | Filtran por tipo y exponen `aria-pressed` sincronizado. |

Clases CSS nuevas (con tokens existentes, sin hex nuevos): `.resultados-contador`,
`.comentario`, `.comentario-cab`, `.comentario-autor`, `.comentario-fecha`,
`.comentario-texto`, `.comentario-form`, `.acciones-rapidas`.

### Contrato `data-accion`

`calificar` · `asignar-tarea` · `confirmar-asesoria` · `reprogramar-asesoria` ·
`rechazar-asesoria` · `publicar-comentario` · `generar-asesoria` · `devolver-tarea` ·
`registrar-avance` · `revisar-diagnostico` · `guardar-recomendaciones` ·
`cambiar-contrasena` · `marcar-todo-leido` · `filtrar-notificacion`.

Todos se interceptan en **fase de captura** con `stopPropagation()`; lo que no es
una de estas acciones lo sigue manejando `lib_js` (por eso el botón genérico del
Inicio conserva su toast por defecto).

---

## 4. Accesibilidad

- Modales propios con `role="dialog"` + `aria-modal="true"` y foco inicial.
- `<caption class="visually-hidden">` en las tablas clave (Actividad reciente,
  Solicitudes y asesorías, Proyectos asignados, Avances y calificaciones, Tareas por
  revisar, Pendientes de revisión).
- Chips de notificación con `aria-pressed` sincronizado al filtrar.
- `<span data-resultados aria-live="polite">` para anunciar el conteo.
- Toast con `aria-live`; controles nuevos siempre con `data-accion`, `aria-label` o
  `placeholder`.

---

## 5. Enlaces a lista filtrada (`?f=`)

Algunas listas aceptan el filtro ya aplicado en la URL:

| Lista | Enlace de ejemplo |
|---|---|
| Tareas por estado | `tareas.html?f=En+revision` |
| Emprendimientos con evidencia | `emprendimientos.html?f=Sin+evidencia` |
| Asesorías por confirmar | `asesorias.html?f=Pendiente+de+confirmar` |

El JS del rol lee `location.search`, busca el primer `select[data-filtro]` que tenga
una opción con ese valor y dispara un `change`, que `lib_js` ya escucha. Funciona en
`file://` y no requiere tocar las librerías.

---

## 6. Flujo de usuario docente

Inicio (panorama + accesos) → Asesorías (confirmar/reprogramar; **generar asesoría**
por estudiante o por proyecto; **BR-002**: el estudiante no agenda solo) →
Emprendimientos (Tarjetas/Tabla con estado de revisión y **evidencia**) → Expediente
(pestañas + bitácora de comentarios + calificar + registrar avance) → Diagnóstico
(recomendaciones) → Tareas (asignar y calificar con evidencia) → Perfil /
Notificaciones.

---

## 7. Consideraciones técnicas

- **Generador, no HTML directo.** A diferencia del plan original (editar el HTML a
  mano), los cambios se portaron a `prototype/paginas_docente.py` y se regeneraron
  con `python generar.py`. Ventaja: no hay deuda de desincronización; correr el
  generador **no** pierde los cambios. Es la única vía que mantiene `admin/`,
  `estudiante/` y `compartido/` byte-idénticos.
- **Bundle autocontenido.** Cada `.html` es un documento independiente (restricción
  de Stitch), así que el CSS/JS docente se repite en los 9 archivos. El helper
  `_inyectar()` añade `<style>` antes del primer `</head>` y `<script>` antes del
  **último** `</body>`; los catálogos de estudiantes/emprendimientos/fases se inyectan
  en el bundle reemplazando el marcador `__OPS__` (`_js_docente()`), para que los
  selectores no se desincronicen de los datos.

  > ⚠️ **Ojo con el punto de inyección.** `lib_js` contiene las cadenas literales
  > `</head>` y `</body>` dentro de su función de impresión (`imprimirDocumento`). Si
  > `_inyectar()` usa el **primer** `</body>` (`replace(..., 1)`), el `<script>` docente
  > cae **dentro** del bundle de `lib_js`; el parser HTML cierra el `<script>` en el
  > primer `</script>` que encuentra y **toda la página queda sin JavaScript** (no
  > funciona el menú acordeón, el burger, la campana ni ningún botón). Por eso el
  > script se inserta con `html.rsplit("</body>", 1)`. Ver §9.
- **Aislamiento.** No se modifican `lib_js.py`, `lib_css.py` ni `lib_charts.py`.
  `lib_ui.py` solo cambia en los diccionarios `NAV["docente"]` y `MIGAS["docente"]`
  (menú agrupado y migas sin Seguimiento). El modal/`toast`/`confirmar` propios
  reconstruyen las clases públicas (`.modal-velo`, `.modal`, `.campo`, `.btn`, …).
- **Sin backend.** Persistencia simulada en `localStorage` (`sgemd:v1:<ruta>`). No
  se introducen dependencias externas.
- **Ids de control.** `lib_ui` numera cada control con un contador global (`_fid`).
  Los pocos campos de id fijo que el JS necesita no consumen ese contador: el
  `_campo_libre("com-obs", …)` del expediente y el helper JS `selCampo`/`campo` que
  arma los modales (`av-*`, `gen-*`). Como el contador es global al proceso, regenerar
  cambia la numeración de los `id`/`for` de todos los roles; es esperado y no rompe nada.

### Verificación

- `python _auditar.py` → **0**.
- `python _check_tipografia.py` → **0**.
- `python _estructura.py` → **1** aviso: el presupuesto de estilos en línea
  (1025 / 699). Es **deuda preexistente y transversal**, no de este refactor: al
  regenerar el estado base (previo a estos cambios) ya daba 1058. El grueso del inline
  está en las vistas de **estudiante** (~625) y **administrador** (~266); las 9 vistas
  docente solo aportan ~84. Con este refactor el total **baja** de 1058 a 1025. Los
  avisos por archivo («sin cerrar», «huérfano», «sin href») **desaparecieron** al
  corregir el punto de inyección (§9): eran un síntoma del `<script>` partido, no un
  ruido del parser.
- **DOM real (jsdom):** las 9 pantallas cargan con `js-listo`, **0 errores JS**,
  acordeón del menú funcional (toggle + `aria-expanded`), burger/`#sb` funcional,
  campana → drawer, modales de acción (`generar-asesoria`, `registrar-avance`,
  `calificar`) abren/cierran, el modo del modal de asesoría alterna, los filtros
  (estudiante, evidencia) filtran filas y actualizan el contador, las pestañas cambian
  de panel y el enlace `?f=Sin+evidencia` aplica el filtro. También se verificó que
  `estudiante/` y `admin/` siguen con `js-listo` y su acordeón operativo.
- **Navegador real (`python _interaccion.py`, Chromium):** **0 problemas**. Las 60
  pantallas cargan sin errores de consola ni excepciones, con `html.js-listo`, el drawer
  y los modales operativos y el estado en `localStorage`. Ningún control queda inerte ni
  ningún `data-accion` sin efecto. *(Antes de la corrección de §9 las 9 vistas docente
  fallaban el bloque de interacción: sin JS no había `js-listo`, ni drawer, ni modal.)*
- **Barrido responsive (`python _responsive.py`, Chromium):** **88** avisos, de los que
  **87** son celdas de tabla «ocultas» a 375 px y **1** un desborde. Es **deuda
  preexistente**: el estado base (con la inyección ya corregida) da **83**. El único
  delta real es `docente/emprendimientos.html` (40 → 45 celdas): esa tabla **se oculta
  entera a 375 px** por diseño (se sustituye por tarjetas) y al añadir la columna
  *Evidencia* suma 5 celdas más (5 filas × 1 columna). El desborde
  (`estudiante/configuracion.html` @1280) es ajeno a este cambio. No hay ningún
  desborde nuevo en las vistas docente.

---

## 8. Segundo refactor (2026) — ajustes de vistas docente

Cambios pedidos sobre el prototipo, aplicados en `paginas_docente.py` + `lib_ui.py`
y regenerados con `generar.py`:

1. **Menú con la estructura del Estudiante.** `NAV["docente"]` dejó de ser plano:
   `Inicio` + grupo **Mis emprendimientos** (*Emprendimientos asignados*, *Diagnóstico*)
   + grupo **Acompañamiento y actividades** (*Asesorías*, *Tareas*). Notificaciones y
   Perfil salen del menú lateral (quedan en la barra superior, como en Estudiante).
   `MIGAS["docente"]` pierde las entradas de Seguimiento.
2. **Se elimina el módulo Seguimiento** completo: `seguimiento.html`,
   `seguimiento-dashboard.html` y `seguimiento-notas.html` (+ su dataset). Su función
   se reparte entre la columna **Evidencia** de *Emprendimientos asignados* y el modal
   *Registrar avance*.
3. **Emprendimientos:** fuera la tarjeta «En fase 2 o 3»; **N:N** (un emprendimiento
   puede tener varios estudiantes y viceversa, `ESTUDIANTES_EMP`); la tarjeta y la
   tabla muestran el grupo; nueva columna **Evidencia** (*Con evidencia* / *Sin
   evidencia*) y **filtro por evidencia**.
4. **Asesorías:** filtro **por estudiante**; acción **Generar asesoría** (modal con
   modo *un estudiante* o *un proyecto completo*, que anexa a todo el grupo); el
   formulario de registro ahora **permite elegir estudiante y emprendimiento**.
5. **Expediente:** tarjeta *Estudiantes del grupo*; acciones *Registrar avance* (modal)
   y *Generar asesoría*.
6. **Perfil:** sin las tarjetas KPI (emprendimientos asignados, asesorías realizadas,
   promedio); sin «Zona horaria» ni «Firma electrónica»; se agrega **Título /
   especialidad** y una tarjeta **Ubicación** (región/rectoría, departamento, ciudad,
   sede).
7. **Notificaciones:** el aviso de evidencia apunta a `emprendimiento-expediente.html`
   (ya no a Seguimiento).

Verificación de este segundo refactor: `_auditar.py` = 0, `_check_tipografia.py` = 0,
`_estructura.py` = 1 (solo el presupuesto inline preexistente), `_interaccion.py` = 0.
DOM real verificado con jsdom y Chromium (ver §7).

---

## 9. Corrección de navegabilidad (bug de inyección del bundle)

**Síntoma:** en las vistas docente **no funcionaba ningún JavaScript** — el menú no
desplegaba, el burger no abría, la campana no respondía y ningún botón reaccionaba.

**Causa raíz:** `_inyectar()` insertaba el `<script>` del rol antes del **primer**
`</body>` del documento con `html.replace("</body>", ..., 1)`. Pero `lib_js.py` incluye
la cadena literal `</body>` (y `</head>`) dentro de su función `imprimirDocumento`
(que arma un documento con `w.document.write(...)`). Ese `</body>` aparece **antes** del
`</body>` real del documento, así que el bundle docente quedaba insertado **en medio de
`lib_js`**:

```html
<script>
  ... lib_js ...
  ... "<footer>…</footer></body>" + ...   <!-- el string de impresión -->
  <script>(function(){ ...bundle docente... })();</script>   <!-- ¡inyectado aquí! -->
  ... resto de lib_js ...
</script></body></html>
```

El parser HTML, dentro de un `<script>`, **solo** atiende `</script>`: el `</script>`
del bundle inyectado **cerraba `lib_js` antes de tiempo**, dejando el resto de `lib_js`
y el bundle docente como texto plano. Resultado: ni `lib_js` ni el bundle docente se
ejecutaban.

> Nota: el bug ya existía en el generador (estado `HEAD`); los `.html` versionados
> estaban **desactualizados** (no tenían el bundle inyectado), por eso el problema se
> hizo visible al regenerar.

**Corrección:** insertar antes del **último** `</body>`:

```python
html = ("<script>" + _js_docente() + "</script>\n</body>").join(
    html.rsplit("</body>", 1))
```

El `<style>` se sigue insertando antes del primer `</head>` (ahí sí es el correcto,
porque la cabecera real precede a `lib_js`).

**Efecto colateral resuelto:** los avisos por archivo de `_estructura.py`
(«`<html>`/`<a>`/`<label>` sin cerrar», «cierre `</body>`/`</script>` huérfano»,
«`label for sin control: evidencia-real`») **desaparecieron**: eran el mismo
`<script>` partido, no un defecto del verificador.

### Ajuste de `_interaccion.py` (sonda de toast)

Al quedar el JS operativo se pudo correr `_interaccion.py`, que destapó 4 avisos
`toast=0 (esperado 1)` — uno por cada pantalla con bloque de comportamiento
(`estudiante/dashboard.html`, `estudiante/tarea-detalle-completada-usuarios.html`,
`docente/dashboard.html`, `admin/usuarios.html`). **No son un fallo del producto:** la
sonda tomaba el primer `<button>` con texto visible y sin `data-accion` suponiendo que
caería en el `default` del manejador (que lanza un toast), pero en esas pantallas el
primer botón así es un `.nav-label` (acordeón) o un botón de paginación, que tienen su
propio comportamiento y no pasan por el `default`. El mismo aviso aparecía en las vistas
de estudiante y administrador, ajenas a este cambio.

Se corrigió la sonda para que cree un botón «pelado» temporal y compruebe el `default`
de forma determinista (en vez de depender de qué botón ocupe el primer lugar del DOM).
Con ello `_interaccion.py` vuelve a **0 problemas** y la comprobación del toast sigue
siendo real (de hecho, más robusta).

---

## 10. Tercer refactor (2026) — las acciones docente pasan a vistas completas

**Motivación.** En las iteraciones anteriores casi todo se resolvía en ventanas
**modales** (*Registrar avance*, *Calificar*, *Asignar tarea*, *Generar asesoría*,
*Confirmar/Reprogramar asesoría*, *Cambiar contraseña*). El equipo pidió **eliminar los
pop-ups**: cada acción debe tener su propia **vista completa**, con contexto suficiente
para trabajar sin perder de vista el emprendimiento o el estudiante.

El alcance pasa de **9 a 17** pantallas (§1) y el único diálogo que se conserva es la
confirmación destructiva *Marcar todo como leído* (no tiene formulario).

### 10.1. Cambios por área

1. **Menú lateral.** En `NAV["docente"]`, **Tareas** se mueve al grupo
   **Mis emprendimientos** (*Emprendimientos asignados · Diagnóstico · Tareas*);
   **Acompañamiento y actividades** queda solo con *Asesorías*. `MIGAS["docente"]` gana
   las migas de las vistas nuevas.
2. **Inicio.** Las acciones rápidas y la actividad reciente **enlazan** a las vistas
   completas (avance, tarea, asesoría) en lugar de abrir modal.
3. **Avances.** Nuevas vistas **Detalle del avance** (`avance-detalle.html`: descripción,
   evidencia adjunta, historial y acciones de edición) y **Registrar avance**
   (`avance-form.html`, formulario-página que reemplaza al modal homónimo).
4. **Tareas.** **Detalle de tarea** (`tarea-detalle.html`) para ver y **calificar**;
   **Devolver tarea** (`tarea-devolver.html`) como vista propia con **motivo** y
   **observaciones**; **Asignar tarea** (`tarea-form.html`) como página.
5. **Asesorías.** Una **sola tabla** con **filtro de estado agrupado**
   (*Por agendar · Agendada · Completada · Cancelada*; el estado detallado se conserva
   en el `badge`). Cada fila abre **Detalle de asesoría** (`asesoria-detalle.html`), la
   vista completa para **confirmar/reprogramar/rechazar**. **Registrar asesoría**
   (`asesoria-form.html`) se rehizo: el **emprendimiento** se elige por **grupo** (agenda
   a todos sus estudiantes), con **hora disponible**, **descripción de necesidades** y
   **tema por defecto** (*FASE 2 - Prototipo: empaque* o *Tarea: …*). Refleja el flujo de
   referencia del estudiante (`solicitar-asesoria`, **sin modificar**).
6. **Emprendimientos asignados.** Nuevo **selector de estudiante**: al elegir uno, la
   lista se reemplaza por **sus emprendimientos como pestañas** (el primero activo por
   defecto). El modelo sigue siendo **N:N** (`ESTUDIANTES_EMP`).
7. **Diagnóstico.** Deja de ser una sola pantalla de *Revisión*: **Diagnóstico**
   (`diagnostico.html`) incorpora **selector de emprendimiento** y **filtros por
   estudiante/proyecto**, **avance por fases** (`progreso_fases`) y una tabla cuyo
   **origen** es la **completación de las 4 fases** o una **serie de tareas clave**. La
   revisión con recomendaciones vive en **Revisión del diagnóstico**
   (`diagnostico-revision.html`).
8. **Contraseña.** El modal se sustituye por la vista **Cambiar contraseña**
   (`contrasena.html`), enlazada desde *Mi perfil*.

### 10.2. Contrato `data-accion` (estado final)

Se mantienen `guardar-avance`, `guardar-calificacion`, `devolver-tarea`, `asignar-tarea`,
`generar-asesoria`, `confirmar-asesoria`, `reprogramar-asesoria`, `rechazar-asesoria`,
`guardar-recomendaciones`, `actualizar-contrasena` (disparan un **toast**, sin modal),
más `publicar-comentario`, `descargar-pdf`, `filtrar-notificacion` y `marcar-todo-leido`
(única confirmación con diálogo). Ya **no existe** `data-accion="ver"` en el rol: ver un
detalle es un **enlace** real.

### 10.3. Verificación

- `_auditar.py` → **0**; `_check_tipografia.py` → **0**.
- `_estructura.py` → **1** aviso: presupuesto de estilos en línea (1107 / 699). Es la
  misma **deuda preexistente y transversal** (el presupuesto ya se superaba antes de este
  refactor); no hay avisos por archivo, etiquetas ni `for` sin control.
- `_interaccion.py` (Chromium) → **0 problemas** en las **65** pantallas.
- `_responsive.py` → **88** avisos, **idéntico** al estado previo (1 desborde ajeno en
  `estudiante/configuracion.html` @1280 y 87 celdas ocultas a 375 px en paneles de
  pestañas). Las tablas nuevas son visibles y no añaden celdas ocultas.
- **jsdom:** las 17 vistas cargan con `js-listo` y 0 errores JS; el selector por
  estudiante muestra sus emprendimientos como pestañas, las pestañas de lista/expediente
  conmutan, los filtros actualizan el contador y `?f=Sin+evidencia` sigue vigente.
- `admin/`, `estudiante/` y `compartido/` **byte-idénticos** (no se tocaron).
