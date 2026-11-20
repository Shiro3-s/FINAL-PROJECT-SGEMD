# Registro de ejecución — Actualización documental SGEMD (2026-10-25)

> **Qué es este documento:** la **prueba de lo que se hizo**. Registra el estado inicial, la evidencia consultada, la verificación en vistas, los cambios aplicados, las decisiones, los bloqueos y el resultado del control de calidad.
>
> **Orquestación aplicada:** [`orquestacion-actualizacion-requisitos-2026-10.md`](./orquestacion-actualizacion-requisitos-2026-10.md).

- **Fecha de ejecución:** 25 de octubre de 2026
- **Modo:** **local**. Sin rama nueva, sin commit, sin push y sin publicación en GitHub.
- **Repositorio:** `C:\Users\storm\Videos\profesor`
- **HEAD al iniciar y al cerrar:** `a5a23d5 fix(docente): corrige textos, tildes y documentación del rol`
- **Alcance:** documentación. **No** se modificó código, HTML ni generadores.

---

## 1. Resumen ejecutivo

Se actualizaron los tres documentos fuente (`docs/fr_nfr_sgemd.md`, `docs/historias_usuario.md` y `README.md`) y se crearon tres documentos de trabajo (orquestación, este registro y el dossier de decisiones). La actualización incorporó:

- **14 requisitos funcionales nuevos** (`FR-011` … `FR-024`), **5 no funcionales** (`NFR-005` … `NFR-009`), **3 procesos** (`BP-004` … `BP-006`) y **7 reglas** (`BR-003` … `BR-009`).
- **16 historias nuevas** (`US-011` … `US-026`) con criterios Gherkin y matriz de cobertura.
- Correcciones puntuales: **FR-004/BR-002/R22** (Admin asigna, docente acepta), **FR-007** (90 días), **FR-008** (borrado lógico + cascada), **FR-005** (notificaciones accionables).
- Conteos verificados: **73 pantallas**, **19 de administrador**.
- Declaración explícita del **alcance estático** del prototipo.

**Resultado:** documentación sincronizada con las vistas verificadas. **Preguntas cerradas:** AQ-03 (verificación por hash), AQ-04 y AQ-05 (decisión del usuario), AQ-08 (rol auditor) y AQ-11 (modelo textual). **Abiertas:** AQ-06, AQ-07, AQ-09, AQ-10 y AQ-12, registradas en el dossier y pendientes de reunión.

---

## 2. Línea base y estado final

### 2.1 Estado inicial

| Documento | Líneas | Estado detectado |
|---|---:|---|
| `docs/fr_nfr_sgemd.md` | 222 | 10 FR / 4 NFR; FR-007 “periodo definido”; FR-004 con “admin aprueba cruces”; sin estados de cuenta ni CRUD |
| `docs/historias_usuario.md` | 187 | Título “Proyecto Quantum”; 90 días ya definidos; asesorías con “docente confirma”; sin historias de admin moderno |
| `README.md` | 950 | Nota de “71 pantallas”; 18 admin implícitas; R22 desactualizada; §8 con fila “Gradar/s see Aspirante”; tablas incompletas |

### 2.2 Estado final

| Documento | Líneas | Estado |
|---|---:|---|
| `docs/fr_nfr_sgemd.md` | 564 | 24 FR / 9 NFR / 6 BP / 9 BR; AQ-01 … AQ-12 registradas; control de cambios |
| `docs/historias_usuario.md` | 549 | SGEMD; 16 historias nuevas (US-011 … US-026); cobertura y control de cambios |
| `README.md` | 1097 | 73 pantallas / 19 admin; R22 corregida; §8 completo; §16 con alcance local |
| `docs/orquestacion-actualizacion-requisitos-2026-10.md` | 319 | Nuevo: método y criterios |
| `docs/registro-actualizacion-requisitos-2026-10.md` | 375 | Nuevo: este documento |
| `docs/dossier-decisiones-pendientes-2026-10.md` | 356 | Nuevo: hojas de decisión AQ-06/07/09/10/12 y anexos |

### 2.3 Archivos efectivamente tocados

