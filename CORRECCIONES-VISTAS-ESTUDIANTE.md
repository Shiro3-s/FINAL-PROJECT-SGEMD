# Correcciones — Vistas de Estudiante (SGEMD)

> Documento de trabajo para corregir el prototipo de estudiante.
> **Base validada:** `prototype/estudiante/` (16 vistas) + generadores (`paginas_estudiante.py`, `lib_ui.py`, `lib_js.py`).
> **Método:** trazabilidad de cada botón contra el kit JS del prototipo; cada hallazgo verificado en el HTML actual.
> **Fecha de validación:** 2026-10-07.

---

## 0. Resumen ejecutivo

- **14 hallazgos reportados por el usuario: 14 confirmados.**
- **10 problemas adicionales encontrados** (pestañas muertas, vistas huérfanas, contadores inconsistentes, breadcrumb muerto, textos en inglés, typos, botones fingidos…).
- Total de acciones de corrección: **≈ 35**, repartidas entre:
  - 🔤 Correcciones de texto (typos / i18n): **9**.
  - ⚙️ Correcciones de comportamiento (funciones/botones): **14**.
  - 🏗️ Correcciones estructurales (faltan vistas/pantallas): **7**.
  - ❓ Decisiones que debe cerrar el equipo/cliente: **5**.

**Importante:** el HTML **no se edita a mano**. Se genera desde Python (`paginas_estudiante.py` + `lib_ui.py` + `lib_js.py`) con el pipeline `generar.py`. Las correcciones se aplican en el generador y se regenera la salida (o se rediseñan las pantallas con prompts de Stitch).

---

## 1. Correcciones por vista

### 1.1 `dashboard.html`
| # | Tipo | Corrección |
|---|------|------------|
| D1 | 🔤 | **"Asesorias attended"** (inglés) → **"Asesorías realizadas"** o "Asesorías asistidas". |
| D2 | ⚙️ | Tarjeta "Próximas asesorías" / "Tareas pendientes": los enlaces "Ver todas" ya navegan bien (a `asesorias.html` / `tareas.html`). Sin cambio. |
| D3 | ⚙️ | Revisar consistencia: el estado de fase en el dashboard (100/62/0/0) debe coincidir con `estado-seguimiento.html` y `plan-trabajo.html` (mismo cálculo de avance). |

### 1.2 `emprendimientos.html`
| # | Tipo | Corrección |
|---|------|------------|
| EM1 | ⚙️ | **Los 2 filtros (etapa/sector) no funcionan**: los `<select>` no tienen el atributo `data-filtro` que el kit JS exige. Agregar `data-filtro="etapa"` y `data-filtro="sector"` (o reescribir el filtro). Hoy solo sirve "Buscar" por texto. |
| EM2 | ⚙️ | **Botón "Crear emprendimiento" no hace nada**: hoy solo muestra el toast "Guardado correctamente". Debe abrir `emprendimiento-editar.html` en modo crear (o un modal de creación con formulario completo). |
| EM3 | 🏗️ | **Falta el manejo de imagen/logo del emprendimiento**: no existe `<img>` ni campo de imagen en listado ni en detalle. Definir cómo se sube (estudiante/admin) y dónde se muestra (tarjeta + detalle). |
| EM4 | ⚙️ | Acciones de fila (`ver` / `editar` / `descargar`) abren **modales genéricos**. `ver` debe navegar a `emprendimiento-detalle.html`; `editar`, a `emprendimiento-editar.html`; `descargar`, generar un PDF real (o aviso si es del cliente). |
| EM5 | ⚙️ | Paginación "Anterior/Siguiente" solo muestra toast → conectar a la paginación real de la tabla (o quitar si es decorativa). |

### 1.3 `emprendimiento-detalle.html`
| # | Tipo | Corrección |
|---|------|------------|
| ED1 | ⚙️ | **Pestañas muertas**: Resumen/Diagnostico/Plan de trabajo/Seguimiento/Tareas/Asesorias son `<button>` sin `data-panel` y no hay paneles `data-panel-nombre` → al hacer clic solo cambia la clase, el contenido **nunca cambia**. Conectar pestañas con sus paneles reales. |
| ED2 | 🏗️ | Hoy "detalle" = solo texto del Resumen. Completar contenido de las 6 pestañas (diagnóstico del emprendimiento, plan, seguimiento, tareas, asesorías). |
| ED3 | ⚙️ | Botón "Editar" (si existe en la vista) debe llevar a `emprendimiento-editar.html` (hoy el listado no lo conecta — ver EM4). |
| ED4 | 🔤 | **Texto corrupto: "Areas de flipped classroom yckis"** → limpiar ("yckis" es basura). Probable: "Áreas de flipped classroom y e-learning" u otro texto del programa. |
| ED5 | ⚙️ | El botón del breadcrumb "Inicio › Mi emprendimiento › Sabor y Sabe" usa `href="#"` → arreglar breadcrumb (ver corrección transversal BT1). |

