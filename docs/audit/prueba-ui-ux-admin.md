# Prueba de Navegación UI/UX — Rol ADMINISTRADOR (Coordinadora)

> **Documento complementario** de [`auditoria-ui-ux-admin.md`](./auditoria-ui-ux-admin.md).
> La auditoría (§1–§4) **describe el deber ser** (diagnóstico, brechas, mapa propuesto). Esta **Prueba** aporta la **evidencia empírica**: se recorre el prototipo *como un Administrador real* y se registra, tarea por tarea, **dónde se rompe**.
> **Ubicación:** `SGEMD-JOEL/prueba-ui-ux-admin.md` (fuera de `FINAL-PROJECT-SGEMD/`).
> **Insumo de hallazgos para:** [`correcciones-adiciones-requisitos.md`](./correcciones-adiciones-requisitos.md).

---

## 1. Metodología

Se aplicaron **tres niveles** de prueba complementarios, cada uno con **4 subagentes independientes** que recorrieron el prototipo con lentes distintos; al final se **contrastaron sus visiones** (una tarea se marca como "completable" **solo si los 4 coinciden**).

### 1.1 Niveles

| Nivel | Nombre | Qué hace | Herramienta |
| --- | --- | --- | --- |
| **1** | Grafo estático de enlaces/acciones | Recorre HTML generado, enlaces, `href`, `data-accion`, formularios y salidas de cada vista | lectura de código/HTML |
| **2** | Walkthrough interactivo | Se opera el prototipo **como Admin** (login → clic real en botones/menú) | navegador automatizado (chrome-devtools) |
| **3** | Heurísticas Nielsen + Cognitive Walkthrough | Evalúa aprendizabilidad, feedback, prevención de errores y control del usuario | análisis heurístico |

### 1.2 Los 4 subagentes (dos tandas)

**Tanda A — recorrido por tareas**
1. **CRUD y Datos** (`C-01…C-12`) 2. **Ciclo de vida y Solicitudes** (`L-01…L-12`)
3. **Estados, errores y Auth** (`E-01…E-12`) 4. **Grafo de navegación** (`G-01…G-14`)

**Tanda B — enfoque CRUD entidad × operación (perspectiva nueva)**
1. **Completitud CRUD** (`K-01…K-14`) 2. **Integridad/validación/persistencia** (`V-01…V-13`)
3. **Máquina de estados y badges** (`S-01…S-13`) 4. **CRUD por rol + trazabilidad** (`P-01…P-12`)

### 1.3 Guion (escenarios del Admin)

`T1` alta de estudiante · `T2` desbloquear perfil limitado · `T3` verificar acta y asignar docente · `T4` aprobar emprendimiento paralelo · `T5` crear/asignar asesoría directa · `T6` crear evento y confirmar asistencia · `T7` revisar inactivos (90 días) · `T8` crear docente con área/carga/permisos · `T9` exportar reporte/backup · `T10` gestionar notificaciones · `X1` logout / sesión expirada / 403 / errores.

---

## 2. Resultado de la prueba — Matriz T1–X1

**Veredicto global: NINGUNA de las 11 tareas se completa de principio a fin.** En todas, el flujo se corta porque la acción clave **no navega, no guarda o no existe**.

| # | Tarea | ¿Completable? | Paso que se rompe | Evidencia |
| --- | --- | --- | --- | --- |
| T1 | Alta de estudiante | ❌ No | No existe vista de creación real; "Guardar" es botón sin destino | `paginas_admin.py` (tabla estudiantes) · `lib_ui.py` `_btn(href="#")` |
| T2 | Desbloquear perfil | ❌ No | No hay acción/vista de desbloqueo; el estado no cambia | `lib_js.py:344-352` (modal genérico) · `paginas_admin.py:274-288` |
| T3 | Verificar acta + asignar docente | ❌ No | Acta sin pantalla; "Asignar" sin destino | `paginas_admin.py` · `_btn` |
| T4 | Aprobar emprendimiento paralelo | ❌ No | No hay bandeja ni acción de aprobación | `README` R-01 vs UI |
| T5 | Crear/asignar asesoría | ❌ No | Admin solo ve **métricas**, no CRUD | `paginas_admin.py:604-635` |
| T6 | Crear evento + confirmaciones | ❌ No | "Aprobar evento" **navega** al form, no aprueba | máquina de estados rota |
| T7 | Revisar inactivos 90 d | ❌ No | Sin semáforo ni listado de inactivos | FR-007 sin gancho de UI |
| T8 | Crear docente (área/carga) | ❌ No | Mismo caso T1 | `usuario-docente` huérfana |
| T9 | Exportar reporte/backup | ❌ No | "Exportar" `href="#"`; sin backup | FR-009/NFR-004 sin vista |
| T10 | Notificaciones | ❌ No | Campana sin enlace; lista sin acciones | `lib_js.py:431-436` |
| X1 | Logout/sesión/403/errores | ❌ No | No hay 403, sesión expirada ni confirmación de logout | `paginas_auth.py` |