| Archivo | Operación | ¿Commit? | ¿Push? |
|---|---|---|---|
| `README.md` | Modificado | No | No |
| `docs/fr_nfr_sgemd.md` | Modificado | No | No |
| `docs/historias_usuario.md` | Modificado | No | No |
| `docs/orquestacion-actualizacion-requisitos-2026-10.md` | Creado | No | No |
| `docs/registro-actualizacion-requisitos-2026-10.md` | Creado | No | No |
| `docs/dossier-decisiones-pendientes-2026-10.md` | Creado | No | No |

> `git status --short` mostró exactamente esos archivos. `git log -1` siguió en `a5a23d5`: **no se creó ningún commit**.

---

## 3. Inventario verificado del prototipo

**Fuente:** `prototype/index.html` y conteo directo de archivos.

| Rol / carpeta | Pantallas | Verificación |
|---|---:|---|
| Acceso global (`prototype/compartido/`) | 4 | Login, registro, OTP y recuperación |
| Estudiante (`prototype/estudiante/`) | 27 | 18 vistas base + 4 detalles de evento + 4 variantes de tarea + 1 variante de emprendimiento |
| Docente (`prototype/docente/`) | 23 | Incluye 4 detalles de evento, formularios y perfil |
| Administrador (`prototype/admin/`) | 19 | Incluye `configuracion.html` |
| **Total** | **73** | `index.html` enlaza **73** archivos `.html` |

**Salida literal de la verificación:**

```
compartido: 4
estudiante: 27
docente: 23
admin: 19
total: 73
enlaces .html en index: 73
menciones de conteo: ['4', '27', '23', '19']
```

---

## 4. Ledger de evidencia

> La verificación fue **estática** sobre el HTML generado y el JavaScript embebido. No se ejecutó una sesión de navegador en esta pasada; por eso los flujos se describen como “implementados en la UI” y su persistencia como “simulada”.

| # | Hecho verificado | Fuente | Evidencia observada | Estado |
|---|---|---|---|---|
| E-01 | Alta de estudiante y docente | `prototype/admin/usuarios.html` | Botones `Nuevo estudiante` y `Nuevo docente`; formularios `form-nuevo-estudiante` / `form-nuevo-docente` | `Implementado en prototipo (UI)` |
| E-02 | Baja lógica de usuarios | `prototype/admin/usuarios.html` | Acción `dar-de-baja` con confirmación y liberación de asignaciones | `Implementado en prototipo (UI)` |
| E-03 | Estados de cuenta | `prototype/admin/usuarios.html` | Selector `sel-estado` con `Activo`, `Limitado`, `Inactivo` | `Implementado en prototipo (UI)` |
| E-04 | Bandeja de solicitudes | `prototype/admin/solicitudes.html` | Pestañas `Desbloqueos`, `Paralelos`, `Citas`; aprobar/rechazar; `Motivo del rechazo` | `Implementado en prototipo (UI)` |
| E-05 | Asignación y reasignación docente | `prototype/admin/asignaciones.html` | `Asignar docente`, `Reasignar docente`, enlace `asignar-docente` | `Implementado en prototipo (UI)` |
| E-06 | Estado del respaldo e integridad | `prototype/admin/respaldos.html` | “Último respaldo”, “Tamaño ocupado”, “verificación de integridad” e historial | `Implementado en prototipo (UI)`; archivo simulado |
| E-07 | Configuración del programa | `prototype/admin/configuracion.html` | “Parámetros del programa”, sedes, cupos, notificaciones y bitácora | `Implementado en prototipo (UI)` |
| E-08 | Notificaciones accionables | `prototype/admin/notificaciones.html` | “Marcar todo como leído”, contador “Sin leer”, filtros por tipo | `Implementado en prototipo (UI)` |
| E-09 | Reportes institucionales | `prototype/admin/reportes.html` | Formatos CSV, PDF y XLSX; tipo y periodo | `Implementado en prototipo (UI)`; descarga simulada |
| E-10 | Expediente consolidado | `prototype/admin/emprendimiento-expediente.html` | Pestañas Avances, Asesorías, Diagnóstico, Comentarios, Evidencias; “Exportar expediente” | `Implementado en prototipo (UI)` |
| E-11 | Aceptación de asesoría por el docente | `prototype/docente/asesoria-detalle.html` | “Confirmar y notificar”, “Proponer otra fecha”, “Rechazar solicitud” | `Implementado en prototipo (UI)`; simulado |
| E-12 | Calendario de compromisos | `prototype/docente/dashboard.html` | “Calendario y compromisos”; día con evento abre modal | `Implementado en prototipo (UI)` |
| E-13 | Recomendación de eventos | `prototype/docente/evento-detalle-startup.html` | Acción “Recomendar” por estudiante o grupo | `Implementado en prototipo (UI)` |
| E-14 | Evidencia obligatoria en tareas | `prototype/estudiante/tarea-detalle.html` | “Marcar como completada” se habilita solo con al menos un archivo de evidencia | `Implementado en prototipo (UI)`; simulado |
| E-15 | Progreso por fases y descarga | `prototype/estudiante/plan-trabajo.html` | Barras por fase y “Descargar plan” | `Implementado en prototipo (UI)`; descarga simulada |
| E-16 | Datos académicos condicionales | `prototype/estudiante/configuracion.html` | “Nivel académico: Pregrado / Posgrado / Egresado”; campos condicionales | `Implementado en prototipo (UI)` |
| E-17 | Notificaciones del estudiante | `prototype/estudiante/notificaciones.html` | “Marcar todas como leídas”; filtros Todas / Sin leer / Tareas / Asesorías / Seguimiento | `Implementado en prototipo (UI)` |
| E-18 | Conteo de 73 pantallas | `prototype/index.html` + carpetas | 4 + 27 + 23 + 19 = 73; 73 enlaces | Verificado |

