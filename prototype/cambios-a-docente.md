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
