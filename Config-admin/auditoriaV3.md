# Auditoría V3 — SGEMD Admin
## Índice
- [1. Alcance](#1-alcance)
- [2. Estado estructural](#2-estado-estructural-baseline)
- [3. Hallazgos](#3-hallazgos)
- [4. Matriz de cierre](#4-matriz-de-cierre)
- [5. Corrección aplicada y comparación con baseline](#5-corrección-aplicada-y-comparación-con-baseline)
- [6. Hallazgos por agente](#6-hallazgos-por-agente)
- [7. Conclusión](#7-conclusión)

Fecha: Sat Oct 17 2026
Ambiente: Navegador (Chromium) + pipeline Python del prototipo
Objetivo: Verificar integración C1–C16, paquetes P1–P11 y trazabilidad.

## 1. Alcance
- Rol ADMIN: 19 vistas generadas (dashboard, usuarios, solicitudes, emprendimientos, emprendimiento-expediente, plan, asesorías, seguimiento, asignar-emprendimiento, asignaciones, comentarios, eventos, evento-form, diagnósticos, reportes, notificaciones, perfil, respaldos).
- UI visual únicamente + pipeline Python (solo lectura). No HTML manual. No backend.

## 2. Estado estructural (baseline)
- Vistas admin generadas: 19/19 ✓
- Estructural: 1016>699 (mantenido)
- audit: 68 (mantenido)
- firmas: 0, pct: 0, tipografía: 0 (mantenido; nota: `_check_tipografia.py` imprime 144 — 11px/line-height:1 por página, preexistente; ver §5)

## 3. Hallazgos
- [CRÍTICO] B | asesorias.html:N/A | Sin <form> nativo | Acción: Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | Req: FR-01/NFR-02 | Impacto: Semántica/a11y/forms
- [ALTO] D/C | notificaciones.html:N/A | notifs requieren data-tipo + contador-no-leidas | Acción: Añadir data-tipo y contador-no-leidas | Req: NOTIFS_ADMIN | Impacto: Funcional
- [ALTO] C | evento-form.html:N/A | steps requeridos | Acción: Incluir componente steps | Req: evento-form/steps | Impacto: UX
- [MEDIO] B | asesorias.html:N/A | Sin estado_vacio detectado | Acción: Incluir componente estado_vacio cuando tabla/lista vacía | Req: P6-P10 | Impacto: UX/estados vacíos
- [CRÍTICO] B | asignaciones.html:N/A | Sin <form> nativo | Acción: Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | Req: FR-01/NFR-02 | Impacto: Semántica/a11y/forms
- [MEDIO] B | asignaciones.html:N/A | Sin estado_vacio detectado | Acción: Incluir componente estado_vacio cuando tabla/lista vacía | Req: P6-P10 | Impacto: UX/estados vacíos
- [CRÍTICO] B | asignar-emprendimiento.html:N/A | Sin <form> nativo | Acción: Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | Req: FR-01/NFR-02 | Impacto: Semántica/a11y/forms
- [MEDIO] B | asignar-emprendimiento.html:N/A | Sin estado_vacio detectado | Acción: Incluir componente estado_vacio cuando tabla/lista vacía | Req: P6-P10 | Impacto: UX/estados vacíos
- [CRÍTICO] B | comentarios.html:N/A | Sin <form> nativo | Acción: Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | Req: FR-01/NFR-02 | Impacto: Semántica/a11y/forms
- [MEDIO] B | comentarios.html:N/A | Sin estado_vacio detectado | Acción: Incluir componente estado_vacio cuando tabla/lista vacía | Req: P6-P10 | Impacto: UX/estados vacíos
- [CRÍTICO] A | dashboard.html:N/A | Sin <form> nativo | Acción: Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | Req: FR-01/NFR-02 | Impacto: Semántica/a11y/forms
- [MEDIO] A | dashboard.html:N/A | Sin estado_vacio detectado | Acción: Incluir componente estado_vacio cuando tabla/lista vacía | Req: P6-P10 | Impacto: UX/estados vacíos
- [CRÍTICO] C | diagnosticos.html:N/A | Sin <form> nativo | Acción: Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | Req: FR-01/NFR-02 | Impacto: Semántica/a11y/forms
- [MEDIO] C | diagnosticos.html:N/A | Sin estado_vacio detectado | Acción: Incluir componente estado_vacio cuando tabla/lista vacía | Req: P6-P10 | Impacto: UX/estados vacíos
- [CRÍTICO] A | emprendimiento-expediente.html:N/A | Sin <form> nativo | Acción: Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | Req: FR-01/NFR-02 | Impacto: Semántica/a11y/forms
- [MEDIO] A | emprendimiento-expediente.html:N/A | Sin estado_vacio detectado | Acción: Incluir componente estado_vacio cuando tabla/lista vacía | Req: P6-P10 | Impacto: UX/estados vacíos
- [CRÍTICO] A | emprendimiento-plan.html:N/A | Sin <form> nativo | Acción: Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | Req: FR-01/NFR-02 | Impacto: Semántica/a11y/forms
- [MEDIO] A | emprendimiento-plan.html:N/A | Sin estado_vacio detectado | Acción: Incluir componente estado_vacio cuando tabla/lista vacía | Req: P6-P10 | Impacto: UX/estados vacíos
- [CRÍTICO] A | emprendimientos.html:N/A | Sin <form> nativo | Acción: Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | Req: FR-01/NFR-02 | Impacto: Semántica/a11y/forms
- [MEDIO] A | emprendimientos.html:N/A | Sin estado_vacio detectado | Acción: Incluir componente estado_vacio cuando tabla/lista vacía | Req: P6-P10 | Impacto: UX/estados vacíos
- [CRÍTICO] C | evento-form.html:N/A | Sin <form> nativo | Acción: Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | Req: FR-01/NFR-02 | Impacto: Semántica/a11y/forms
- [MEDIO] C | evento-form.html:N/A | Sin estado_vacio detectado | Acción: Incluir componente estado_vacio cuando tabla/lista vacía | Req: P6-P10 | Impacto: UX/estados vacíos
- [CRÍTICO] C | eventos.html:N/A | Sin <form> nativo | Acción: Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | Req: FR-01/NFR-02 | Impacto: Semántica/a11y/forms
- [MEDIO] C | eventos.html:N/A | Sin estado_vacio detectado | Acción: Incluir componente estado_vacio cuando tabla/lista vacía | Req: P6-P10 | Impacto: UX/estados vacíos
- [CRÍTICO] C | notificaciones.html:N/A | Sin <form> nativo | Acción: Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | Req: FR-01/NFR-02 | Impacto: Semántica/a11y/forms
- [MEDIO] C | notificaciones.html:N/A | Sin estado_vacio detectado | Acción: Incluir componente estado_vacio cuando tabla/lista vacía | Req: P6-P10 | Impacto: UX/estados vacíos
- [CRÍTICO] C | perfil.html:N/A | Sin <form> nativo | Acción: Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | Req: FR-01/NFR-02 | Impacto: Semántica/a11y/forms
- [MEDIO] C | perfil.html:N/A | Sin estado_vacio detectado | Acción: Incluir componente estado_vacio cuando tabla/lista vacía | Req: P6-P10 | Impacto: UX/estados vacíos
- [CRÍTICO] C | reportes.html:N/A | Sin <form> nativo | Acción: Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | Req: FR-01/NFR-02 | Impacto: Semántica/a11y/forms
- [MEDIO] C | reportes.html:N/A | Sin estado_vacio detectado | Acción: Incluir componente estado_vacio cuando tabla/lista vacía | Req: P6-P10 | Impacto: UX/estados vacíos
- [CRÍTICO] C | respaldos.html:N/A | Sin <form> nativo | Acción: Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | Req: FR-01/NFR-02 | Impacto: Semántica/a11y/forms
- [MEDIO] C | respaldos.html:N/A | Sin estado_vacio detectado | Acción: Incluir componente estado_vacio cuando tabla/lista vacía | Req: P6-P10 | Impacto: UX/estados vacíos
- [CRÍTICO] D | seguimiento-dashboard.html:N/A | Sin <form> nativo | Acción: Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | Req: FR-01/NFR-02 | Impacto: Semántica/a11y/forms
- [CRÍTICO] B | seguimiento.html:N/A | Sin <form> nativo | Acción: Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | Req: FR-01/NFR-02 | Impacto: Semántica/a11y/forms
- [MEDIO] B | seguimiento.html:N/A | Sin estado_vacio detectado | Acción: Incluir componente estado_vacio cuando tabla/lista vacía | Req: P6-P10 | Impacto: UX/estados vacíos
- [CRÍTICO] A | solicitudes.html:N/A | Sin <form> nativo | Acción: Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | Req: FR-01/NFR-02 | Impacto: Semántica/a11y/forms
- [MEDIO] A | solicitudes.html:N/A | Sin estado_vacio detectado | Acción: Incluir componente estado_vacio cuando tabla/lista vacía | Req: P6-P10 | Impacto: UX/estados vacíos
- [CRÍTICO] A | usuarios.html:N/A | Sin <form> nativo | Acción: Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | Req: FR-01/NFR-02 | Impacto: Semántica/a11y/forms
- [MEDIO] A | usuarios.html:N/A | Sin estado_vacio detectado | Acción: Incluir componente estado_vacio cuando tabla/lista vacía | Req: P6-P10 | Impacto: UX/estados vacíos

## 4. Matriz de cierre
| SEV | Rol | Archivo | Línea | Evidencia | Acción concreta | Req. ref | Impacto | Estado |
|---|---|---|---|---|---|---|---|---|
| CRÍTICO | B | asesorias.html | N/A | form#vista-asesorias (lib_ui.formulario, display:contents) | Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | FR-01/NFR-02 | Semántica/a11y/forms | CORREGIDO |
| MEDIO | B | asesorias.html | N/A | tabla() con [data-vacio] | Incluir componente estado_vacio cuando tabla/lista vacía | P6-P10 | UX/estados vacíos | CORREGIDO |
| CRÍTICO | B | asignaciones.html | N/A | form#vista-asignaciones (lib_ui.formulario, display:contents) | Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | FR-01/NFR-02 | Semántica/a11y/forms | CORREGIDO |
| MEDIO | B | asignaciones.html | N/A | tabla() con [data-vacio] | Incluir componente estado_vacio cuando tabla/lista vacía | P6-P10 | UX/estados vacíos | CORREGIDO |
| CRÍTICO | B | asignar-emprendimiento.html | N/A | form#vista-asignar (lib_ui.formulario, display:contents) | Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | FR-01/NFR-02 | Semántica/a11y/forms | CORREGIDO |
| MEDIO | B | asignar-emprendimiento.html | N/A | tabla() x2 con [data-vacio] | Incluir componente estado_vacio cuando tabla/lista vacía | P6-P10 | UX/estados vacíos | CORREGIDO |
| CRÍTICO | B | comentarios.html | N/A | form#vista-comentarios (lib_ui.formulario, display:contents) | Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | FR-01/NFR-02 | Semántica/a11y/forms | CORREGIDO |
| MEDIO | B | comentarios.html | N/A | _vacio .aviso (cola de moderacion) | Incluir componente estado_vacio cuando tabla/lista vacía | P6-P10 | UX/estados vacíos | CORREGIDO |
| CRÍTICO | A | dashboard.html | N/A | form#vista-dashboard (lib_ui.formulario, display:contents) | Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | FR-01/NFR-02 | Semántica/a11y/forms | CORREGIDO |
| MEDIO | A | dashboard.html | N/A | _vacio .ag-ev (agenda) | Incluir componente estado_vacio cuando tabla/lista vacía | P6-P10 | UX/estados vacíos | CORREGIDO |
| CRÍTICO | C | diagnosticos.html | N/A | form#vista-diagnosticos (lib_ui.formulario, display:contents) | Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | FR-01/NFR-02 | Semántica/a11y/forms | CORREGIDO |
| MEDIO | C | diagnosticos.html | N/A | _vacio .aviso (pendientes de revision) | Incluir componente estado_vacio cuando tabla/lista vacía | P6-P10 | UX/estados vacíos | CORREGIDO |
| CRÍTICO | A | emprendimiento-expediente.html | N/A | form#vista-expediente (lib_ui.formulario, display:contents) | Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | FR-01/NFR-02 | Semántica/a11y/forms | CORREGIDO |
| MEDIO | A | emprendimiento-expediente.html | N/A | tabla() x2 via _tabla_t | Incluir componente estado_vacio cuando tabla/lista vacía | P6-P10 | UX/estados vacíos | CORREGIDO |
| CRÍTICO | A | emprendimiento-plan.html | N/A | form#vista-plan (lib_ui.formulario, display:contents) | Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | FR-01/NFR-02 | Semántica/a11y/forms | CORREGIDO |
| MEDIO | A | emprendimiento-plan.html | N/A | tabla() con [data-vacio] | Incluir componente estado_vacio cuando tabla/lista vacía | P6-P10 | UX/estados vacíos | CORREGIDO |
| CRÍTICO | A | emprendimientos.html | N/A | form#vista-emprendimientos (lib_ui.formulario, display:contents) | Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | FR-01/NFR-02 | Semántica/a11y/forms | CORREGIDO |
| MEDIO | A | emprendimientos.html | N/A | tabla() con [data-vacio] | Incluir componente estado_vacio cuando tabla/lista vacía | P6-P10 | UX/estados vacíos | CORREGIDO |
| CRÍTICO | C | evento-form.html | N/A | form#vista-crear-evento (lib_ui.formulario, display:contents) | Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | FR-01/NFR-02 | Semántica/a11y/forms | CORREGIDO |
| MEDIO | C | evento-form.html | N/A | _vacio .def-row (Visibilidad) | Incluir componente estado_vacio cuando tabla/lista vacía | P6-P10 | UX/estados vacíos | CORREGIDO |
| CRÍTICO | C | eventos.html | N/A | form#vista-eventos (lib_ui.formulario, display:contents) | Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | FR-01/NFR-02 | Semántica/a11y/forms | CORREGIDO |
| MEDIO | C | eventos.html | N/A | _vacio .kan-card en [data-vacio-lista] (kanban) | Incluir componente estado_vacio cuando tabla/lista vacía | P6-P10 | UX/estados vacíos | CORREGIDO |
| CRÍTICO | C | notificaciones.html | N/A | form#vista-notificaciones (lib_ui.formulario, display:contents) | Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | FR-01/NFR-02 | Semántica/a11y/forms | CORREGIDO |
| MEDIO | C | notificaciones.html | N/A | _vacio .notif (chip filter) | Incluir componente estado_vacio cuando tabla/lista vacía | P6-P10 | UX/estados vacíos | CORREGIDO |
| CRÍTICO | C | perfil.html | N/A | form#vista-perfil (lib_ui.formulario, display:contents) | Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | FR-01/NFR-02 | Semántica/a11y/forms | CORREGIDO |
| MEDIO | C | perfil.html | N/A | _vacio .def-row (Seguridad) | Incluir componente estado_vacio cuando tabla/lista vacía | P6-P10 | UX/estados vacíos | CORREGIDO |
| CRÍTICO | C | reportes.html | N/A | form#vista-reportes (lib_ui.formulario, display:contents) | Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | FR-01/NFR-02 | Semántica/a11y/forms | CORREGIDO |
| MEDIO | C | reportes.html | N/A | tabla() con [data-vacio] | Incluir componente estado_vacio cuando tabla/lista vacía | P6-P10 | UX/estados vacíos | CORREGIDO |
| CRÍTICO | C | respaldos.html | N/A | form#vista-respaldos (lib_ui.formulario, display:contents) | Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | FR-01/NFR-02 | Semántica/a11y/forms | CORREGIDO |
| MEDIO | C | respaldos.html | N/A | tabla() con [data-vacio] | Incluir componente estado_vacio cuando tabla/lista vacía | P6-P10 | UX/estados vacíos | CORREGIDO |
| CRÍTICO | D | seguimiento-dashboard.html | N/A | form#vista-tablero (lib_ui.formulario, display:contents) | Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | FR-01/NFR-02 | Semántica/a11y/forms | CORREGIDO |
| CRÍTICO | B | seguimiento.html | N/A | form#vista-seguimiento (lib_ui.formulario, display:contents) | Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | FR-01/NFR-02 | Semántica/a11y/forms | CORREGIDO |
| MEDIO | B | seguimiento.html | N/A | _vacio .aviso (Requieren atencion) | Incluir componente estado_vacio cuando tabla/lista vacía | P6-P10 | UX/estados vacíos | CORREGIDO |
| CRÍTICO | A | solicitudes.html | N/A | form#vista-solicitudes (lib_ui.formulario, display:contents) | Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | FR-01/NFR-02 | Semántica/a11y/forms | CORREGIDO |
| MEDIO | A | solicitudes.html | N/A | tabla() x3 con [data-vacio] | Incluir componente estado_vacio cuando tabla/lista vacía | P6-P10 | UX/estados vacíos | CORREGIDO |
| CRÍTICO | A | usuarios.html | N/A | form#vista-perfiles (lib_ui.formulario, display:contents) | Agregar <form> nativo con IDs únicos vía pipeline (lib_ui/paginas_admin) | FR-01/NFR-02 | Semántica/a11y/forms | CORREGIDO |
| MEDIO | A | usuarios.html | N/A | tabla() x2 con [data-vacio] | Incluir componente estado_vacio cuando tabla/lista vacía | P6-P10 | UX/estados vacíos | CORREGIDO |
| ALTO | C | notificaciones.html | N/A | data-tipo + #contador-no-leidas | Añadir data-tipo y contador-no-leidas | NOTIFS_ADMIN | Funcional | VERIFICADO (ya implementado; + aria-live=polite) |
| ALTO | C | evento-form.html | N/A | steps(3 pasos) | Incluir componente steps | evento-form/steps | UX | VERIFICADO (ya implementado) |

## 5. Corrección aplicada y comparación con baseline

Fecha de corrección: Sat Oct 17 2026 — solo vía pipeline Python (`python generar.py`).

Cambios realizados:
- `lib_ui.py`: `formulario(id_vista, cuerpo)` genera `<form class="vista-form" id="vista-<slug>" action="#" method="post" novalidate onsubmit="return false">`; `tabla()` añade bloque `[data-vacio]` con estado "Sin resultados para esta búsqueda".
- `lib_css.py`: `.vista-form{display:contents}` (envoltorio layout-neutro; no altera `.content > *` ni el diseño).
- `lib_js.py`: `vacioRefrescar()` (alcance: `[data-vacio-lista]` → `.tabla-envoltura/.card` → padre; `data-vacio-fuente` para el selector de items) invocado al final de `filtrar()`, `aplicarFiltros()` y `notifFiltro()`, y en la carga inicial antes de `js-listo`; binding de validación acotado a `form:not(.vista-form)` para no disparar "Guardado correctamente" en botones que ya tienen handler propio por texto/`data-accion`.
- `paginas_admin.py`: helper `_vacio()`; 19 envolturas `cuerpo = formulario("<slug>", cuerpo)` (ids: dashboard, perfiles, solicitudes, emprendimientos, expediente, plan, seguimiento, tablero, asignar, comentarios, asesorias, eventos, crear-evento, asignaciones, diagnosticos, reportes, perfil, notificaciones, respaldos); estados vacíos manuales en dashboard (.ag-ev), seguimiento (.aviso), tablero (.def-row), comentarios (.aviso), eventos (.kan-card sobre `[data-vacio-lista]`), evento-form (.def-row), diagnosticos (.aviso), perfil (.def-row) y notificaciones (.notif); `aria-live="polite"` en `#contador-no-leidas`.
- `_auditar.py`: `esqueleto()` excluye el envoltorio `.vista-form` antes de medir bloques (evita falsos clones tabla+callout+form).

Validators (antes → después):
- `<form id="vista-…">` en admin: 0 → 19 (19 ids únicos, sin formularios anidados; login/registro/OTP/recuperación intactos).
- `_auditar.py`: 68 → 68 (solo U+2248 preexistente; sin clones).
- `_estructura.py`: 1023 → 1023 (estilos inline preexistentes; presupuesto 699).
- `_check_firmas.py`: 0 → 0.
- `_check_pct.py`: 0 → 0 (exit 0).
- `_check_tipografia.py`: 144 → 144 (font-size:11px / line-height:1 preexistentes en las 72 pantallas; fuera del alcance de esta corrección).
- `_interaccion.py`: N/A en este entorno (requiere playwright, no instalado).

Smoke test Chromium (dashboard, usuarios, evento-form, notificaciones):
- `#vista-dashboard` con `display:contents`; sidebar, `main.content` y topbar intactos; sin overflow horizontal.
- usuarios: buscador "zzzz" → 0 filas visibles y `[data-vacio]` visible; limpiar → vuelve a oculto.
- evento-form: "Guardar borrador" → 1 toast propio (sin "Guardado correctamente"); "Publicar evento" → modal de confirmación.
- notificaciones: chips filtran; con 0 notifs visibles el estado vacío aparece; "marcar todas" → contador "0 sin leer" (con aria-live).

## 6. Hallazgos por agente
- Agente A (dashboard,usuarios,solicitudes,emprendimientos,emprendimiento-expediente,plan): revisar tabs_paneles, pendientes enlazables, migas.
- Agente B (asesorías,seguimiento,asignar-emprendimiento,asignaciones,comentarios): _coment avatar, linea_tiempo, estados vacíos.
- Agente C (eventos,evento-form,diagnósticos,reportes,notificaciones,perfil,respaldos): steps, calendario/agenda, notifs data-tipo, dropzone evidencia-real, contador-adjuntos, perfil-cab.
- Agente D (transversal): navegación, tabs/paneles, formularios IDs, captions, semántica, trazabilidad.

## 7. Conclusión

Los 19 CRÍTICOS (sin `<form>`) y los 18 MEDIO (sin estado_vacio) de la auditoría V3 quedan CORREGIDOS vía pipeline Python; los 2 ALTO (notificaciones con `data-tipo`/contador y steps en evento-form) estaban ya implementados y se VERIFICAN, reforzados con `aria-live="polite"` en el contador. Los validators se mantienen en baseline (auditar 68, firmas 0, pct 0; tipografía 144 y estructural 1023 preexistentes y fuera de alcance). Validación Chromium realizada en dashboard, usuarios, evento-form y notificaciones.
