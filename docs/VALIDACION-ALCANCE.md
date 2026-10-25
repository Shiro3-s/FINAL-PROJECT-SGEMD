# Validación de alcance — qué falta por implementar

> **Objetivo:** validar **qué falta** comparando la **spec maestra actualizada** (`README.md`, 2026-10-25, reconciliado con el prototipo) contra el **estado real del repositorio**.
>
> **Criterio:** este documento mide la distancia entre el **prototipo** y la implementación real, no entre dos documentos.
>
> **Base de la spec:** `README.md` §3 (funcionalidades), §5 (modelo de datos), §6 (reglas), §7 (API), §8 (frontend), §11–§13 (MVP y criterios) y §16 (alcance ampliado).
>
> **Estado real verificado:**
> - `prototype/` → **73 pantallas HTML estáticas** (4 acceso + **27** estudiante + 23 docente + **19** admin), generadas desde Python. **No hay backend**: login simulado, sesión en `localStorage`, "guardar/descargar" son simulaciones.
> - `core/`, `agents/`, `skills/`, `interfaces/`, `config/`, `tools/`, `evaluations/` → **framework de agentes** (scaffolding de IA), **no** es la aplicación SGEMD.
> - **No existe** backend (Node/Express), frontend React, ni base de datos PostgreSQL.
> - Documentación: completa (`docs/`, `CORRECCIONES-VISTAS-ESTUDIANTE.md`).

**Leyenda:** ✅ existe · 🟡 parcial/simulado · ❌ falta · 🆕 requisito nuevo (no estaba antes de la actualización).

---

## 0. Resumen en una frase

La spec y el prototipo (UI) están **avanzados**; **toda la capa real** (backend, API, base de datos y frontend React) **está por construir**. Del alcance ampliado, **8 elementos** siguen sin pantalla o sin lógica en el prototipo; el resto está representado como interfaz.

## 1. Estado por capa

| Capa | Estado | Detalle |
| ---- | ------ | ------- |
| **Spec / documentación** | ✅ | `README.md` completo y actualizado (§16). |
| **Prototipo (UI estática)** | 🟡 | 73 pantallas navegables, sin lógica real ni datos. |
| **Frontend real (React)** | ❌ | No existe. |
| **Backend (Node + Express)** | ❌ | No existe. |
| **API REST** | ❌ | Definida en §7; sin implementar. |
| **Base de datos (PostgreSQL)** | ❌ | Modelo en §5 (**41 tablas** = 27 de negocio + 14 catálogos); sin `schema.sql` montado. |
| **Seguridad (JWT/bcrypt/OTP)** | ❌ | Real; el prototipo solo lo simula. |

## 2. Validación módulo por módulo

| Módulo | Spec (§) | Prototipo (UI) | Backend/API | Falta principal |
| ------ | -------- | -------------- | ----------- | --------------- |
| Login | 3 | ✅ (simulado) | ❌ | Autenticación real con JWT. |
| Registro | 3 | ✅ (simulado) | ❌ | Alta real + hash bcrypt. |
| Verificación OTP | 3 | ✅ (simulado) | ❌ | OTP real 8 díg. / 5 min por SMTP. |
| Recuperar contraseña | 3 | ✅ (simulado) | ❌ | Flujo real por correo. |
| **Correo de bienvenida** 🆕 | 3, 16 | ❌ | ❌ | Envío automático tras el registro. |
| **Validación y activación** 🆕 | 3, 6, 16 | 🟡 (texto "cuenta Limitada") | ❌ | Flujo completo + tabla `habilitaciones`. |
| Usuarios y roles | 2, 3 | ✅ | ❌ | CRUD real + control por rol. |
| **Rol de auditor** 🆕 | 2, 16 | ❌ | ❌ | Alcance por definir; no implementar aún. |
| Emprendimientos | 3 | 🟡 (lista, detalle y edición; **sin alta**) | ❌ | CRUD + alta desde el panel del Administrador + alcance por propietario. |
| Asignaciones | 3 | ✅ | ❌ | Asignación docente↔estudiante↔empr. |
| Seguimiento | 3 | ✅ | ❌ | Notas reales + autor. |
| Asesorías | 3 | ✅ | ❌ | Solicitud del estudiante, asignación del Admin, confirmación/reprogramación docente + notificaciones. |
| Tareas / plan de trabajo | 3 | ✅ | ❌ | Estados, prioridad, calificación y % de avance derivados de BD. |
| **Diagnóstico *data-driven*** 🆕 | 3, 5 | 🟡 (5 secciones / 22 preguntas fijas) | ❌ | Banco de preguntas desde **Excel** y cálculo del puntaje. |
| **Caracterización y valoración** 🆕 | 3, 5, 16 | 🟡 (resultados visibles, sin cálculo) | ❌ | Generación automática + feedback. |
| **Informe descargable** 🆕 | 3, 7 | 🟡 (botón falso) | ❌ | Generación real (PDF). |
| **Acta de compromiso** 🆕 | 3, 6, 16 | ❌ (**no hay vista**) | ❌ | Subir + revisar + ficha `actas`. |
| **Notificaciones (disparadores)** 🆕 | 3, 6, 7 | 🟡 (bandeja con filtros, sin emisión) | ❌ | Triggers + tabla `notificaciones`. |
| Eventos | 3 | ✅ | ❌ | CRUD + registro/asistencia. |
| Dashboards | 3 | ✅ (datos falsos) | ❌ | Métricas reales por rol. |
| Progreso | 3 | ✅ | ❌ | Derivado de etapa + tareas. |
| Gestión de archivos | 3 | 🟡 (carga simulada en tareas y avances) | ❌ | Subida/descarga real (hasta 500 MB) + borrado en cascada. |
| Reportes / exportar | 8 | 🟡 (`admin/reportes.html`) | ❌ | Exportación real (CSV/Excel/PDF). |
| Catálogos | 7 | 🟡 (valores fijos en el generador) | ❌ | Endpoints de solo lectura (14 catálogos). |
| **Bandeja de solicitudes** 🆕 | 3, 7 | ✅ | ❌ | Desbloqueos, paralelos y citas en una sola cola. |
| **Configuración del programa** 🆕 | 3, 7 | ✅ | ❌ | Parámetros, sedes y bitácora. |
| **Respaldos** 🆕 | 3, 7 | ✅ | ❌ | Creación real, integridad y retención. |
| **Comentarios y recomendaciones** 🆕 | 3, 7 | ✅ | ❌ | Bitácora del expediente y recomendación de eventos. |