**Comprobación automatizada:** las 25 búsquedas de evidencia devolvieron `OK` (alta de estudiante/docente, baja, estados, solicitudes, asignación, respaldos, configuración, notificaciones, reportes, evidencia, datos académicos, plan, calendario, recomendación, aceptación de asesoría y expediente).

---

## 5. Bitácora de verificación en vistas

| ID | Inconsistencia | Fuentes en conflicto | Vista consultada | Evidencia observada | Resultado | ¿Requiere usuario? |
|---|---|---|---|---|---|---|
| V-01 | ¿Quién confirma la asesoría? | `fr_nfr` FR-004/BR-002 vs. `historias` §3 y R22 vs. corrección C-1/C-2 | `admin/asignaciones.html`, `admin/solicitudes.html`, `docente/asesoria-detalle.html` | El admin asigna/reasigna; el docente confirma, propone fecha o rechaza | **Resuelto por vista** → FR-004, FR-015, BR-002, R22 | No |
| V-02 | ¿Cuántos días para inactividad? | SRS “periodo definido” vs. Historias “90 días” | `admin/usuarios.html` (estados y filtro) | El estado `Inactivo` existe; el umbral no se calcula en el prototipo | **Resuelto por vista + decisión documental** → 90 días (AQ-01 cerrada) | No |
| V-03 | ¿La cuenta la activa el usuario o el admin? | Documento previo vs. A-3/D4 | `admin/usuarios.html` | Selector de estado solo en el panel admin | **Resuelto por vista** → FR-013, BR-003 | No |
| V-04 | ¿El admin crea usuarios? | README antiguo “crear (public o admin)” vs. A-1 | `admin/usuarios.html` | Botones de alta de estudiante y docente | **Resuelto por vista** → FR-011 | No |
| V-05 | ¿Quién crea el emprendimiento? | README “admin crea” vs. D2 | `admin/solicitudes.html`, `estudiante/emprendimientos.html` | Flujo de aprobación con estados y pestaña Paralelos | **Resuelto por vista** → FR-012, BR-004 | No |
| V-06 | ¿“Eliminar” borra físicamente? | FR-008 previo vs. A-4 | `admin/usuarios.html` | Acción “Dar de baja” con confirmación; no borrado directo | **Resuelto por vista** → FR-008, BR-006 | No |
| V-07 | ¿Existe una bandeja única? | Auditoría vs. vistas dispersas | `admin/solicitudes.html` | Tres pestañas y contador de pendientes | **Resuelto por vista** → FR-014 | No |
| V-08 | ¿Hay respaldos en la UI? | FR-009 solo exportación vs. A-7 | `admin/respaldos.html` | Estado, historial, integridad, crear y exportar | **Resuelto por vista** → FR-018 | No |
| V-09 | ¿Las notificaciones son accionables? | FR-005 “enviar” vs. A-8 | `admin/notificaciones.html` | Enlaces de aviso, filtros y “Marcar todo como leído” | **Resuelto por vista** → FR-005, FR-019 | No |
| V-10 | ¿“Registrar avance” duplicado es un bug? | Auditoría vs. D5 | Vistas admin y docente | La acción existe en ambos roles de forma intencional | **Resuelto por vista + decisión** → BR-008 | No |
| V-11 | ¿El estudiante puede completar tareas sin evidencia? | README §3 vs. vista | `estudiante/tarea-detalle.html` | El botón se habilita al adjuntar al menos un archivo | **Resuelto por vista** → FR-023, BR-007 | No |
| V-12 | ¿Hay 71 u 73 pantallas? ¿18 o 19 admin? | README/`VALIDACION-ALCANCE` vs. `prototype/README` | `prototype/index.html` y carpetas | 73 enlaces; 19 admin (incluye Configuración) | **Resuelto por vista** → README corregido | No |
| V-13 | ¿El índice es la entrada del producto? | A-21 vs. prototipo | `prototype/index.html`, `compartido/login.html` | El índice existe como catálogo; el login es la entrada lógica | **Resuelto por vista + decisión documental** → README §8 | No |
| V-14 | ¿El `.py` de `context_admin` está disponible? | Solicitud del usuario vs. repositorio | Búsqueda en `Videos`, `Pictures` y carpeta indicada | Archivo localizado en 3 copias idénticas (SHA-256 `EDCDE30F…836B5872`); 28/28 ítems mapeados | **Resuelto** → AQ-03 cerrada | No |

