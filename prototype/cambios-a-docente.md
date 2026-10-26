# Cambios a Docente — Refactor UX/UI del Rol Docente (SGEMD)

> Documento de trabajo. Registra **todo** lo que se hará sobre el Rol Docente.
> Estado: **ejecutado** (ver *Nota de ejecución*).
> Ámbito: solo los 12 archivos `prototype/docente/*.html`. No se tocan `admin/`,
> `estudiante/`, `compartido/` ni las librerías `lib_*`.

## Nota de ejecución

El refactor **se aplicó por completo**. Se desvió en un punto respecto al plan
original: en lugar de editar el HTML directo (§3), los cambios se **portaron a
`prototype/paginas_docente.py`** y se regeneraron con `python generar.py`. Esto
elimina la deuda de desincronización que el propio documento anticipaba en §8 y es
la única forma de que `admin/`, `estudiante/` y `compartido/` queden byte-idénticos.
Resultado: `_auditar.py` = 0, `_estructura.py` = 0 (inline 613/699), `_check_tipografia.py`
= 0; verificación manual con Chrome DevTools (consola y responsive) sin hallazgos.
Detalle funcional en [`../docs/docente-rol-ux.md`](../docs/docente-rol-ux.md).
`_interaccion.py` no se ejecutó (Playwright no instalado); su cobertura se hizo a mano.

Las secciones siguientes se conservan como registro del plan; los puntos que
difieren de lo ejecutado quedan señalados en línea.

---

## 1. Objetivo

Elevar la UX del **Rol Docente** del SGEMD, alinear la interfaz con la lógica de
negocio (seguimiento, evaluación, retroalimentación y asesorías) y completar
desde el frontend la estructura visual y lógica faltante para que el panel del
docente sea 100% funcional a nivel de interfaz.

---

## 2. Alcance

Las 12 pantallas de `prototype/docente/`:

| # | Archivo | Pantalla |
|---|---|---|
| 21 | `dashboard.html` | Inicio |
| 22 | `asesorias.html` | Mis asesorías |
| 23 | `asesoria-form.html` | Registrar asesoría |
| 24 | `emprendimientos.html` | Emprendimientos asignados |
| 25 | `emprendimiento-expediente.html` | Expediente del emprendimiento |
| 26 | `seguimiento.html` | Seguimiento (lista) |
| 27 | `seguimiento-dashboard.html` | Tablero de seguimiento |
| 28 | `seguimiento-notas.html` | Registrar avance y calificar |
| 29 | `diagnostico.html` | Revisión del diagnóstico |
| 30 | `tareas.html` | Tareas asignadas |
| 31 | `perfil.html` | Mi perfil |
| 32 | `notificaciones.html` | Notificaciones |

**Fuera de alcance:** Admin, Estudiante, Compartido. **Descartado:** módulo
"Grupos" (no existe en el SGEMD y `DESIGN.md` prohíbe inventar módulos).

---

## 3. Estrategia técnica (HTML-first) — *superado*

> **Ejecutado de otra forma:** el bundle CSS/JS sí es el descrito abajo, pero se
> inyecta desde `paginas_docente.py` (`_inyectar()`), no editando el `.html` a mano.
> El resto de esta sección describe ese bundle tal como quedó.

Se editan **directamente los `.html` generados**, sin correr `generar.py`. En cada
archivo que lo requiera se inyectan dos bloques:

1. **`<style>`** (etiqueta **plana `<style>`**, sin atributos → así `_estructura.py`
   la excluye del presupuesto inline). Usa **solo tokens existentes**
   (`--amarillo`, `--azul-real`, `--azul-noche`, `--gris`, `--r-md`, …) y tamaños
   de fuente de la escala aprobada (32/28/24/20/18/16/14/13px), interlineado ≥1.15.
   **Cero hex nuevos.**
2. **`<script>`** antes de `</body>`, autocontenido, con **delegación en fase de
   captura** (`addEventListener("click", h, true)` + `stopPropagation()`), que
   actúa **solo** sobre mis `data-accion` nuevos. El resto del comportamiento lo
   sigue manejando `lib_js`.

### 3.1 Reglas de aislamiento y compatibilidad
- No se modifica `lib_js.py`, `lib_css.py`, `lib_ui.py`, `lib_charts.py`.
- `abrirModal`/`toast`/`confirmar` de `lib_js` son **privados** (dentro del IIFE):
  el script propio **reconstruye el modal** con las clases `.modal-velo`, `.modal`,
  `.modal-head`, `.modal-cuerpo`, `.modal-foot`, `.campo`, `.btn`.
- El JS no usa literales `style="..."`, ni `%%`, ni `__X__`, ni hex/Unicode fuera
  de la paleta permitida (todo esto lo escanea `_auditar.py` sobre el archivo
  completo).
- **No** se interceptan botones genéricos: `_interaccion.py` exige que el primer
  `<button>` con texto y sin `data-accion` de `dashboard.html` produzca **1 toast**
  (comportamiento `default` de `lib_js`). Mi handler ignora todo lo que no sea una
  de mis acciones.
- Todo control nuevo lleva gancho: `data-accion`, `aria-label` o `placeholder`
  (regla de "controles inertes" de `_interaccion.py`).
- Enlaces `a.btn` nuevos siempre con `href` real o `data-accion`.

