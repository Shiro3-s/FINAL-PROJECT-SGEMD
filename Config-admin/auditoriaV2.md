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
   A03: vista #6 de Etapa 3 — creada en el kanban de `eventos()`; pendiente solo la persistencia real.)*
3. 🔴 **A08** — CRUD de asesorías. *(Vista #5 de Etapa 3 — creado: programación con Nuevo/Ver/Editar/
   Cancelar en `asesorias()`; falta la persistencia real y el reflejo en el docente.)*
4. 🔴 **E001** — "Volver a responder" en `diagnostico-resultados.html` (navegación). *(Vista #7 de
   Etapa 3 — arreglado: enlace real a `diagnostico.html` y regreso a resultados tras reenviar.)*
5. 🟠 **A05** — Cablear filtros `select.filtro` (`_sel` → `data-filtro`). *(Vista #8 de Etapa 3 —
   hecho: `_sel()` emite `data-filtro`, primera opción con `value=""` y acote por columna vía
   `data_filtro_col()`; `aplicarFiltros` restringido a `select.filtro`/`[data-filtro]`.)*
6. 🟠 **A06/A07/A27/A15/A16** — Redireccionamientos y acciones desviadas. *(Vista #9 de Etapa 3 —
   hecho: "Abrir plan" navega, "Editar" abre modal real, "Exportar" descarga CSV (con fallback a
   métricas sin tabla), comentarios usan anclas `#cola`, y "Ver instrumento" abre modal.)*
7. 🟠 **F1/F2** — Acciones sin `data-accion` y confirmación de cierre de sesión. *(Vista #10 de
   Etapa 3 — hecho: los 8 botones inertes de F1 quedaron cableados a sus `case` y el cierre de sesión
   de F2 pide `confirmar()`. El estado "sesión expirada"/403 se dejó fuera por decisión del usuario.)*
8. 🟡 **A29/A32** — Deuda CSS (`.acciones-cell` inexistente, `--azul-real-10` inexistente).
   *(Ítem 8 de la limpieza — hecho: `.acciones-cell` definida como fila de botones alineada a la
   derecha y `.drop.sobre` usa el token existente `--azul-06`.)*
9. 🟡 **A12** — Limpiar entradas stale en `_subidas.json`. *(Ítem 9 de la limpieza — hecho:
   eliminadas `admin/usuario-docente.html` y `admin/usuario-estudiante.html` del manifiesto (51 → 49
   entradas). Nota: `docente/seguimiento*.html` también quedó obsoleto tras reestructurar el
   prototipo, pero se dejó fuera por ser limpieza solo de admin.)*
10. 🟡 **A25/A14/A26** — Consistencia de métricas y del drawer de notificaciones. *(Ítem 10 de la
    limpieza — hecho: dashboard "Eventos por aprobar" 2→1; perfil "Decisiones pendientes" 6→12 (= suma
    del desglose del dashboard); una fuente única `NOTIFS_ADMIN` (`lib_ui.py`) alimenta el badge de la
    campana, el drawer y la métrica "Sin leer"; `shell()` deriva ambos del rol administrador.)*

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