---

## 6. Matriz de vacíos aplicada

| ID | Hallazgo | Evidencia | Verificado en vista | Destino | Acción | Estado |
|---|---|---|---|---|---|---|
| G-01 | Asignación de asesoría contradictoria | C-1, C-2, C-6 | `admin/asignaciones.html`, `docente/asesoria-detalle.html` | FR-004, FR-015, BR-002, R22, US-015 | Corregir | **Aplicado** |
| G-02 | Inactividad sin umbral | C-3, AQ-01 | `admin/usuarios.html` | FR-007, BR-005, AQ-01 | Corregir | **Aplicado** |
| G-03 | Estados de cuenta ausentes | A-3, D4 | `admin/usuarios.html` | FR-013, BR-003, US-013 | Añadir | **Aplicado** |
| G-04 | CRUD de usuarios ausente | A-1, D1 | `admin/usuarios.html` | FR-011, US-011 | Añadir | **Aplicado** |
| G-05 | Aprobación de emprendimientos ausente | A-2, D2 | `admin/solicitudes.html` | FR-012, BR-004, US-012 | Añadir | **Aplicado** |
| G-06 | Borrado lógico y cascada | A-4, D3 | `admin/usuarios.html` | FR-008, BR-006 | Añadir | **Aplicado** |
| G-07 | Validación y unicidad | A-5 | Formularios admin | FR-016, US-016 | Añadir | **Aplicado** |
| G-08 | Expediente consolidado | A-6, A-14 | `admin/emprendimiento-expediente.html` | FR-017, US-017 | Añadir | **Aplicado** |
| G-09 | Respaldos sin UI | A-7, A-15 | `admin/respaldos.html` | FR-018, US-018 | Añadir | **Aplicado** |
| G-10 | Notificaciones no accionables | A-8 | `admin/notificaciones.html` | FR-005, FR-019, US-019 | Añadir | **Aplicado** |
| G-11 | Solicitudes dispersas | A-13 | `admin/solicitudes.html` | FR-014, US-014 | Añadir | **Aplicado** |
| G-12 | Asesoría directa del admin | A-12 | `admin/asignaciones.html` | FR-015, US-015 | Añadir | **Aplicado** |
| G-13 | Configuración del programa ausente | `configuracion.html` | `admin/configuracion.html` | FR-020, US-020 | Añadir | **Aplicado** |
| G-14 | Eventos y recomendación no documentados | Refactor docente | `docente/evento-detalle-*.html` | FR-021, US-021 | Añadir | **Aplicado** |
| G-15 | Progreso por fases y descarga | Refactor estudiante | `estudiante/plan-trabajo.html` | FR-022, US-022 | Añadir | **Aplicado** |
| G-16 | Evidencia obligatoria | Vista estudiante | `estudiante/tarea-detalle.html` | FR-023, BR-007, US-023 | Añadir | **Aplicado** |
| G-17 | Datos académicos condicionales | Vista estudiante | `estudiante/configuracion.html` | FR-024, US-024 | Añadir | **Aplicado** |
| G-18 | Accesibilidad no medida | Auditoría UI/UX | `lib_ui.py`, vistas | NFR-005 | Añadir | **Aplicado** |
| G-19 | Consistencia de estados | Auditoría V2/V3 | Vistas de los tres roles | NFR-006 | Añadir | **Aplicado** |
| G-20 | Auditabilidad no documentada | A-6 | `admin/configuracion.html` (bitácora) | NFR-007 | Añadir | **Aplicado** |
| G-21 | Responsive no documentado | `lib_css.py` | Vistas por rol | NFR-008 | Añadir | **Aplicado** |
| G-22 | Mantenibilidad del HTML generado | `generar.py` | Generadores | NFR-009 | Añadir | **Aplicado** |
| G-23 | Conteos 71/18 desactualizados | `VALIDACION-ALCANCE.md` | `prototype/index.html` | README §1, §16.6 | Corregir | **Aplicado** |
| G-24 | README §8 incompleto y con typo | README | Tablas de los tres roles | README §8 | Corregir | **Aplicado** |
| G-25 | Prototipo presentado como backend | README/VALIDACION | `prototype/**` | Encabezados y §16 | Aclarar | **Aplicado** |
| G-26 | Duplicidad de avance/diagnóstico | A-19, D5 | Vistas admin/docente | BR-008 | Aclarar | **Aplicado** |
| G-27 | Entrada por `index.html` | A-21 | `index.html`, `login.html` | README §8 | Aclarar | **Aplicado** |
| G-28 | `.py` de `context_admin` | Solicitud del usuario | Archivo localizado e idéntico por hash | AQ-03 | Mapear | **Aplicado** |