### 3.2 Restricciones de los auditores (deben quedar en 0)
- Paleta cerrada de 6 hex; `rgba()` solo derivado de esos 6.
- Presupuesto inline `666/699` → **0 estilos inline nuevos** (usar clases).
- Anchos `width/min-width` en línea >1180px: prohibido.
- `id` únicos, `label for` con control, `<tr>/<td>` pareados, landmarks presentes.
- Badge de rol `>DOCENTE<` y logo único intactos.
- No anidar `.card` dentro de `.card` (`_auditar.py` → "tabla dentro de card").
- **Clones:** no debe aparecer una firma de ≥3 bloques repetida en `docente/`.
  Tras los cambios solo `emprendimientos` (`tarjetas+callout+tabs`) y
  `expediente` (`tabla+kanban+tabs`) llegan a 3, y **difieren** entre sí.

---

## 4. Mejoras transversales

1. **Filtros funcionales.** Hoy los `<select class="filtro">` no filtran: no tienen
   `data-filtro` ni un contenedor `data-tabla-zona`. Se corrige así:
   - Envolver `toolbar` + `card tabla-envoltura` en `<div data-tabla-zona>`
     (div plano, **no** `.card`).
   - Añadir `data-filtro` y `data-filtro-col="N"` a cada `<select>`.
   - Poner `value=""` en el option "Todos…" (sin esto, `aplicarFiltros()` compara el
     texto "Todos…" y **oculta todas las filas**; ver `lib_js.py` línea 237).
2. **Contador de resultados:** `<span data-resultados aria-live="polite">` en cada
   zona filtrable.
3. **Acciones reales** (hoy son toasts/toggles):
   - Calificar → **modal de calificación**.
   - Asignar tarea → **modal de asignación**.
   - Registrar avance (listado) → **navega** a `seguimiento-notas.html`.
   - Confirmar asesoría → **modal de confirmación/reprogramación**.
4. **Jerarquía/navegación:** tabs en Expediente y Emprendimientos; acciones rápidas
   en el Dashboard.
5. **Accesibilidad:** `<caption class="visually-hidden">` en tablas clave; modales
   con `role="dialog" aria-modal="true"`; foco inicial; `aria-pressed`/`aria-live`.
6. **Estados de revisión** con `badge`: Pendiente · En revisión · Calificada ·
   Devuelta.

---

## 5. Cambios por pantalla

**21 `dashboard.html`** — Tarjeta "Acciones rápidas" (botones con `data-accion`:
registrar-avance, calificar, registrar-asesoria, revisar-diagnostico); bloque
"Próximas asesorías" (`.agenda`); "Compromisos de hoy" con enlaces reales.
*No tocar botones de texto existentes sin `data-accion` (prueba de toast).*

**22 `asesorias.html`** — `data-tabla-zona` + filtros **estado** y
**emprendimiento** funcionales (`value=""`, `data-filtro-col`); contador; acción
**Confirmar** en filas pendientes; "Editar" → modal confirmar/reprogramar;
"Ver detalle" → modal.

**23 `asesoria-form.html`** — "Confirmar y notificar" → modal resumen; "Proponer
otra fecha" → modal con fecha/hora; "Rechazar solicitud" → confirmación.

**24 `emprendimientos.html`** — Tabs **Tarjetas / Tabla** (`data-panel` /
`data-panel-nombre`). La tabla = *proyectos asignados*: Emprendimiento, Estudiante,
Sector, Etapa, Avance, **Estado de revisión**, Última actividad, Acciones. Filtros
etapa/sector + contador. Cada fila abre el expediente.

**25 `emprendimiento-expediente.html`** — Tabs **Avances · Tareas · Asesorías ·
Diagnóstico · Comentarios**; **bitácora de comentarios** (lista
`.comentario` con autor·fecha·texto + `textarea` con `placeholder` y botón con
`data-accion="publicar-comentario"`); "Calificar" del kanban → modal de
calificación.

**26 `seguimiento.html`** — `data-tabla-zona` + filtros **fase** y **evidencia**
funcionales + contador; "Registrar avance" navega a `seguimiento-notas.html`;
"Ver historial" → modal.

**27 `seguimiento-dashboard.html`** — Pendientes por prioridad enlazan a la lista
filtrada; acción rápida "Registrar avance".

**28 `seguimiento-notas.html`** — `<select>` **estado de revisión**; "Registrar
avance" → confirmación + toast; "Guardar borrador" → toast.

**29 `diagnostico.html`** — Tabla "Pendientes de revisión" con acción **Revisar**
→ modal de retroalimentación; "Guardar recomendaciones" → confirmación.

**30 `tareas.html`** — `data-tabla-zona` + filtros **estado** y **prioridad**
funcionales + contador; **modal de calificación** desde cada "Calificar"
(`data-accion="calificar"`); **modal de asignación** desde "Asignar tarea"; acción
"Devolver al estudiante".

**31 `perfil.html`** — Confirmación al "Guardar cambios"; "Cambiar contraseña" →
modal; tarjeta de preferencias de notificación (In-App).

**32 `notificaciones.html`** — Acciones de cada aviso abren la pantalla correcta;
"Marcar todo como leído" con confirmación; filtro por tipo.

---

## 6. Componentes nuevos (CSS/JS inline aislado)

