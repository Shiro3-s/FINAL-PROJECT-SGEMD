# Orquestación — Actualización documental SGEMD (FR/NFR · README · Historias de Usuario)

> **Qué es este documento:** la orquestación de trabajo con la que se actualizaron los tres documentos fuente del proyecto SGEMD. Sirve como prompt maestro reutilizable y como contrato de método: define insumos, jerarquía de verdad, reglas, fases y criterios de aceptación.
>
> **Qué no es:** no es el registro de lo ejecutado. La evidencia, la bitácora de verificación y el cierre están en [`registro-actualizacion-requisitos-2026-10.md`](./registro-actualizacion-requisitos-2026-10.md).

- **Fecha:** 25 de octubre de 2026
- **Ámbito de ejecución:** **local**. No se crea rama, no se hace commit, no se hace push y no se publica nada en GitHub.
- **Ámbito documental:** FR/NFR, README e historias de usuario.
- **Alcance:** actualizar documentos existentes; **no** rediseñar el producto ni modificar código.

---

## 0. Rol del ejecutor

Actúa como **Analista de Requisitos Senior + Product Owner + Technical Writer**.

El trabajo es **sincronizar documentación existente con evidencia verificable**. No se inventa alcance, no se renumeran identificadores y no se declara como terminado lo que solo está simulado.

---

## 1. Insumos obligatorios

### A. Documentos a actualizar

| Alias | Archivo | Rol documental |
|---|---|---|
| FrynFr | `docs/fr_nfr_sgemd.md` | SRS: procesos, requisitos funcionales y no funcionales, reglas y trazabilidad |
| Read.md | `README.md` (raíz) | Especificación y contexto maestro del MVP |
| HistoriasUso | `docs/historias_usuario.md` | Actores, procesos, historias Gherkin y recorrido |

> `prototype/README.md` **no** es el Read.md: es evidencia secundaria del prototipo.

### B. Evidencia de lo implementado

| Fuente | Aporte |
|---|---|
| `prototype/index.html` | Inventario autoritativo de pantallas enlazadas |
| `prototype/admin/**` (19) | Vistas reales del rol administrador |
| `prototype/estudiante/**` (27) | Vistas reales del rol estudiante |
| `prototype/docente/**` (23) | Vistas reales del rol docente |
| `prototype/compartido/**` (4) | Login, registro, OTP y recuperación |
| `prototype/paginas_admin.py`, `paginas_estudiante.py`, `paginas_docente.py` | Generadores: origen del comportamiento |
| `prototype/lib_ui.py`, `lib_js.py`, `lib_css.py` | Kit compartido |
| `prototype/cambios-a-admin.md` | Refactor admin: fichas, deep-links, asignación, configuración, respaldos |
| `prototype/cambios-a-docente.md` | Refactor docente |
| `prototype/orquestacion-docente-2026.md` | Verificación del rol docente |
| `CORRECCIONES-VISTAS-ESTUDIANTE.md` | Hallazgos y cierre del rol estudiante |
| `Config-admin/correcciones-adiciones-requisitos.md` | Correcciones C-1…C-7 y adiciones A-1…A-21 |
| `Config-admin/auditoriaV2.md`, `auditoriaV3.md` | Auditorías del rol admin |
| `Config-admin/auditoria-ui-ux-admin.md` | Diagnóstico UI/UX y cambio de FR-004/BR-002 |
| `Config-admin/prueba-ui-ux-admin.md` | Prueba funcional: 0/11 tareas completables |
| `docs/VALIDACION-ALCANCE.md` | Brecha spec vs. repositorio (conteos desactualizados) |
| `docs/estructura_de_vistas_sgemd.md` | Estructura de vistas por rol |

### C. Fuente específica de correcciones

- Se solicitó el archivo `.py` llamado **“correcciones”** de `context_admin`.
- **No existe en el repositorio** ni se localizó en carpetas hermanas al momento de ejecutar.
- **Decisión de ejecución:** no se asume su contenido. Se trabaja con `Config-admin/correcciones-adiciones-requisitos.md` y con la verificación directa de las vistas. El faltante queda registrado como **bloqueo parcial** en el registro de ejecución y como pregunta abierta.
- **Regla:** si el archivo aparece, cada uno de sus ítems debe mapearse a un ID de destino antes de cerrar la entrega.

---

## 2. Contexto

Se realizaron mejoras, auditorías y una base extensa del prototipo SGEMD:

- **Administrador:** refactor de 19 pantallas con datos reales en tablas, fichas de detalle, enlaces profundos por `hash`, bandeja de solicitudes, asignación/reasignación docente, configuración del programa y respaldos.
- **Estudiante:** correcciones y auditoría funcional; detalle propio por emprendimiento, avance por fases, descarga del plan, datos académicos condicionales, evidencia para completar tareas, detalle de eventos y filtros de notificaciones.
- **Docente:** refactor UX/UI; acciones como vistas completas, calendario de compromisos, recomendación de eventos y perfil.
- **Documentación:** auditorías UI/UX, correcciones de requisitos y una lista de adiciones que nunca se incorporó a los tres documentos fuente.

Los documentos actuales se quedaron atrás: no reflejan esas capacidades, conservan requisitos ya corregidos en otros documentos y tienen conteos y estados desactualizados.

---

## 3. Objetivo

Actualizar los tres documentos para que describan el **estado real y vigente** del prototipo y del alcance acordado, incorporando:

1. lo ya implementado en las vistas;
2. lo definido en `correcciones-adiciones-requisitos.md`;
3. lo que eventualmente aporte el `.py` de correcciones de `context_admin`;
4. lo que sigue pendiente de backend, **sin presentarlo como terminado**.

---

## 4. Jerarquía de verdad

Cuando dos fuentes se contradicen, se resuelve en este orden:

| Nivel | Fuente | Qué responde |
|---|---|---|
| 1 | **Vista real del rol** en `prototype/**` | Qué se implementó y cómo se comporta |
| 2 | **Generador / código** (`paginas_*.py`, `lib_*.py`) | De dónde sale ese comportamiento |
| 3 | **`.py` de correcciones de `context_admin`** | Cambios explícitos solicitados |
| 4 | **Changelogs y orquestaciones cerradas** | Evidencia secundaria de lo hecho |
| 5 | **Auditorías y pruebas UI/UX** | Hallazgos y decisiones de diseño |
| 6 | **Documentos actuales** (`fr_nfr`, `historias`, `README`) | Se actualizan; no mandan |

### Regla de interpretación

- La **vista** dice **qué pasó** (hecho observable).
- El **usuario** dice **qué se espera** (intención de negocio).
- Si la vista contradice a un documento, **gana la vista** para describir el estado actual.
- Si la vista no alcanza para saber si eso es lo deseado, **se pregunta al usuario**.
- Nunca se resuelve una contradicción por “documento más reciente” ni por mayoría.

---

## 5. Reglas no negociables

1. **No** modificar código, HTML ni generadores. Solo los tres documentos y los reportes de método/evidencia.
2. **No** renumerar IDs existentes (FR, NFR, BR, BP, AQ). Los nuevos se agregan al final.
3. **No** borrar requisitos: si quedaron obsoletos, se marcan como “Reemplazado por …” o “Fuera del alcance actual”.
4. Cada cambio debe **citar evidencia**: archivo, sección, vista o ítem de corrección.
5. Etiquetar siempre el estado de cada capacidad:
   - `Implementado en prototipo (UI)`
   - `Simulado en prototipo (localStorage / sin backend)`
   - `Pendiente de backend`
   - `Fuera de alcance / Post-MVP`
6. No declarar como real lo que solo es cosmético. El prototipo es estático.
7. Español formal, tildes correctas, tablas consistentes.
8. Mantener estilo y estructura de cada documento (mínimo diff).
9. Si falta información, registrarla en “Supuestos y preguntas abiertas”; **no inventar**.
10. Los conteos (FR, NFR, pantallas, historias) deben recalcularse y **coincidir** entre los tres documentos.
11. **Ante cualquier inconsistencia** entre auditorías, correcciones, changelogs, el `.py` o los documentos actuales, **no resolverla sobre el papel**. Abrir la vista del rol afectado y verificar. Solo si después de ver la vista persiste la duda de negocio, consultar al usuario.

---

## 6. Protocolo de verificación en la vista

### Nivel 1 — Verificar en el HTML generado

- Localizar la vista exacta del rol afectado (p. ej. `prototype/admin/usuarios.html`).
- Buscar el elemento, texto, acción, estado, filtro o dato en conflicto.
- Revisar el generador correspondiente y las librerías compartidas.
- Registrar archivo, selector o texto y comportamiento observado.

### Nivel 2 — Reproducir el flujo

- Si la inconsistencia es funcional (botón, filtro, pestaña, modal, descarga, estado, validación), abrir la vista y reproducir el flujo.
- Verificar el efecto real: qué cambia, qué se guarda, qué se muestra.
- Registrar evidencia observable.
- No confundir “el botón existe” con “el botón funciona”.

### Nivel 3 — Consultar al usuario

Solo si tras los niveles 1 y 2 persiste una duda que la vista no puede resolver:

- regla de negocio ambigua;
- decisión de cliente;
- alcance no definido;
- dos comportamientos igualmente válidos;
- conflicto entre lo implementado y lo que el negocio quiere.