- **A08 — Programación de asesorías (vista #5, Etapa 3).** En `asesorias()` (admin) se conservan las
  métricas y los gráficos existentes y se agrega debajo la tarjeta **"Programación de asesorías"**:
  botón **Nueva asesoría** en la cabecera + tabla (Estudiante, Docente, **Fecha · hora**, Tema,
  Modalidad, Estado con badge, @ACC). Acciones por fila: **Ver** (ficha genérica `fichaDe`),
  **Editar** (modal con formulario prellenado), **Cancelar** (confirmación "Se cancelará la asesoría
  de X del Y a las Z…"). Datos `ASESORIAS` con fecha en ISO y amo con `_fmt_fecha()` para la vista;
  `campo()`/`select()` ahora aceptan `name=""` (`lib_ui.py`) para que `abrirFormAsesoria()` prellene
  por `[name=…]`. BADGE ampliado (`programada` b-amarillo, `confirmada`/`en curso` b-azul,
  `finalizada` b-linea, `cancelada` b-neutra). Habilitado solo crear/editar/cancelar (sin borrado
  físico). Verificado en navegador: modal Nueva asesoría, prefill de Editar completo (incluida la
  fecha ISO), ficha de Ver, confirmación de Cancelar y toast únicos. _(Pendiente: persistencia real y
  reflejo en la agenda del docente.)_

- **F-transversal — Duplicados de toast en modales genéricos.** Los botones del pie generados por
  `abrirModal()` («Cancelar», «Confirmar», «Guardar cambios», etc.) no llevan `data-accion` pero el
  dispatcher los reprocesaba por su texto (`accionDe` → slug): «Cancelar» caía en `case "cancelar"`
  (toast "Cancelado"), «Confirmar»/«Aprobar» en el `default` (toast con el propio texto). Resultado:
  cada acción de cualquier modal mostraba **dos toasts**. Se corrige con `e.stopPropagation()` en los
  listeners de los botones del pie y de `.modal-x` (`lib_js.py`, `abrirModal`), de modo que los
clics generados por el modal nunca llegan al dispatcher del documento. Verificado: cada acción de
   la vista #5 emite un único toast. Beneficia a las vistas #2, #3 y #4.

- **A03 — Aprobación de eventos (vista #6, Etapa 3).** En el kanban de `eventos()` el botón "Aprobar"
  que antes navegaba a `evento-form.html` ahora es **Aprobar evento** (btn-primario, con los datos del
  evento en `data-*`: titulo, fecha, lugar, confirmados, sector) más **Rechazar** (btn-secundario).
  - **Aprobar evento** → `botonAprobarEvento()` arma el modal de aprobación con la **ficha** (Evento,
    Fecha y hora, Lugar, Confirmados, Dirigido a) y el aviso "Se publicará y notificará a los
    estudiantes del sector correspondiente"; al confirmar la tarjeta pasa de "Por aprobar" a
    **Publicado** con badge `b-azul Publicado` y pie "Editar", y se muestra el toast. Si "Por aprobar"
    queda vacía se muestra la nota "Sin pendientes" y los contadores de columna se actualizan.
  - **Rechazar** → `rechazarConMotivo()` (extendido con un cuarto parámetro opcional `alRechazar`)
    mueve la tarjeta a la columna **Borrador** con badge `b-neutra Rechazado` y pie "Editar".
  - Helpers de kanban (`kanbanColumnas`, `kanbanContar`, `kanbanMover`) y `editarEventoLink()` en
    `lib_js.py`; helper `_evento()` en `paginas_admin.py`.
  Verificado en navegador: clases de botón correctas, modal de aprobación con ficha + aviso,
  movimiento a Publicado/Borrador con badge y contadores, toast único y nota de columna vacía; sin
  errores de consola. _(Pendiente: persistencia real y reflejo en la agenda del estudiante.)*

- **E001 — "Volver a responder" en el diagnóstico (vista #7, Etapa 3).** El botón inerte de
  `diagnostico_resultados()` ahora es un enlace real `a.btn.btn-primario href="diagnostico.html"`
  (rehacer el diagnóstico desde cero). Al terminar, `enviar-diagnostico` (`lib_js.py`) persiste el
  envío, muestra el toast y tras 750 ms navega de vuelta a `diagnostico-resultados.html`. Verificado
  en navegador: clic en "Volver a responder" abre el formulario (5 secciones), avanzar hasta
  "Enviar diagnóstico" hace el toast y regresa automáticamente a los resultados. Sin errores de
  consola.

- **A05 — Filtros de tablas del admin cableados (vista #8, Etapa 3).** `_sel()` (`paginas_admin.py`)
  ahora emite `data-filtro="<slug>"`, pone `value=""` en la primera opción ("Todos/Todas…") y acepta
  `data_filtro_col(n)` para acotar por columna (0-based). Cableado: usuarios "Filtrar área" (sin
  columna: aplica a las dos tablas por texto de fila) y emprendimientos sector→col 3,
  etapa→col 5, docente→col 7. Además se corrigió un bug transversal: `aplicarFiltros` (`lib_js.py`)
  consideraba como filtros todos los `<select>` de la página (incluidos los de formularios ocultos),
  lo que ocultaba filas al primer cambio una vez escuchaba cualquier filtro; ahora solo
  `select.filtro`/`select[data-filtro]` (los `data-filtro="off"` de `_sel_estado` siguen excluidos).
Verificado en navegador en usuarios (Moda → [1,5], Tecnología → [1,5], limpiar → [5,5]) y
   emprendimientos (FASE 2 → 2, Sin asignar → 1, limpiar → 5); página de estudiante sin regresión.
   Sin errores de consola.

- **A06/A07/A27/A15/A16 — Acciones y redireccionamientos corregidos (vista #9, Etapa 3).** Nuevos
  helpers en `paginas_admin.py`: `_exportar(etiqueta)` (botón `data-accion="exportar"`) y `_emp(...)`
  (botón con `data-*` de la fila). En `emprendimientos()`: "Abrir plan" pasó de `boton_accion("eye")`
  a `<a class="table-act" href="emprendimiento-plan.html">`, y "Editar" a `_emp("editar-emprendimiento")`
  que abre el formulario real embebido `#form-emprendimiento` (nombre, código bloqueado, estudiante,
  sector, tipo, etapa, avance, docente) vía `abrirFormEmprendimiento()`; se corrigió que el código —
  campo sin `name` porque se pinta con `bloqueo` — se prefilla con `input[disabled]`. En
  `comentarios()` se añadió `<div id="cola">` y los 3 avisos + "Moderar cola" pasaron a ancla `#cola`
  (scroll) en vez de recargar la misma página. En `diagnosticos()` "Ver instrumento" abre modal
  (`#contenido-instrumento` + case `ver-instrumento`) con las 5 secciones y 22 preguntas reales. Los
  botones "Exportar" de `asesorias()`, `seguimiento()`, `seguimiento-dashboard()` y `asignaciones()`
  (antes navegaban a `reportes.html`) ahora descargan CSV vía `exportar`: el case usa
  `csvDeTabla() || csvDeMetricas()` (nuevo fallback para pantallas sin tabla que resume
  `.metrica-lbl`/`.metrica-val`; `seguimiento` y su tablero no tienen `<table>`). Verificado en
  navegador: modal de edición prefilleado completo (EMP-041), instrumento con sus 22 preguntas,
  anclas `#cola`, y CSVs descargados correctos en las 4 páginas (7, 3, 4 y 4 filas). Sin errores de
  consola.

- **F1 — Acciones inertes cableadas (vista #10, Etapa 3).** Se conectó cada botón sin acción a su
  `case` en `lib_js.py`. En `paginas_admin.py`: `perfil()` reorganizó las tarjetas — "Guardar
  cambios" (`data-accion="guardar-perfil"`) quedó en la tarjeta "Acciones" y se añadió una tarjeta
  **"Cambiar contraseña"** con 3 campos (`Contraseña actual`, `Nueva contraseña`, `Repetir nueva
  contraseña`) y botón `data-accion="actualizar-contrasena"` (el patrón general ya usado en la
  estudiante), envolviendo los datos editables en `<div class="campos-perfil">`; en
  `asignar_emprendimiento()` "Confirmar asignación" → `confirmar-asignacion`; en `evento_form()`
  "Publicar evento" → `publicar-evento`; en `reportes()` "Generar reporte" → `generar-reporte` y
  "Descargar plantilla" → `descargar-plantilla`; en `notificaciones()` "Marcar todo como leído" →
  `marcar-todas-como-leidas`. En `paginas_docente.py`: `tareas()` ganó el formulario embebido
  `#form-tarea` (Título, Emprendimiento, Estudiante, Prioridad, Vence el, Puntos, Descripción) y
  "Asignar tarea" → `asignar-tarea`; `perfil()` replicó el cambio de la admin; `notificaciones()`
  quedó cableado igual. En `lib_js.py` se añadió `csvPlantillaReporte()` (cabecera de 8 columnas +
  fila vacía); `guardar-perfil` ahora toma `.campos-perfil` con fallback a `.card` (la estudiante no
  tiene ese contenedor); y los `case` nuevos: `confirmar-asignacion` y `publicar-evento` (confirmar +
  toast + volver a su lista a los 750 ms), `generar-reporte` (confirmar + toast de encolado),
  `descargar-plantilla` (descarga CSV real), `asignar-tarea` (`abrirFormulario`), y
  `marcar-todas-como-leidas` extendido para marcar también los `.aviso` con botón `aprobar` (los
  avisos del docente), dejando el toast informativo "No hay notificaciones sin leer" en las
  pantallas basadas en agenda (admin). Verificado en navegador: modal "Asignar tarea" (7 campos +
  toast "Tarea asignada"), "Actualizar contraseña" (valida vacío/nueva<8/coincidencia → éxito y
  limpia), "Guardar cambios" persiste con clave por pantalla y excluye los campos bloqueados,
  "Descargar plantilla" descarga CSV real, "Generar reporte"/"Publicar evento"/"Confirmar
  asignación" abren confirmación y actúan, "Marcar todo" marca 4 avisos (docente) o informa (admin),
  y la estudiante sigue persistiendo sin regresión. Sin errores de consola.

- **F2 — Confirmación de cierre de sesión (vista #10, Etapa 3).** El `case "cerrar-sesion"` del
  dispatcher y el enlace del mini menú `.who` quedaron envueltos en
  `confirmar("Cerrar sesión", "¿Seguro que quieres cerrar tu sesión?", cerrarSesion)`. Verificado en
  navegador: el mini menú muestra el modal y "Cancelar" mantiene la sesión. *(El estado "sesión
  expirada"/403 se dejó fuera por decisión del usuario; ver §5 ítem 7.)*

- **A29 — `.acciones-cell` definida (ítem 8, limpieza).** `_acc()` (`paginas_admin.py`,
  `paginas_docente.py`) emitía `<div class="acciones-cell">…</div>` sin regla en el CSS. Se agregó en
  `lib_css.py` junto a las reglas de tabla: `.acciones-cell{display:flex;align-items:center;
  justify-content:flex-end}` — la fila de botones queda alineada a la derecha como la celda `.acc`.
  Verificado en navegador: la celda de acciones computa `display:flex; justify-content:flex-end;
  align-items:center` y los botones (32 px) siguen pegados al borde derecho.

- **A32 — `--azul-real-10` inexistente (ítem 8, limpieza).** `.drop.sobre` (`lib_css.py`) usaba una
  variable que no existía en `:root` (el fondo no se aplicaba). Se cambió al token existente
  `--azul-06`, el mismo que emplea el estado de arrastre hermano `.kan-col.sobre`. Verificado en
  navegador: `.drop.sobre` pasa a `rgba(0,74,147,0.06)` con borde `rgb(0,74,147)`. Además, una
  auditoría de variables CSS confirma `USADAS SIN DECLARAR: []` (antes listaba `--azul-real-10`).

- **A12 — Entradas stale en `_subidas.json` (ítem 9, limpieza).** El manifiesto de pantallas subidas
  a Stitch aún listaba dos páginas del admin ya eliminadas del prototipo: `admin/usuario-docente.html`
  ("Editar docente") y `admin/usuario-estudiante.html` ("Editar estudiante"). Se eliminaron ambas
  entradas; el JSON pasa de **51 a 49** claves y sigue siendo válido. *(El manifiesto también
   conserva `docente/seguimiento.html`, `-dashboard` y `-notas`, obsoletos tras la reestructuración del
   prototipo; se dejaron por estar fuera del alcance admin de esta limpieza.)*

- **A25/A14/A26 — Consistencia de métricas y del drawer de notificaciones (ítem 10, limpieza).**
  - **A25 (métricas):** en `paginas_admin.py`, dashboard **"Eventos por aprobar" 2 → 1** (coincide con
    la única tarjeta de la columna "Por aprobar" del kanban y con la agenda de notificaciones) y perfil
    **"Decisiones pendientes" 6 → 12** (= 3 + 1 + 3 + 5, la suma del desglose "Pendientes de decisión"
    del dashboard).
  - **A14/A26 (campana y drawer):** nueva fuente única `NOTIFS_ADMIN` en `lib_ui.py` (misma forma que
    `NOTIFS_EST`: `(leida, titulo, texto, fecha, icono, tipo, href)`), con voz de administrador y **2
    sin leer**. `shell()` ahora, para `rol == "administrador"`, deriva `notif_lista` de `NOTIFS_ADMIN`
    (drawer) y el badge del número de no leídas; su parámetro `notif` pasa de valor fijo `3` a `None`
    (solo cambia el admin; estudiante y docente conservan su comportamiento). La métrica "Sin leer" de
    `admin/notificaciones.html` se calcula desde la misma fuente.
    Verificado en navegador (`python generar.py`, 70 pantallas): las 17 páginas de admin muestran badge
    **2** y `<ul class="sg-notif-fuente" data-notif-fuente>`; la campana abre el drawer con 4 avisos de
    voz admin que enlazan a `asignar-emprendimiento.html`, `diagnosticos.html`, `eventos.html` y
    `reportes.html`; dashboard "Eventos por aprobar" = 1, perfil "Decisiones pendientes" = 12,
    notificaciones "Sin leer" = 2. Estudiante (badge 3, fuente presente) y docente (badge 3, sin fuente)
    sin cambios; sin errores de consola nuevos (solo el ruido `file:` preexistente).

- **Barrido final de verificación del admin (cierre de Etapa 3).** Verificación de las **17 páginas** de
  `admin/` (dashboard, usuarios, solicitudes, emprendimientos, emprendimiento-plan, seguimiento,
  seguimiento-dashboard, asignar-emprendimiento, comentarios, asesorias, eventos, evento-form,
  asignaciones, diagnosticos, reportes, perfil, notificaciones). Sin hallazgos nuevos:
  - **Acciones cableadas:** las **30** acciones `data-accion` reales del DOM de admin tienen su `case`
    en `lib_js.py` → **0 inertes**. Las aparentes faltantes `perfil`/`configuracion`/`preferencias` se
    resuelven inline en el mini‑menú (`.who`, `lib_js.py`): `perfil`→`perfil.html`, `configuracion` solo
    existe en estudiante/docente, y en admin "Preferencias" es **intencionalmente "sin vista"** (toast
    informativo). Nota: una extracción ingenua marca acciones falsas porque incluye los literales del JS
    inlinado; hay que recortar el `<script>` antes de extraer.
  - **Enlaces:** **0** enlaces `*.html` muertos dentro de `admin/`.
  - **Consola:** **0 errores** en las 17 páginas en carga limpia. El mensaje
    `Unsafe attempt to load URL … 'file:' URLs are treated as unique security origins` visto al inicio
    era un **artefacto preservado** del DevTools (no se reproduce en pestaña nueva ni en carga limpia del
    dashboard); no es un error de la aplicación.
  - **Plantilla/robustez:** sin `{{`, `%(`, `None`, `undefined`, `TODO` ni `Lorem`; todas las páginas con
    `<title>`. (Los `}}` detectados son llaves de cierre de `@media` en CSS, no fuga de plantilla.)
  - **Sin regresiones:** badge `2` en las 17 páginas admin y drawer con los 4 avisos de voz
    administrador; estudiante (badge 3, fuente presente) y docente (badge 3, sin fuente) intactos.