> **Divergencia documentada (Nivel 1 vs Nivel 2):** el **grafo** se ve "sano" — **0 enlaces rotos** y **0 páginas sin salida** — pero la operación **falla igual**, porque el problema no son los enlaces sino los **botones que no navegan** (`<button>` sin `href` ni `data-accion`).

---

## 3. Hallazgos consolidados (deduplicados)

Severidad: 🔴 bloqueante · 🟠 mayor · 🟡 menor. La columna **Decisión aplicada** remite a las resoluciones acordadas (ver §5 y `correcciones-adiciones-requisitos.md`).

### 3.1 Completitud del CRUD (lente `K-*` / tanda B-A)

**Completitud global del CRUD Admin = 30,3 %.** Patrón: *Read* casi siempre OK; *Create* y *Delete* son los grandes ausentes; *Update* siempre cae en modal genérico o toast.

| Entidad | C | R | U | D | Sev. |
| --- | --- | --- | --- | --- | --- |
| Usuarios (Estudiante) | AUSENTE | OK | FALSO | AUSENTE | 🔴 |
| Usuarios (Docente) | AUSENTE | OK | FALSO | AUSENTE | 🔴 |
| Perfil/Cuenta | — | OK | FALSO | AUSENTE | 🟠 |
| Emprendimiento | AUSENTE | OK | FALSO | AUSENTE | 🔴 |
| Plan/Tarea | AUSENTE | OK | AUSENTE | AUSENTE | 🔴 |
| Diagnóstico | — | OK | FALSO | — | 🟠 |
| Seguimiento | FALSO | OK | FALSO | — | 🟠 |
| Asesoría | AUSENTE | SOLO MÉTRICAS | AUSENTE | AUSENTE | 🔴 |
| Archivo (FR-008) | AUSENTE | PARCIAL | AUSENTE | AUSENTE | 🔴 |
| Evento | parcial (`evento-form`) | OK | FALSO | AUSENTE | 🟠 |
| Notificación | AUSENTE | OK | AUSENTE | AUSENTE | 🟡 |
| Backup (FR-009) | AUSENTE | AUSENTE | — | — | 🔴 |

### 3.2 Integridad, validación y persistencia (`V-*`)

| ID | Hallazgo | Sev. | Evidencia |
| --- | --- | --- | --- |
| V-01 | **0 `<form>`** en las 18 pantallas admin → no hay envío real | 🔴 | HTML generado |
| V-02 | `required` presente pero **inerte** (usuario-docente=5, evento-form=6, perfil=4) | 🔴 | `lib_ui.py` `campo()` |
| V-03 | "Guardar/Publicar/Confirmar" no leen ni persisten: solo `toast` fijo | 🔴 | `lib_js.py:402-414` |
| V-06/V-07 | Sin **borrado lógico** ni **cascada FR-008** de archivos | 🔴 | — |
| V-08 | Sin control de **duplicados/unicidad** (docente repetido, tope de 12 h) | 🟠 | — |
| V-10 | Sin persistencia real; nada se conserva entre pantallas | 🟠 | `localStorage` solo sesión |

### 3.3 Máquina de estados y badges (`S-*`)

| ID | Hallazgo | Sev. | Evidencia |
| --- | --- | --- | --- |
| S-03 | El mapa `BADGE` es **código muerto**; colores hardcodeados e inconsistentes | 🟠 | `paginas_admin.py` |
| S-07 | **Kanban de eventos roto**: CSS y JS usan clases distintas (`.kan-col` vs `.k-col`) → sin arrastre | 🟠 | CSS/JS |
| S-08 | "Aprobar evento" **navega**, no aprueba | 🟠 | `lib_js.py` |
| S-01/S-02 | Falta estado **Limitado** y transición de **desbloqueo**; desactivar no cambia badge | 🔴 | — |

### 3.4 Permisos, identidad y trazabilidad (`P-*`)