1. **Modal de calificación:** Puntaje (`number` 0–100, `required`), Resultado
   (Aprobada / Devuelta / En revisión), Retroalimentación (`textarea`).
2. **Modal de asignación de tarea:** Título, Emprendimiento, Prioridad, Fecha
   límite, Evidencia requerida, Instrucciones.
3. **Modal de confirmación/reprogramación de asesoría:** Fecha, Hora, Modalidad,
   Lugar + resumen.
4. **Bitácora de comentarios** (expediente).
5. **Tabs de expediente/emprendimientos** (reutiliza el sistema de `lib_js`:
   `data-panel`, `data-panel-nombre`, `aria-selected`).
6. **Contador de resultados** (`aria-live="polite"`).

### 6.1 Clases CSS nuevas (con tokens existentes, sin hex)
`.resultados-contador`, `.comentario`, `.comentario-cab`, `.comentario-autor`,
`.comentario-fecha`, `.comentario-texto`, `.comentario-form`, `.acciones-rapidas`.

### 6.2 Contrato `data-accion` nuevo
`calificar` · `asignar-tarea` · `confirmar-asesoria` · `reprogramar-asesoria` ·
`publicar-comentario` · `devolver-tarea` · (dashboard) `registrar-avance`,
`revisar-diagnostico`. Todos interceptados en captura; el resto lo maneja `lib_js`.

---

## 7. Flujo de usuario docente (actualizado)

Inicio (panorama + accesos) → Asesorías (confirmar/reprogramar; BR-002: el
estudiante no agenda solo) → Emprendimientos (Tarjetas/Tabla con estado de
revisión) → Expediente (pestañas + comentarios + calificar) → Seguimiento (avance y
calificación con puntaje/retroalimentación) → Diagnóstico (recomendaciones) →
Tareas (asignar y calificar con evidencia) → Perfil/Notificaciones.

---

## 8. Consideraciones técnicas

- Cada `.html` es autocontenido (Stitch sirve documentos independientes), por eso
  el CSS/JS docente se repite en los 12 archivos: es el patrón del proyecto.
- **Deuda resuelta:** el refactor vive en `paginas_docente.py`; correr
  `python generar.py` **reproduce** los cambios. No hay HTML desincronizado.
- Sin backend: persistencia en `localStorage` (`sgemd:v1:<ruta>`).
- No se introducen dependencias externas.

---

## 9. Documentación a actualizar — *hecho*

- **Nuevo:** `docs/docente-rol-ux.md` — ✅ creado.
- **Actualizar:** `docs/estructura_de_vistas_sgemd.md` §3.3 (Perfil Docente) → hecho.
- **Nota:** `prototype/README.md` (bundle inline docente + generación sin pérdida) → añadida.

---

## 10. Verificación

- `python _auditar.py` → **0**. ✅
- `python _estructura.py` → **0**, inline 613/699, 47 anchos fijos sin crecer. ✅
- `python _check_tipografia.py` → **0**. ✅
- `python _interaccion.py` (Playwright/Chromium) → **no ejecutado**: Playwright no
  está instalado. ✅ *Sustituido por verificación manual con Chrome DevTools.*
- Manual con DevTools (Chrome): consola **0 errores** en las 12 pantallas; filtros,
  modales, tabs y confirmaciones OK; responsive 1440/768/375 px sin desbordes. ✅
- Confirmado que `estudiante/`, `admin/` y `compartido/` **no cambian** (`git status`
  solo lista `paginas_docente.py` + 12 `docente/*.html`). ✅

---

## 11. Entregables

1. Los 12 `prototype/docente/*.html` refactorizados. ✅
2. `prototype/cambios-a-docente.md` (este documento). ✅
3. `docs/docente-rol-ux.md` + actualizaciones en `docs/estructura_de_vistas_sgemd.md`
   y `prototype/README.md`. ✅
4. En el chat: resumen + DIFF/extractos de las pantallas clave.

---

## 12. Segundo refactor (2026) — vistas docente alineadas a Estudiante

> Ajuste posterior pedido por el equipo. Cambia el alcance de 12 a **9** pantallas.
> Todo se aplicó en el generador y se regeneró con `python generar.py`.

1. **Menú igual al del Estudiante.** `NAV["docente"]` pasa de plano a
   `Inicio` + grupo **Mis emprendimientos** (*Emprendimientos asignados*,
   *Diagnóstico*) + grupo **Acompañamiento y actividades** (*Asesorías*, *Tareas*).
   Notificaciones y Perfil dejan el menú lateral (van en la barra superior).
   `MIGAS["docente"]` pierde Seguimiento. Archivos: `lib_ui.py` (solo `NAV`/`MIGAS`).
2. **Se elimina Seguimiento:** `seguimiento.html`, `seguimiento-dashboard.html`,
   `seguimiento-notas.html` y su dataset `SEGUIMIENTO`. Los archivos se borran de
   `prototype/docente/`.
3. **Emprendimientos:** fuera la tarjeta «En fase 2 o 3»; modelo **N:N** con
   `ESTUDIANTES_EMP` (un emprendimiento con varios estudiantes, un estudiante con
   varios emprendimientos); tarjeta y tabla muestran el grupo; **columna Evidencia**
   (*Con evidencia* / *Sin evidencia*) y **filtro por evidencia**.