### 1.4 `emprendimiento-editar.html`
| # | Tipo | Corrección |
|---|------|------------|
| EE1 | ⚙️ | **"Guardar cambios" no guarda**: hoy solo toast "Guardado correctamente". Debe capturar el formulario y persistir (localStorage en prototipo; API en producción). |
| EE2 | ⚙️ | **"Cancelar" no regresa** a `emprendimiento-detalle.html` (o listado). Conectar navegación. |
| EE3 | 🏗️ | Vista **huérfana**: no se llega desde el listado (el "editar" del listado abre modal genérico). Conectar EM4. |
| EE4 | 🏗️ | Agregar campo de imagen/logo y previsualización (consistente con EM3). |

### 1.5 `diagnostico.html`
| # | Tipo | Corrección |
|---|------|------------|
| DG1 | ⚙️ | **"Siguiente seccion" no navega**: acción `siguiente-seccion` no existe en el kit JS → solo toast. Implementar navegación real entre las 5 secciones con validación. |
| DG2 | 🏗️ | **Las secciones 2–5 están vacías**: solo existen 4 preguntas (todas de la sección 1 "Perfil del emprendimiento"). Falta el contenido de: **Problema o necesidad**, **Propuesta de valor**, **Mercado objetivo**, **Capacidad operativa**. |
| DG3 | 🔤 | **Inconsistencia en el contador**: dice "Progreso: 5 de 22 preguntas respondidas" pero el HTML solo tiene 4 preguntas. Definir el número real de preguntas del diagnóstico (sección por sección) y hacer que el progreso las cuente. |
| DG4 | ⚙️ | "Guardar borrador" / "Guardar y salir" solo muestran toast → persistir el avance real (localStorage) para poder retomar. |

### 1.6 `diagnostico-resultados.html`
| # | Tipo | Corrección |
|---|------|------------|
| DR1 | ⚙️ | Revisar que los resultados se calculen con las respuestas del diagnóstico (hoy es contenido estático de ejemplo). |
| DR2 | ⚙️ | "Descargar PDF"/botones de exportar → toast fingido. Definir si descarga real (y para qué rol). |
| DR3 | ⚙️ | Breadcrumb "Diagnostico › Resultado" con `href="#"` → arreglar (BT1). |

### 1.7 `plan-trabajo.html`
| # | Tipo | Corrección |
|---|------|------------|
| PT1 | 🏗️ | **No hay pantalla propia por fase/tarea**: las tareas de cada fase son etiquetas sin botón. Cada fase (y su tarea) debe abrir su propio detalle (qué se hizo, evidencia, autor, fechas). |
| PT2 | 🔤 | **"Ideacion y precipitacion de ideas"** → revisar redacción (¿"Ideación y priorización de ideas"?). |
| PT3 | 🔤 | **"Buscar alianza y alianzas"** → "Buscar alianzas estratégicas". |
| PT4 | 🔤 | **"Escalamiento y Clifton"** → revisar nombre real de la FASE 4 (¿"Escalamiento"? ¿"CliftonStrengths"?). |
| PT5 | ⚙️ | "Descargar plan" → solo toast. Definir si descarga el plan (PDF) o se quita. |
| PT6 | ⚙️ | Los estados por tarea (Completada/En curso/Pendiente/Bloqueada) deben poder cambiar de estado vía acción del docente, y el estudiante debe ver el avance por fase (sub-progreso). |

### 1.8 `estado-seguimiento.html`
| # | Tipo | Corrección |
|---|------|------------|
| ES1 | 🔤 | **"Miiovimiento en el plan"** (doble i, typo) → **"Movimiento en el plan"** / "Mi avance en el plan". |
| ES2 | 🔤 | **"While no sea activada por un administrador"** → "**Mientras** no sea activada por un administrador" (inglés mal mezclado). |
| ES3 | ⚙️ | El % por fase debe calcularse igual que en `plan-trabajo.html` y `dashboard.html` (consistencia D3). |

