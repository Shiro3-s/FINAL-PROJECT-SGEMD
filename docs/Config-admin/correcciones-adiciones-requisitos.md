# Correcciones y Adiciones a los Requisitos — SGEMD

> **Origen:** puntos ciegos detectados en [`auditoria-ui-ux-admin.md`](./auditoria-ui-ux-admin.md) y confirmados con evidencia en [`prueba-ui-ux-admin.md`](./prueba-ui-ux-admin.md).
> **Objetivo:** registrar, de forma accionable, **CORRECCIONES** (texto vigente que hay que ajustar) y **ADICIONES** (requisitos/vistas que faltan) para los documentos fuente del proyecto.
> **Documentos destino:** `FINAL-PROJECT-SGEMD/docs/fr_nfr_sgemd.md`, `FINAL-PROJECT-SGEMD/docs/historias_usuario.md`, `FINAL-PROJECT-SGEMD/README.md`.
> **Estado:** propuesta. **No** se han modificado los documentos fuente (decisión del interesado). Los textos aquí son el "después" propuesto.
> **Ubicación:** `SGEMD-JOEL/correcciones-adiciones-requisitos.md` (fuera de `FINAL-PROJECT-SGEMD/`).

---

## 0. Decisiones que gobiernan estas adiciones

| ID | Decisión | Impacto |
| --- | --- | --- |
| D1 | El **Admin CREA usuarios** (docente/estudiante) | + alta real en Usuarios |
| D2 | **Estudiante crea, Admin aprueba** el emprendimiento (incl. paralelo) | + flujo de aprobación |
| D3 | Borrado **lógico + cascada** de archivos (FR-008) | + semántica de borrado |
| D4 | Estados **Limitado → Activo → Inactivo**, cambio **solo Admin** | + desbloqueo/reactivación |
| D5 | "Registrar avance" / "Revisar diagnóstico" = **ambos roles** | se **documenta** la duplicidad |
| D6 | Alcance del prototipo = **cosmético**, sin backend | se **declara** la limitación |

---

## 1. `docs/fr_nfr_sgemd.md`

### 1.1 Correcciones

| # | Tipo | Requisito | Antes → Después | Fuente |
| --- | --- | --- | --- | --- |
| C-1 | CORRECCIÓN | **FR-004** | "El Administrador asigna… apruebe/gestione cruces; prohibido el agendamiento libre del estudiante" → "**El Admin crea y asigna asesorías directamente** (sin flujo de permiso de horario); el **estudiante solicita**; el **docente acepta** las que le correspondan; se mantiene prohibida la **integración con calendarios externos** y el agendamiento automático." | Auditoría §5.1.1 · Prueba T5 |
| C-2 | CORRECCIÓN | **BR-002** | "…cruces confirmados manualmente por **administración o el asesor**" → "**Admin con asignación directa** + **Docente confirma/acepta**; se elimina la ambigüedad 'administración o el asesor'." | Auditoría §5.1.1 |
| C-3 | CORRECCIÓN | **FR-007** (inactividad) | "periodo de tiempo definido" → "**90 días (3 meses)** sin actividad". | AQ-01 · `historias_usuario.md` §7 |
| C-4 | CORRECCIÓN | **Matriz de trazabilidad §8 (BP-002, FR-005)** | Ajustar filas para reflejar el **rol dual** (Admin asigna / Docente acepta) y las notificaciones correspondientes. | Auditoría §5.1.1 |

### 1.2 Adiciones

| # | Requisito nuevo | Enunciado propuesto | Fuente |
| --- | --- | --- | --- |
| A-1 | **CRUD de usuarios por el Admin** | "El sistema permitirá al Administrador **crear, editar, activar/desactivar y dar de baja lógica** las cuentas de **estudiante y docente**, asignando el rol al momento del alta." | R-01 · Prueba T1/T8 · K-01 |
| A-2 | **Aprobación de emprendimiento** | "El **estudiante registra** su emprendimiento y el **Admin lo aprueba/rechaza**; el estado inicial es **Pendiente de aprobación**. El Admin autoriza el **segundo emprendimiento paralelo**." | D2 · Prueba T4 · K-04 |
| A-3 | **Estados de cuenta** | "La cuenta tendrá los estados **Limitado → Activo → Inactivo**. **Solo el Admin** desbloquea (Limitado→Activo) y reactiva (Inactivo→Activo, tras 90 días)." | D4 · AQ-02 · S-01/S-02 |
| A-4 | **Semántica de borrado** | "Eliminar/Desactivar/Ocultar son **bajas lógicas reversibles** con confirmación. Al **eliminar** un emprendimiento/usuario, sus **archivos adjuntos (FR-008) se eliminan en cascada**." | D3 · V-06/V-07 |
| A-5 | **Validación de formularios** | "Toda alta/edición usará **formularios con validación** de campos obligatorios y de **unicidad** (documento, correo, docente no repetido, tope de carga de **12 h**)." | V-01/V-02/V-08 |
| A-6 | **Expediente trazable (FR-006)** | "El expediente del emprendimiento reunirá **asesorías + diagnósticos + seguimientos** en una sola vista con **log de auditoría** de cambios." | P-09/P-10 · FR-006 |
| A-7 | **Respaldos con UI (FR-009/NFR-004)** | "El Admin dispondrá de **Exportar base de datos (CSV/Excel)** y verá el **estado del backup diario**." | Prueba T9 |
| A-8 | **Notificaciones accionables (FR-005)** | "El centro de notificaciones abrirá el objeto referido (asesoría, solicitud, evento) y permitirá marcarlas como leídas." | Prueba T10 · E-06 |

---

