# Auditoría UI/UX — Rol ADMINISTRADOR (Coordinadora)

> **Alcance:** exclusivamente el rol **Administrador (Coordinadora, R-01)** del prototipo SGEMD.
> **Base:** `FINAL-PROJECT-SGEMD/README.md`, `docs/historias_usuario.md`, `docs/fr_nfr_sgemd.md`, estructura de vistas y código del prototipo (`prototype/paginas_admin.py`, `prototype/lib_ui.py`, `prototype/index.html`).
> **Ubicación de este informe:** `SGEMD-JOEL/auditoria-ui-ux-admin.md` (fuera de `FINAL-PROJECT-SGEMD/`).

---

## 1. Diagnóstico del prototipo

### 1.1 Por qué usar el `index` actual es un error de UX
- `prototype/index.html` es una **lista plana de enlaces** a todas las vistas (50 pantallas, 3 roles + auth). No hay flujo, jerarquía ni punto de entrada por rol. Para presentar el proyecto al cliente, esto se percibe como un "mapa de archivos", no como un producto. Un producto real inicia en **Login → Dashboard del rol**; el índice no debe ser la puerta de entrada.
- No comunica el **recorrido del usuario** (journey). El evaluador no sabe qué pantalla sigue a cuál, ni qué acciones son posibles en cada una.

### 1.2 Fallas de navegación específicas del Administrador
1. **Menú lateral plano que satura.** El sidebar del admin declara **11 ítems sin categorías** (`lib_ui.py` → `NAV["administrador"]`): Inicio, Gestión de perfiles, Emprendimientos, Seguimiento, Asignaciones, Diagnósticos, Eventos, Asesorías, Reportes, Notificaciones, Perfil.
2. **Vistas huérfanas.** Existen páginas del admin que **no están en ningún menú** y solo se alcanzan por enlaces internos o por el `index`: `usuario-docente`, `usuario-estudiante`, `emprendimiento-plan`, `seguimiento-dashboard`, `comentarios`, `evento-form`, `asignar-emprendimiento`. Son callejones sin salida o puntos de entrada invisibles.
3. **Acciones "de mentira" (dead-ends de CRUD).** `_btn(...)` usa `href="#"` por defecto, por lo que botones como *Guardar*, *Exportar*, *Generar* y *Confirmar asignación* no llevan a ningún lado. Acciones de tabla como *Ver detalle*, *Editar docente*, *Editar estudiante*, *Asignar* y *Seleccionar* (`_acc(_b(...))`) **no tienen destino**.
4. **No existe ni un solo modal/diálogo.** Todo el CRUD debería resolverse en capas intermedias (crear/editar/confirmar/eliminar); hoy no hay ninguna. Ver/editar siempre implicaría salir de la pantalla.
5. **Migajas de pan muertas.** `shell()` genera `href="#"` en todos los niveles salvo el último → no navegan.
6. **Controles inertes:** buscador global (solo placeholder), paginación decorativa (`paginas()`), campana de notificaciones sin enlace, checkboxes de selección masiva sin barra de acciones.
7. **Requisitos del Admin sin gancho de UI:** desbloquear perfil limitado (AQ-02/BR-001), aprobar emprendimiento paralelo (R-01), semaforización de inactivos (FR-007), respaldo de BD (FR-009/NFR-004) y CRUD de asesorías no tienen vista ni acción.
8. **Transiciones de estado ausentes:** no hay pantalla de "no autorizado (403)", "sesión expirada (8 h)", confirmación de logout; login redirige directo al dashboard.
9. **Capas de acción desconectadas:** `ICONO_ACCION` (`lib_ui.py`) ya define intenciones (`ver/editar/aprobar/borrar/descargar`), pero ningún JS las consume para abrir modales o navegar.

---

## 2. Inventario de brechas (Gap Analysis)

### 2.1 Vistas actuales que sobran o están mal enfocadas

| Vista actual | Problema | Acción propuesta |
| --- | --- | --- |
| `index.html` (índice) | Reemplaza el flujo por un mapa de archivos | **Eliminar como navegación**; dejar login como entrada |
| `usuario-docente` / `usuario-estudiante` | Páginas separadas de "creación" con botón Guardar muerto | Convertir en **modales** de crear/editar usuario |
| `seguimiento` y `seguimiento-dashboard` | Dos módulos de seguimiento solapados | Unificar dentro del **detalle del emprendimiento (pestaña Seguimiento)** |
| `emprendimiento-plan` | "Plan" suelto, fuera del menú | Fusionar en pestaña **Plan de trabajo/Tareas** del detalle |
| `comentarios` | Propósito difuso (¿seguimiento? ¿mensajes?) | Fusionar en Seguimiento o retirar |
| `asignar-emprendimiento` | Wizard huérfano con "Confirmar asignación" muerto | **Modal** de asignación disparado desde Usuarios/Emprendimientos |
| `diagnosticos`, `eventos`, `asesorias`, `reportes` | Listas planas sin filtros ni CRUD | Rediseñar con **filtros + acciones CRUD** |