### 1.9 `seguimiento.html`
| # | Tipo | Corrección |
|---|------|------------|
| SE1 | 🏗️ | **No existe vista específica por registro de seguimiento**: la columna Acciones (`ver`) abre un modal genérico con una sola línea. Crear ficha de seguimiento (qué se registró, por quién, cuándo, evidencia, estado, historial que llevó al avance). |
| SE2 | 🏗️ | El estudiante actualmente solo "ve" seguimientos del docente. Verificar que los avances propios del estudiante también entren a esta tabla (regla de negocio SGEMD: seguimiento bidireccional). |
| SE3 | ⚙️ | Verificar con la spec qué actores crean registros y qué estados tiene un registro (la regla BR del README). |

### 1.10 `tareas.html`
| # | Tipo | Corrección |
|---|------|------------|
| TA1 | 🔤/⚙️ | **Contadores inconsistentes**: el encabezado dice "10 en total · 6 completadas · 4 pendientes · 1 vencida" pero las listas muestran 3 pendientes + 1 en revisión + 3 completadas = **7**. Hacer que los contadores sumen lo que realmente lista la vista (o listar todo). |
| TA2 | 🏗️ | **"Vencidas 1" no tiene sección propia** en la vista → agregar sección "Vencidas" (o quitarla si no existe). |
| TA3 | ⚙️ | **"Descargar reporte" no tiene filtro**: descarga general sin opción de elegir tarea/fase/rango/estado. ⚠️ Decisión de cliente pendiente (ver §4). |
| TA4 | ⚙️ | Las 3 secciones usan el mismo layout de tarjeta → definir distinciones visuales mínimas (aunque el contenido sea el mismo) o dejarlo intencional. |
| TA5 | ⚙️ | Card "Abrir/Ver" ya navega a `tarea-detalle.html` ✅. Mantener. |

### 1.11 `tarea-detalle.html`
| # | Tipo | Corrección |
|---|------|------------|
| TD1 | ⚙️ | **No se puede subir archivo**: la zona "Arrastra o haz clic" es un `<div class="drop">` **sin handler** y no hay `<input type="file">` en el HTML. Convertir en `<label>` de un input file real (con drag&drop) y listar los adjuntos. |
| TD2 | ⚙️ | Botón **"Adjuntar ahora"** crea un input dinámico y hace `.click()`, pero al elegir archivo **solo cambia el texto y muestra toast** → la lista "Adjuntos" nunca se actualiza (sigue "0 archivos"). Implementar la adición real de adjuntos (nombre, tamaño, fecha, estado). |
| TD3 | ⚙️ | **"Marcar como completada" está `disabled` fijo en el HTML y el JS nunca lo habilita** → el estudiante **jamás** puede marcarla. Habilitarlo cuando exista evidencia adjunta (o según regla de negocio) y persistir el cambio de estado. |
| TD4 | 🏗️ | Decidir con el equipo: ¿el estudiante marca "completada" o solo la envía a revisión y el docente la califica? (La tabla de `tareas.html` dice "En revision · esperando calificacion"; la spec definirá el flujo). |

### 1.12 `asesorias.html`
| # | Tipo | Corrección |
|---|------|------------|
| AS1 | ⚙️ | **BUG GRAVE: "Ver detalle" (×2) y "Ver acta" apuntan a `solicitar-asesoria.html`** (la pantalla para SOLICITAR una asesoría), no a la ficha de cada asesoría. Crear vista/panel de detalle de asesoría (o navegar a una ficha propia). |
| AS2 | 🏗️ | **Asesorías realizadas incompletas**: la tarjeta solo muestra fecha, docente, hora, modalidad y "Realizada". Falta el **motivo/tema** (¿por qué se pidió?), el **acta** y el resultado. |
| AS3 | 🏗️ | Mismo diseño de tarjeta para los 3 estados (Pendiente de confirmar / Confirmada / Realizada) → diferenciar visual y funcionalmente (acciones distintas por estado). |
| AS4 | ⚙️ | "Solicitar asesoria" (botón del header) sí navega a `solicitar-asesoria.html` ✅. Mantener. |

### 1.13 `solicitar-asesoria.html`
| # | Tipo | Corrección |
|---|------|------------|
| SA1 | ⚙️ | **"Fecha y hora preferida" es `<input type="date">` → solo fecha, sin hora.** Agregar selector de hora (o `datetime-local`) según la regla de negocio (el estudiante propone, el docente confirma). |
| SA2 | 🏗️ | **No existe la opción de elegir 3 fechas posibles** (propuesta del usuario). Diseñar componente de selección múltiple de fechas (cada fecha con su franja horaria opcional). ⚠️ Confirmar si la decisión del cliente es 1 fecha o 3. |
| SA3 | ⚙️ | "Enviar solicitud" → solo toast. Debe crear la solicitud (localStorage en prototipo) y mostrar su estado en `asesorias.html`. |
| SA4 | ⚙️ | El select de emprendimiento está fijo ("Sabor y Sabe") → debe listar los emprendimientos del estudiante. |