## 3. Requisitos NUEVOS que no existen ni como pantalla

Estos salieron del proceso real (reunión) y de las anotaciones del equipo. **No todos siguen ausentes**: la adopción del prototipo como fuente de verdad obligó a revisar cuáles ya están representados como interfaz. Estado real:

| # | Requisito | ¿Pantalla en el prototipo? | Falta |
|---|---|---|---|
| 1 | Correo de bienvenida | ❌ | Envío automático y plantilla |
| 2 | Validación/activación con **habilitaciones** por módulo | 🟡 (estado *Limitado* y bandeja de desbloqueo) | Proceso y tabla `habilitaciones` |
| 3 | Banco de preguntas **desde Excel** | 🟡 (22 preguntas fijas) | Importación y administración |
| 4 | **Generación automática** de caracterización y valoración | 🟡 (resultados fijos) | Fórmula y derivación (AQ-09) |
| 5 | **Informe descargable** real | 🟡 (botón simulado) | Generación PDF |
| 6 | **Acta de compromiso** | ❌ | Vista, carga, revisión y estados |
| 7 | **Notificaciones con disparadores** | 🟡 (bandeja, sin emisión) | Triggers y envío |
| 8 | **Rol de auditor** | ❌ | Pantallas y guardas de solo lectura |

## 4. En el prototipo, pero solo simulado (necesita backend)

Aunque la pantalla exista, **nada persiste ni consulta un servidor**:

- Login / registro / OTP / recuperación (sesión en `localStorage`).
- "Guardar" y "Cancelar" en formularios.
- "Descargar"/"Exportar" (reportes, resultados de diagnóstico, plan de trabajo).
- "Marcar como completada" una tarea, "Inscribirse" a un evento.
- "Marcar todas como leídas" (notificaciones).
- Filtros, paginación y buscadores (trabajan sobre HTML estático).
- Dashboards y gráficos (datos inventados).

Detalle exhaustivo de las vistas del estudiante en `../CORRECCIONES-VISTAS-ESTUDIANTE.md` y en los pendientes del estudiante (material local, no versionado).

## 5. Prioridades sugeridas (alineadas con el README §12)

**P0 — Imprescindible (base real):**
- [ ] Esquema PostgreSQL completo (todas las tablas del §5, incluidas las nuevas).
- [ ] Backend Node + Express con capas y middlewares de rol.
- [ ] Autenticación real (registro, OTP, login, JWT, logout).
- [ ] CRUD de usuarios/emprendimientos/asignaciones/seguimiento/tareas/asesorías.
- [ ] Validación y activación del emprendedor + correo de bienvenida.
- [ ] Frontend React real (reemplaza el prototipo estático).

**P1 — Importante:**
- [ ] Diagnóstico *data-driven* desde Excel + caracterización/valoración + informe.
- [ ] Acta de compromiso (subida + revisión).
- [ ] Notificaciones con disparadores.
- [ ] Eventos y gestión de archivos reales.

**P2 — Post-MVP:**
- [ ] Rol de auditor (tras definir alcance).
- [ ] Comparativa de emprendimientos, push, i18n.

## 6. Conclusión de la validación

- **Lo que sirve:** la spec (actualizada) y el prototipo son una base sólida para construir; el diseño de UI y las reglas ya están representados.
- **Lo que falta:** prácticamente **toda la implementación** (BD + backend + frontend React). De los 8 elementos del alcance ampliado, **3 no tienen ninguna pantalla** (correo de bienvenida, acta, auditor) y **4 están parcialmente representados** como UI.
- **Bloqueantes para empezar:** cerrar las **decisiones abiertas** (§11 y §16.2 del README): alcance del auditor, criterios de validación, rúbrica del diagnóstico, formato del informe, tiempo de revisión del acta y los documentos que no están (`control.pdf`, Excel de preguntas).
