# Prototipo SGEMD

Prototipo navegable del **SGEMD — Sistema de Gestión de Emprendimiento Minuto de Dios**.
73 pantallas + índice, tres roles (Estudiante, Docente, Administrador) y las cuatro
pantallas globales de acceso.

- **Stitch:** https://stitch.withgoogle.com/projects/3060781598377201049
- **Índice local:** [`index.html`](index.html) — ábrelo con doble clic, sin servidor


> **Advertencia de alcance:** este es un prototipo de interfaz. **No hay backend.**
> El login es simulado y la "sesión" vive en `localStorage` del navegador. Nada de
> lo que se ve aquí envía correos, guarda datos ni valida contra un servidor real.

---

## Contenido

- [Prototipo SGEMD](#prototipo-sgemd)
  - [Contenido](#contenido)
  - [1. Cómo verlo](#1-cómo-verlo)
    - [Opción A — el índice local (recomendada para revisar)](#opción-a--el-índice-local-recomendada-para-revisar)
    - [Opción B — Stitch](#opción-b--stitch)
    - [Cuentas de demostración](#cuentas-de-demostración)
  - [2. Qué contiene](#2-qué-contiene)
  - [3. Las vistas por rol](#3-las-vistas-por-rol)
    - [3.1 Acceso global (4)](#31-acceso-global-4)
    - [3.2 Estudiante (20 vistas, 27 archivos)](#32-estudiante-20-vistas-27-archivos)
    - [3.3 Docente (23)](#33-docente-23)
    - [3.4 Administrador (19)](#34-administrador-19)
  - [4. Reglas de negocio representadas](#4-reglas-de-negocio-representadas)
  - [5. Sistema de diseño](#5-sistema-de-diseño)
    - [Paleta cerrada](#paleta-cerrada)
    - [Tipografía](#tipografía)
    - [Formas y espaciado](#formas-y-espaciado)
    - [Responsive](#responsive)
  - [6. Logo](#6-logo)
  - [7. Cómo está construido](#7-cómo-está-construido)
  - [8. Comandos](#8-comandos)
  - [9. Validación automática](#9-validación-automática)
  - [10. Publicación en Stitch](#10-publicación-en-stitch)
    - [Por qué el flujo es como es](#por-qué-el-flujo-es-como-es)
  - [11. Limitaciones conocidas](#11-limitaciones-conocidas)
  - [12. Cambios del rol Estudiante (`prototype/Fixstudent`)](#12-cambios-del-rol-estudiante-prototypefixstudent)
    - [12.6 Auditoría funcional de las vistas de Estudiante](#126-auditoría-funcional-de-las-vistas-de-estudiante)
  - [13. Cambios del rol Administrador (`prototype/Admin-Refactor`)](#13-cambios-del-rol-administrador-prototypeadmin-refactor)
    - [13.7 Verificación](#137-verificación)
  - [Ver también](#ver-también)

---

## 1. Cómo verlo

### Opción A — el índice local (recomendada para revisar)

```
prototype/index.html
```

Doble clic. El índice agrupa las 73 pantallas por carpeta y enlaza a cada una, así
que sirve como mapa de navegación del prototipo completo. Ábrelo **desde el
sistema de archivos**: los enlaces son relativos y con `file://` funcionan tal cual.

### Opción B — Stitch

<https://stitch.withgoogle.com/projects/3060781598377201049>

Cada pantalla es un documento independiente dentro del proyecto.

> **Comentario:** este enlace se actualizó porque el proyecto anterior
> (`projects/8880818071963426152`) se borró debido a un error. El prototipo se creó
> de nuevo en Stitch y se resubieron las 51 pantallas, por lo que la dirección cambió.

### Cuentas de demostración

El login trae un panel desplegable con las tres cuentas. También puedes escribirlas
a mano:

| Rol | Usuario | Contraseña | Destino |
|---|---|---|---|
| Estudiante | `estudiante` | `estudiante` | `estudiante/dashboard.html` |
| Docente | `profesor` | `profesor` | `docente/dashboard.html` |
| Administrador | `admi` | `admi` | `admin/dashboard.html` |

En el login, pulsar una fila del panel completa el usuario y resalta el botón
**Usar**. La contraseña se compara tal cual, sin distinguir mayúsculas.

---

## 2. Qué contiene

| Carpeta | Archivos | Contenido |
|---|---|---|
| `compartido/` | 4 | Login, registro, verificación OTP, recuperación de contraseña |
| `estudiante/` | 27 | Inicio, emprendimiento (lista + detalle por emprendimiento), diagnóstico, plan, seguimiento, tareas, asesorías, eventos, perfil, configuración, notificaciones |
| `docente/` | 23 | Inicio (dashboard con calendario), emprendimientos asignados (por estudiante), expediente, avances, diagnóstico, tareas, asesorías, eventos (catálogo + detalle con recomendación), perfil (dashboard de la cuenta), configuración, notificaciones |
| `admin/` | 19 | Inicio, gestión de perfiles, solicitudes, emprendimientos (lista + expediente + plan), seguimiento (lista + tablero), tareas, asesorías, eventos (catálogo + alta), asignaciones, diagnósticos, reportes, respaldos, perfil, notificaciones, configuración |
| **Total** | **73** | más `index.html` como índice local |

Son **66 vistas lógicas** repartidas en **73 archivos**: varias vistas se reproducen
en más de un archivo. El *detalle de tarea* del estudiante (#15) se reproduce en cinco
estados (`tarea-detalle.html` más los de `en-revision`, `completada-precio`,
`completada-usuarios` y `completada-clientes`), el *detalle del evento* —en el rol
Estudiante (#18b) y en el Docente (#36)— en cuatro archivos cada uno, uno por evento
(`evento-detalle-startup`, `evento-detalle-capacitacion`,
`evento-detalle-asesoria-grupal` y `evento-detalle-showroom`), y el *detalle del
emprendimiento* (#08) en uno por emprendimiento (`emprendimiento-detalle.html` y
`emprendimiento-detalle-mochilas.html`).

Elementos de interfaz comunes a todo el prototipo:

- **Shell con barra lateral** por rol, con secciones y estado activo; en ≤1023 px
  se colapsa en un panel deslizable con botón hamburguesa.
- **Barra superior** con logo, buscador, notificaciones y menú de usuario.
- **Tablas** con búsqueda, filtros, orden y acciones por fila.
- **Tarjetas de métrica**, avisos destacados (*callouts*), etiquetas de estado
  (*badges*) y tablas de detalle. Los tres términos son nombres de componente del
  diseño, no del código: en el HTML son clases `.aviso` y `.badge`.
- **Gráficos SVG** generados por código, sin librerías externas.
- **Modales y notificaciones** para confirmaciones y acciones críticas.

---

## 3. Las vistas por rol

### 3.1 Acceso global (4)

| # | Vista | Qué resuelve |
|---|---|---|
| 01 | Login | Acceso con usuario y contraseña, recordar usuario, panel de cuentas demo |
| 02 | Registro | Alta de cuenta: datos personales, documento, correos, teléfono, contraseña y consentimiento |
| 03 | Verificar OTP | Código de 8 dígitos; explica que el perfil queda *Limitado* hasta la activación |
| 04 | Recuperar contraseña | Correo + documento; respuesta genérica para no revelar qué cuentas existen |

### 3.2 Estudiante (20 vistas, 27 archivos)

| # | Vista | Qué resuelve |
|---|---|---|
| 05 | Inicio | Resumen de estado, tareas por completar y próximas asesorías; las tarjetas muestran una vista previa al pasar el mouse |
| 06 | Estado de seguimiento | Avance general por fase, con **una barra y su porcentaje por cada fase**, y requisitos por cumplir |
| 07 | Mi emprendimiento | Listado de sus emprendimientos; el **detalle de cada uno se abre en su propia vista** |
| 08 | Detalle del emprendimiento — Sabor y Sabe | Ficha completa por pestañas: resumen, diagnóstico, plan, seguimiento, tareas y asesorías |
| 08b | Detalle del emprendimiento — Mochilas Origen | La misma plantilla con la ficha, las redes y el avance propios de Mochilas Origen |
| 09 | Editar emprendimiento | Solo nombre, descripción y redes; el resto es de solo lectura |
| 10 | Diagnóstico | Cuestionario por etapas, con selector de **sector** y **tipo de emprendimiento** |
| 11 | Resultados del diagnóstico | Puntajes por dimensión y recomendaciones |
| 12 | Plan de trabajo | Fases y tareas por emprendimiento; **Descargar plan** genera un documento con el resumen y el detalle por fase |
| 13 | Seguimiento | Historial de avances (**solo lectura**) |
| 13b | Detalle del seguimiento | Un registro: tipo, título, descripción y avance al momento |
| 14 | Mis tareas | Tablero por emprendimiento y por estado, con fecha límite |
| 15 | Detalle de tarea | Instrucciones, evidencia, **fecha de envío** con indicador de puntualidad y comentarios del docente |
| 16 | Mis asesorías | Historial y próximas sesiones, con el número de emprendimientos |
| 17 | Solicitar asesoría | Elige **fecha propuesta**; el docente confirma fecha y hora |
| 18 | Eventos | Convocatorias y eventos del programa |
| 18a | Detalle del evento — Startup Minuto de Dios | En qué consiste, datos e inscripción (presencial) |
| 18b | Detalle del evento — Capacitación en modelado | En qué consiste, datos, inscripción y enlace de acceso (virtual) |
| 18c | Detalle del evento — Asesoría grupal | En qué consiste, datos e inscripción (presencial) |
| 18d | Detalle del evento — Showroom | En qué consiste, datos e inscripción (presencial) |
| 19 | Mi perfil | Datos básicos del estudiante y sus emprendimientos; el botón para editar lleva a Configuración |
| 19b | Configuración | Edita datos personales, **académicos condicionales** (pregrado / posgrado / egresado), contraseña y foto |
| 20 | Notificaciones | Cada aviso enlaza a su vista; incluye filtros y campana |

### 3.3 Docente (23)

Las acciones del docente son **vistas completas**, no ventanas emergentes (solo *Marcar todo como leído* conserva un diálogo de confirmación).

| # | Vista | Qué resuelve |
|---|---|---|
| 21 | Inicio | Métricas, **avance por emprendimiento** a ancho completo y **calendario de compromisos** (arranca hoy; cada día muestra sus asesorías, tareas y eventos) |
| 22 | Mis asesorías | **Una tabla** con filtro de estado agrupado (*Por agendar · Agendada · Completada · Cancelada*) |
| 23 | Detalle de asesoría | Vista completa: confirmar, reprogramar o rechazar la solicitud |
| 24 | Registrar asesoría | Agenda por **grupo** (todo el emprendimiento): tema por defecto, hora disponible y necesidades |
| 25 | Emprendimientos asignados | Los asignados (N:N) en Tarjetas/Tabla; **selector de estudiante** que muestra sus emprendimientos como **pestañas** |
| 26 | Expediente del emprendimiento | Historial: avances, tareas, asesorías, diagnóstico, estudiantes del grupo, comentarios |
| 27 | Detalle del avance | Un avance: descripción, evidencia adjunta, historial y edición |
| 28 | Registrar avance | Formulario-página del avance (fase, puntaje 0–100, estado de revisión, evidencia) |
| 29 | Diagnóstico | Selector de emprendimiento y filtros; se calcula por **4 fases** o por **tareas clave** |
| 30 | Revisión del diagnóstico | Lectura del resultado y recomendaciones al estudiante |
| 31 | Tareas asignadas | Crea, asigna y califica tareas |
| 32 | Detalle de tarea | Vista completa de la entrega: evidencia, calificación y devolución |
| 33 | Devolver tarea | Vista propia con **motivo** y **observaciones** |
| 34 | Asignar tarea | Formulario-página de la tarea y su evidencia |
| 35 | Eventos | Catálogo de eventos del programa con tabla, calendario y recomendaciones enviadas |
| 36 | Detalle del evento (Startup) | Información completa del evento + **recomendación embebida** (por emprendimiento o estudiante) |
| 37 | Detalle del evento (Capacitación) | Igual que 36; evento **virtual** con su enlace de acceso |
| 38 | Detalle del evento (Asesoría grupal) | Igual que 36; incluye los pasos de la asesoría |
| 39 | Detalle del evento (Showroom) | Igual que 36; incluye la nota de montaje del stand |
| 40 | Mi perfil | **Dashboard de la cuenta:** datos, emprendimientos asignados y estado |
| 41 | Configuración | Edita datos, preferencias de notificación y accesos de seguridad |
| 42 | Cambiar contraseña | Vista propia para la contraseña institucional |
| 43 | Notificaciones | Avisos del sistema |

> **Refactor UX/UI del Rol Docente:** las pantallas fueron rediseñadas en cuatro
> iteraciones (filtros funcionales, pestañas, bitácora de comentarios, accesibilidad,
> **acciones como vistas completas** y, en la última, **calendario interactivo de
> compromisos**, **detalle de evento con recomendación** y **perfil como dashboard**).
> El menú lateral usa los **mismos grupos/acordeón que el rol Estudiante**, con
> *Tareas* dentro de **Mis emprendimientos**. El CSS/JS del rol va **embebido en cada
> HTML** y se genera desde `paginas_docente.py` (helper `_inyectar`), así que correr
> `python generar.py` **reproduce** los cambios sin pérdida. Detalle en
> [`../docs/docente-rol-ux.md`](../docs/docente-rol-ux.md).

### 3.4 Administrador (19)

| # | Vista | Qué resuelve |
|---|---|---|
| 01 | Inicio | Panorama institucional: usuarios, emprendimientos y seguimiento, con series reales del programa |
| 02 | Gestión de perfiles | **Dos tablas** (docentes y estudiantes) con buscador, filtros, paginación y ficha por fila; alta, edición y bloqueo de cuentas |
| 03 | Solicitudes pendientes | Bandejas de desbloqueo, segundo emprendimiento y citas de asesoría, con pestañas por estado, ficha y aprobación |
| 04 | Emprendimientos | Registro maestro del programa: filtros por sector, etapa y sede, y ficha de cada emprendimiento |
| 05 | Expediente del emprendimiento | Ficha completa del emprendimiento y de su grupo |
| 06 | Plan de trabajo | Plan, fases y carga de trabajo del emprendimiento |
| 07 | Seguimiento | Estado y avance de los emprendimientos, con registro de avance desde la fila |
| 08 | Tablero de seguimiento | Métricas consolidadas de seguimiento institucional |
| 11 | Asesorías | Indicadores de uso, respuesta y programación del servicio de asesorías |
| 12 | Eventos | Aprueba y publica eventos del programa, con calendario |
| 13 | Crear evento | Publica un evento y notifica a los asistentes |
| 14 | Asignaciones | Asigna docentes registrados a los emprendimientos y permite **reasignar** en modal |
| 15 | Diagnósticos | Resultados del diagnóstico de los estudiantes |
| 16 | Reportes | Exporta reportes institucionales en CSV, PDF o XLSX |
| 17 | Tareas | Consulta, alta y baja de tareas por emprendimiento |
| 18 | Mi perfil | Datos del administrador y su actividad |
| 19 | Notificaciones | Registro de aprobaciones y decisiones del equipo |
| 20 | Respaldos y recuperación | Gestión de respaldos y verificación de integridad |
| 21 | Configuración | Parámetros del programa, sedes, notificaciones y bitácora |

> **Refactor UX/UI del Rol Administrador:** las 19 pantallas se regeneraron desde
> `paginas_admin.py` (no se editó HTML a mano), de modo que las tablas se pintan con
> los datos del generador, cada fila abre su **ficha** en modal y los
> **buscadores/filtros responden de verdad**. Hay **enlaces profundos** por `hash`
> (`#est-912646`, `#emp-EMP-041`, `#doc-DOC-014`, `#sol-…`) y un acceso directo
> (`#asignar-docente`) que abre el primer emprendimiento sin docente. El CSS/JS del
> rol va embebido en cada HTML y `python generar.py --rol admin` reproduce los
> cambios. Detalle en [`cambios-a-admin.md`](cambios-a-admin.md).

---

## 4. Reglas de negocio representadas

Estas restricciones no son cosméticas: están reflejadas en las pantallas y son la
razón de que las vistas no sean idénticas entre roles.

- **BR-002 — el estudiante no agenda al docente.** Al solicitar asesoría elige una
  *fecha propuesta*; la hora la confirma el docente. El estudiante nunca elige
  docente ni horario confirmado.
- **BR-003 — el estudiante edita poco.** Solo nombre, descripción y redes. Tipo,
  sector, etapa y acta son de solo lectura.
- **Seguimiento del estudiante es de solo lectura.** El docente registra y califica
  avances (desde el modal «Registrar avance» y la columna de evidencia); el estudiante
  consulta.
- **Toda tarea exige evidencia** para cerrarse.
- **Toda eliminación pide confirmación** antes de ejecutarse.
- **El docente solo ve sus emprendimientos asignados**; el administrador ve todos.
- **Roles y alcance:** los tres paneles laterales tienen ítems distintos porque las
  capacidades lo son.

La especificación completa está en [`../README.md`](../README.md) (raíz) y
[`../docs/`](../docs).

---

## 5. Sistema de diseño

La guía completa está en [`DESIGN.md`](DESIGN.md). Resumen:

### Paleta cerrada

Solo se admiten **seis** colores; cualquier otro valor es un error (lo verifica
`_auditar.py`):

| Token | Valor | Uso |
|---|---|---|
| `--amarillo` | `#ffd300` | Acento: botón primario, resaltes, foco |
| `--blanco` | `#ffffff` | Fondos de superficie |
| `--azul-profundo` | `#162644` | Texto secundario, bordes suaves |
| `--azul-noche` | `#051533` | Texto principal y barra lateral |
| `--azul-real` | `#004a93` | Enlaces, acentos fríos |
| `--gris` | `#bbbbbb` | Bordes y separadores |

Reglas de uso: `#ffd300` **nunca** como texto sobre blanco; `#bbbbbb` **nunca** como
texto legible. Los tintes de superficie y estado se derivan con `rgba()` de esos
mismos seis (`--azul-06`, `--noche-04`, `--amarillo-14`…), nunca con colores nuevos.

### Tipografía

- **Familia:** `Inter`. Se carga por `<link>` a Google Fonts (pesos 400/500/600/700/800);
  si esa petición falla o el equipo está sin internet, cae a la pila del sistema
  (`-apple-system`, `Segoe UI`, `Roboto`, `Arial`) sin romper el layout.
- **Escala de ocho pasos:** 32 · 28 · 24 · 20 · 18 · 16 · 14 · 13 px.
- Nada por debajo de 13 px; interlineado nunca más cerrado que 1.15.

### Formas y espaciado

- Radios: `8px` (control), `12px` (tarjeta), `999px` (píldora).
- Espaciado en múltiplos de `8px`: 8 · 16 · 24 · 32 · 40 · 48.
- Sombras: tres niveles, siempre con tinte azul-noche, nunca negro puro.

### Responsive

Verificado a **1440 · 1280 · 768 · 375 px**:

| Ancho | Comportamiento |
|---|---|
| ≥1280 | Sidebar de 264 px, contenido en rejilla de 4 columnas |
| 1024–1279 | Sidebar colapsado a iconos (72 px) |
| 768–1023 | Sidebar fuera de flujo, se abre con hamburguesa; rejillas a 1 columna |
| ≤767 | Encabezados apilados, tabla por tarjeta (`data-label: valor`) |
| ≤479 | Buscador oculto, botones a ancho completo |

Las tablas no se ocultan ni se recortan: a 375 px se apilan como tarjetas y en
anchos intermedios usan scroll horizontal deliberado.

---

## 6. Logo

Las variantes del logo viven en `_marca/`. El PNG fuente original
(`docs/Logo_sinfondo.png`), del que las derivaba `_marca/preparar_logo.py`, **ya no
está en el repositorio**, así que los archivos versionados de `_marca/` son la
fuente de verdad:

| Archivo | Uso |
|---|---|
| `_marca/logo-color-1200.png` | Lockup a color; es la pantalla de marca que se sube a Stitch |
| `_marca/logo-blanco-600.png` | Versión blanca para el sidebar y fondos oscuros |
| `logo_datos.py` | Data URIs en base64 de ambas, para incrustar sin pedir archivo externo |

El logo va **embebido como data URI** dentro del HTML. Stitch entrega cada pantalla
como documento independiente, así que una referencia por URL externa no sería fiable.

---

## 7. Cómo está construido

**El HTML no se edita a mano: se genera desde Python.** Editar un `.html` generado
se pierde en la siguiente ejecución.

```
prototype/
├── generar.py              Orquestador: emite las 73 pantallas + index.html
├── paginas_auth.py         4 pantallas de acceso + su CSS y su JS
├── paginas_estudiante.py   27 pantallas del estudiante
├── paginas_docente.py      23 pantallas del docente
├── paginas_admin.py        19 pantallas del administrador
├── lib_ui.py               Shell, navegación, tablas, formularios, tarjetas
├── lib_css.py              Tokens, paleta, responsive, componentes
├── lib_js.py               Interacciones (filtros, menús, modales, toasts)
├── lib_charts.py           Gráficos SVG sin dependencias
├── logo_datos.py           Data URIs del logo (generado)
├── _marca/preparar_logo.py Deriva las variantes de logo
├── index.html              Índice local (generado)
├── compartido/ estudiante/ docente/ admin/   HTML generado
└── DESIGN.md               Guía de diseño
```

Cada pantalla es un **documento HTML autocontenido en lo que importa**: CSS e iconos
SVG embebidos, logo en data URI, gráficos generados por código y el JS al final del
`<body>`. Sin frameworks, sin `fetch`, sin módulos ES. La única dependencia externa es
la tipografía, que se pide a Google Fonts por `<link>`.

Esto es una restricción de Stitch, que sirve cada pantalla como documento separado:
nada puede depender de otro archivo del proyecto, así que cada HTML tiene que
contenerlo todo. La única excepción que queda es la fuente, y por eso el logo **no**
va por URL: un data URI no puede fallar.

> La carpeta se llama `prototype`; antes se llamaba `temporal`. Si ves esa palabra en
> un script o en un commit antiguo, es el nombre previo.

---

## 8. Comandos

Todos se ejecutan **desde `prototype/`**. La única dependencia opcional es
Playwright, y solo para las auditorías de navegador (`pip install playwright` y
`playwright install chromium`).

```powershell
# Generar (emite las 73 pantallas + index.html)
python generar.py

# Generar solo un rol, para no reescribir el resto
python generar.py --rol admin
python generar.py --rol estudiante --rol docente

# Generar solo una pantalla (repetible), en los roles que se pidan
python generar.py --vista dashboard.html
python generar.py --rol estudiante --vista perfil.html --vista configuracion.html

# Regenerar las variantes de logo desde el PNG fuente (hoy fuera del repo)
python _marca\preparar_logo.py

# Publicar en Stitch
python subir.py --force

# Volver a leer Stitch y rehacer el informe de duplicados
python _reconciliar.py
```

`subir.py` y `_reconciliar.py` usan la variable de entorno `STITCH_API_KEY`.

---

## 9. Validación automática

El prototipo no se dio por bueno "a ojo": hay **ocho auditorías** sobre las 73
pantallas —cinco estáticas y tres de navegador—. Las estáticas cierran sin
hallazgos en paleta, tipografía, firmas, porcentajes y estructura, con una
salvedad: `_estructura.py` marca el presupuesto de **estilos inline** por encima
del umbral (`PRESUPUESTO_INLINE`), que queda registrado como deuda pendiente y no
bloquea la navegación.

| Script | Qué comprueba |
|---|---|
| `_estructura.py` | Balance de etiquetas, landmarks por rol, `id`/`label`, coherencia de tablas |
| `_auditar.py` | Paleta cerrada, placeholders sin expandir, `%%` sueltos, texto corrupto |
| `_check_firmas.py` | Que las llamadas a `lib_ui`/`lib_charts` existan con la firma real |
| `_check_tipografia.py` | Escala de ocho pasos, mínimo 13 px, interlineado ≥ 1.15 |
| `_check_pct.py` | Literales con `%` sueltos que romperían el formateo |
| `_responsive.py` | 1440/1280/768/375 px: sin desbordes, sin celdas ocultas ni sin etiqueta |
| `_interaccion.py` | Chromium real: filtros, menús, modales, formularios, avisos de error |
| `_accesos.py` | Los tres accesos de punta a punta, incluido el rechazo de contraseña mala |

Dos scripts más son de apoyo, no de verificación:

| Script | Para qué |
|---|---|
| `_normalizar_tipografia.py` | Corrección de una pasada e idempotente de la escala tipográfica |
| `_analisis_controles.py` / `_analisis_inline.py` | Catálogo de controles a hacer interactivos y de estilos inline a extraer |

Las de navegador usan `file://` a propósito: reproducen exactamente cómo se verá la
pantalla en Stitch, sin servidor de por medio. Requieren Playwright (`pip install
playwright` y `playwright install chromium`); en la última pasada no estaba
instalado, así que no se ejecutaron.

---

## 10. Publicación en Stitch

- **Proyecto:** `projects/3060781598377201049`
- **Enlace:** https://stitch.withgoogle.com/projects/3060781598377201049
- **Total:** 51 documentos — 50 pantallas de interfaz más una de marca
  (`_marca/logo-color-1200.png`). El prototipo local ya genera **73 archivos HTML**;
  Stitch conserva los 50 originales: no se subieron los cuatro estados extra de
  *detalle de tarea* ni las vistas nuevas (*detalle del seguimiento*, *configuración*
  y el detalle de cada evento).
- **Comentario:** el enlace se actualizó al recrear el proyecto. El anterior
  (`projects/8880818071963426152`) se borró por un error; se creó uno nuevo en
  Stitch y se resubieron las 51 pantallas.

`index.html` **no** se sube: es una galería local y sus enlaces relativos no
funcionarían dentro de Stitch.

### Por qué el flujo es como es

Stitch expone `screens:batchCreate` como única operación de escritura: no hay PATCH,
PUT ni DELETE de pantallas (devuelven `404`). Eso condiciona todo:

1. `subir.py` marca cada entrada como `pendiente` **antes** de llamar a la API y solo
   la pasa a `ok` si la respuesta trae un id. Si el proceso muere a mitad, queda
   registrado y se puede reintentar con `--force`.
2. No se puede corregir una pantalla subida: hay que borrarla a mano desde la UI de
   Stitch y volver a subirla. Por eso se valida todo **antes** de subir.
3. `_reconciliar.py` relee el proyecto y genera `_duplicados.md` con qué conservar y
   qué eliminar a mano.

---

## 11. Limitaciones conocidas

- **No hay backend.** Login, registro, OTP, recuperación, "guardar" y "descargar"
  son simulaciones. Los mensajes lo declaran en pantalla para que el prototipo no se
  lea como algo en producción.
- **La sesión es del navegador.** `localStorage`, en un `try/catch` porque Stitch
  podría particionarla. Una sesión real necesita backend, `bcrypt` para el hash y
  JWT para el token.
- **Los enlaces entre pantallas no son fiables en Stitch.** Stitch renderiza cada
  documento por separado; la navegación real es por el índice local.
- **Sin control de permisos en el cliente.** Las vistas ya vienen recortadas por rol
  porque se generaron así; un usuario real no debe depender de eso.
- **Responsive validado en navegador de escritorio.** Chromium con viewport
  emulado; no se probó en Safari ni en un móvil físico.
- **La tipografía depende de internet.** Si Google Fonts no responde, las 73
  pantallas se ven con la fuente del sistema. El diseño aguanta el cambio, pero las
  medidas no son idénticas a las capturadas.

---

## 12. Cambios del rol Estudiante (`prototype/Fixstudent`)

Rama **`prototype/Fixstudent`**: correcciones sobre las vistas del rol Estudiante.
El alcance fue **solo estudiante** —las pantallas del rol y el kit compartido que
necesitan (`lib_ui.py`, `lib_js.py`, `lib_css.py`)— sin tocar Docente ni
Administrador. No hay cambios de backend: sigue siendo prototipo.

La rama sale de **`prototype/student`** y añade **un commit** con los cinco puntos
de abajo: 32 archivos (27 pantallas de `estudiante/`, el kit compartido, el
generador del rol y este README).

### 12.1 Mochilas Origen tiene su propia vista de detalle

**Antes:** el botón *Ver detalle* de Mochilas Origen llevaba a
`emprendimiento-detalle.html`, que es la ficha de **Sabor y Sabe**. El estudiante
veía otro emprendimiento y la miga decía `Inicio › Mi emprendimiento › Sabor y Sabe`.

**Ahora:** cada emprendimiento abre su propia vista, con su información:

| Archivo | Emprendimiento | Qué muestra |
|---|---|---|
| `emprendimiento-detalle.html` | Sabor y Sabe | Ficha de alimentos y bebidas, avance 62 %, docente asignado |
| `emprendimiento-detalle-mochilas.html` | Mochilas Origen | Moda y accesorios · Textil, avance 24 %, diagnóstico 2 de 5, **sin docente asignado** |

La plantilla se compartió (`_detalle_emp()`): pestañas de resumen, diagnóstico, plan
de trabajo, seguimiento, tareas y asesorías. La lista *Mi emprendimiento* apunta cada
botón a su vista y `lib_ui.py` resuelve la miga por emprendimiento.

### 12.2 Avance por fases con una barra por fase

En *Estado de seguimiento*, la barra apilada ponía la fase 1 al 100 % y **tapaba la
fase 2 al 62 %**: el estudiante solo veía la primera. Se reemplazó por una barra
independiente por fase, cada una con su nombre y su porcentaje:

| Fase | Avance |
|---|---|
| FASE 1 · Ideación y priorización de ideas | 100 % |
| FASE 2 · Estructuración y ejecución | 62 % |
| FASE 3 · Consolidación del proceso | 0 % |
| FASE 4 · Escalamiento | 0 % |

Helper nuevo `_fase_avance()` en `paginas_estudiante.py` y clases `.fase-avance*`
en `lib_css.py`. La barra repetida dentro de cada tarjeta del *plan de trabajo* se
retiró: el porcentaje ya está en la cabecera de la fase.

### 12.3 Descargar plan de trabajo ordenado

**Antes:** la descarga volcaba un **CSV plano** con las celdas desordenadas.

**Ahora:** genera un **documento estructurado** —el mismo formato del resto de
descargas— con encabezado, una tabla **Resumen de avance** (fase · % · tareas
completadas) y, debajo, el detalle de las tareas de cada fase. Se añadieron estilos
al documento (`CSS_DOC` en `lib_js.py`) para que se lea bien al guardarlo como PDF.
El botón pasó de `data-accion="descargar"` a `data-accion="descargar-plan"`.

### 12.4 Detalle del seguimiento con más información

El **detalle de un registro** de seguimiento (vista 13b) se reorganizó en dos
columnas: a la izquierda *Datos del registro* (título, tipo, fecha, fase,
emprendimiento, **registrado por**) y la *Descripción* del avance; a la derecha el
**avance del emprendimiento al momento del registro** (el anillo de porcentaje) y la
tarjeta ***Cómo leer el seguimiento***, que explica que cada registro documenta un
avance concreto y que la frecuencia de acompañamiento se calcula sobre estos
registros y alimenta el estado de seguimiento.

> Queda pendiente añadir al detalle las **evidencias** del registro, el **historial
> de cambios de la fase** y el bloque **qué sigue**. Hoy el detalle cubre datos,
> descripción, avance y la guía de lectura.

### 12.5 Datos académicos condicionales

En *Configuración → Datos académicos*, **Nivel académico** tiene tres opciones y cada
una muestra un juego de campos distinto:

| Nivel | Campos que muestra |
|---|---|
| **Pregrado** | Semestre (Primero–Décimo) y Modalidad |
| **Posgrado** | Tipo de posgrado, duración, Semestre según el tipo y Modalidad |
| **Egresado** | Fecha de grado del pregrado, Programa del que se graduó, Sede de graduación y Número de acta o diploma |

El **Semestre depende del tipo de posgrado**, con la duración de referencia de
UNIMINUTO:

| Tipo de posgrado | Semestres | Opciones del campo |
|---|---|---|
| Especialización | 2 periodos | Primero – Segundo |
| Maestría | 3 a 4 periodos | Primero – Cuarto |
| Doctorado | 6 a 8 periodos | Primero – Octavo |

Bajo *Tipo de posgrado* hay una nota que se actualiza sola (*"Duración: 3 a 4
semestres; elige el semestre en el que vas"*). **Egresado** oculta Semestre y
Modalidad: para ser egresado hay que haber culminado el pregrado, así que el dato
central es la fecha del título (la del acta o el diploma), junto con el programa, la
sede y el número de acta. **Modalidad** ahora ofrece Presencial · Virtual · **Mixta**.

Implementado con `attrs=` en `select()`/`campo()` de `lib_ui.py` y el bloque
`sincronizarAcademico()` de `lib_js.py`.

### 12.6 Auditoría funcional de las vistas de Estudiante

Se recorrieron las 27 pantallas del rol con un Chrome real (CDP) haciendo clic en
todos los controles (`data-accion`, enlaces, pestañas, chips, acordeones,
paginación y filtros) y verificando el efecto observable de cada uno. Resultado:
**27/27 sin errores de JavaScript**, sin enlaces roto y sin botones muertos.

Se encontró y corrigió **un solo fallo real**:

- **`emprendimiento-detalle-mochilas.html` · "Descargar expediente"** generaba un
  PDF prácticamente vacío (55 caracteres, sin datos). El botón estaba oculto
  (`display:none`) y llevaba `data-doc="1"`; como `tablaDoc()` de `lib_js.py`
  selecciona `main [data-doc]` como el contenedor del documento, devolvía **el
  propio botón** en lugar de una tabla. Ahora el botón es visible y la ficha
  exportable es el **panel "Resumen"** (`data-doc="1"`), de modo que el PDF incluye
  datos básicos, descripción, redes y etapa. La descarga pasó de 55 a ~1007
  caracteres útiles.

Verificado además como correcto (no eran fallos):

| Control | Comprobación |
|---|---|
| Filtros de Mi emprendimiento | FASE 2 → 1 fila, Textil → 1 fila |
| Chips de Notificaciones | Sin leer → 3, Tareas/Asesorías/Seguimiento → 1 |
| Pestañas (detalle, plan, tareas, estado) | Cambian el panel visible |
| Diagnóstico por secciones | Avanza sección 1→4 y se detiene en la última |
| Adjuntar evidencia → Marcar completada | Habilita el botón al adjuntar y persiste el estado |
| Datos académicos condicionales | Pregrado 10, Especialización 2, Maestría 4, Doctorado 8; Egresado oculta semestre y modalidad |
| Descargar plan de trabajo | Documento de ~5.6 KB con 7 tablas |
| "Subir imagen" / "Adjuntar ahora" | Abren el selector de archivos nativo (el test automático no puede observarlo) |

### 12.7 Cómo regenerar

El HTML no se edita a mano; se genera. Para emitir **solo** las pantallas del rol
Estudiante (sin reescribir Docente, Administrador ni las de acceso):

```powershell
# desde prototype/
python generar.py          # emite las 73 pantallas + index.html (todos los roles)
```

Si solo se tocó el rol Estudiante, `generar.py` completo reescribe también los otros
roles porque comparten `lib_ui`/`lib_css`/`lib_js`. Para un alcance estricto conviene
regenerar únicamente la carpeta `estudiante/` y revisar el `git status` antes de
commitear.

---

## 13. Cambios del rol Administrador (`prototype/Admin-Refactor`)

Rama **`prototype/Admin-Refactor`**: refactor del rol Administrador. Sale de
**`prototype/student`** (commit `8e71c8c`, el punto de clone) y añade **dos commits**:
el refactor y la documentación. 36 archivos en total.

Alcance: las **19 pantallas** de `prototype/admin/` y, porque el kit es compartido,
los cambios mínimos de `lib_ui.py` y el nuevo CLI de `generar.py`. Se
regeneraron además **8 pantallas** de Docente y Estudiante (los identificadores de
estudiante ahora son los mismos de 6 dígitos que usa la gestión de perfiles del
administrador). **Ningún otro archivo del repo cambia.**

### 13.1 Los datos salen del generador

Antes, varias pantallas pintaban literales sueltos en el HTML. Ahora estudiantes,
docentes, emprendimientos, solicitudes, tareas, asesorías y eventos se modelan
como tuplas en `paginas_admin.py` y las tablas se construyen con `_tabla_adm()`:
zona filtrable, buscador, filtros por columna, paginación, contador de
resultados y estados vacíos. Una celda puede ser `("html", "valor")` cuando
lleva markup (por ejemplo el `<select>` de estado de cada fila).

### 13.2 Buscadores, filtros y paginación que responden

Los filtros comparan contra el **valor vivo** del `<select>` de la celda (no
contra su texto), con un pequeño retardo de 220 ms para no filtrar en cada
pulsación. El filtro de *Estado* de la gestión de perfiles es el caso que
exponía el bug: antes ocultaba o mostraba todas las filas.

### 13.3 Fichas y enlaces profundos

Cada fila abre su **ficha** en modal (mismo origen de datos: los `data-*` de la
fila) y hay **enlaces profundos** por `hash`:

| Hash | Qué abre |
|---|---|
| `#est-912646` | La ficha del estudiante (salta de página y resalta la fila) |
| `#emp-EMP-041` | La ficha del emprendimiento |
| `#doc-DOC-014` | La ficha del docente |
| `#sol-…` | La ficha de la solicitud |
| `#asignar-docente` | El modal de asignación sobre el primer emprendimiento sin docente |

### 13.4 Asignaciones: asignar y reasignar docente

La acción **Reasignar docente** clona una plantilla oculta (`#form-asignar-docente`),
la rellena con los datos de la fila y abre el modal con el docente preseleccionado;
al confirmar, la fila, la celda y el título del botón se actualizan. El ítem
**Asignar docente** del menú apunta a `asignaciones.html#asignar-docente`.

### 13.5 Seguimiento: registrar avance con prefill

El modal **Registrar avance** (lo abre el kit) llega con el emprendimiento, el
estudiante, la etapa y el avance de la fila. Como el kit clona las plantillas con
`innerHTML` —lo que pierde el `option` seleccionado y los valores escritos a
mano—, el `ADMIN_JS` del rol repone esos valores después (su listener se
registra después del del kit).

### 13.6 Solicitudes, Configuración y el resto de pantallas

**Solicitudes** quedó con pestañas por estado, tabla por bandeja, ficha de
detalle y el flujo de aprobación del kit. **Configuración** (`configuracion.html`)
es una pantalla **nueva** del rol: parámetros del programa, sedes, notificaciones
y bitácora. El resto de pantallas (Inicio, Emprendimientos, Expediente, Plan,
Tablero, Tareas, Asesorías, Eventos, Diagnósticos, Reportes, Perfil,
Notificaciones, Respaldos) se regeneraron con el mismo criterio.

### 13.7 Verificación

- `python verify.py` → **10/10 OK**. Dos de esas comprobaciones (**Asignar
  docente** y **`#form-asignar-docente`**) **ya fallaban en `HEAD`**: son deuda
  preexistente, y este refactor las resuelve.
- Comprobación estructural propia de las 19 pantallas: **sin etiquetas sin
  cerrar, sin `id` duplicados** y con el bundle JS del rol validado con
  `node --check`.
- Navegador real (Chrome DevTools) sobre las 19 pantallas: **0 errores y 0
  warnings de consola**. Probados: las dos tablas de la gestión de perfiles
  (búsqueda, filtros, paginación, ficha), el flujo completo de reasignar docente
  (modal con prefill → confirmar → la fila cambia + aviso), las pestañas de
  solicitudes, el modal de registrar avance con su prefill y los enlaces
  profundos de tipo `#emp-` y `#doc-`.
- `git status` antes de commitear: **solo** los 36 archivos del alcance. El resto
  del repo queda byte-idéntico.

### 13.8 Fuera de alcance (deuda preexistente)

Se documentó pero **no** se unificó, porque tocaría a otros roles o excede el
refactor: los dominios de correo (`@sgemd.edu.co` en el administrador frente a
`@minutodedios.edu.co` en el estudiante), los nombres sin tilde heredados de la
línea base en algunas bandejas y la función `asignar()` de `paginas_admin.py`,
que no está registrada en el mapa de pantallas. Detalle en
[`cambios-a-admin.md`](cambios-a-admin.md) §6.

---

## Ver también

- [`DESIGN.md`](DESIGN.md) — guía de diseño completa (paleta, tipografía, componentes)
- [`cambios-a-admin.md`](cambios-a-admin.md) — registro del refactor del rol Administrador
- [`cambios-a-docente.md`](cambios-a-docente.md) — registro del refactor del rol Docente
- [`../README.md`](../README.md) — especificación maestra del SGEMD
- [`../docs/fr_nfr_sgemd.md`](../docs/fr_nfr_sgemd.md) — requisitos funcionales y no funcionales