### 1.14 `eventos.html`
| # | Tipo | Corrección |
|---|------|------------|
| EV1 | 🏗️ | **No existe vista de detalle por evento**: la acción `ver` abre un modal genérico con el texto de la fila. Crear ficha de evento (descripción, fecha, hora, agenda, aforo, estado). |
| EV2 | ⚙️ | **"Inscribirse" no actualiza nada**: solo cambia la clase del botón + toast. No mueve el evento a la lista "Eventos en los que ya estás inscrito" ni pinta el calendario. Implementar la inscripción real (vincular con localStorage + estado). |
| EV3 | 🏗️ | **El calendario es estático**: no muestra los eventos listados (ni los del día como marcadores). Conectar el calendario con los eventos (día → punto/lista). |
| EV4 | 🏗️ | La lista "Ya estás inscrito" tiene un solo ítem estático → debe reflejar los eventos donde el estudiante realmente se inscribió. |

### 1.15 `notificaciones.html`
| # | Tipo | Corrección |
|---|------|------------|
| NO1 | ⚙️ | **"Marcar todas como leídas" no hace nada** (acción inexistente en el kit) → implementar: marca las 4 notificaciones como leídas visualmente. |
| NO2 | ⚙️ | **Los filtros (Todas/Sin leer/Tareas/Asesorias/Seguimiento) no producen efecto real**: el kit filtra filas de `<table>` (`tbody tr`) pero las notificaciones son una lista `<li>` → o convertir a tabla, o implementar filtro por `data-*` en los `<li>`. |
| NO3 | ⚙️ | El estado "leída/no leída" no existe en los ítems → agregar estado y persistirlo. |

### 1.16 `perfil.html`
| # | Tipo | Corrección |
|---|------|------------|
| PE1 | ⚙️ | **"Guardar cambios" no guarda**: solo toast. Capturar y persistir los datos del formulario (nombre, emprendimientos, etc.). |
| PE2 | ⚙️ | **"Actualizar contrasena" no hace nada**: la acción no existe en el kit → implementar validación (contraseña actual + nueva + confirmación) y persistir/avisar según backend. |
| PE3 | ⚙️ | **"Cerrar sesion" (botón del perfil) solo muestra toast** → el logout real solo funciona desde el menú del avatar (iniciales "ML", esquina superior derecha). Conectar el botón del perfil al mismo cierre de sesión (borrar `sgemd:sesion` + redirigir a login). |
| PE4 | ⚙️ | "Cancelar" debe descartar cambios y volver (o no hacer nada si no hay edición pendiente). |

---

## 2. Correcciones transversales (compartidas por todas las vistas)

| # | Tipo | Corrección |
|---|------|------------|
| BT1 | ⚙️ | **Breadcrumb muerto**: los enlaces "Inicio › Sección ›…" son `<a href="#">`. La navegación real del breadcrumb no existe (solo la barra lateral). Decidir: conectar el breadcrumb a las páginas destino o quitarlo. |
| BT2 | ⚙️ | Botones "Exportar", "Descargar plan", "Descargar PDF", "Descargar reporte", "Enviar", "Guardar…": **todos son toasts fingidos** (el prototipo no tiene backend). Para la demo es aceptable, pero documentar que es comportamiento de prototipo y que la versión final debe persistir/descargar de verdad. |
| BT3 | ⚙️ | **El kit JS deduce la acción del texto del botón** (`slug`). Esto hace que botones nuevos "funcionen" con toasts genéricos sin cableado real. Al corregir, dar `data-accion` explícita a cada botón real para que el manejo sea intencional. |
| BT4 | ⚙️ | **Logout**: existe solo una implementación (menú de avatar). Unificar en una función `cerrarSesion()` compartida y usarla en todos los botones de cierre. |

---

## 3. Errores de texto (typos / i18n) — checklist global 🔤