4. **Asesorías:** **filtro por estudiante**; nueva acción **Generar asesoría**
   (modal: *un estudiante* o *un proyecto completo* → anexa a todo el grupo);
   `asesoria-form.html` permite **elegir estudiante y emprendimiento**.
5. **Expediente:** tarjeta *Estudiantes del grupo*; acciones *Registrar avance*
   (modal nuevo) y *Generar asesoría*.
6. **Perfil:** sin KPIs, sin Zona horaria ni Firma electrónica; + **Título /
   especialidad** y tarjeta **Ubicación** (región/rectoría, departamento, ciudad, sede).
7. **Notificaciones:** el aviso de evidencia apunta a `emprendimiento-expediente.html`.

### Verificación de este segundo refactor

- `python _auditar.py` → **0**; `python _check_tipografia.py` → **0**.
- `python _estructura.py` → **1** aviso: presupuesto de estilos en línea (1025 / 699),
  deuda **preexistente y transversal** (el estado base ya daba 1058; el grueso está en
  `estudiante/` y `admin/`, no en `docente/`). Los avisos por archivo desaparecieron
  tras corregir el bug de inyección (ver abajo).
- **Bug de navegabilidad corregido:** `_inyectar()` insertaba el `<script>` del rol en
  el **primer** `</body>`, que en `lib_js` está dentro de un string de
  `imprimirDocumento`; el bundle caía dentro de `lib_js` y el parser cerraba el
  `<script>` antes de tiempo, dejando **toda la vista sin JavaScript**. Ahora se inserta
  antes del **último** `</body>` (`html.rsplit("</body>", 1)`). Detalle en
  [`../docs/docente-rol-ux.md`](../docs/docente-rol-ux.md) §9.
- **DOM real (jsdom):** las 9 pantallas cargan con `js-listo` y 0 errores JS; acordeón,
  burger, campana→drawer, modales, filtros (estudiante/evidencia), pestañas y `?f=`
  verificados. `estudiante/` y `admin/` siguen funcionando.
- **Navegador real (`_interaccion.py`, Chromium):** **0 problemas** en las 60 pantallas.
  Se ajustó la sonda de toast del verificador (tomaba un `.nav-label`/paginación como si
  fuera un botón inerte); ver `../docs/docente-rol-ux.md` §9.
- **Responsive (`_responsive.py`):** 88 avisos, deuda preexistente (base ya 83). El único
  delta es `docente/emprendimientos.html` (40 → 45 celdas ocultas a 375 px), porque su
  tabla se oculta entera a ese ancho y se le sumó la columna *Evidencia*. Sin desbordes
  nuevos en docente.

---

## 13. Tercer refactor (2026) — acciones docente como vistas completas

> Ajuste posterior pedido por el equipo tras revisar el prototipo. Cambia el alcance de
> **9 a 17** pantallas. Todo se aplicó en `prototype/paginas_docente.py` (+ `NAV`/`MIGAS`
> en `lib_ui.py`) y se regeneró con `python generar.py`.

**Idea de fondo:** el docente ya no resuelve casi nada en ventanas modales. Cada acción
—ver un avance, calificar o devolver una tarea, registrar o confirmar una asesoría,
revisar un diagnóstico, cambiar la contraseña— lleva a una **vista completa** con su
propio contexto. Solo sobrevive un diálogo (sin formulario) para la confirmación
destructiva *Marcar todo como leído*.

1. **Menú.** En `NAV["docente"]`, **Tareas** se mueve al grupo **Mis emprendimientos**
   (queda: *Emprendimientos asignados · Diagnóstico · Tareas*); **Acompañamiento y
   actividades** deja solo *Asesorías*. `MIGAS["docente"]` suma las migas de las vistas
   nuevas (detalle/generar asesoría, detalle/registrar avance, revisión, detalle/
   devolver/asignar tarea, cambiar contraseña).
2. **Inicio (dashboard).** Acciones rápidas y actividad reciente ahora **enlazan** a las
   vistas completas (avance, tarea, asesoría, diagnóstico); se quitaron los botones que
   abrían modal.
3. **Avances.** Nueva **vista completa de avance** (`avance-detalle.html`): descripción,
   evidencia adjunta, datos, historial y acciones de edición; y **registrar/editar avance**
   (`avance-form.html`) como formulario-página (antes era el modal *Registrar avance*).
   El expediente enlaza a ambas.
4. **Tareas.** **Vista completa por tarea** (`tarea-detalle.html`) para visualizar y
   **calificar**; **devolver** tiene su **propia vista** (`tarea-devolver.html`) con
   **motivo** (select) y **observaciones**; **asignar tarea** pasa a página
   (`tarea-form.html`). La lista enlaza a las tres.
5. **Asesorías.** La tabla es **una sola** con **filtro por estado agrupado**
   (*Por agendar · Agendada · Completada · Cancelada*, derivado del estado detallado
   *Pendiente de confirmar · Confirmada · Finalizada · Cancelada por el estudiante*).
   Cada fila abre **detalle de asesoría** (`asesoria-detalle.html`, vista completa con
   confirmar/reprogramar/rechazar). Desde el **expediente**, el tab *Asesorías* lleva a
   esa lista. **Registrar/generar asesoría** (`asesoria-form.html`) se rediseñó: el
   emprendimiento se elige por **grupo** (agenda a todos sus estudiantes), con **hora
   disponible**, **descripción de necesidades** y **tema por defecto** (p. ej.
   *FASE 2 - Prototipo: empaque* o *Tarea: …*). Refleja el flujo de referencia del
   estudiante (`solicitar-asesoria`, **no modificado**).
