# Auditoría V2 — vistas del prototipo SGEMD

Segunda pasada de auditoría (solo lectura, análisis estático) sobre el HTML generado
(`prototype/{compartido,estudiante,docente,admin}/*.html`) y el código Python que lo produce.
Objetivo: detectar vistas **faltantes**, **redireccionamientos mal cableados** y **problemas de
diseño/correlación**, tras cerrar la Etapa 2 (correlación Estudiante↔Admin).

## Leyenda

- **Sev**: 🔴 bloqueante · 🟠 mayor · 🟡 menor.
- **Tipo**: `Faltante` (no existe la acción/vista) · `Redirect` (existe pero apunta/muestra algo
  equivocado) · `Diseño` (correlación, tokens, a11y, consistencia).
- **Fuente**: `Est` = subagente Estudiante · `Adm` = subagente Admin · `Trv` = subagente
  Transversal · `Doc` = subagente Docente (baseline, rol intocable).

Datos globales: **52 páginas** (compartido 4, estudiante 20, docente 12, admin 16), **0 enlaces HTML
rotos**, `index.html` con 52 enlaces válidos, dispatcher `lib_js.py` con **58 `case`** (35
alcanzables, 23 muertos).

---

## 1. Estudiante (patrón de referencia)

| ID | Sev | Vista | Tipo | Descripción | Evidencia |
|----|-----|-------|------|-------------|-----------|
| E001 | 🔴 | diagnostico-resultados.html | Redirect | Botón **"Volver a responder"** sin `href` ni `data-accion`: no navega ni ejecuta nada. | `paginas_estudiante.py` (bloque resultados) |
| E002 | 🟠 | emprendimiento-detalle.html | Diseño | Breadcrumbs no enlazables (texto plano, no `<a>`) → rompe el patrón del resto de vistas. | `paginas_estudiante.py` |
| E003 | 🟡 | (global estudiante) | Diseño | Pestañas sin uso (`tabs()` sin cablear) donde otras vistas usan `tabs_paneles()`. | `lib_ui.py:512` |
| E004 | 🟡 | (global estudiante) | Diseño | Botones de estado sin `aria-pressed` consistente entre vistas. | varias |
| E005 | 🟡 | (global estudiante) | Diseño | Avisos por texto cuando existía `data-accion` disponible en el mismo grupo. | varias |

> Nota: el informe del subagente Estudiante llegó parcial (E001–E005 son los confirmados). El
> bloque principal de hallazgos estudiante quedó truncado en la entrega.

---

## 2. Administrador (35 hallazgos)

