# Sincronización de la documentación con el prototipo (2026-10-25)

> **Motivo:** el prototipo de `prototype/` (73 pantallas) se adopta como **fuente principal de verdad**. Este registro documenta qué se cambió, con qué evidencia y qué quedó pendiente. No introduce requisitos nuevos: traduce lo que el prototipo ya muestra.

## 1. Criterio de contraste

| Orden | Fuente | Uso |
|---|---|---|
| 1 | **Decisión escrita y cerrada** (`README.md` §11, dossier AQ) | Manda sobre todo lo demás |
| 2 | **Prototipo verificado** (`prototype/`, 73 pantallas) | Fuente de campos, estados, catálogos y flujos |
| 3 | **Modelo textual** (`README.md` §5) | Traducción del prototipo a tablas y columnas |
| 4 | **Documentación previa** (SRS, diagramas, historias, vistas) | Se corrige cuando contradice 1–3 |

**Regla:** si el prototipo y un documento difieren, prevalece el prototipo **salvo** que exista una decisión escrita en contra. Lo que el prototipo no representa se marca como **pendiente**; no se rellena por invención.

## 2. Base verificada

| Elemento | Valor |
|---|---|
| Pantallas totales | **73** |
| Acceso compartido | 4 |
| Estudiante | 27 (18 vistas base + 9 variantes) |
| Docente | 23 |
| Administrador | 19 |
| Backend / API / PostgreSQL | **No existen** |
| Persistencia del prototipo | `localStorage` y datos fijos del generador Python |
| Scripts de auditoría citados en `prototype/README.md` | **12 no están en el repositorio** |

## 3. Datos canónicos extraídos del prototipo

| Dimensión | Valores |
|---|---|
| Estado de cuenta | `Limitado` · `Activo` · `Inactivo` |
| Estado de tarea | `Pendiente` · `En curso` · `En revisión` · `Completada` · `Vencida` · `Devuelta` |
| Estado de revisión | `Pendiente` · `En revisión` · `Calificada` · `Devuelta` |
| Prioridad | `Alta` · `Media` · `Baja` |
| Estado de asesoría | `Por agendar` · `Programada` · `Confirmada` · `En curso` · `Completada` · `Cancelada` |
| Estado de evento | `Pendiente` · `Aprobado` · `Rechazado` · `Publicado` |
| Respaldo | Tipo `Completo` · `Parcial`; estado `Exitosa` · `Fallida` |
| Etapa del emprendimiento | Ideación · Prototipo · Validación · Formalización |
| Fase del plan | Ideación y priorización · Estructuración y ejecución · Consolidación · Escalamiento |
| Diagnóstico | 5 secciones · 22 preguntas · 6 dimensiones · 4 bandas |
| Parámetros | `carga_max_horas=12` · `max_emprendimientos_docente=12` · `cupos_por_sede=40` · 3 sedes |
| Respaldo programado | Diario 09:00 · retención 30 días |

## 4. Modelo de datos

- Se reescribió `README.md` §5: **41 tablas = 27 de negocio + 14 catálogos**.
- Se retiró el conteo de **42 relaciones**, que no era trazable.
- Se agregaron las entidades que el prototipo muestra y el modelo no podía guardar: `comentarios`, `recomendaciones_evento`, `solicitudes`, `configuracion_programa`, `respaldos`, `auditoria_eventos`, `preguntas_diagnostico`, `respuestas_diagnostico`, `valoracion`, `actas`, `habilitaciones` y `notificaciones.Url`.
- Se agregaron columnas de estado y calificación: `EstadoAprobacion`, `EsParalelo`, `Prioridad`, `Puntos`, `PuntajeObtenido`, `Retroalimentacion`, `EstadoRevision`, `MotivoDevolucion` y `HorasSemanales`.
- `adjuntos` y sus tres pivotes tienen ficha propia.

## 5. Contradicciones resueltas

