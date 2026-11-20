# SGEMD — Guía de diseño del sistema

Plataforma educativa para gestionar clases de emprendimiento. Tres roles con
layouts separados: **ESTUDIANTE**, **DOCENTE** y **ADMINISTRADOR**, más las
pantallas globales de acceso (Login, Registro, Verificar OTP, Recuperar
contraseña).

---

## 1. PALETA — REGLA ABSOLUTA

Estos son los **únicos seis colores** permitidos en todo el producto. No
introducir ningún otro hex, ni tintes, ni degradados fuera de esta lista.

| Token | Hex | Uso |
| --- | --- | --- |
| Amarillo institucional | `#ffd300` | Acento, relleno de botón, badge, barra activa, marcador de posición activo. **Siempre con texto `#051533` encima.** |
| Blanco | `#ffffff` | Fondos de página, tarjetas, tablas, campos de formulario. |
| Azul profundo | `#162644` | Cabeceras de tabla, texto secundario sobre blanco, superficies intermedias. |
| Azul noche | `#051533` | Header, sidebar, footer, botones primarios, texto principal. |
| Azul real | `#004a93` | Botón primario, enlaces, estados activos, íconos de marca. |
| Gris | `#bbbbbb` | Bordes, separadores, placeholders, campos deshabilitados, texto deshabilitado. |

### Reglas de contraste (verificadas, WCAG AA)

- `#ffd300` es **acento de relleno, nunca color de texto sobre blanco**
  (contraste 1.32:1, ilegible). Sobre `#051533` o `#004a93` sí funciona como texto.
- `#bbbbbb` sobre blanco da 1.92:1 — **no usarlo para texto**. Para texto
  secundario o deshabilitado sobre blanco usar `#162644`.
- Texto principal: `#051533`. Texto secundario: `#162644`.
- Blanco sobre `#051533` (14.7:1) y blanco sobre `#004a93` (8.4:1) pasan AA.
- Variantes suaves permitidas, derivadas de los mismos tokens con opacidad:
  `rgba(4,74,147,.06)`, `rgba(4,74,147,.12)`, `rgba(4,74,147,.28)`,
  `rgba(5,21,51,.03)`, `rgba(5,21,51,.04)`, `rgba(5,21,51,.55)`,
  `rgba(255,211,0,.14)`. **Nunca un hex nuevo.**

---

## 2. LOS TRES ROLES

Cada rol tiene su **propio layout, su propio menú lateral y su propio conjunto
de pantallas**. Nunca mezclar funciones entre roles.

**Header común a los tres roles:** logo de marca (intacto) a la izquierda ·
buscador global · ícono de notificaciones con contador · avatar + nombre +
**etiqueta del rol** (`ESTUDIANTE` / `DOCENTE` / `ADMINISTRADOR`).

**Sidebar — ESTUDIANTE**
Inicio · Estado de seguimiento · Mi emprendimiento · Diagnóstico · Plan de
trabajo · Seguimiento · Tareas · Asesorías · Eventos · Perfil

**Sidebar — DOCENTE**
Inicio · Mis asesorías · Emprendimientos asignados · Seguimiento · Diagnóstico ·
Tareas · Perfil

**Sidebar — ADMINISTRADOR**
Inicio · Gestión de perfiles · Emprendimientos · Seguimiento · Asignaciones ·
Diagnósticos · Eventos · Asesorías · Reportes · Perfil

Estados: ítem activo con fondo `#004a93` y texto blanco. Ítem en hover con
`rgba(255,255,255,.08)`. Resto del menú en blanco al 78 % de opacidad.

---

## 3. COMPONENTES

### 3.1 Botones

| Variante | Fondo | Texto | Borde |
| --- | --- | --- | --- |
| Primario | `#004a93` | `#ffffff` | — |
| Primario hover | `#162644` | `#ffffff` | — |
| Secundario | `#ffffff` | `#051533` | 1px `#bbbbbb` |
| Acento | `#ffd300` | `#051533` | — |
| Eliminar | `#051533` | `#ffffff` | — |

- Alto 40px, padding `0 18px`, radio 8px, peso 600.
- Siempre con ícono a la izquierda del texto.
- **Eliminar exige modal de confirmación obligatorio.** Nunca rojo: se resuelve
  con `#051533` e ícono de advertencia.

### 3.2 Formularios

- Label sobre el campo: 13px, peso 500, `#051533`.
- Campo: fondo `#ffffff`, borde 1px `#bbbbbb`, radio 8px, alto 40px.
- Focus: borde `#004a93` + halo `rgba(4,74,147,.12)`.
- Placeholder: `#bbbbbb`.
- **Campo deshabilitado por regla de rol:** fondo `rgba(5,21,51,.03)`, texto
  `#bbbbbb`, ícono de candado y texto auxiliar indicando qué rol lo administra
  (por ejemplo: "Solo ADMINISTRADOR puede modificar esta información").
- Errores: texto bajo el campo con ícono, sin fondo, borde `#162644`. Sin rojo.
- Selector de archivo: borde punteado `#bbbbbb`, fondo `rgba(5,21,51,.02)`,
  ícono de subir en `#004a93`.

### 3.3 Tablas — componente central del producto