6. **Emprendimientos asignados.** Nuevo **selector por estudiante**: al elegir uno, la
   lista se sustituye por **los emprendimientos de ese estudiante como pestañas**; el
   primer emprendimiento queda activo por defecto. Los emprendimientos del docente
   siguen siendo N:N (p. ej. *Mariana Lopez* tiene *Sabor y Sabe* y *Krea Textil*;
   *Diego Torres* tiene *Sabor y Sabe* y *EcoPack*).
7. **Diagnóstico.** Deja de ser solo *Revisión del diagnóstico*: **vista propia** con
   **selector de emprendimiento** y **filtros por estudiante/proyecto**, **avance por
   fases** y tabla de diagnósticos cuyo **origen** es la **completación de las 4 fases**
   o una **serie de tareas clave**. La revisión y recomendaciones viven en
   `diagnostico-revision.html` (vista completa).
8. **Cambiar contraseña.** El modal se reemplaza por la vista `contrasena.html`
   (enlazada desde *Mi perfil*).

### Contrato `data-accion` (estado final)

Se mantienen `guardar-avance`, `guardar-calificacion`, `devolver-tarea`, `asignar-tarea`,
`generar-asesoria`, `confirmar-asesoria`, `reprogramar-asesoria`, `rechazar-asesoria`,
`guardar-recomendaciones`, `actualizar-contrasena` (todos disparan un **toast** de
confirmación, ya sin modal), `publicar-comentario`, `descargar-pdf`, `filtrar-notificacion`
y `marcar-todo-leido` (única confirmación con diálogo). Desaparecen los `data-accion="ver"`
del rol: ver algo ahora es un **enlace**.

### Verificación de este tercer refactor

- `python _auditar.py` → **0** (sin clones: las firmas de las vistas nuevas son únicas).
- `python _check_tipografia.py` → **0**.
- `python _estructura.py` → **1** aviso: presupuesto de estilos en línea (1107 / 699),
  deuda preexistente y transversal (no hay avisos por archivo, etiquetas ni `for`).
- `python _interaccion.py` (Chromium) → **0 problemas** en las 65 pantallas.
- **Responsive (`_responsive.py`):** 88 avisos, **idéntico** al estado previo (1 desborde
  ajeno en `estudiante/configuracion.html` @1280 y 87 celdas ocultas a 375 px en paneles
  de pestañas). Las tablas nuevas (`diagnostico`, `diagnostico-revision`) son visibles y
  no añaden celdas ocultas.
- **DOM real (jsdom):** las 17 vistas cargan con `js-listo` y 0 errores JS; el selector
  por estudiante muestra sus emprendimientos como pestañas (primer tab activo), las
  pestañas de la lista y del expediente conmutan, los filtros (estado agrupado de
  asesorías, evidencia, estudiante) filtran y actualizan el contador, y `?f=Sin+evidencia`
  sigue aplicando el filtro.
- `admin/`, `estudiante/` y `compartido/` **no cambian** (`git status` solo lista
  `paginas_docente.py`, `lib_ui.py` y los `docente/*.html`).

---

## 14. Cuarto ajuste (2026) — corrección de los 4 fallos reportados + auditoría

> Solo rol Docente. Todo se aplicó en `prototype/paginas_docente.py` y se regeneró con
> `python generar.py --rol docente`; `prototype/index.html`, `lib_*`, `admin/`,
> `estudiante/` y `compartido/` quedan **byte-idénticos**.

**Fallos reportados y su causa raíz**

1. **Pestañas con altura excesiva.** El contenedor `.pest` era hijo de un `.grid` y se
   estiraba a la altura de la columna vecina. Se añadió
   `.grid > .tabs, .grid > .pest { align-self: start; margin-bottom: 0 }`; medido a
   1442/1282/1026/914 px: `.pest` 39 px y botones 38 px.
2. **Pestañas anidadas en blanco.** El kit JS conmuta *todos* los `[data-panel-nombre]`
   de la página, así que las pestañas internas (selector de estudiante y expediente)
   ocultaban también los paneles externos. Las pestañas internas usan ahora un contrato
   propio (`data-tabs-local`, `data-tab-local`, `data-tab-panel`, clase `.pest`) que solo
   conmuta los paneles hermanos de su barra. El panel externo *Tabla* permanece visible y
   el contenido interno se renderiza (666 px).
3. **Paginación falsa.** `paginas()` solo movía la etiqueta *Mostrando X a Y*; las tablas
   tenían 6 filas y prometían 24 registros. Se extendieron los datos a sus totales reales
   (`TAREAS_DOC` 23, `ASESORIAS` 24, `DIAGNOSTICOS` 15) y se añadió un controlador de
   tablas propio del rol (`[data-pag-doc]`, `[data-filtro='1']`, `[data-diag-emp]`,
   `[data-resultados]`, `[data-vacio]`) que corta filas de verdad, recalcula páginas,
   vuelve a la página 1 al filtrar o buscar y convive con el filtro del kit. El paginador
   se movió dentro de la tarjeta de la tabla (parámetro `pag` de `_tabla_con_titulo`).
   Resultado: Tareas 23 filas/5 páginas, Asesorías 24/4, Diagnóstico 15/3.
