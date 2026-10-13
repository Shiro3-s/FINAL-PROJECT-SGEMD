# Rol Docente — Refactor UX/UI (SGEMD)

Documentación de los cambios aplicados al **Rol Docente** del prototipo SGEMD:
qué se refactorizó, qué componentes nuevos existen, cuál es el flujo actualizado y
qué consideraciones técnicas hay que tener en cuenta antes de regenerar.

- **Alcance:** las 12 pantallas de `prototype/docente/`. No se tocaron `admin/`,
  `estudiante/`, `compartido/` ni las librerías `lib_*`.
- **Origen de los cambios:** portados al generador `prototype/paginas_docente.py`
  (ver sección *Consideraciones técnicas*), luego regenerados con `generar.py`.

---

## 1. Inventario de pantallas

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

---

## 2. Mejoras transversales

1. **Filtros funcionales.** Los `<select class="filtro">` ahora filtran de verdad:
   cada zona filtrable lleva `<div data-tabla-zona>` alrededor de `toolbar` +
   tabla, los selects llevan `data-filtro` + `data-filtro-col`, el option "Todos…"
   tiene `value=""` y existe un `<span data-resultados aria-live="polite">` con el
   contador (p. ej. "2 resultados").
2. **Acciones reales** en lugar de toasts sueltos: calificar y asignar tarea abren
   modal; confirmar/reprogramar asesoría abren modal; devolver tarea y marcar todo
   como leído piden confirmación; registrar avance navega a `seguimiento-notas.html`.
3. **Jerarquía y navegación:** tabs en Expediente (Avances · Tareas · Asesorías ·
   Diagnóstico · Comentarios) y en Emprendimientos (Tarjetas / Tabla); tarjeta de
   acciones rápidas en el Inicio.
4. **Estados de revisión** con `badge`: Pendiente · En revisión · Calificada ·
   Devuelta.
5. **Enlaces a lista filtrada:** el tablero de seguimiento enlaza a las listas ya
   filtradas mediante query string `?f=<valor>` (ver sección 5).

---

## 3. Componentes nuevos

| Componente | Dónde | Descripción |
|---|---|---|
| Modal de calificación | Expediente, Tareas, Inicio | Puntaje (number 0–100, `required`), Resultado (Aprobada / Devuelta / En revisión) y retroalimentación (`textarea`). |
| Modal de asignación de tarea | Tareas, Inicio | Título, Emprendimiento, Prioridad, Fecha límite, Evidencia requerida e Instrucciones. |
| Modal de asesoría | Asesorías, asesoría-form | Confirmación y reprogramación: Fecha, Hora, Modalidad, Lugar + resumen. |
| Bitácora de comentarios | Expediente | Lista `.comentario` (autor · fecha · texto) + `textarea` con `placeholder` y botón `data-accion="publicar-comentario"`.
| Tabs | Expediente, Emprendimientos | Reutiliza el sistema de `lib_js` (`data-panel`, `data-panel-nombre`, `aria-selected`). |
| Contador de resultados | zonas filtrables | `<span data-resultados aria-live="polite">`. |
| Chips de notificación | Notificaciones | Filtran por tipo y exponen `aria-pressed` sincronizado. |

Clases CSS nuevas (con tokens existentes, sin hex nuevos): `.resultados-contador`,
`.comentario`, `.comentario-cab`, `.comentario-autor`, `.comentario-fecha`,
`.comentario-texto`, `.comentario-form`, `.acciones-rapidas`.

### Contrato `data-accion`

`calificar` · `asignar-tarea` · `confirmar-asesoria` · `reprogramar-asesoria` ·
`rechazar-asesoria` · `publicar-comentario` · `devolver-tarea` · `registrar-avance` ·
`confirmar-avance` · `revisar-diagnostico` · `guardar-recomendaciones` ·
`cambiar-contrasena` · `marcar-todo-leido` · `filtrar-notificacion`.

