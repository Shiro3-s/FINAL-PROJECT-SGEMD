# Dossier de decisiones pendientes — SGEMD

> **Fecha de elaboración:** 25 de octubre de 2026 · **trabajo local** (sin rama nueva, sin commit y sin push a GitHub).
> **Uso:** documento de trabajo para la reunión de cierre con la Coordinadora del Centro Progresa.
> **Regla de oro:** ninguna hoja se considera cerrada sin una **decisión escrita**, con fecha y responsable. Este dossier **no decide por defecto** ni inventa contenido.

---

## 1. Propósito

Reunir en un solo documento las preguntas que aún bloquean la implementación de SGEMD, con la evidencia verificada en el prototipo, las opciones disponibles, una recomendación no vinculante y el impacto documental de cada decisión.

El dossier complementa —no sustituye— al SRS ([`fr_nfr_sgemd.md`](./fr_nfr_sgemd.md)), a las historias ([`historias_usuario.md`](./historias_usuario.md)) y al registro de ejecución ([`registro-actualizacion-requisitos-2026-10.md`](./registro-actualizacion-requisitos-2026-10.md)). Las preguntas se identifican con los mismos códigos `AQ-xx` del SRS §9.

### 1.1 Jerarquía de verdad aplicada

1. La **decisión escrita** del responsable del programa.
2. El **modelo textual** de `README.md` §5.
3. La **evidencia verificada** en el HTML generado de `prototype/**`.
4. La documentación previa (SRS, historias, anotaciones), cuando no contradiga lo anterior.

> **Los diagramas no se usan como evidencia, fuente ni entregable.** Están desactualizados respecto del modelo textual y su actualización queda fuera de este cierre (ver §10).

---

## 2. Tablero de preguntas

| AQ | Tema | Estado al 2026-10-25 | Responsable de la decisión |
|---|---|---|---|
| AQ-06 | Campos obligatorios del registro y criterios de validación del emprendedor | **Abierta** | Coordinadora + equipo |
| AQ-07 | Funcionalidades disponibles antes de la validación (cuenta `Limitado`) | **Abierta** | Coordinadora |
| AQ-08 | Permisos del rol auditor (rol 4) | **Cerrada** | Usuario (decisión registrada) |
| AQ-09 | Rúbrica del diagnóstico y formato del informe descargable | **Abierta** | Coordinadora + equipo |
| AQ-10 | Plazo de revisión del acta y efecto completo del rechazo | **Abierta** | Coordinadora |
| AQ-11 | Estructura definitiva de tablas y relaciones | **Cerrada** (modelo textual) | Equipo |
| AQ-12 | Insumos ausentes: `control.pdf` y Excel de preguntas | **Abierta** (insumo solicitado) | Coordinadora |

**Cierre ya registrado — AQ-08:** el rol auditor (rol 4) tendrá **solo lectura y exportación de reportes**; **no edita** datos ni accede a información sensible completa. Se documenta con NFR-002, NFR-007, FR-010, FR-017 y la historia **US-026**, sin crear un FR nuevo.

---

## 3. Hoja AQ-06 — Campos obligatorios y criterios de validación

### 3.1 Pregunta única

¿Qué campos del registro son obligatorios y qué criterios debe cumplir un emprendedor para que el Administrador lo valide y active?

### 3.2 Hallazgos verificados

- El formulario `prototype/compartido/registro.html` tiene **10 etiquetas** y **8 controles con atributo `required`**: **7 campos de captura** y **1 casilla de aceptación**.
- Los campos marcados como obligatorios son: nombres, apellidos, tipo y número de documento, correo personal, correo institucional, celular y contraseña; la casilla exige aceptar el tratamiento de datos.
- El teléfono fijo **no** es obligatorio.
- Los controles del formulario **no tienen atributo `name`** (la única aparición de `name=` en el archivo es el `meta viewport`). Por tanto, la captura y el envío reales son `Pendiente de backend`.
- El prototipo **no contiene una lista de criterios de validación** del emprendedor (búsqueda de `criterio`, `checklist` y `validar` sin resultados sustantivos). La única evidencia es el paso de `Limitado` a `Activo` por el Administrador.