- Cabecera: fondo `#162644`, texto `#ffffff`, 12px, peso 600, mayúsculas,
  tracking 0.04em, **sin esquinas redondeadas arriba**.
- Filas: separador 1px `#bbbbbb`. Alternancia opcional `rgba(5,21,51,.03)`.
- Hover de fila: `rgba(4,74,147,.05)`.
- Encabezado fijo al hacer scroll vertical; barra de herramientas (buscador +
  filtros + botón de acción) fija encima.
- **Columna de acciones siempre a la derecha**, alineada a la derecha, íconos de
  20px en `#004a93` separados 4px.
- Alineación: números a la derecha, texto a la izquierda, fechas consistentes.
- Paginación: `Anterior` / `Siguiente` + «Mostrando X–Y de Z», controles en
  `#ffffff` con borde `#bbbbbb`.
- **Estado vacío:** ícono grande `#bbbbbb`, título en `#051533`, texto auxiliar
  y botón de acción.

### 3.4 Badges y etiquetas de estado

- Un badge es **ícono + texto. Nunca solo color.** Formato: fondo `rgba(...)`
  derivado del color del estado, texto `#051533` o `#ffffff`, borde 1px, radio
  999px, 12px, peso 600.
- **Semáforo de etapas: prohibido usar rojo, verde o naranja.** Se resuelve con
  color de marca + ícono + etiqueta textual:

| Etapa | Fondo | Texto | Ícono |
| --- | --- | --- | --- |
| Idea / planificación | `#ffd300` | `#051533` | bombilla |
| En ejecución | `#004a93` | `#ffffff` | engranaje |
| Consolidado / escalable | `#ffffff` | `#004a93` | flecha ascendente |

### 3.5 Tarjetas

- Fondo `#ffffff`, borde 1px `#bbbbbb`, radio 12px, padding 20–24px.
- Sombra muy sutil `0 1px 2px rgba(5,21,51,.06)`. Sin sombras duras.
- Encabezado: título 16px peso 600 `#051533` + acción a la derecha.
- **Tarjeta de métrica:** número 32px peso 700 `#051533`, etiqueta 13px
  `#162644`, ícono `#004a93` sobre cuadro `rgba(4,74,147,.08)`, y barra de
  progreso con fondo `rgba(4,74,147,.15)` y valor `#004a93`.

### 3.6 Gráficos

- Solo con la paleta. Barras y líneas en `#004a93` y `#162644`. Área bajo la
  línea en `rgba(4,74,147,.12)`. Rejilla y ejes en `#bbbbbb`. Texto de ejes en
  `#162644`.
- **Ejes y etiquetas siempre visibles con su valor numérico**: el prototipo no
  depende de tooltips.
- Sin librería externa: SVG inline o generado por script.
- Leyenda con punto de color + etiqueta de texto.

### 3.7 Modales y notificaciones

- Overlay `rgba(5,21,51,.55)`, panel `#ffffff`, radio 12px, sombra
  `0 24px 64px rgba(5,21,51,.28)`.
- Panel de notificaciones: drawer derecho de 360px, fondo `#ffffff`, ítems con
  separador `#bbbbbb`, no leídas con punto `#ffd300` y borde izquierdo 3px
  `#004a93`.

---

## 4. LOGO

El logo institucional es un archivo real y **no se redibuja, no se recolorea, no
se sustituye por un círculo con iniciales ni por texto**. Se inserta la imagen
original respetando su proporción cuadrada 1:1, con margen libre alrededor.

Se muestra sobre un cuadro `#ffffff` con padding de 12px, porque el archivo tiene
fondo transparente y sobre azul oscuro sería invisible.

Aparece en: login, sidebar de los tres roles y header.

---

## 5. RESPONSIVE

- **Ancho de referencia obligatorio: 1440 px.**
- ≥ 1280: sidebar fijo de 264px, contenido en grid de 12 columnas.
- 1024–1279: sidebar colapsado a íconos, 72px.
- < 1024: sidebar en drawer oculto, con botón de menú en el header.
- < 768: grids de 2 columnas pasan a 1. Las tablas hacen scroll horizontal con
  la primera columna fija y las acciones siempre accesibles.

---

## 6. ACCESIBILIDAD

- Contraste AA en todo el texto. Nunca texto `#ffd300` sobre blanco ni
  `#bbbbbb` sobre blanco.
- Cada control con label explícito; íconos con `aria-label`.
- Foco visible: anillo `0 0 0 3px rgba(4,74,147,.28)`.
- Orden de tabulación lógico, tablas con `<th scope>`, formularios con
  `<label for>`.

---

## 7. PROHIBICIONES ABSOLUTAS

1. Cualquier color fuera de los seis hex listados.
2. Rojo, verde o naranja para semáforos, alertas o estados. Resolver con ícono,
   texto y color de marca.
3. Texto `#ffd300` sobre blanco, o texto `#bbbbbb` sobre blanco.
4. Redibujar, recortar, recolorear o sustituir el logo.
5. Glassmorphism, degradados decorativos, sombras duras, esquinas muy
   redondeadas en tablas.
6. Inventar módulos, roles, campos o métricas que no existan en la
   especificación.
7. Interacciones de un rol disponibles para otro rol.