### 2.2 Vistas / capas faltantes obligatorias (Admin)

**Colas y bandejas de trabajo**
- **Bandeja "Solicitudes pendientes"** que agrupe y permita resolver: (a) **desbloqueo de perfil limitado** (AQ-02/BR-001), (b) **aprobación de emprendimiento paralelo** (R-01), (c) **citas por confirmar/asignar** (FR-004).
- **Listado de estudiantes inactivos** con semáforo y acción *reactivar/contactar* (FR-007, umbral **90 días**).

**CRUD en modales (rol principal)**
- **Crear/editar usuario** (estudiante y docente) con asignación de **rol**, activar/desactivar, subir avatar — y opción de **asignar** en el mismo flujo.
- **Crear/editar/eliminar emprendimiento** (con propietario-estudiante, etapa, sector, redes).
- **Crear/editar/eliminar asignación** (mentor + estudiante + emprendimiento opcional), reasignar.
- **CRUD de asesorías**: el Admin puede **crear/asignar directamente sin permiso de horario**; reprogramar y cancelar.
- **CRUD de eventos** (ya existe `evento-form`; falta listado con acciones) y de **tareas/plan**.

**Drill-down e informes**
- **Pantalla "Seleccionar emprendimiento"** (picker) que fija el contexto y abre el **detalle con pestañas**: Resumen · Seguimiento · Asesorías · Tareas · Diagnósticos · Archivos · Reportes.
- **Barra de filtros persistente** (por emprendimiento, profesor, estudiante) en las vistas globales.
- **Reportes** con **filtro por proyecto específico** + exportar (PDF/CSV/Excel).
- **Respaldos**: botón **"Exportar base de datos (CSV/Excel)"** (FR-009) y estado de **backup diario** (NFR-004).

**Capas del sistema**
- **Modales de confirmación** (eliminar, aprobar, desbloquear, cancelar cita) + **toasts** de resultado.
- **Pantallas de estado**: No autorizado (403), Sesión expirada, Confirmación de logout.

---

## 3. Nuevo Mapa de Navegación (Admin User Flow)

### 3.1 Menú lateral propuesto (colapsable: categoría → subcategoría)

```
● Inicio (Dashboard global)
● Solicitudes  ⟵ bandeja de pendientes (badge con contador)
 │   ├─ Desbloqueos de perfil
 │   ├─ Emprendimientos paralelos
 │   └─ Citas por asignar
▾ Emprendimientos
 │   ├─ Emprendimientos            (listado + CRUD + filtro)
 │   ├─ Seguimiento
 │   ├─ Plan de trabajo / Tareas
 │   ├─ Diagnósticos
 │   └─ Reportes                   (filtro por proyecto + export)
▾ Usuarios
 │   ├─ Estudiantes               (CRUD + estado Limitado/Inactivo)
 │   ├─ Docentes                  (CRUD)
 │   └─ Asignaciones              (CRUD + reasignar)
● Asesorías                        (CRUD + filtros profesor/estudiante/emprendimiento)
● Eventos                          (CRUD + asistencia)
● Notificaciones
▾ Configuración
 │   ├─ Respaldos                 (Exportar BD CSV/Excel + backup diario)
 │   └─ Perfil del admin
```

> Regla: la categoría se **colapsa** para no saturar; dentro de un emprendimiento se navega por **pestañas** (drill-down), no volviendo al menú.

### 3.2 Recorrido paso a paso (journey del Administrador)