### 3.3 Opciones

| Opción | Contenido | Ventaja | Riesgo |
|---|---|---|---|
| A | Mantener los 7 campos + casilla y exigir además documento y correo únicos | Coherente con el formulario actual y con FR-016 | Puede dejar fuera datos que la Coordinadora exige para validar |
| B | Añadir campos de caracterización al registro (programa, semestre, sede, tipo de usuario) | Concentra la información en un solo momento | Alarga el registro y duplica lo que ya existe en Configuración |
| C | Registro mínimo (identificación y contacto) y validación posterior con lista de criterios | Reduce el abandono en el registro | Exige definir y mantener la lista de criterios |

### 3.4 Recomendación (no vinculante)

Opción **C**, con los 7 campos actuales como mínimo obligatorio y una **lista de criterios de validación** aprobada por la Coordinadora (por ejemplo: documento verificado, correo institucional válido, reunión de socialización realizada y datos de contacto confirmados). La lista debe registrarse en el SRS antes de implementar.

> La recomendación **no** define los criterios: solo propone dónde deben quedar registrados.

### 3.5 Impacto documental si se decide

| Documento | Cambio |
|---|---|
| `docs/fr_nfr_sgemd.md` | Ampliar FR-016 con la lista de campos y criterios; ajustar AQ-06 |
| `docs/historias_usuario.md` | Escenarios de US-011 y US-013 con los criterios aprobados |
| `README.md` | §16.1 y §16.2 sin el pendiente de campos obligatorios |

### 3.6 Decisión

| Campo | Registro |
|---|---|
| Decisión | _(pendiente)_ |
| Fecha | _(pendiente)_ |
| Responsable | _(pendiente)_ |
| Observaciones | _(pendiente)_ |

### 3.7 Consecuencia de no decidir

El registro queda con validación solo visual y la activación sin criterios verificables. No se puede implementar la captura ni la validación en backend sin redefinir el formulario después.

---

## 4. Hoja AQ-07 — Acceso previo a la validación

### 4.1 Pregunta única

¿Qué puede hacer un emprendedor mientras su cuenta está en estado `Limitado`?

### 4.2 Hallazgos verificados

| Vista | Evidencia | Lectura |
|---|---|---|
| `prototype/estudiante/estado-seguimiento.html` | “Tu cuenta está en estado **Limitado**. Mientras no sea activada por un administrador, el **diagnóstico inicial no puede enviarse**.” | El diagnóstico está bloqueado antes de la activación |
| `prototype/estudiante/emprendimiento-detalle.html` | Botón **“Responder diagnóstico”** activo, con enlace a `diagnostico.html` | El diagnóstico está disponible antes de la activación |

**Contradicción registrada:** ambas vistas describen el mismo estado `Limitado` con reglas opuestas. Ninguna de las dos prevalece por sí sola; la decisión debe resolverlo.

### 4.3 Opciones

| Opción | Contenido | Ventaja | Riesgo |
|---|---|---|---|
| A | `Limitado` = perfil, acta y notificaciones; diagnóstico, emprendimiento, tareas y asesorías bloqueados | Coherente con el aviso de `estado-seguimiento.html` y con el flujo de socialización previa (BP-001) | El estudiante no puede adelantar trabajo antes de la reunión |
| B | `Limitado` = perfil y diagnóstico; el resto bloqueado | Permite llegar a la reunión con información | Contradice el aviso de bloqueo y el orden del flujo documentado |
| C | `Limitado` = solo lectura de todo el módulo, sin crear registros | Da contexto al estudiante | No está evidenciado en el prototipo y complica los permisos |

### 4.4 Recomendación (no vinculante)

Opción **A**: mientras la cuenta esté `Limitado`, el estudiante solo accede a su perfil, a la carga del acta y a sus notificaciones; el diagnóstico y el alta del emprendimiento se habilitan al pasar a `Activo`. Con esta decisión debe corregirse el botón de `emprendimiento-detalle.html` en el próximo ciclo de prototipo.

### 4.5 Impacto documental si se decide