4. **Diagnóstico y expediente estáticos.** Ambos mostraban siempre *Sabor y Sabe*.

**Diagnóstico (reestructurado, no clonado de Tareas).** Una sola zona con buscador y
filtros *Emprendimiento · Estudiante · Proyecto / grupo · Origen · Estado* + contador
(conserva los cuatro datos previos). Debajo, un bloque de contexto por emprendimiento
(`data-diag-contexto`, solo uno visible): KPIs, *Avance por fases*, *Comportamiento
entrepreneurial*, *Historial de diagnósticos* y *Datos del emprendimiento*; más un bloque
agregado *Todos* con promedios y la cartera completa. Al cambiar de emprendimiento se
actualizan KPIs, gráficas, historial, datos y la tabla; el filtro *Proyecto / grupo* se
reconstruye con el grupo del emprendimiento elegido (o los 5 en *Todos*).

**Expediente por emprendimiento.** `emprendimiento-expediente.html` pre-renderiza cinco
`<section data-exp-perfil>` y muestra la que indica `?emp=<slug>` (título de pestaña,
`h1` y miga incluidos); un slug inválido cae en el primero. Los 19 enlaces de
*Emprendimientos asignados* y de la tabla llevan ya su `?emp=`. Limitación conocida del
prototipo: las vistas de detalle por fila (avance, tarea, asesoría, diagnóstico) siguen
siendo genéricas y no reciben el emprendimiento.

**Notificaciones.** *Marcar como leída* tiene estado real: `.leida` en el aviso, botón
deshabilitado con texto *Leída*, descuento del contador y un solo toast. *Marcar todo*
pide confirmación y deja los 6 avisos leídos y el contador en 0.

**Doble toast.** El manejador del rol corre en fase de captura y el kit volvía a procesar
el mismo clic. Ahora cada acción resuelta por el docente hace `stopPropagation()` (también
los botones del diálogo); `descargar-pdf` y `actualizar-contrasena` se dejan al kit a
propósito para conservar la descarga real y la validación de contraseña.

**Verificación.** 23 pantallas regeneradas, consola limpia (0 errores y 0 avisos), sin IDs
duplicados, enlaces internos correctos salvo el `evento-form.html` preexistente que emite
`lib_js`. Comprobado en navegador: paginación y filtros de las tres tablas, los 5
emprendimientos + *Todos* en Diagnóstico, los 5 `?emp=` (y el fallback), notificaciones y
un único toast por acción. `git diff --exit-code -- prototype/index.html` pasa.

**Deuda preexistente no tocada:** el dashboard anuncia 8 emprendimientos (la cartera tiene
5) y 9 tareas por revisar (la tabla lista 23).


## 15. Quinto ajuste (2026) — Inicio del docente con vista previa y datos reales

**Alcance.** Solo el rol docente. No se tocó `lib_ui.py`, `lib_css.py`, `lib_js.py`,
`lib_charts.py`, ni las carpetas `admin/`, `estudiante/` o `compartido/`. Sin push ni
cambios de rama.

**Tarjetas de Inicio como enlaces con vista previa.** Las cuatro tarjetas de
`dashboard()` dejaron de ser `metricas()` estáticas y ahora se construyen con un helper
local `_metrica_enlace()`, apoyado en las clases que ya traía el kit
(`.card.metrica.metrica-enlace` y `.mini-prev`). Al pasar el cursor —o al enfocar con el
teclado— aparece una mini vista previa con el contenido de la vista de destino y, al hacer
clic, se abre esa vista:

| Tarjeta | Valor | Destino | Vista previa |
|---|---|---|---|
| Emprendimientos asignados | 5 | `emprendimientos.html` | Avance de los tres primeros + cartera + con evidencia |
| Asesorías del mes | 13 | `asesorias.html` | 6 agendadas · 4 por agendar · 3 completadas · próxima asesoría |
| Tareas por revisar | 6 | `tareas.html?f=En+revision` | 5 alta · 1 media · primera tarea en revisión |
| Avances registrados | 15 | `emprendimientos.html` | 10 con evidencia · 5 sin · último avance |

Las cifras y las barras se calculan desde `ASIGNADOS`, `ASESORIAS`, `TAREAS_DOC` y
`AVANCES_EMP` (antes eran `8 / 14 / 9 / 23` escritas a mano). Se agregó un chevron visible
`.metrica-flecha` que se rellena y se desplaza 2 px en hover/foco, y una nota inferior
`.metrica-nota`; ambos son CSS local del rol (`DOCENTE_CSS`). El enlace conserva un
`aria-label` fijo y la preview va con `aria-hidden="true"`, de modo que el nombre accesible
no cambia al mostrarse. `prefers-reduced-motion` desactiva la transición del chevron.

**Coherencia del resto de Inicio.**

- *Carga semanal*: 7 alta + 11 media + 5 baja = 23 (antes 9 + 14 + 5 = 28). De paso se
  corrigió la etiqueta duplicada que generaba `stacked_tareas` («Prioridad prioridad alta»)
  pasando las prioridades en minúscula.