---

## 7. Mapa de correcciones y adiciones

### 7.1 Correcciones

| ID | Corrección | Aplicada en |
|---|---|---|
| C-1 | FR-004: Admin asigna; estudiante solicita; docente acepta | `fr_nfr` FR-004 |
| C-2 | BR-002: se elimina “administración o el asesor” | `fr_nfr` BR-002 |
| C-3 | FR-007: 90 días | `fr_nfr` FR-007, BR-005; AQ-01 |
| C-4 | Matriz de trazabilidad BP-002/FR-005 | `fr_nfr` §8 |
| C-5 | Asesorías: coordinadora asigna + docente acepta | `historias` §3, §5, US-015 |
| C-6 | README R22/§3 | `README` R22, §3 Asesorías |
| C-7 | R-01 alineado con CRUD | `fr_nfr` R-01; `README` §2 |

### 7.2 Adiciones

| ID | Adición | Requisito / historia |
|---|---|---|
| A-1 | CRUD de usuarios | FR-011, US-011 |
| A-2 | Aprobación de emprendimiento y paralelo | FR-012, US-012 |
| A-3 | Estados de cuenta | FR-013, US-013 |
| A-4 | Semántica de borrado | FR-008, BR-006 |
| A-5 | Validación de formularios | FR-016, US-016 |
| A-6 | Expediente trazable | FR-017, US-017 |
| A-7 | Respaldos con UI | FR-018, US-018 |
| A-8 | Notificaciones accionables | FR-005, FR-019, US-019 |
| A-9 | Crear usuario | US-011 |
| A-10 | Aprobar emprendimiento | US-012 |
| A-11 | Desbloquear/reactivar cuenta | US-013 |
| A-12 | Asignar asesoría directa | FR-015, US-015 |
| A-13 | Bandeja de solicitudes | FR-014, US-014 |
| A-14 | Consultar expediente | FR-017, US-017 |
| A-15 | Exportar respaldo | FR-018, US-018 |
| A-16 | Admin = CRUD completo | `README` §6 R33–R41 |
| A-17 | Estados de cuenta y dueño único | `README` R34; FR-013 |
| A-18 | Borrado lógico + cascada | `README` R36; BR-006 |
| A-19 | Duplicidad intencional | BR-008; `historias` §7 |
| A-20 | Declaración de alcance estático | Encabezados; `README` §16; `historias` §7 |
| A-21 | Navegación Login → Dashboard | `README` §8 |