| Documento | Cambio |
|---|---|
| `docs/fr_nfr_sgemd.md` | FR-013 y AQ-07 con la matriz de acceso previo |
| `docs/historias_usuario.md` | Nuevo escenario en US-013 |
| `README.md` | §16.1 con la regla de acceso previo |

### 4.6 Decisión

| Campo | Registro |
|---|---|
| Decisión | _(pendiente)_ |
| Fecha | _(pendiente)_ |
| Responsable | _(pendiente)_ |
| Observaciones | _(pendiente)_ |

### 4.7 Consecuencia de no decidir

Se mantiene una contradicción visible entre dos pantallas y no puede implementarse la autorización por estado de cuenta.

---

## 5. Hoja AQ-09 — Rúbrica del diagnóstico e informe

### 5.1 Pregunta única

¿Cómo se transforman las respuestas del diagnóstico en puntajes, fortalezas y oportunidades, y qué contenido y formato tiene el informe descargable?

### 5.2 Hallazgos verificados

- `prototype/admin/diagnosticos.html` describe el instrumento como **5 secciones y 22 preguntas**:

| Sección | Preguntas |
|---|---|
| 1. Perfil del emprendimiento | 5 |
| 2. Problema o necesidad | 4 |
| 3. Propuesta de valor | 4 |
| 4. Mercado objetivo | 4 |
| 5. Capacidad operativa y financiera | 5 |
| **Total** | **22** |

- La misma vista muestra una distribución por bandas: **90–100**, **70–89**, **50–69** y **menos de 50**.
- `prototype/estudiante/diagnostico-resultados.html` muestra **6 dimensiones** con porcentajes: Visión 85 %, Creatividad 78 %, Resiliencia 70 %, Liderazgo 82 %, Trabajo en equipo 88 % y Capacidad de decisión 66 %.
- La misma vista ofrece **“Descargar PDF”** y describe el contenido como “Puntaje, comportamiento entrepreneurial y recomendaciones del docente”; **no** define la plantilla ni el detalle de esas secciones.
- **No existe** en el prototipo la fórmula que convierte respuestas en puntajes, ni la regla que genera fortalezas y oportunidades, ni la plantilla del informe.
- El Excel de preguntas que debía alimentar el instrumento **no está en el repositorio** (ver AQ-12).

### 5.3 Opciones

| Opción | Contenido | Ventaja | Riesgo |
|---|---|---|---|
| A | Rúbrica por dimensión con pesos definidos y bandas 90–100 / 70–89 / 50–69 / <50; informe con secciones, puntaje por dimensión, banda, fortalezas, oportunidades y recomendaciones | Trazable y consistente con lo ya visible | Requiere validar los pesos con la Coordinadora |
| B | Puntaje total único y texto genérico | Rápido de implementar | Pierde el detalle por dimensión que ya muestra el prototipo |
| C | Rúbrica definida fuera del sistema (Excel) y cargada como parámetro | Flexibilidad sin reprogramar | Depende de un insumo que hoy no existe |

### 5.4 Recomendación (no vinculante)

Opción **A**, manteniendo las **5 secciones**, las **22 preguntas**, las **6 dimensiones**, las **4 bandas** y la descarga en **PDF** ya visibles. Los pesos y la regla de fortalezas/oportunidades deben aprobarse por escrito antes de implementar; hasta entonces no se inventan valores.

### 5.5 Impacto documental si se decide

| Documento | Cambio |
|---|---|
| `docs/fr_nfr_sgemd.md` | FR-002 con la rúbrica y el formato del informe; AQ-09 cerrada |
| `docs/historias_usuario.md` | Escenarios de la historia de diagnóstico |
| `README.md` | §16.2 sin el pendiente de rúbrica e informe |

### 5.6 Decisión

| Campo | Registro |
|---|---|
| Decisión | _(pendiente)_ |
| Fecha | _(pendiente)_ |
| Responsable | _(pendiente)_ |
| Observaciones | _(pendiente)_ |

### 5.7 Consecuencia de no decidir

El diagnóstico seguirá mostrando porcentajes sin fórmula reproducible y el informe no podrá implementarse; dos estudiantes con las mismas respuestas podrían obtener resultados distintos.

---

## 6. Hoja AQ-10 — Plazo y efecto del rechazo del acta