**Formato obligatorio de la consulta:**

1. Qué se verificó y en qué vista.
2. Qué dice cada fuente en conflicto.
3. Qué se observó realmente.
4. Dos o tres opciones concretas con su impacto documental.
5. Recomendación, si la hay.

**Prohibido preguntar lo que ya se puede verificar en la vista.**

---

## 7. Fases de ejecución

### F0 — Inventario y congelamiento

- Registrar fecha, rama y versión de cada documento.
- Listar secciones e IDs existentes.
- Crear la tabla de control de cambios.

### F1 — Extracción de evidencia

- Leer el `.py` de correcciones y extraer cada ítem (ID, texto, vista afectada, tipo).
- Recorrer changelogs y auditorías y extraer capacidades implementadas.
- Verificar en el prototipo que lo afirmado existe.
- Producir un **ledger de evidencia**: hecho → archivo/vista → estado.

### F1.5 — Resolución de inconsistencias en la vista (GATE)

Para cada contradicción:

1. Identificar las fuentes en conflicto.
2. Abrir la vista del rol afectado.
3. Revisar el generador si el HTML no explica el comportamiento.
4. Reproducir el flujo si es funcional.
5. Clasificar: `Resuelto por vista`, `Resuelto por vista + decisión documental` o `Requiere confirmación del usuario`.
6. Registrar en la bitácora.

| ID | Inconsistencia | Fuentes en conflicto | Vista consultada | Evidencia observada | Resultado | ¿Requiere usuario? |
|---|---|---|---|---|---|---|
| V-01 | … | auditoría vs. `.py` | `prototype/<rol>/<vista>.html` | … | Resuelto / Escalado | Sí/No |

### F2 — Matriz de vacíos (GATE obligatorio)

| ID | Hallazgo | Evidencia | Verificado en vista | Tipo | Destino | Acción | Prioridad | Estado |
|---|---|---|---|---|---|---|---|---|
| G-01 | … | archivo:sección | `rol/vista.html` | FR/NFR/BR/US/README | fr_nfr / historias / README | Corregir / Añadir / Aclarar / Reemplazar / Retirar | Alta/Media/Baja | Aplicado / Bloqueado / Requiere confirmación |

### F3 — Actualizar `fr_nfr_sgemd.md`

- Corregir FR/BR/NFR que contradigan la evidencia.
- Agregar requisitos nuevos con IDs secuenciales al final.
- Actualizar procesos BP, reglas BR, matriz de trazabilidad y resumen.
- Cerrar ambigüedades solo si la evidencia o el usuario lo permiten.
- Añadir “Control de cambios” con fecha y lista de IDs tocados.

### F4 — Actualizar `historias_usuario.md`

- Incorporar historias nuevas por rol en Gherkin V2.
- Asignar `US-###` solo a las nuevas; no renumerar las existentes.
- Actualizar procesos, journey, casos límite y decisiones.
- Añadir criterios verificables.
- Añadir cobertura: historia → FR/NFR/BR.

### F5 — Actualizar `README.md`

- Sincronizar §2 Roles, §3 Funcionalidades, §6 Reglas, §8 Frontend, §11 Decisiones, §12 MVP, §13 Criterios y §16 Trazabilidad.
- Corregir conteos de pantallas y estados del prototipo.
- Declarar explícitamente el alcance estático/simulado.
- No convertir el README en changelog.

### F6 — QA cruzada

- IDs únicos y sin duplicados.
- Todo FR nuevo aparece en la matriz de trazabilidad.
- Toda historia nueva referencia al menos un FR/NFR/BR.
- Los tres documentos cuentan lo mismo (cifras, roles, estados).
- No hay contradicciones del tipo “admin asigna” vs. “docente confirma”.
- Toda inconsistencia resuelta tiene evidencia de la vista consultada.
- Toda duda de negocio quedó registrada y consultada.
- Tildes, tablas y enlaces internos correctos.
- Ningún ítem del `.py` quedó sin mapear: **AQ-03 cerrada** por equivalencia de archivo (SHA-256).

### F7 — Entrega

1. Los tres documentos actualizados.
2. Registro de ejecución con ledger, bitácora, matriz, decisiones, consultas, supuestos e IDs.
3. Resumen ejecutivo breve.

---

## 8. Semillas de vacíos detectadas

> No darlas por ciertas: cada una se confirma contra la vista y la evidencia.