**Cobertura:** 28 de 28 ítems entre correcciones y adiciones quedaron mapeados (A-9…A-15 se resolvieron como historias). La equivalencia del archivo se verificó por **SHA-256** y **AQ-03 quedó cerrada**: no hay bloqueos.

---

## 8. Decisiones tomadas

| ID | Decisión | Sustento |
|---|---|---|
| D-01 | El **admin asigna directamente** la asesoría y el **docente acepta/reprograma** | Vistas V-01; C-1, C-2, C-6 |
| D-02 | La inactividad se fija en **90 días** | Historias §7; V-02; C-3 |
| D-03 | Los estados de cuenta son **Limitado → Activo → Inactivo**, con cambio exclusivo del Admin | `admin/usuarios.html`; A-3, D4 |
| D-04 | El **estudiante registra** el emprendimiento y el **Admin lo aprueba**; el paralelo requiere autorización | `admin/solicitudes.html`; A-2, D2 |
| D-05 | El borrado es **lógico y reversible**, con cascada de adjuntos | `admin/usuarios.html`; A-4, D3 |
| D-06 | “Registrar avance” y “Revisar diagnóstico” duplicados son **intencionales** | V-10; A-19, D5 |
| D-07 | El prototipo es **estático**; guardar/descargar/exportar/notificar son simulaciones | `prototype/**`; A-20, D6 |
| D-08 | Se **mantienen los IDs existentes** y se agregan nuevos al final | Regla 2 de la orquestación |
| D-09 | El archivo de correcciones se validó por **hash**; no se asumió contenido distinto | V-14; AQ-03 |
| D-10 | **Todo el trabajo queda local**: sin rama, commit ni push | Instrucción del usuario (2026-10-25) |
| D-11 | El rol **auditor (rol 4)** es de **solo lectura y exportación de reportes**, sin edición ni datos sensibles completos; no se crea FR nuevo | Decisión del usuario; AQ-08; NFR-002, NFR-007, FR-010, FR-017, US-026 |
| D-12 | La **estructura definitiva** es el **modelo textual** de `README.md` §5 (29 tablas, 42 relaciones); los diagramas no son fuente ni se actualizan | Decisión del usuario; AQ-11; modelo textual |
| D-13 | **AQ-06, AQ-07, AQ-09 y AQ-10** se deciden en reunión con la Coordinadora; **no se asumen por defecto** | Instrucción del usuario; dossier §3–§6 |
| D-14 | **AQ-12** se registra como **insumo solicitado**; si no llega, no bloquea ni se inventa contenido | Instrucción del usuario; dossier §8 |

---

## 9. Preguntas abiertas y bloqueos

| ID | Tipo | Descripción | Impacto | Acción requerida |
|---|---|---|---|---|
| AQ-03 | **Cerrada** | Archivo localizado e idéntico por SHA-256 (`EDCDE30F…836B5872`); **28/28 ítems** mapeados | Bajo | Sin acción pendiente |
| AQ-04 | **Cerrada** | La restauración es **operación técnica**; el Admin solo exporta y consulta estado/integridad | Bajo | Sin acción pendiente (`Fuera de alcance / Post-MVP`) |
| AQ-05 | **Cerrada** | **Motivo obligatorio** en el rechazo del acta; notifica al estudiante (BR-009) | Bajo | Validación de UI `Pendiente de backend` |
| AQ-06 | **Abierta** | Campos obligatorios y criterios de validación del emprendedor | Alto | Reunión con la Coordinadora (dossier §3) |
| AQ-07 | **Abierta** | Acceso previo en cuenta `Limitado`; contradicción entre dos vistas | Alto | Reunión con la Coordinadora (dossier §4) |
| AQ-08 | **Cerrada** | Rol auditor: **solo lectura + exportación**, sin edición ni datos sensibles completos; sin FR nuevo | Medio | Implementación `Fuera de alcance / Post-MVP`; US-026 |
| AQ-09 | **Abierta** | Rúbrica del diagnóstico y formato del informe | Alto | Reunión con la Coordinadora (dossier §5) |
| AQ-10 | **Abierta** | Plazo de revisión del acta y efecto completo del rechazo | Medio | Reunión con la Coordinadora (dossier §6) |
| AQ-11 | **Cerrada** | Estructura definitiva = modelo textual (29 tablas, 42 relaciones) | Medio | `README.md` §5; dossier §7 |
| AQ-12 | **Abierta** | `control.pdf` y Excel de preguntas solicitados; no están en el repositorio | Medio | Dossier §8; no bloquea ni se inventa |

