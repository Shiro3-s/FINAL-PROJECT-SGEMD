# Validación de alcance — qué falta por implementar

> **Objetivo:** validar **qué falta** comparando la **spec maestra actualizada** (`README.md`, 2026-10-12) contra el **estado real del repositorio**.
>
> **Base de la spec:** `README.md` §3 (funcionalidades), §5 (modelo de datos), §6 (reglas), §7 (API), §8 (frontend), §11–§13 (MVP y criterios) y §16 (alcance ampliado).
>
> **Estado real verificado:**
> - `prototype/` → **65 pantallas HTML estáticas** (4 acceso + 26 estudiante + 17 docente + 18 admin), generadas desde Python. **No hay backend**: login simulado, sesión en `localStorage`, "guardar/descargar" son simulaciones.
> - `core/`, `agents/`, `skills/`, `interfaces/`, `config/`, `tools/`, `evaluations/` → **framework de agentes** (scaffolding de IA), **no** es la aplicación SGEMD.
> - **No existe** backend (Node/Express), frontend React, ni base de datos PostgreSQL.
> - Documentación: completa (`docs/`, `CORRECCIONES-VISTAS-ESTUDIANTE.md`).

**Leyenda:** ✅ existe · 🟡 parcial/simulado · ❌ falta · 🆕 requisito nuevo (no estaba antes de la actualización).

---

## 0. Resumen en una frase

La spec y el prototipo (UI) están **avanzados**; **toda la capa real** (backend, API, base de datos y frontend React) **está por construir**, y hay **7 requisitos nuevos** que no existen ni siquiera como pantalla en el prototipo.

## 1. Estado por capa

| Capa | Estado | Detalle |
| ---- | ------ | ------- |
| **Spec / documentación** | ✅ | `README.md` completo y actualizado (§16). |
| **Prototipo (UI estática)** | 🟡 | 65 pantallas navegables, sin lógica real ni datos. |
| **Frontend real (React)** | ❌ | No existe. |
| **Backend (Node + Express)** | ❌ | No existe. |
| **API REST** | ❌ | Definida en §7; sin implementar. |
| **Base de datos (PostgreSQL)** | ❌ | Modelo en §5; sin `schema.sql` montado. |
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
| Emprendimientos | 3 | ✅ | ❌ | CRUD + alcance por propietario. |
| Asignaciones | 3 | ✅ | ❌ | Asignación docente↔estudiante↔empr. |
| Seguimiento | 3 | ✅ | ❌ | Notas reales + autor. |
| Asesorías | 3 | ✅ | ❌ | Solicitud/confirmación + notificaciones. |
| Tareas / plan de trabajo | 3 | ✅ | ❌ | Estados y % de avance derivados de BD. |
| **Diagnóstico *data-driven*** 🆕 | 3, 5 | 🟡 (5 secciones fijas) | ❌ | Banco de preguntas desde **Excel**. |
| **Caracterización y valoración** 🆕 | 3, 5, 16 | ❌ | ❌ | Generación automática + feedback. |
| **Informe descargable** 🆕 | 3, 7 | 🟡 (botón falso) | ❌ | Generación real (PDF). |
| **Acta de compromiso** 🆕 | 3, 6, 16 | 🟡 (solo mención) | ❌ | Subir + revisar + ficha `actas`. |
| **Notificaciones (disparadores)** 🆕 | 3, 6, 7 | 🟡 (pantalla sin lógica) | ❌ | Triggers + tabla `notificaciones`. |
| Eventos | 3 | ✅ | ❌ | CRUD + registro/asistencia. |
| Dashboards | 3 | ✅ (datos falsos) | ❌ | Métricas reales por rol. |
| Progreso | 3 | ✅ | ❌ | Derivado de etapa + tareas. |
| Gestión de archivos | 3 | ❌ | ❌ | Subida/descarga real (hasta 500 MB). |
| Reportes / exportar | 8 | 🟡 (`admin/reportes.html`) | ❌ | Exportación real (CSV/Excel/PDF). |
| Catálogos | 7 | ❌ | ❌ | Endpoints de solo lectura. |

## 3. Requisitos NUEVOS que no existen ni como pantalla

Estos salieron del proceso real (reunión) y de las anotaciones del equipo, y **no están** en el prototipo:

1. **Correo de bienvenida** automático tras el registro.
2. **Validación/activación** del emprendedor por el administrativo, con **habilitaciones** por módulo (el prototipo solo muestra el texto "cuenta Limitada").
3. **Banco de preguntas en Excel** para el diagnóstico (hoy las 5 secciones están fijas en el HTML).
4. **Generación automática** de caracterización y **valoración** a partir de las respuestas.
5. **Informe descargable** real (hoy el botón no descarga nada).
6. **Acta de compromiso y confidencialidad**: subir + revisar + estados.
7. **Notificaciones con disparadores** (al administrativo y al estudiante).
8. **Rol de auditor** (pendiente de definir su alcance).

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
- **Lo que falta:** prácticamente **toda la implementación** (BD + backend + frontend React) y **8 requisitos nuevos** que hoy no tienen ni pantalla.
- **Bloqueantes para empezar:** cerrar las **decisiones abiertas** (§11 y §16.2 del README): alcance del auditor, criterios de validación, rúbrica del diagnóstico, formato del informe, tiempo de revisión del acta y los documentos que no están (`control.pdf`, Excel de preguntas).