## 2. `docs/historias_usuario.md`

### 2.1 Correcciones

| # | Tipo | Historia | Ajuste | Fuente |
| --- | --- | --- | --- | --- |
| C-5 | CORRECCIÓN | Asignación de asesorías (§3/§5) | Mantener que **la coordinadora asigna y cruza horarios manualmente** y **agregar** la **aceptación por el docente**. | Auditoría §5.1.1 |

### 2.2 Adiciones (historias nuevas del rol Coordinadora)

| # | Historia (formato "Como… quiero… para…") | Criterios de aceptación | Fuente |
| --- | --- | --- | --- |
| A-9 | **Crear usuario** — "Como coordinadora quiero **crear cuentas de estudiante/docente** para habilitar el acceso." | Se crea con rol y estado inicial; validación de unicidad; queda Activo o Limitado. | D1 · T1/T8 |
| A-10 | **Aprobar emprendimiento** — "…quiero **aprobar o rechazar** el emprendimiento registrado por el estudiante, incluido el **paralelo**." | Estados Pendiente→Aprobado/Rechazado; notifica al estudiante. | D2 · T4 |
| A-11 | **Desbloquear/Reactivar cuenta** — "…quiero **desbloquear** un perfil Limitado y **reactivar** uno Inactivo." | Transiciones registradas; bloquea "Asignar docente" hasta acta firmada (BR-001). | D4 · T2/T7 |
| A-12 | **Asignar asesoría directa** — "…quiero **crear y asignar una asesoría** sin pedir permiso de horario." | Admin crea (emprendimiento+docente+fecha); notifica a estudiante y docente. | D3 · T5 |
| A-13 | **Bandeja de solicitudes** — "…quiero **ver y resolver en un solo lugar** desbloqueos, aprobaciones y citas pendientes." | Contador con pendientes; cada ítem se resuelve con confirmación + toast. | Auditoría §4 (sugerencia 3) |
| A-14 | **Consultar expediente** — "…quiero **ver el expediente completo** de un emprendimiento." | Reúne asesorías, diagnósticos y seguimientos; trazable. | A-6 · FR-006 |
| A-15 | **Exportar respaldo** — "…quiero **exportar la base** (CSV/Excel) y ver el estado del backup." | Descarga inmediata; panel de estado. | A-7 · T9 |

---

## 3. `FINAL-PROJECT-SGEMD/README.md`

### 3.1 Correcciones

| # | Tipo | Sección | Ajuste | Fuente |
| --- | --- | --- | --- | --- |
| C-6 | CORRECCIÓN | **R22 / §3** | "solicita el estudiante; **confirma el docente**" → "el estudiante **solicita**; **el Admin puede asignar directamente**; el docente **confirma/acepta**". | Auditoría §5.1.1 |
| C-7 | CORRECCIÓN | **R-01** | Alinear el enunciado de que el Admin **gestiona** usuarios con la capacidad explícita de **crear/editar/eliminar**. | D1 · C-1 |

### 3.2 Adiciones

| # | Tipo | Contenido a agregar | Fuente |
| --- | --- | --- | --- |
| A-16 | ADICIÓN | Regla: **Admin = CRUD completo** sobre Usuarios, Emprendimientos (aprobación), Asignaciones, Asesorías, Eventos y Plan/Tareas. | R-01 · K-* |
| A-17 | ADICIÓN | Regla de **estados de cuenta** (Limitado/Activo/Inactivo) y **dueño único** del cambio (Admin). | D4 |
| A-18 | ADICIÓN | Regla de **borrado lógico + cascada FR-008**. | D3 |
| A-19 | ADICIÓN | Regla de **duplicidad intencional**: "Registrar avance" y "Revisar diagnóstico" existen para **Admin y Docente** (documentar para evitar tratarlo como bug). | D5 |
| A-20 | ADICIÓN | **Declaración de alcance:** "El prototipo es **estático/cosmético, sin backend**; las operaciones de guardado son simuladas." | D6 |
| A-21 | ADICIÓN | Nota de **navegación:** reemplazar el `index.html` como puerta de entrada por **Login → Dashboard por rol** (ver Auditoría §1.1). | G-01 |

---

## 4. Riesgos de consistencia a vigilar (transversal)

| ID | Riesgo | Acción |
| --- | --- | --- |
| R-1 | **Roles:** prototipo usa claves (`administrador`) vs doc `Roles_idRoles1` (1/2/3) | Unificar al conectar backend |
| R-2 | **Badges/estados** inconsistentes entre vistas | Normalizar `Limitado/Activo/Inactivo/Pendiente de aprobación` |
| R-3 | **Exportaciones dispersas** | Centralizar en **Reportes** y **Respaldos** |
| R-4 | **FR-004/BR-002** resuelto solo en el informe, no en fuentes | Aplicar C-1/C-2/C-4/C-5/C-6 |
| R-5 | **Kanban de eventos roto** (`.kan-col` vs `.k-col`) | Corregir clases CSS/JS |

---

## 5. Correlación documental

```
prompt_de_auditoria_ui_ux.md        (encargo)
        │
        ▼
auditoria-ui-ux-admin.md            (§1–§4 deber ser · §5.1.1 cambio FR-004/BR-002)
        │  complementada por
        ▼
prueba-ui-ux-admin.md               (evidencia: 0/11 tareas completables, hallazgos K/V/S/P/C/L/E/G)
        │  genera
        ▼
correcciones-adiciones-requisitos.md (ESTE documento → aplicar a fr_nfr · historias_usuario · README)
```

---

*Fin. Vive fuera de `FINAL-PROJECT-SGEMD/`. Ningún documento fuente fue modificado.*