> Las preguntas cerradas (**AQ-03, AQ-04, AQ-05, AQ-08 y AQ-11**) tienen decisión y evidencia verificada al **2026-10-25**. Las abiertas (**AQ-06, AQ-07, AQ-09, AQ-10 y AQ-12**) se registran en `docs/dossier-decisiones-pendientes-2026-10.md` y **no se deciden por defecto**.

---

## 10. Control de calidad cruzada

| Verificación | Resultado | Evidencia |
|---|---|---|
| IDs únicos y secuenciales en el SRS | ✅ | 24 FR, 9 NFR, 6 BP, 9 BR, 12 AQ |
| IDs existentes sin renumerar | ✅ | FR-001…010, NFR-001…004, BR-001/002, BP-001…003, AQ-01/02 conservados |
| Historias nuevas con ID | ✅ | US-011 … US-026 (16) |
| Toda historia nueva referencia requisito | ✅ | Matriz §8 de `historias_usuario.md` |
| Todo FR nuevo en la matriz de trazabilidad | ✅ | `fr_nfr_sgemd.md` §8 |
| Conteos coherentes entre documentos | ✅ | 73 pantallas / 19 admin en README, SRS y registro |
| Contradicción “admin asigna” vs. “docente confirma” | ✅ Resuelta | FR-004, FR-015, BR-002, R22, US-015 |
| Inactividad coherente | ✅ | 90 días en FR-007, BR-005, historias §7 y US-013 |
| Alcance estático declarado | ✅ | Encabezados, README §16, historias §7 |
| Typos y tablas del README §8 | ✅ | Tabla admin reconstruida; fila “Gradar/s see Aspirante” eliminada |
| `.py` de `context_admin` mapeado | ✅ | V-14; SHA-256 `EDCDE30F…836B5872`; 28/28 |
| Restauración de respaldos definida | ✅ | AQ-04; FR-018; `README` §3 |
| Motivo obligatorio del acta | ✅ | AQ-05; BR-009; US-025 |
| Rol auditor definido sin FR nuevo | ✅ | AQ-08; NFR-002, NFR-007, FR-010, FR-017; US-026 |
| Estructura definitiva desde el modelo textual | ✅ | AQ-11; `README.md` §5 (29 tablas, 42 relaciones) |
| Diagramas usados como evidencia | ✅ Ninguno | Nota de diagramas desactualizados en README §4 y dossier §10 |
| Código/HTML/generadores modificados | ✅ Ninguno | Solo se editaron `.md` |
| Commit / push / rama | ✅ Ninguno | `HEAD` sin cambios; `git status` local |

---

## 11. Qué **no** se hizo

- No se modificó ningún archivo de `prototype/**`, `core/**`, `agents/**`, `skills/**` ni ningún `.py`.
- No se creó rama, no se hizo `git add`, `git commit` ni `git push`.
- No se publicó nada en GitHub, Stitch ni ningún servicio externo.
- No se ejecutó una prueba de navegador interactiva; la verificación fue estática sobre el HTML y el JS generados.
- No se inventaron decisiones: **AQ-03** se cerró por verificación de archivo, **AQ-04/AQ-05** por decisión expresa del usuario y **AQ-08/AQ-11** por decisión del usuario y modelo textual (2026-10-25). Las preguntas **AQ-06, AQ-07, AQ-09, AQ-10 y AQ-12** quedaron **abiertas**.

---

## 12. Cómo reproducir la verificación

```powershell
# Conteo real de pantallas
Get-ChildItem prototype\admin,prototype\estudiante,prototype\docente,prototype\compartido -Filter *.html |
  Group-Object Directory | Select-Object Name, Count

# Enlaces del índice
(Select-String -Path prototype\index.html -Pattern 'href="[^"]+\.html"').Count

# Estado local (debe mostrar solo los .md modificados/creados)
git status --short
git log -1 --oneline
```