- *Próximas asesorías*: Hoy (Sabor y Sabe, 10:00) + las dos siguientes de `ASESORIAS`
  (14 nov Krea 15:30 y 18 nov Krea 09:00). Antes la tercera fila decía 22 nov con los
  datos de Krea, que en realidad es el 14.
- *Calendario*: las asesorías del mes ya no se escriben a mano. `dashboard()` completa el
  calendario desde `ASESORIAS` (desde el 12, el «hoy» del prototipo, sin duplicar las que
  ya estaban): aparecen 14, 18, 19, 20, 21, 22, 25 y 26; el 22 quedó como Sabor y Sabe
  10:00, modalidad mixta y por confirmar; el 26 suma la asesoría de EcoPack a las 08:00
  junto al evento de empleabilidad. Los eventos y tareas propios siguen en
  `COMPROMISOS_DIA` (se quitó de allí el 22, que era el dato equivocado).
- *Actividad reciente*: la calificación de 92 pasa a Sabor y Sabe (es su avance del 12 nov;
  Krea no tiene 92) y EcoPack pasa a «Confirmaste la asesoría del 26 de noviembre», porque
  la del 20 sigue pendiente.

**Verificación.** `python generar.py --rol docente` (23 pantallas) y
`git diff --exit-code -- prototype/index.html` sin cambios. En navegador, a 1440, 1280,
1024, 768 y 375 px: 4/4/2/2/1 columnas, preview visible en hover y en foco de teclado,
`z-index:40`, sin recortes ni scroll horizontal, chevron en azul al pasar el cursor y
consola limpia. Clic en *Tareas por revisar* abre `tareas.html?f=En+revision` con el filtro
aplicado y «6 resultados»; *Emprendimientos* muestra 5; sin IDs duplicados.

## 16. Sexto ajuste (2026) — Emprendimientos y Diagnóstico con el sistema de Inicio

**Alcance.** Solo el rol docente. Se reutilizó el patrón de las tarjetas de Inicio
(`_metrica_enlace`: vista previa al pasar el cursor o enfocar con Tab, chevron visible y
clic que navega). No se tocó `lib_ui.py`, `lib_css.py`, `lib_js.py`, `lib_charts.py` ni
las carpetas `admin/`, `estudiante/` o `compartido/`. Sin push, sin commits, sin cambios
de rama.

### 16.1 Emprendimientos asignados · las 3 tarjetas filtran la tabla

Antes eran `metricas()` estáticas con barras escritas a mano (62 % y 25 %). Ahora se
calculan desde `ASIGNADOS` y `REVISION` y cada una abre la pestaña **Tabla** con el
filtro ya aplicado:

| Tarjeta | Valor · barra · nota | Destino | Resultado |
|---|---|---|---|
| Asignados | 5 · 100 % · 5 expedientes | `?vista=tabla` | 5 filas |
| Con evidencia | 3 · 60 % · 3 de 5 | `?vista=tabla&f=Con+evidencia` | 3 filas |
| Requieren atención | 2 · 40 % · 1 en revisión · 1 devuelta | `?vista=tabla&f=Requieren+atención` | 2 filas |

Las previews muestran los nombres reales: los tres primeros emprendimientos con su % de
avance, «Sabor y Sabe, EcoPack, Muebles Origen» y «Sabor y Sabe en revisión · Muebles
Origen devuelta». Se envuelven en `g-3` para que las tres queden parejas (3 columnas en
escritorio, 1 en móvil).

**Filtro nuevo «Estado de revisión»** (columna 5) con las opciones *En revisión*,
*Devuelta* y *Requieren atención*. Esta última declara `data-valores="En revision|Devuelta"`
y el motor acepta la fila cuando coincide **cualquiera** de los dos estados, algo que el
filtro anterior no podía hacer porque comparaba un solo valor.

### 16.2 Diagnóstico · 4 tarjetas por contexto (24 en total)

`_diag_kpis()` ya no devuelve `metricas()` suelto: entrega un `g-4` con cuatro enlaces.
En los 5 contextos por emprendimiento:

| Tarjeta | Destino | Vista previa |
|---|---|---|
| Fases completadas | `emprendimiento-expediente.html?emp=<slug>` | F1 a F4 con su % |
| Diagnósticos | `diagnostico-revision.html` | 3 registrados · último con fecha · puntaje |
| Tareas clave | `tareas.html?emp=<emprendimiento>` | «2 de 5 completadas · 3 pendientes» |
| Puntaje heurístico | `diagnostico-revision.html` | «7.8 de 10 · recomendación del docente» |

En el contexto agregado **Todos**: Emprendimientos y Fases · `emprendimientos.html`;
Diagnósticos · `diagnostico-revision.html`; Tareas clave · `tareas.html`. La barra de
*Diagnósticos* dejó de ser 60 fijo y ahora es 100 % («3 de 3 registrados»), coherente con
el dato real. Se corrigió además el singular («1 pendiente», antes «1 pendientes»).

### 16.3 Soporte local (todo dentro de `paginas_docente.py`)

- `?vista=tabla` activa la pestaña Tabla de Emprendimientos al cargar, para que el
  resultado filtrado sea visible (antes `?f=Con+evidencia` filtraba pero la página seguía
  en Tarjetas).