### 6.1 Pregunta única

¿En cuánto tiempo debe revisarse el acta de compromiso y qué ocurre —exactamente— cuando se rechaza?

### 6.2 Hallazgos verificados

- **BR-009** ya definió que el rechazo exige **motivo obligatorio** y notifica al estudiante.
- El prototipo **no fija un plazo de revisión del acta** ni muestra un vencimiento asociado a ella. Las coincidencias de “vence” en `admin/solicitudes.html` y `estudiante/emprendimiento-detalle.html` pertenecen al formulario genérico de **tareas** (“Vence el”), no al acta.
- La bandeja de solicitudes sí admite prioridad y vencimiento para las **tareas** creadas desde su formulario; ese plazo no aplica al acta.
- El prototipo **no tiene vista de acta**; la carga y la revisión son `Pendiente de backend` (US-025).
- La asignación de docente está bloqueada sin acta aprobada (**BR-001**), pero no se especifica qué pasa con el emprendimiento ni con la cuenta tras un rechazo.

### 6.3 Opciones

| Dimensión | Opción 1 | Opción 2 | Opción 3 |
|---|---|---|---|
| Plazo de revisión | 5 días hábiles con recordatorio al tercero | 3 días hábiles sin recordatorio | Sin plazo, solo alerta en bandeja |
| Efecto del rechazo | El acta vuelve a `Rechazada`; el estudiante puede volver a cargarla; la asignación sigue bloqueada; la cuenta no se suspende | Igual, pero con un máximo de intentos | El rechazo suspende la cuenta hasta nueva revisión |

### 6.4 Recomendación (no vinculante)

Plazo de **5 días hábiles** con recordatorio al tercer día; rechazo que devuelve el acta a `Rechazada`, notifica con el motivo, permite una nueva carga y **mantiene bloqueada la asignación** sin suspender la cuenta. El plazo y el efecto deben quedar en BR-009 y en US-025.

### 6.5 Impacto documental si se decide

| Documento | Cambio |
|---|---|
| `docs/fr_nfr_sgemd.md` | BR-009 ampliada con plazo y efecto; AQ-10 cerrada |
| `docs/historias_usuario.md` | US-025 con el escenario de vencimiento y recarga |
| `README.md` | §16.2 sin el pendiente del tiempo de revisión |

### 6.6 Decisión

| Campo | Registro |
|---|---|
| Decisión | _(pendiente)_ |
| Fecha | _(pendiente)_ |
| Responsable | _(pendiente)_ |
| Observaciones | _(pendiente)_ |

### 6.7 Consecuencia de no decidir

El acta puede quedar indefinidamente en revisión, el estudiante no sabe cuándo reclamar y la asignación docente queda bloqueada sin una salida documentada.

---

## 7. AQ-11 — Estructura definitiva (cerrada por modelo textual)

**Decisión registrada:** la estructura definitiva se toma **solo** del modelo textual de `README.md` §5. **Ningún diagrama se usa como fuente ni se corrige en este cierre.**

### 7.1 Estado del modelo textual

| Elemento | Valor |
|---|---|
| Tablas declaradas por el modelo | **29** |
| Relaciones declaradas | **42** (16 de negocio con comportamiento + 13 catálogos, según la clasificación del modelo) |
| Fichas de sección en `README.md` §5 | **13** (agrupan varias tablas cada una) |
| Catálogos listados en tabla | **12** |
| `adjuntos` y sus tres pivotes | Anunciados en las convenciones, **sin ficha individual** |
| Tabla técnica de auditoría | `auditoria_eventos`: **no modelada**, `Pendiente de backend` |

> **Precaución de lectura:** el total de **29 tablas y 42 relaciones** es el que declara el modelo, no el que se obtiene contando encabezados de ficha: varias fichas agrupan dos o más tablas (por ejemplo, diagnóstico con preguntas y respuestas, o eventos con su pivote de asistencia). No se recalcula ni se corrige el total en este cierre.

### 7.2 Observaciones de consistencia