| ID | Sev | Vista | Tipo | Descripción | Evidencia |
|----|-----|-------|------|-------------|-----------|
| A01 | 🔴 | usuarios.html | Faltante | No existe acción **crear usuario** pese a que el subtítulo promete "Altas, edición y estado de acceso". Solo hay botones de edición por fila. | `paginas_admin.py:189-201`; subtítulo `:206` |
| A02 | 🔴 | usuarios.html | Faltante | El callout dice que el admin "puede **activar o desactivar** el acceso" y hay columna Estado, pero **no hay control** para cambiarlo; en los formularios el Estado es solo lectura. | callout `:180-181`; badges `:176,197`; estado read-only `:232-237`, `:266-271` |
| A03 | 🔴 | eventos.html | Redirect | Botón **"Aprobar"** de un evento pendiente navega a `evento-form.html` (formulario de *creación*), no ejecuta aprobación. Igual "Editar"/"Ver". | `:633-634`, `:640,647,652,659` |
| A04 | 🔴 | emprendimientos.html | Faltante | No existe **aprobación de emprendimientos/solicitudes** (el docstring dice "Aprueba solicitudes"): solo `Abrir plan` y `Editar`; sin cola de solicitudes. | `:300`; docstring `:5` |
| A05 | 🟠 | usuarios.html, emprendimientos.html | Faltante | **Filtros `select.filtro`** (área, sector, etapa, docente) **no cableados**: `_sel` no emite `data-filtro`; el JS solo escucha `select[data-filtro]`. | `_sel` `:91-93`; bind `lib_js.py:287` |
| A06 | 🟠 | emprendimientos.html | Redirect | **"Abrir plan"** es `boton_accion("eye",…)` → `data-accion="ver"` → modal genérico en vez de navegar a `emprendimiento-plan.html`. | `:300`; `lib_ui.py:149`; `lib_js.py:555` |
| A07 | 🟠 | emprendimientos.html | Redirect | **"Editar"** usa `boton_accion("edit",…)` → `abrirEditor` genérico (un solo campo), no un formulario real. | `:300`; `lib_ui.py:150`; `lib_js.py:606-612` |
| A08 | 🟠 | asesorias.html | Faltante | Solo **métricas/gráficos**: no hay listado ni CRUD de asesorías del admin (a diferencia del docente). | `:584-615` |
| A09 | 🟠 | (global admin) | Faltante | No existe vista ni acción de **respaldos/backups**. | sin coincidencias en `admin\*.html`; comentario CSS `lib_css.py:124` |
| A10 | 🟠 | (global admin) | Faltante | No existe **expediente del emprendimiento** en admin (sí en docente). | ausencia en `admin\*.html`; equivalente `docente/emprendimiento-expediente.html` |
| A11 | 🟠 | perfil.html | Faltante | **"Cambiar contraseña"** sin `data-accion` ni campos de contraseña; cae al toast por defecto. Caso `actualizar-contrasena` inalcanzable. | botón `:904`; caso `lib_js.py:767-795` |
| A12 | 🟠 | _subidas.json (metadato) | Redirect | El manifiesto **sigue listando** `admin/usuario-docente.html` y `admin/usuario-estudiante.html`, páginas ya eliminadas. | `_subidas.json:130-145` |
| A13 | 🟠 | notificaciones.html | Faltante | La bandeja usa `agenda()`, que **no genera elementos `.notif`**; el contador de no leídas nunca actúa. "Marcar todo como leído" sin `data-accion` y slug sin caso. | `agenda` `:958`; `lib_js.py:1115,1120`; botón `:964-965`; caso `lib_js.py:883` |
| A14 | 🟠 | notificaciones.html | Diseño | **Badge de campana del topbar fijo en 3** en todas las páginas (el `shell` no recibe `notif`), mientras la vista dice "Sin leer 2". | `lib_ui.py:210,263`; métrica `:953` |
| A15 | 🟠 | comentarios.html | Redirect | Enlaces **autorreferentes**: "Moderar cola" y cada aviso apuntan a `comentarios.html` (misma página). | `:537,543,572` |
| A16 | 🟡 | diagnosticos.html | Redirect | **"Ver instrumento"** enlaza a `reportes.html` (página equivocada). | `:819` |
| A17 | 🟡 | asignar-emprendimiento.html | Faltante | **"Confirmar asignación"** / **"Cancelar"** sin `data-accion`; "Confirmar" cae al toast genérico. | `:505-508`; `lib_js.py:899-903` |
| A18 | 🟡 | asignar-emprendimiento.html | Diseño | **"Seleccionar"** usa `boton_accion("check",…)` → `data-accion="aprobar"`: el check desvía selección a aprobar. | `:482,490,493`; `lib_ui.py:156`; `lib_js.py:614` |
| A19 | 🟡 | asignaciones.html | Diseño | **"Asignar"** usa `boton_accion("edit",…)` → `data-accion="editar"` (editor genérico), desalineando rótulo e intención. | `:745`; `lib_ui.py:150` |
| A20 | 🟡 | seguimiento.html | Faltante | **"Registrar avance"** mapea a `data-accion="editar"` (modal genérico); no hay formulario real de avance en admin. | `:407`; `lib_ui.py:150`; `lib_js.py:606` |
| A21 | 🟡 | evento-form.html | Faltante | **"Publicar evento"** sin `data-accion` (solo toast); no hay transición Borrador→Publicado. `steps` estáticos. | `:705`; `steps` `:673,474` |
| A22 | 🟡 | evento-form.html, reportes.html | Redirect | Botones de cabecera **"Guardar"** y **"Generar"** (`_btn` con href por defecto) quedan `href="#"` muerto. | `_btn` `:122`; `:716`, `:871`; HTML `admin\evento-form.html:491`, `admin\reportes.html:491` |
| A23 | 🟡 | reportes.html | Faltante | **"Generar reporte"** / **"Descargar plantilla"** sin `data-accion` (toast por texto). Vista previa = modal genérico, no previsualización real. | `:862,864,833` |
| A24 | 🟡 | dashboard.html | Faltante | **"Pendientes de decisión"** es lista estática (texto+número) sin enlaces ni acciones. | `:155-160` |
| A25 | 🟡 | dashboard.html, perfil.html | Diseño | Métricas **inconsistentes**: dashboard "Eventos por aprobar 2" vs eventos "Por aprobar 1"; perfil "Decisiones pendientes 6" vs dashboard (13). | `:157` vs `:623`; `:879` |
| A26 | 🟡 | (global admin) | Diseño | El **drawer de notificaciones (campana)** muestra mensajes con voz de estudiante al administrador. | `lib_js.py:860-864` |
| A27 | 🟡 | asesorias.html, seguimiento.html, seguimiento-dashboard.html | Redirect | Acciones **"Exportar"** (icono download) **navegan a `reportes.html`** en vez de exportar. | `:615,425-426,469` |
| A28 | 🟡 | usuarios.html | Faltante | Sin acción **eliminar/deshabilitar usuario** ni "Nuevo usuario" (CRUD incompleto). | `:191-201` |
| A29 | 🟡 | lib_ui.py (clase CSS) | Diseño | `_acc()` emite `<div class="acciones-cell">` pero **la clase no existe en el CSS**. | `lib_ui.py:83`; ausente en `lib_css.py` |
| A30 | 🟡 | paginas_admin.py (inline) | Diseño | Estilos en línea con hex incrustado en celdas de avance (rompe política de tokens). | `:87-88` |
| A31 | 🟡 | lib_ui.py (inline) | Diseño | Checkbox de tabla con `style="…accent-color:#004a93…"` inline en `tabla(con_checkbox=True)`. | `lib_ui.py:345-350`; `paginas_admin.py:548` |
| A32 | 🟡 | lib_css.py | Diseño | Variable CSS **inexistente** `--azul-real-10` en `.drop.sobre` (tokens declarados: `--azul-06`/`--azul-12`); el fondo no se aplica. | `lib_css.py:330` vs tokens `:34` |
| A33 | 🟡 | lib_js.py (comentario) | Diseño | Comentario obsoleto "los grupos solo existen en Estudiante" (Admin ya usa menú jerárquico); el NAV admin añade ítems planos `Notificaciones`/`Perfil` que el patrón estudiante no tiene. | `lib_js.py:172-175`; `lib_ui.py:101-121` vs `74-90` |
| A34 | 🟡 | usuarios.html | Diseño | `abrirFormulario` copia `innerHTML` de `#form-*`, **duplicando IDs** de campos (original oculto + copia en modal) → a11y. | `lib_js.py:370-379`; contenedores `:202-203` |
| A35 | 🟡 | usuarios.html | Diseño | Los formularios embebidos **no están dentro de `<form>`** → no aplican `required`; "Guardar" solo emite toast. | `_cuerpo_docente/estudiante` `:210-273`; validación `lib_js.py:1161` |

