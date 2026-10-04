# Prototipo SGEMD

Prototipo navegable del **SGEMD — Sistema de Gestión de Emprendimiento Minuto de Dios**.
50 pantallas + índice, tres roles (Estudiante, Docente, Administrador) y las cuatro
pantallas globales de acceso.

- **Stitch:** https://stitch.withgoogle.com/projects/8880818071963426152
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
    - [3.2 Estudiante (16)](#32-estudiante-16)
    - [3.3 Docente (12)](#33-docente-12)
    - [3.4 Administrador (18)](#34-administrador-18)
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
  - [Ver también](#ver-también)

---

## 1. Cómo verlo

### Opción A — el índice local (recomendada para revisar)

```
prototype/index.html
```

Doble clic. El índice agrupa las 50 pantallas por carpeta y enlaza a cada una, así
que sirve como mapa de navegación del prototipo completo. Ábrelo **desde el
sistema de archivos**: los enlaces son relativos y con `file://` funcionan tal cual.

### Opción B — Stitch

<https://stitch.withgoogle.com/projects/8880818071963426152>

Cada pantalla es un documento independiente dentro del proyecto.

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

| Carpeta | Pantallas | Contenido |
|---|---|---|
| `compartido/` | 4 | Login, registro, verificación OTP, recuperación de contraseña |
| `estudiante/` | 16 | Inicio, emprendimiento, diagnóstico, plan, seguimiento, tareas, asesorías, eventos, perfil, notificaciones |
| `docente/` | 12 | Inicio, asesorías, expedientes, seguimiento, diagnósticos, tareas, perfil, notificaciones |
| `admin/` | 18 | Inicio, gestión de perfiles, emprendimientos, seguimiento, asignaciones, moderación, métricas, eventos, reportes, perfil, notificaciones |
| **Total** | **50** | más `index.html` como índice local |

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

### 3.2 Estudiante (16)

| # | Vista | Qué resuelve |
|---|---|---|
| 05 | Inicio | Resumen de estado, pendientes y próximas asesorías |
| 06 | Estado de seguimiento | Fase actual del emprendimiento y requisitos por cumplir |
| 07 | Mi emprendimiento | Listado de sus emprendimientos |
| 08 | Detalle del emprendimiento | Ficha completa: tipo, sector, etapa, acta, avance |
| 09 | Editar emprendimiento | Solo nombre, descripción y redes; el resto es de solo lectura |
| 10 | Diagnóstico | Cuestionario por etapas |
| 11 | Resultados del diagnóstico | Puntajes por dimensión y recomendaciones |
| 12 | Plan de trabajo | Hitos y responsables |
| 13 | Seguimiento | Historial de avances (**solo lectura**) |
| 14 | Mis tareas | Listado con estado y fecha límite |
| 15 | Detalle de tarea | Instrucciones, evidencia exigida y entregas |
| 16 | Mis asesorías | Historial y próximas sesiones |
| 17 | Solicitar asesoría | Elige **fecha propuesta**; el docente confirma fecha y hora |
| 18 | Eventos | Convocatorias y eventos del programa |
| 19 | Mi perfil | Datos personales y preferencias |
| 20 | Notificaciones | Avisos del sistema |

### 3.3 Docente (12)

| # | Vista | Qué resuelve |
|---|---|---|
| 21 | Inicio | Emprendimientos asignados y tareas pendientes |
| 22 | Mis asesorías | Agenda y estado de las sesiones |
| 23 | Registrar asesoría | **Confirma fecha y hora**; deja observaciones |
| 24 | Emprendimientos asignados | Solo los que tiene asignados |
| 25 | Expediente del emprendimiento | Historial completo: avances, tareas, asesorías, diagnóstico |
| 26 | Seguimiento (lista) | Filtra por entrepreneurship y estado |
| 27 | Tablero de seguimiento | Avance y recomendaciones por dimensiones |
| 28 | Registrar avance y calificar | Calificación con evidencia y comentarios |
| 29 | Revisión del diagnóstico | Lectura del resultado y recomendaciones al estudiante |
| 30 | Tareas asignadas | Crea, asigna y califica tareas |
| 31 | Mi perfil | Datos y carga académica |
| 32 | Notificaciones | Avisos del sistema |

### 3.4 Administrador (18)

| # | Vista | Qué resuelve |
|---|---|---|
| 33 | Inicio | Métricas generales del programa |
| 34 | Gestión de perfiles | Alta, edición y baja de docentes y estudiantes |
| 35 | Editar docente | Formulario de docente |
| 36 | Editar estudiante | Formulario de estudiante + documento |
| 37 | Emprendimientos | Los 46 emprendimientos del programa |
| 38 | Plan de trabajo del emprendimiento | Vista completa del plan |
| 39 | Seguimiento (lista) | Filtros por rol, estado y fecha |
| 40 | Tablero de seguimiento | Consolidado de avances del programa |
| 41 | Asignar emprendimiento | Asigna docente mentor a un emprendimiento |
| 42 | Moderación de comentarios | Aprueba, oculta y elimina comentarios |
| 43 | Métricas de asesorías | Gráficos de uso y cumplimiento |
| 44 | Eventos | Listado y estado de aprobación |
| 45 | Crear evento | Formulario de evento con validación |
| 46 | Asignaciones | Historial de asignaciones docente ↔ emprendimiento |
| 47 | Diagnósticos respondidos | Todos los diagnósticos del programa |
| 48 | Exportar reportes | Reportes en CSV/Excel |
| 49 | Mi perfil | Datos del administrador |
| 50 | Notificaciones | Avisos del sistema |

---

## 4. Reglas de negocio representadas

Estas restricciones no son cosméticas: están reflejadas en las pantallas y son la
razón de que las vistas no sean idénticas entre roles.

- **BR-002 — el estudiante no agenda al docente.** Al solicitar asesoría elige una
  *fecha propuesta*; la hora la confirma el docente. El estudiante nunca elige
  docente ni horario confirmado.
- **BR-003 — el estudiante edita poco.** Solo nombre, descripción y redes. Tipo,
  sector, etapa y acta son de solo lectura.
- **Seguimiento del estudiante es de solo lectura.** El docente registra y califica;
  el estudiante consulta.
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

Fuente única: [`../docs/Logo_sinfondo.png`](../docs/Logo_sinfondo.png) (PNG RGBA, sin
fondo). `_marca/preparar_logo.py` deriva de ahí las variantes que usa el prototipo:

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
├── generar.py              Orquestador: emite las 50 pantallas + index.html
├── paginas_auth.py         4 pantallas de acceso + su CSS y su JS
├── paginas_estudiante.py   16 pantallas del estudiante
├── paginas_docente.py      12 pantallas del docente
├── paginas_admin.py        18 pantallas del administrador
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
# Generar (emite las 50 pantallas + index.html)
python generar.py

# Derivar las variantes de logo desde docs/Logo_sinfondo.png
python _marca\preparar_logo.py

# Publicar en Stitch
python subir.py --force

# Volver a leer Stitch y rehacer el informe de duplicados
python _reconciliar.py
```

`subir.py` y `_reconciliar.py` usan la variable de entorno `STITCH_API_KEY`.

---

## 9. Validación automática

El prototipo no se dio por bueno "a ojo": hay ocho auditorías y todas dan **0
problemas** sobre las 50 pantallas.

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
pantalla en Stitch, sin servidor de por medio.

---

## 10. Publicación en Stitch

- **Proyecto:** `projects/8880818071963426152`
- **Enlace:** https://stitch.withgoogle.com/projects/8880818071963426152
- **Total:** 51 pantallas en el proyecto — las 50 de interfaz más una de marca
  (`_marca/logo-color-1200.png`).

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
- **La tipografía depende de internet.** Si Google Fonts no responde, las 50
  pantallas se ven con la fuente del sistema. El diseño aguanta el cambio, pero las
  medidas no son idénticas a las capturadas.

---

## Ver también

- [`DESIGN.md`](DESIGN.md) — guía de diseño completa (paleta, tipografía, componentes)
- [`../README.md`](../README.md) — especificación maestra del SGEMD
- [`../docs/fr_nfr_sgemd.md`](../docs/fr_nfr_sgemd.md) — requisitos funcionales y no funcionales
- [`../docs/estructura_de_vistas_sgemd.md`](../docs/estructura_de_vistas_sgemd.md) — inventario de vistas