- `adjuntos` y sus **tres tablas pivote** se anuncian en las convenciones del modelo, pero **no tienen ficha individual** en §5. Quedan como parte del modelo textual, sin ficha propia, y así deben implementarse hasta que se amplíe la sección.
- Las **13 fichas** de §5 agrupan tablas; no equivalen a 13 tablas ni permiten recalcular el total. El conteo vigente es el declarado: **29 tablas y 42 relaciones**.
- `auditoria_eventos` **no está modelada**. NFR-007 exige registrar autor, fecha, valor anterior y valor nuevo; la tabla correspondiente se implementará en backend.
- El conteo de 29 tablas y 42 relaciones **no** se deduce de los diagramas: se toma del modelo textual.

### 7.3 Consecuencia

La implementación de la base de datos puede comenzar con el modelo textual. Cualquier cambio posterior exige actualizar §5 y, por separado, los diagramas (fuera de este cierre).

---

## 8. AQ-12 — Insumos solicitados

### 8.1 Solicitud

| Insumo | Para qué se necesita | Estado |
|---|---|---|
| `control.pdf` | Contrastar los campos y criterios del registro (AQ-06) | **Solicitado; no está en el repositorio** |
| Excel de preguntas del diagnóstico | Estructurar el instrumento y la rúbrica (AQ-09) | **Solicitado; no está en el repositorio** |

### 8.2 Regla si no llegan

Si los insumos no llegan antes de la reunión:

- **No se bloquea** el cierre documental.
- **No se inventa** su contenido ni se transcriben datos personales.
- AQ-06 y AQ-09 quedan **abiertas** y se resuelven con la evidencia del prototipo y la decisión de la Coordinadora.
- Los documentos mantienen la referencia al insumo como **pendiente**.

### 8.3 Decisión

| Campo | Registro |
|---|---|
| ¿Se recibieron? | _(pendiente)_ |
| Fecha | _(pendiente)_ |
| Observaciones | _(pendiente)_ |

---

## 9. AQ-08 — Rol auditor (cierre registrado)

| Aspecto | Decisión |
|---|---|
| Alcance | **Solo lectura** y **exportación de reportes** |
| Edición | **No** edita datos de ningún módulo |
| Datos sensibles | **No** accede a información sensible completa |
| Requisitos que lo cubren | NFR-002 (autorización por rol y alcance), NFR-007 (auditabilidad), FR-010 (dashboards), FR-017 (expediente) |
| Historia | **US-026** |
| FR nuevo | **No se crea** (no se usa FR-025) |
| Estado en prototipo | `Fuera de alcance / Post-MVP`: el rol no existe en las vistas actuales |

---

## 10. Nota sobre los diagramas

Los diagramas del repositorio **no son fuente de verdad** y **no se actualizan** en este ciclo:

| Archivo | Motivo |
|---|---|
| `docs/diagrama-clases.md` / `.drawio` / `.png` | Declara 20 clases y 31 relaciones; el modelo textual vigente declara 29 tablas y 42 relaciones |
| `docs/diagrama-componentes.md` / `.drawio` / `.png` | No refleja los roles ni los módulos añadidos en esta actualización |
| `docs/context-diagram.png` | No cubre el alcance ampliado |

**Regla:** ninguna decisión, requisito o evidencia de este dossier se apoya en un diagrama. Su actualización se planifica como trabajo aparte.

---

## 11. Acta de la reunión

| Campo | Registro |
|---|---|
| Fecha | _(pendiente)_ |
| Participantes | _(pendiente)_ |
| AQ tratadas | AQ-06, AQ-07, AQ-09, AQ-10, AQ-12 |
| Decisiones tomadas | _(pendiente)_ |
| Compromisos y fechas | _(pendiente)_ |

---

## 12. Lista de verificación posterior

- [ ] Cada AQ tratada tiene decisión, fecha y responsable.
- [ ] Las decisiones se trasladaron al SRS, a las historias y al `README.md`.
- [ ] AQ-06, AQ-07, AQ-09, AQ-10 y AQ-12 cambiaron de estado solo si hubo decisión escrita.
- [ ] No se creó ningún `FR-025` para el auditor.
- [ ] Los diagramas siguen sin modificarse y sin usarse como evidencia.
- [ ] No se versionó ni publicó nada: el trabajo permanece local.