**Veredicto Admin:** cosméticamente completo y correlacionado (menú jerárquico tipo Estudiante,
shell, toasts/modales, sin enlaces rotos), pero **funcionalmente superficial** en flujos de gestión:
sin alta de usuarios, sin Activar/Desactivar real, sin aprobación de eventos/emprendimientos, y
varios filtros/acciones desviados o inertes. Los problemas son de **cobertura de acciones y de
mapeo intención→destino**, no de maquetación.

---

## 3. Transversal

| ID | Sev | Vista | Tipo | Descripción | Evidencia |
|----|-----|-------|------|-------------|-----------|
| F1 | 🟠 | global | Redirect/Faltante | Botones sin `data-accion` cuyo slug no coincide con ningún `case` → toast genérico, no ejecutan. Ejemplos: "Cambiar contraseña" (`paginas_docente.py:536`, `paginas_admin.py:904`) vs case `actualizar-contrasena`; "Asignar tarea" (`paginas_docente.py:501`); "Confirmar asignación" (`paginas_admin.py:505`); "Publicar evento" (`:705`); "Generar reporte" (`:862`); "Descargar plantilla" (`:864`); "Marcar todo como leído" vs case `marcar-todas-como-leidas`. | varias |
| F2 | 🟠 | global | Faltante | **"Cerrar sesión"** sin `confirmar()`, sin estado "sesión expirada"/403. | `lib_js.py:878-880,1279,1314-1315`; `paginas_estudiante.py:1357` |
| F3 | 🟡 | global | Diseño | Estado **"Limitado"** (rol/estado propuesto) no aplicado en ninguna vista. | varias |
| F4 | 🟡 | lib_js.py | Diseño | 23 `case` del dispatcher **muertos** (ningún botón los dispara). | `lib_js.py` (58 case) |