| ID | Hallazgo | Sev. | Evidencia |
| --- | --- | --- | --- |
| P-01 | **Sin guarda de rol ni pantalla 403** | 🔴 | `lib_js.py` (no lee sesión) |
| P-02 | **Identidad ficticia**: el shell fija rol/usuario; la sesión guardada nunca se lee | 🔴 | `lib_ui.py` `shell()` |
| P-07/P-08 | "Registrar avance" y "Revisar diagnóstico" duplicados admin/docente sin regla de dueño | 🟠 | `paginas_admin.py` / `paginas_docente.py` |
| P-09/P-10 | **FR-006 no se genera**: el expediente no reúne asesorías+diagnóstico; sin log de auditoría | 🟠 | — |

### 3.5 Navegación y controles inertes (`G-*` / `C-*` / `E-*`)

| ID | Hallazgo | Sev. |
| --- | --- | --- |
| G-01 | `_btn` por defecto `href="#"` → dead-ends sistemáticos | 🔴 |
| G-04 | Migajas de pan muertas (`shell()`) | 🟡 |
| C-05 | Paginación decorativa (`paginas()`) | 🟡 |
| E-04 | Login redirige sin validación; sin 403/sesión expirada | 🟠 |
| E-06 | Buscador global solo *placeholder* | 🟡 |

---

## 4. Conteos objetivos (Nivel 1, medibles)

| Métrica | Valor | Lectura |
| --- | --- | --- |
| Pantallas admin | **18** | alcance auditado |
| Botones en admin | **209** | volumen de interacción |
| Botones **sin `data-accion`** | **53** | acciones sin comportamiento |
| Enlaces `href="#"` | **27** | dead-ends |
| Formularios `<form>` | **0** | sin envío/validación |
| Páginas huérfanas | **2** (`usuario-docente`, `usuario-estudiante`) | entradas invisibles |
| Enlaces rotos | **0** | el grafo "se ve sano" |
| Páginas sin salida | **0** | pero los botones no navegan |
| **Tareas del guion completables** | **0 / 11** | resultado final |

---

## 5. Vistas faltantes y CRUD requerido (derivado de esta prueba)

Con las **6 decisiones** acordadas (ver [`correcciones-adiciones-requisitos.md`](./correcciones-adiciones-requisitos.md)):

| # | Vista/acción nueva | Cubre | Decisión |
| --- | --- | --- | --- |
| 1 | **Modal Crear/Editar usuario** (estudiante y docente) | T1, T8 | D1 Admin crea |
| 2 | **Bandeja "Solicitudes pendientes"** (desbloqueos, paralelos, citas) | T2, T4, T5 | D1/D2 |
| 3 | **Aprobar emprendimiento** (+paralelo) | T4 | D2 |
| 4 | **Desbloquear/Reactivar cuenta** (Limitado↔Activo↔Inactivo) | T2, T7 | D4 |
| 5 | **CRUD de asesoría** (asignación directa del Admin) | T5 | D3 (ya resuelto) |
| 6 | **Kanban/lista de eventos** con aprobación real | T6 | — |
| 7 | **Listado de inactivos (90 días)** con semáforo | T7 | D4 |
| 8 | **Respaldos** (Exportar BD CSV/Excel + estado backup diario) | T9 | D6 |
| 9 | **Centro de notificaciones** con acciones | T10 | — |
| 10 | **Modales de confirmación** + pantallas **403/Sesión expirada/Logout** | X1 | — |
| 11 | **Expediente trazable FR-006** (asesorías + diagnóstico + log) | P-09/P-10 | — |

---

## 6. Correlación con la auditoría

- **§1–§4** de `auditoria-ui-ux-admin.md` = *diagnóstico y deber ser*.
- **Esta Prueba** = *evidencia de que el prototipo no soporta ese deber ser* (0/11 tareas).
- **§5.1.1** de la auditoría (inconsistencia **FR-004 / BR-002**) se confirma aquí desde la práctica: en **T5** el Admin no tiene CRUD de asesorías, por lo que **ninguna** de las dos lecturas del requisito es implementable hoy.
- Los puntos ciegos detectados se registran como correcciones/adiciones en [`correcciones-adiciones-requisitos.md`](./correcciones-adiciones-requisitos.md).

---

*Fin de la prueba. Vive fuera de `FINAL-PROJECT-SGEMD/` y complementa a `auditoria-ui-ux-admin.md`.*