| # | Archivo | Actual | Correcto sugerido |
|---|---------|--------|-------------------|
| T1 | `dashboard.html` | "Asesorias attended" | "Asesorías realizadas" |
| T2 | `estado-seguimiento.html` | "Miiovimiento en el plan" | "Movimiento en el plan" / "Mi avance en el plan" |
| T3 | `estado-seguimiento.html` | "While no sea activada por un administrador" | "Mientras no sea activada por un administrador" |
| T4 | `plan-trabajo.html` | "Ideacion y precipitacion de ideas" | "Ideación y priorización de ideas" (confirmar con el programa real) |
| T5 | `plan-trabajo.html` | "Buscar alianza y alianzas" | "Buscar alianzas estratégicas" |
| T6 | `plan-trabajo.html` / `estado-seguimiento.html` | "Escalamiento y Clifton" | Revisar nombre real de la FASE 4 |
| T7 | `emprendimiento-detalle.html` | "Areas de flipped classroom yckis" | Limpiar (quitar "yckis") |
| T8 | `tareas.html` | Contadores 10/6/4/1 vs listas 3+1+3 | Alinear números |
| T9 | General | Acentos/ñ faltantes en todo el prototipo ("Diagnostico", "Asesorias", "contrasena", "seccion", "proximas"…) | Revisar normalización de tildes (el pipeline ya tiene `_normalizar_tipografia.py`). |

---

## 4. Decisiones pendientes con el equipo / cliente ❓

1. **Reporte de tareas**: ¿el estudiante descarga un reporte filtrado por tarea/fase/rango, o es un reporte general? (Ítem del usuario: "preguntar a los compañeros si es decisión del cliente".)
2. **Asesorías**: ¿1 fecha + hora, o **3 fechas posibles** (propuesta del usuario)? ¿El estudiante elige hora o la fija el docente? (La spec: el estudiante propone y el docente/admi confirma → el prototipo no lo cumple porque no hay hora.)
3. **Imagen del emprendimiento**: ¿campo obligatorio? ¿quién la sube (estudiante o admin)? ¿dónde se muestra?
4. **Flujo de tareas**: ¿el estudiante puede "marcar como completada" directamente, o envía a revisión y el docente la califica? (La tabla actual sugiere "en revisión → esperando calificación".)
5. **Calendario de eventos**: ¿días con evento se pintan solos, o el estudiante ve los eventos en una pantalla aparte?

---

## 5. Priorización sugerida

### Fase 1 — Correcciones rápidas (texto y cables, bajo esfuerzo)
- T1–T9 (typos/i18n/números).
- ES1, ES2 (typos de estado seguimiento).
- EM1 (agregar `data-filtro` a los 2 selects).
- PE3 (conectar "Cerrar sesión" del perfil al logout real).
- NO1 (marcar todas como leídas).
- DR3, EE2, SA3 (navegación/guardado simple).

### Fase 2 — Funcionalidad corregible en el mismo kit (esfuerzo medio)
- ED1 (paneles de pestañas del detalle).
- TD1–TD3 (input file real, adjuntos, habilitar "Marcar como completada").
- DG1–DG4 (navegación del diagnóstico + contenido secciones 2–5 + contador real).
- EV2 (inscripción a eventos que actualice inscritos y calendario).
- NO2 (filtros de notificaciones).
- AS1 (corregir destino de "Ver detalle"/"Ver acta") + AS2/AS3 (ficha y estados de asesoría).

### Fase 3 — Estructural (requiere decidir UX/spec primero)
- PT1 (pantalla por fase/tarea), SE1 (ficha de seguimiento), EV1/EV3/EV4 (detalle y calendario de eventos), EM2/EM3/EM4 (crear con imagen y navegación real), EM5/PT5/DR2 (descargas reales).
- Las 5 decisiones del §4 deben cerrarse ANTES de esta fase.

---

## 6. Cómo aplicar las correcciones

1. **Wording/texto (Fase 1):** editar `paginas_estudiante.py` (y `paginas_docente.py`/`paginas_admin.py` si se propagan) y regenerar con `python generar.py`.
2. **Comportamiento (Fase 2):** ajustar `lib_js.py` (el Dispatcher) — agregar casos reales para las acciones (navegación, subida de archivos, inscripción) en lugar de toasts genéricos.
3. **Estructura (Fase 3):** requiere rediseño en **Stitch** con prompts específicos (se pueden generar con `stitch-prompt-pro` a partir de este documento) o nuevas funciones en los generadores Python.
4. **Validación:** después de regenerar, re-correr la verificación (los archivos `_analisis_*.py` / `_auditar.py` del pipeline ayudan a auditar la salida).

> ⚠️ **No se debe tocar el remoto ni hacer commits de estas correcciones sin revisarlas con el equipo.** Este documento es la hoja de ruta; el original del cliente (README) es la fuente de la verdad de las reglas de negocio.