---

## 4. Docente (baseline — rol intocable, solo registro)

| ID | Sev | Vista | Tipo | Descripción | Evidencia |
|----|-----|-------|------|-------------|-----------|
| D-01 | 🔴 | asesoria-form.html | Faltante | Flujo BR-002 sin transición: "Confirmar y notificar" / "Proponer otra fecha" / "Rechazar solicitud" son `<a href="#">` sin `data-accion`. | `paginas_docente.py:106-107,213-216` |
| D-02 | 🟠 | (varias) | Diseño | `select.filtro` **sin `data-filtro`** → inertes (a diferencia de estudiante). | `paginas_docente.py:161-166,485-490` vs `paginas_estudiante.py:286-292` |
| D-03 | 🟠 | seguimiento/tareas/asesorias/notificaciones | Faltante | Varias acciones sin `data-accion`. | `paginas_docente.py` |

> Estos hallazgos **no se corrigen** mientras la regla "Docente intacto" siga vigente; quedan como
> baseline para una eventual pasada sobre el rol Docente.

---

## 5. Prioridad sugerida (para Etapa 3 y limpieza)

1. 🔴 **A01/A02/A28** — Alta de usuario + control Activar/Desactivar en `usuarios()`. *(A01: vista #1.
   A02/A28: vista #4 — selector de estado Activo/Limitado/Inactivo por fila con confirmación; hecho.
   Vinculado a A05 por el arreglo del wiring de `data-filtro`.)*
2. 🔴 **A03/A04** — Aprobación real de eventos y de emprendimientos/solicitudes. *(A04: vistas #2 y #3 —
   bandeja "Solicitudes pendientes" y revisión de emprendimiento creadas; falta aplicar el cambio real.
   A03 pendiente.)*
3. 🔴 **E001** — "Volver a responder" en `diagnostico-resultados.html` (navegación).
4. 🟠 **A05** — Cablear filtros `select.filtro` (`_sel` → `data-filtro`).
5. 🟠 **A06/A07/A27/A15/A16** — Redireccionamientos y acciones desviadas.
6. 🟠 **F1/F2** — Acciones sin `data-accion` y confirmación de cierre de sesión.
7. 🟡 **A29/A32** — Deuda CSS (`.acciones-cell` inexistente, `--azul-real-10` inexistente).
8. 🟡 **A12** — Limpiar entradas stale en `_subidas.json`.
9. 🟡 **A25/A14/A26** — Consistencia de métricas y del drawer de notificaciones.

---

## 6. Correcciones ya aplicadas (post-auditoría)