| # | Contradicción | Resolución |
|---|---|---|
| 1 | 12 horas vs 12 emprendimientos | **No son excluyentes**: el prototipo aplica ambos y los expone como parámetros. Se modelan ambos topes. |
| 2 | Tres catálogos de fases | Se separan `etapaemprendimiento` y `faseplan`; los alias cortos del detalle quedan como deuda de normalización. |
| 3 | Cuenta `Limitado` con acceso contradictorio al diagnóstico | **AQ-07 sigue abierta**; el modelo soporta ambos comportamientos vía `habilitaciones`. No se decide por defecto. |
| 4 | Acta exigida sin vista para cargarla | Se modela `actas`, pero el flujo queda **pendiente** (FR-003 / BR-001). |
| 5 | Motivo de rechazo obligatorio vs confirmación con campo vacío | Se registra como **defecto del prototipo**; la regla se mantiene vigente (R38). |
| 6 | El estudiante registra el emprendimiento (FR-012) | El prototipo **no lo permite**: el alta la hace el Administrador. FR-012 queda **parcial**. |
| 7 | Rol auditor definido sin pantallas | Se conserva como **Post-MVP**; el catálogo `roles` ya tiene el valor 4 y los diagramas lo incluyen. |
| 8 | Notificaciones en tiempo real | El prototipo solo tiene bandeja: **sin WebSocket**. La emisión queda como deuda de backend. |

## 6. Documentos actualizados

| Documento | Cambio |
|---|---|
| `README.md` | Cabecera y jerarquía; §2 (topes, vacío de alta); §3 (estados, fases, acta, notificaciones); §4 (41 tablas, diagramas regenerados); §5 (modelo completo); §6 (R17, R19, R35, R37, R38, R42–R46); §7 (solicitudes, configuración, respaldos, comentarios, recomendaciones, catálogos); §11 (AQ-11); §16 (vacíos y conteos); **§17 nueva** |
| `docs/fr_nfr_sgemd.md` | Alineación con el prototipo; FR-012 y FR-024 a `Parcial`; FR-016 con ambos topes; AQ-11 y conteos corregidos; nota de diagramas |
| `docs/diagrama-clases.md` | Regenerado en 3 bloques: 27 clases + 14 catálogos + enumeraciones |
| `docs/diagrama-componentes.md` | Regenerado: 15 servicios, rol auditor, procesos programados, borrado en cascada |
| `docs/*.png` | Regenerados desde el Mermaid (clases, componentes y contexto) |
| `docs/context-diagram.mmd` | Regenerado: auditor, correo de bienvenida, almacenamiento de archivos, respaldos |
| `docs/estructura_de_vistas_sgemd.md` | §3.2 reescrita con las 27 pantallas reales; se elimina el flujo donde el estudiante agenda asesorías y el dashboard con métricas inventadas |
| `docs/VALIDACION-ALCANCE.md` | 73 pantallas; estado real por módulo; requisitos nuevos revisados uno a uno |
| `docs/dossier-decisiones-pendientes-2026-10.md` | Jerarquía, AQ-11 con el conteo corregido y nota de diagramas |
| `docs/historias_usuario.md` | Ambos topes (12 h y 12 emprendimientos); alta del emprendimiento por el Administrador |
| `PROTOTIPO-STITCH.md` | 73 pantallas y reparto 4/27/23/19 |
| `prototype/README.md` | Nota sobre los 12 scripts de auditoría ausentes |

## 7. Vacíos que no se rellenaron

1. **Alta de emprendimiento por el estudiante** (FR-012): sin formulario ni vista de *Pendiente*.
2. **Vista del acta** (FR-003): sin descarga, carga ni revisión.
3. **Rol auditor** (rol 4): sin pantallas.
4. **Motivo obligatorio** en rechazos: el prototipo confirma con el campo vacío.
5. **Notificaciones en tiempo real**: solo bandeja.
6. **Borrado físico en cascada** de adjuntos: no hay evidencia visual.
7. **Cálculo automático del diagnóstico**: 22 preguntas y resultados fijos.
8. **Inactividad a 90 días**: el estado existe, el proceso no.
9. **Restauración de respaldos**: solo creación y descarga simuladas.
10. **Normalización de alias de fase** en el detalle del emprendimiento.

## 8. Riesgos y siguiente paso

- **Riesgo 1:** los diagramas `.drawio` y `.png` siguen siendo derivados y pueden estar obsoletos. La fuente es el Mermaid versionado.
- **Riesgo 2:** `prototype/README.md` cita auditorías que no se pueden reproducir. No deben usarse como evidencia de calidad.
- **Riesgo 3:** AQ-06, AQ-07, AQ-09, AQ-10 y AQ-12 siguen abiertas; el backend no debe codificar decisiones por defecto.
- **Siguiente paso:** congelar el modelo de 41 tablas, generar `schema.sql` y construir el backend por módulos, empezando por auth y usuarios.