```
[Login] → valida credenciales → guarda token (JWT 8 h)
   └─ redirige → [Dashboard Admin]

[Dashboard Admin]
   ├─ Métricas globales (usuarios por rol, emprendimientos, asignaciones activas, tareas, asesorías, distribución por etapa)
   ├─ Tarjetas de alerta: Solicitudes pendientes · Estudiantes inactivos · Citas por asignar
   └─ Clic en "Solicitudes" → [Bandeja de solicitudes]
        ├─ Desbloquear perfil → modal confirmar → badge "Limitado" → "Activo"
        ├─ Aprobar emprendimiento paralelo → modal confirmar → alta del 2.º emprendimiento
        └─ Asignar cita → [Asesorías] (Admin asigna directamente)

[Menú → Emprendimientos → Emprendimientos]
   └─ Filtro por proyecto/sector/etapa + botón "Crear emprendimiento" (modal)
        └─ Clic en una fila "Ver detalle" → [Detalle del emprendimiento]
             ├─ Pestañas: Resumen · Seguimiento · Asesorías · Tareas · Diagnósticos · Archivos · Reportes
             ├─ "Asignar docente" (modal, respeta BR-001: requiere acta firmada)
             └─ "Exportar" → [Reportes] (filtrado a este proyecto)

[Menú → Usuarios → Estudiantes]
   ├─ "Crear estudiante" (modal) · "Editar" (modal) · "Desbloquear" (si Limitado)
   └─ Filtro "Inactivos (90 días)" → lista → "Reactivar/Contactar"

[Menú → Asesorías]
   ├─ Filtros: Profesor · Estudiante · Emprendimiento · Estado
   └─ "Crear asesoría" (modal: emprendimiento + docente + fecha/hora) → confirmar
        └─ Notificación In-App al estudiante y al docente

[Menú → Configuración → Respaldos]
   └─ "Exportar base de datos (CSV/Excel)" → descarga inmediata (FR-009)
        └─ Panel de estado del backup diario (NFR-004)

[Topbar] → Logout → modal confirmar → limpia token → [Login]
[Token expirado] → [Sesión expirada] → [Login]
[Rol sin permiso] → [No autorizado (403)]
```

---

## 4. Sugerencias de Modelado UX

1. **Menú jerárquico colapsable + contexto pegajoso.** Agrupar en categorías colapsables (Emprendimientos, Usuarios, Configuración) con las subcategorías ocultas por defecto, y conservar **breadcrumbs vivos** (`Inicio › Emprendimientos › Café Andino › Seguimiento`). Así el admin nunca pierde el contexto ni se satura el sidebar (alineado con NFR-001, máx. 3 clics).

2. **Patrón maestro-detalle con drill-down + filtros persistentes.** Una vista de "Seleccionar emprendimiento" que fija el contexto y abre un **detalle con pestañas**, complementada con una **barra de filtros fija** (proyecto/profesor/estudiante) que se conserva entre pantallas. Reduce saltos y evita listas planas que obligan a "volver atrás".

3. **"Bandeja de pendientes" como centro de gravedad del admin.** Un solo punto (dashboard + ícono en el menú, con contador) que reúne desbloqueos, aprobaciones paralelas y citas por asignar, cada uno resoluble con **modal de confirmación + toast**. Convierte las tareas dispersas del rol (R-01, AQ-02, FR-004, FR-007) en un flujo de trabajo profesional y trazable.

---

## 5. Anexo — Cambios e inconsistencias de requisitos

> **Motivo:** se detectó una **falencia/conflicto** en los requisitos sobre **quién gobierna el agendamiento de asesorías**. Debe resolverse en los documentos fuente antes de construir el backend y el mapa de navegación definitivo.

### 5.1 Inconsistencia: dueño del agendamiento de asesorías

| Fuente | Qué afirma | Ubicación |
| --- | --- | --- |
| **FR-004** | El **Administrador** asigna manualmente docentes y **aprueba/gestiona los cruces** de espacios. Prohíbe el agendamiento libre del estudiante. | `docs/fr_nfr_sgemd.md` §4 |
| **BR-002** | "los cruces serán confirmados manualmente por **administración o el asesor**". | `docs/fr_nfr_sgemd.md` §6 |
| **README R22 / §3** | "solicita el estudiante; **confirma el docente**". | `README.md` |
| **Historias de Usuario** | "La **coordinadora** asigna y cruza los horarios manualmente". | `docs/historias_usuario.md` §3 y §5 |
| **Decisión nueva (acordada)** | El **docente puede aceptar** la asesoría, **pero el Admin puede asignar directamente sin necesidad de permiso de horario**. | Respuesta del interesado |

**Conflicto:** los documentos se contradicen entre **Admin dueño de la agenda** (FR-004, BR-002, Historias) y **Docente confirma** (README R22/§3).

#### 5.1.1 Cambio exacto requerido — Antes → Después

**FR-004 — Asignación y Agendamiento** (`docs/fr_nfr_sgemd.md` §4)