- **A01 — Alta de usuario (vista #1, Etapa 3).** `usuarios()` ahora tiene **"Nuevo docente"** y
  **"Nuevo estudiante"** en la cabecera de cada tarjeta (`data-accion="nuevo-docente"` /
  `"nuevo-estudiante"`). Formularios de alta embebidos (`#form-nuevo-docente`,
  `#form-nuevo-estudiante`) abiertos en modal vía `abrirFormulario()` (extendido con etiqueta de
  confirmación y mensaje de toast). Estado inicial = **selector Activo/Limitado (por defecto Activo)**;
  credenciales por **correo de activación** (sin campo de contraseña). Verificado en navegador:
  ambos modales abren con sus campos/selects y "Crear …" muestra toast y cierra. `paginas_admin.py`,
  `lib_js.py`. _(A02 y A28 quedan parcialmente cubiertos: falta el control real de Activar/Desactivar
  y eliminar/deshabilitar desde la tabla.)_

- **A04 — Bandeja "Solicitudes pendientes" (vista #2, Etapa 3).** Nueva página `admin/solicitudes.html`
  (ítem de primer nivel en el NAV del Admin, con **badge de pendientes** = 10). Bandeja con
  `tabs_paneles` de tres pestañas — **Desbloqueos (4)**, **Paralelos (3)**, **Citas (3)** — y 3 KPIs.
  Datos en `SOLIC_DESBLOQUEOS` / `SOLIC_PARALELOS` / `SOLIC_CITAS` (`paginas_admin.py`). Cada fila con
  **Aprobar** (`solicitud-aprobar` → `confirmar()`) y **Rechazar** (`solicitud-rechazar` → modal con
  `<textarea>` de motivo + aviso), más toast de resultado. Cierra parcialmente **A04** (aprobación de
  emprendimientos/solicitudes) y avanza el **X1** (modales de confirmación). Extiende `_item_nav`/NAV
  con badge opcional (`lib_ui.py`), `.nav-badge` (`lib_css.py`) y los dos casos en `lib_js.py`.
  Verificado en navegador: pestañas conmutan (panel activo visible, resto `hidden`), modal de
  aprobación y de rechazo abren correctamente, badge = 10. _(Pendiente: que Aprobar/Rechazar apliquen
  el cambio real en las tablas de origen — desbloqueo en `usuarios()`, paralelo y cita — y descuenten
  el badge.)_

- **A04 — Revisión de emprendimiento (vista #3, Etapa 3).** En `emprendimientos()` cada fila tiene un
  botón **Revisar** (`data-accion="revisar-emprendimiento"`) con los datos del emprendimiento en
  `data-*` (emp, cod, estu, sector, tipo, etapa, docente). Abre un **modal de revisión** con la ficha
  y **Aprobar** (`confirmar()` → "pasará a estado Aprobado…") / **Rechazar** (motivo). Los botones del
  modal usan `cerrar:false` para encadenar el segundo modal sin cerrarse. Helpers reutilizables
  `rechazarConMotivo()` y `revisarEmprendimiento()` en `lib_js.py` (la bandeja de Solicitudes del vista
  #2 ahora reutiliza `rechazarConMotivo`). Verificado en navegador: modal de revisión con datos y 3
  botones; Aprobar → confirm correcto (1 solo modal a la vez); Rechazar → modal de motivo.
  _(Pendiente: reflejar el nuevo estado "Aprobado" en la tabla/columna y que Aprobar aplique el cambio.)_

- **A02/A28 — Estado de cuenta Activo/Limitado/Inactivo (vista #4, Etapa 3).** En `usuarios()` la
  columna "Estado" de docentes y estudiantes ahora es un **selector por fila** `select.sel-estado`
  (`_sel_estado()` en `paginas_admin.py`) con `data-filtro="off"`. Al cambiar:
  1. el select revierte de inmediato al estado actual,
  2. abre **modal de confirmación** ("¿Cambiar el acceso de X a Y?") con aviso según el destino
     (Inactivo → pierde el acceso hasta reactivar; Limitado → acceso restringido; Activo → acceso completo),
  3. **Confirmar** persiste el valor y muestra toast; Cancelar / X / Esc dejan el estado intacto.
  CSS `.sel-estado` compacto en `lib_css.py`. **Arreglo de wiring asociado (F-transversal):** los
  selectores `[data-filtro]` y `select[data-filtro]` de `lib_js.py` ahora excluyen `data-filtro="off"`
  (`:not([data-filtro='off'])`), como ya hacía la línea 290 — antes un elemento con `data-filtro="off"`
  recibía listeners de click/cambio y disparaba `aplicarFiltros()`. Verificado en navegador: 10
  selects visibles sin filtrar filas; modal + Confirmar/Cancelar correctos; sin errores de consola;
  y sin regresión en `estudiante/emprendimientos.html` (filtro por etapa 2→1 fila).