Todos se interceptan en **fase de captura** con `stopPropagation()`; lo que no es
una de estas acciones lo sigue manejando `lib_js` (por eso el botón genérico del
Inicio conserva su toast por defecto).

---

## 4. Accesibilidad

- Modales propios con `role="dialog"` + `aria-modal="true"` y foco inicial.
- `<caption class="visually-hidden">` en las tablas clave (Actividad reciente,
  Solicitudes y asesorías, Proyectos asignados, Avances y calificaciones, Avance por
  estudiante, Tareas por revisar, Pendientes de revisión).
- Chips de notificación con `aria-pressed` sincronizado al filtrar.
- `<span data-resultados aria-live="polite">` para anunciar el conteo.
- Toast con `aria-live`; controles nuevos siempre con `data-accion`, `aria-label` o
  `placeholder`.

---

## 5. Enlaces a lista filtrada (`?f=`)

El tablero de seguimiento (`seguimiento-dashboard.html`) enlaza a las listas con el
filtro ya aplicado:

| Pendiente | Enlace |
|---|---|
| Evidencias por revisar | `tareas.html?f=En+revision` |
| Avances sin calificar | `seguimiento.html?f=Sin+evidencia` |
| Asesorías por confirmar | `asesorias.html?f=Pendiente+de+confirmar` |

El JS del rol lee `location.search`, busca el primer `select[data-filtro]` que tenga
una opción con ese valor y dispara un `change`, que `lib_js` ya escucha. Funciona en
`file://` y no requiere tocar las librerías.

---

## 6. Flujo de usuario docente

Inicio (panorama + accesos) → Asesorías (confirmar/reprogramar; **BR-002**: el
estudiante no agenda solo) → Emprendimientos (Tarjetas/Tabla con estado de revisión)
→ Expediente (pestañas + bitácora de comentarios + calificar) → Seguimiento (avance y
calificación con puntaje/retroalimentación) → Diagnóstico (recomendaciones) → Tareas
(asignar y calificar con evidencia) → Perfil / Notificaciones.

---

## 7. Consideraciones técnicas

- **Generador, no HTML directo.** A diferencia del plan original (editar el HTML a
  mano), los cambios se portaron a `prototype/paginas_docente.py` y se regeneraron
  con `python generar.py`. Ventaja: no hay deuda de desincronización; correr el
  generador **no** pierde los cambios. Es la única vía que mantiene `admin/`,
  `estudiante/` y `compartido/` byte-idénticos.
- **Bundle autocontenido.** Cada `.html` es un documento independiente (restricción
  de Stitch), así que el CSS/JS docente se repite en los 12 archivos. El helper
  `_inyectar()` añade `<style>` (etiqueta plana, fuera del presupuesto inline) y
  `<script>` antes de `</body>`.
- **Aislamiento.** No se modifican `lib_js.py`, `lib_css.py`, `lib_ui.py` ni
  `lib_charts.py`. El modal/`toast`/`confirmar` propios reconstruyen las clases
  públicas (`.modal-velo`, `.modal`, `.campo`, `.btn`, …).
- **Sin backend.** Persistencia simulada en `localStorage` (`sgemd:v1:<ruta>`). No
  se introducen dependencias externas.
- **`_fid` = 20** en docente: los campos de id fijo (`com-obs`, `rev-estado`) usan
  helpers `_campo_libre`/`_select_libre` que no consumen el contador global de ids.

### Verificación

- `python _auditar.py` → **0**.
- `python _estructura.py` → **0** (inline 613/699, 47 anchos fijos).
- `python _check_tipografia.py` → **0**.
- **Manual con Chrome DevTools** (`file://`): errores de consola en las 12 pantallas
  → **0**; barrido responsive 1440/768/375 px sin desbordes; funcionalidad de
  filtros, modales, tabs, confirmaciones y enlaces `?f=` comprobada.
- **Pendiente:** `python _interaccion.py` no se ejecutó (requiere Playwright, no
  instalado en el entorno). La cobertura se cubrió de forma manual con Chrome.