**Script auxiliar usado durante la ejecución:** `C:\Users\storm\AppData\Local\Temp\opencode\verificacion_final.py` (fuera del repositorio).

---

## 13. Cierre

- **Documentos actualizados:** 3.
- **Documentos nuevos:** 3 (orquestación, este registro y el dossier de decisiones).
- **Requisitos nuevos:** 14 FR + 5 NFR + 3 BP + 7 BR.
- **Historias nuevas:** 16 (`US-011` … `US-026`).
- **Correcciones aplicadas:** C-1 … C-7.
- **Adiciones aplicadas:** A-1 … A-21.
- **Preguntas cerradas:** AQ-01 … AQ-05, AQ-08 y AQ-11.
- **Preguntas abiertas:** AQ-06, AQ-07, AQ-09, AQ-10 y AQ-12 (reunión pendiente; sin decisión por defecto).
- **Publicación:** ninguna; **todo permanece local**.

---

## 14. Cierre de preguntas abiertas (2026-10-25)

| AQ | Decisión registrada | Evidencia |
|---|---|---|
| AQ-03 | Archivo de correcciones localizado; copia idéntica por SHA-256 (`EDCDE30F…836B5872`); 28/28 ítems mapeados | `Config-admin/correcciones-adiciones-requisitos.md` |
| AQ-04 | La restauración es **operación técnica**; el Admin solo exporta y consulta estado/integridad | `admin/respaldos.html`; FR-018 |
| AQ-05 | **Motivo obligatorio** en el rechazo del acta, con notificación al estudiante | `admin/solicitudes.html` (modal); BR-009; US-025 |
| AQ-08 | Rol auditor de **solo lectura y exportación**, sin edición ni datos sensibles completos; sin FR nuevo | Decisión del usuario; NFR-002, NFR-007, FR-010, FR-017; US-026 |
| AQ-11 | Estructura definitiva = **modelo textual** (29 tablas, 42 relaciones); diagramas fuera de uso | `README.md` §5; dossier §7 |

> **Pendientes que no cubren estas decisiones (AQ-06, AQ-07, AQ-09, AQ-10, AQ-12):** campos obligatorios del registro, funcionalidades previas a la validación, rúbrica e informe del diagnóstico, plazo y efecto del rechazo del acta, `control.pdf` y Excel de preguntas. Se tratan en `docs/dossier-decisiones-pendientes-2026-10.md`; **no se cierran sin decisión escrita**.

---

## 15. Cierre documental del 2026-10-25

### 15.1 Entregables

| Documento | Tipo | Estado |
|---|---|---|
| `README.md` | Actualizado | Roles (R-04), API del auditor, decisiones, MVP, criterios, §16.2–§16.6 |
| `docs/fr_nfr_sgemd.md` | Actualizado | R-04, FR-010, FR-017, NFR-002, NFR-007, AQ-06 … AQ-12, §10–§12 |
| `docs/historias_usuario.md` | Actualizado | US-026, matriz, §7 y §9 |
| `docs/orquestacion-actualizacion-requisitos-2026-10.md` | Nuevo | Método y cierre de preguntas |
| `docs/registro-actualizacion-requisitos-2026-10.md` | Nuevo | Evidencia, decisiones y este cierre |
| `docs/dossier-decisiones-pendientes-2026-10.md` | Nuevo | Hojas de decisión y anexos |

### 15.2 Conteos finales

| Elemento | Valor |
|---|---|
| FR | **24** |
| NFR | **9** |
| BP | **6** |
| BR | **9** |
| AQ registradas | **12** (7 cerradas: AQ-01…AQ-05, AQ-08, AQ-11; 5 abiertas: AQ-06, AQ-07, AQ-09, AQ-10, AQ-12) |
| Historias nuevas | **16** (US-011 … US-026) |
| Pantallas | **73** (4 + 27 + 23 + 19) |

### 15.3 Límites respetados

- Solo se editaron archivos `.md`.
- No se tocó `prototype/**`, HTML, generadores ni diagramas.
- No se creó rama, commit ni push.
- No se decidió por defecto ninguna pregunta abierta.
- No se usó ningún diagrama como evidencia.

*Fin del registro.*