- `?emp=<emprendimiento>` preselecciona el filtro del mismo nombre. Se añadió *Filtrar
  por emprendimiento* a Tareas (columna 1) para dar destino real a «Tareas clave».
  El `?emp=` del expediente sigue funcionando: allí no hay filtros de tabla que coincidan
  con un slug.
- `_filtro()` acepta `valores={etiqueta: "A|B"}` y emite `data-valores`; `coincide()` en
  el JS del rol resuelve la coincidencia múltiple.
- `_metrica_enlace()` acepta `aria_val` opcional para que el lector de pantalla anuncie el
  dato completo («1 de 4», «7.8 de 10») cuando en pantalla número y unidad van separados.

**Fuera de alcance (sin cambios).** Los cuadros de las páginas de detalle (asesoría,
avance, tarea, revisión) siguen informativos porque describen el registro abierto, no un
resumen navegable. Eventos y Notificaciones conservan sus tarjetas estáticas.

### 16.4 Verificación

`python generar.py --rol docente` (23 pantallas) y `git diff --exit-code --
prototype/index.html` sin cambios. En navegador:

- Emprendimientos: 3/3 tarjetas con preview y foco de teclado; clic en cada una lleva a la
  pestaña Tabla con **5 / 3 / 2** resultados y los estados correctos (En revision y
  Devuelta en el caso de atención).
- Diagnóstico: 24 enlaces (6 contextos · 4), `g-4` en los 6; los 4 destinos por
  emprendimiento y los 4 de «Todos» responden.
- Clic real en «Tareas clave» de Sabor y Sabe → `tareas.html?emp=Sabor+y+Sabe` con el
  filtro aplicado y 5 filas; el expediente con `?emp=ecopack` sigue abriendo su sección.
- `?f=En+revision` (Tareas) y `?f=Agendada` (Asesorías) siguen funcionando igual.
- 1440 / 1280 / 1024 / 768 / 375 px: sin recortes, sin scroll horizontal, previews dentro
  del viewport; sin IDs duplicados y consola limpia.

## 17. Séptimo ajuste (2026) — Ortografía y textos del rol docente

**Alcance.** Solo el rol docente. Todos los cambios están en `paginas_docente.py` y en las
23 pantallas que genera; no se tocaron `lib_ui.py`, `lib_css.py`, `lib_js.py`,
`lib_charts.py` ni las carpetas `admin/`, `estudiante/` o `compartido/`. Sin push, sin
commits y sin cambios de rama.

### 17.1 Diagnóstico — título y datos

- La tarjeta que decía **«Comportamiento entrepreneurial»** ahora dice solo
  **«Comportamiento»** en los 6 contextos (Todos y los 5 emprendimientos).
- **«Puntaje heuristics» → «Puntaje heurístico»**, también en la tarjeta del expediente.
- Las filas sin fecha muestran **«Sin fecha»** en la columna Fecha en lugar de repetir
  «Pendiente» (Krea Textil, EcoPack y Aromas del Sur).

### 17.2 Tildes y nombres propios

Se acentuaron los textos visibles de las 23 pantallas: `En revisión`, `Última revisión`,
`Última actividad`, `Estado de revisión`, `Descripción del avance`, `Calificación`,
`Código`, `Observación`, `Cotización`, `Diagnóstico`, `Catálogo`, `Colección`,
`Medición`, `Duración`, `Sesión`, `Asesoría`, `Acción`, `Próximas asesorías`,
`Acciones rápidas`, `Marcar todo como leído`, `30 días después`, entre otros. También se
acentuaron los nombres **Lucía Fernández**, **Sofía Ramírez**, **Mariana López** y
**Andrés Felipe**.

**Lo que no cambió (a propósito).**

- Los valores internos siguen sin tilde: `En revision` es el dato y el contrato de
  `?f=En+revision`. La insignia y la opción del filtro muestran «En revisión» mediante
  `ESTADO_VIS` / `_estado_vis()` y `_filtro(..., etiquetas=...)`; el `value` de la opción
  queda intacto.
- Los nombres de archivo (`ficha-tecnica.docx`) y los slugs de URL
  (`capacitacion-modelado`) siguen sin tilde.
- `data-valores="En revision|Devuelta"` del filtro «Requieren atención» no se tocó.

### 17.3 Verificación

- `python -m py_compile prototype/paginas_docente.py` sin errores.
- `python generar.py --rol docente` (23 pantallas) y
  `git diff --exit-code -- prototype/index.html` sin cambios.
- Auditoría de texto visible en las 23 páginas: 0 palabras sin tilde de la lista de
  control, 0 palabras corruptas y 0 formas que convivan con y sin tilde. La única
  excepción es `capacitacion` dentro de la URL visible `…/capacitacion-modelado`.
- Navegador: `tareas.html?f=En+revision` muestra «En revisión» en la opción y 6
  resultados; `emprendimientos.html?vista=tabla&f=Con+evidencia` da 3 filas y
  `?f=Requieren+atención` da 2 filas; Diagnóstico conserva 4 enlaces por contexto y las
  6 tarjetas «Comportamiento»; el expediente muestra «Última revisión», «Descripción del
  avance», «Calificación» y «Código».
- 1440 / 1280 / 1024 / 768 / 375 px en Diagnóstico, Emprendimientos, Tareas y
  Expediente: sin scroll horizontal, sin recortes de las previews y consola limpia.