- **ANTES (texto vigente):**
  > "El sistema deberá incluir un módulo donde el Administrador asigne manualmente docentes a estudiantes y apruebe/gestione los cruces de espacios para asesorías. […] Prohibido el agendamiento libre o automático por parte del estudiante."

- **DESPUÉS (texto propuesto):**
  > "El sistema deberá incluir un módulo donde el **Administrador cree y asigne asesorías de forma directa** (emprendimiento + docente + fecha/hora), **sin requerir un flujo de permiso de horario**. El **estudiante podrá solicitar** asesorías, y el **docente podrá aceptar** las asignadas/solicitadas que le correspondan. Se mantiene **prohibido el agendamiento automático o la integración con calendarios externos** por parte del estudiante."

- **Rol Relacionado:** Administrador (asignación directa) **+ Docente (aceptación)**.
- **Regla de Negocio asociada:** BR-002 (actualizada) + BR-001 (el acta sigue bloqueando la asignación definitiva).

**BR-002 — Gestión de Agenda** (`docs/fr_nfr_sgemd.md` §6)

- **ANTES (texto vigente):**
  > "Se prohíbe la integración con calendarios externos (Google/Outlook) y el agendamiento libre por estudiantes; la plataforma alojará toda la lógica y los cruces serán confirmados manualmente por **administración o el asesor**."

- **DESPUÉS (texto propuesto):**
  > "Se prohíbe la integración con calendarios externos (Google/Outlook) y el agendamiento automático por estudiantes. La plataforma alojará toda la lógica de agenda: **el Administrador tiene asignación directa** de asesorías y **el Docente participa confirmando/aceptando** las que le correspondan. Se elimina la ambigüedad 'administración o el asesor', fijando responsabilidades únicas."

**Alineación obligatoria de documentos dependientes:**
- **`README.md`** — R22 y §3 ("solicita el estudiante; confirma el docente") → ajustar a "el estudiante solicita; **el Admin puede asignar directamente**; el docente confirma/acepta".
- **`docs/historias_usuario.md`** — §3 y §5 ("la coordinadora asigna y cruza los horarios manualmente") → mantener la asignación por coordinadora y **agregar** la aceptación por docente.
- **`docs/fr_nfr_sgemd.md`** — Matriz de trazabilidad (§8, fila BP-002) y FR-005 (notificaciones "al confirmar una asesoría") → revisar que sigan siendo coherentes con el nuevo rol dual.

### 5.2 Ambigüedades resueltas durante la auditoría

| ID | Ambigüedad | Resolución acordada |
| --- | --- | --- |
| **AQ-01** | Días exactos para semaforización por inactividad | **90 días (3 meses)** — confirmado en `historias_usuario.md` §7. Actualizar `fr_nfr_sgemd.md` para reflejarlo (hoy dice "periodo de tiempo definido"). |
| **AQ-02** | Cómo se habilita la plataforma tras la reunión | Control **manual del Admin** vía acción **"Desbloquear perfil"** (estado *Limitado → Activo*). |
| **BR-001 / Acta** | Quién gestiona el acta de confidencialidad | El **paso "pendiente por firma" es exclusivo del Estudiante**; el Admin solo lo refleja como **estado/compuerta** (bloquea "Asignar docente" hasta estar firmada). |

### 5.3 Riesgos de consistencia a vigilar
- **Roles:** el prototipo usa claves (`administrador`) y la documentación usa `Roles_idRoles1` (1=Admin, 2=Estudiante, 3=Docente). Unificar al conectar el backend.
- **Estados de dato en UI:** normalizar badges de **Limitado**, **Inactivo**, **Pendiente de aprobación** (paralelo/cita) y **Activo** en todas las vistas.
- **Exportaciones dispersas:** centralizar los botones "Exportar" (hoy repartidos en dashboard/emprendimientos/seguimiento/diagnósticos) en **Reportes** y **Respaldos**, evitando duplicidad.

---

## 6. Documentos relacionados

- [`prueba-ui-ux-admin.md`](./prueba-ui-ux-admin.md) — **evidencia empírica**: recorrido como Admin (Niveles 1/2/3, guion T1–X1). Resultado: **0/11 tareas completables** y hallazgos `K/V/S/P/C/L/E/G`.
- [`correcciones-adiciones-requisitos.md`](./correcciones-adiciones-requisitos.md) — **puntos ciegos** a aplicar en `docs/fr_nfr_sgemd.md`, `docs/historias_usuario.md` y `README.md`.

---

*Fin del informe. Este documento vive fuera de `FINAL-PROJECT-SGEMD/` por decisión del interesado.*