| Semilla | Qué revisar |
|---|---|
| FR-004 / BR-002 / R22 | Admin asigna directamente; estudiante solicita; docente acepta. Verificar en `admin/asignaciones.html`, `admin/solicitudes.html` y `docente/asesorias.html` |
| FR-007 / AQ-01 | `fr_nfr` dice “periodo definido”; Historias fija 90 días. Cerrar con evidencia o consulta |
| Estados de cuenta | Limitado → Activo → Inactivo, cambio solo Admin (A-3) |
| CRUD de usuarios | Alta, edición, baja lógica (A-1) |
| Aprobación de emprendimientos | Estudiante crea, Admin aprueba; paralelo (A-2) |
| Borrado lógico | Cascada de adjuntos (A-4) |
| Validación y unicidad | Formularios, documento, correo, carga docente (A-5) |
| Expediente | Asesorías + diagnósticos + seguimientos + log de auditoría (A-6) |
| Respaldos | UI, exportación y estado del backup (A-7) |
| Notificaciones | Accionables y “marcar como leídas” (A-8) |
| Bandeja de solicitudes | Desbloqueos, aprobaciones y citas (A-13) |
| Asesoría directa | Asignación por el Admin (A-12) |
| Vistas no listadas en README §8 | Configuración, solicitudes, reportes, respaldos, seguimiento, diagnósticos, eventos, fichas y deep-links; estudiante y docente |
| NFR faltantes | Accesibilidad, consistencia, auditabilidad, responsive, mantenibilidad (solo con evidencia) |
| Conteos | 71/18 vs. 73/19: verificar en `prototype/index.html` y `generar.py` |
| README §8 | Fila “Gradar/s see Aspirante” y tablas incompletas |
| Prototipo vs. backend | Guardar/descargar/exportar son simulaciones; no hay API ni PostgreSQL |
| `.py` de `context_admin` | **Resuelto (AQ-03):** archivo localizado; 28 ítems mapeados |

### 8.1 Cierre de preguntas abiertas (2026-10-25)

| AQ | Decisión | Evidencia |
|---|---|---|
| AQ-03 | Archivo de correcciones localizado; copia idéntica por SHA-256 (`EDCDE30F…836B5872`); 28/28 ítems mapeados | `Config-admin/correcciones-adiciones-requisitos.md` |
| AQ-04 | Restauración = operación técnica; el Admin solo exporta y consulta estado/integridad | `admin/respaldos.html`; decisión del usuario |
| AQ-05 | Motivo obligatorio en el rechazo del acta, con notificación al estudiante | `admin/solicitudes.html` (modal de motivo); BR-009 |
| AQ-08 | Rol auditor de solo lectura y exportación de reportes, sin edición ni datos sensibles completos; sin FR nuevo | Decisión del usuario; NFR-002, NFR-007, FR-010, FR-017; US-026 |
| AQ-11 | Estructura definitiva = modelo textual de `README.md` §5 (29 tablas, 42 relaciones); diagramas fuera de uso | Modelo textual; dossier §7 |

> **Abiertas y no decididas por defecto:** AQ-06 (campos y criterios), AQ-07 (acceso previo), AQ-09 (rúbrica e informe), AQ-10 (plazo y efecto del acta) y AQ-12 (insumos). Se tratan en `docs/dossier-decisiones-pendientes-2026-10.md`.

---

## 9. Criterios de aceptación de la entrega

- [ ] Los tres documentos fuente actualizados y los tres documentos de trabajo entregados (orquestación, registro y dossier).
- [ ] Cero IDs renumerados o duplicados.
- [ ] Cero contradicciones entre los documentos.
- [ ] Toda inconsistencia verificada en la vista del rol antes de decidir.
- [ ] Toda capacidad nueva con evidencia y estado (UI / simulado / backend).
- [ ] Toda duda de negocio consultada al usuario y registrada.
- [ ] Todo ítem del `.py` mapeado (AQ-03 cerrada).
- [ ] Matriz de trazabilidad completa.
- [ ] Conteos recalculados y coherentes.
- [ ] Registro de ejecución entregado.
- [ ] Preguntas abiertas listadas, no inventadas.
- [ ] Ningún diagrama usado como evidencia ni modificado.

---

## 10. Orden de ejecución aplicado

1. Inventario de pantallas y documentos.
2. Extracción de correcciones (C-1…C-7, A-1…A-21).
3. Verificación en vistas de cada hallazgo.
4. Resolución de contradicciones y registro de bloqueos.
5. Actualización de `fr_nfr_sgemd.md`.
6. Actualización de `historias_usuario.md`.
7. Actualización de `README.md`.
8. QA cruzada y cierre.
9. Cierre de AQ-03, AQ-04 y AQ-05 con decisión del usuario y registro de evidencia.

---

*Fin de la orquestación. La ejecución y su evidencia están en `registro-actualizacion-requisitos-2026-10.md`.*
