# SGEMD

Plataforma educativa de gestion declasses de emprendimiento. Tres roles con
layouts separados: ESTUDIANTE, DOCENTE, ADMINISTRADOR, mas pantallas globales de
acceso.

## PALETA — REGLA ABSOLUTA

Unicos seis colores permitidos en todo el producto. Ningun otro hex, ningun
tinte, ningun degradado fuera de esta lista.

- `#ffd300` amarillo institucional: acento, relleno de boton, badge, barra
  activa. Siempre con texto `#051533` encima.
- `#ffffff` blanco: fondos de pagina, tarjetas, tablas, campos.
- `#162644` azul profundo: cabeceras de tabla, texto secundario sobre blanco.
- `#051533` azul noche: header, sidebar, footer, botones primarios, texto
  principal.
- `#004a93` azul real: boton primario, enlaces, estados activos.
- `#bbbbbb` gris: bordes, separadores, placeholders, deshabilitados.

## CONTRASTE

- `#ffd300` nunca es color de texto sobre blanco: 1.32:1, ilegible. Sobre
  `#051533` o `#004a93` si funciona.
- `#bbbbbb` sobre blanco da 1.92:1: nunca texto. Texto secundario o
  deshabilitado sobre blanco usa `#162644`.
- Variantes suaves solo por opacidad: `rgba(4,74,147,.06)`,
  `rgba(4,74,147,.12)`, `rgba(5,21,51,.04)`, `rgba(255,211,0,.14)`.

## COMPONENTES

- Botones: primario `#004a93` texto blanco; secundario blanco con borde
  `#bbbbbb`; acento `#ffd300` con texto `#051533`; eliminar `#051533` con
  confirmacion en modal. Alto 40px, radio 8px, icono a la izquierda.
- Tablas: cabecera `#162644` texto blanco 12px mayusculas, separadores
  `#bbbbbb`, columna de acciones siempre a la derecha, encabezado fijo,
  buscador y filtros encima, paginacion, estado vacio con icono y accion.
- Badges: siempre icono mas texto, nunca solo color. Semáforo de etapas sin
  rojo ni verde: idea `#ffd300` con icono de bombilla, en ejecucion `#004a93`
  con icono de engranaje, consolidado blanco con borde `#004a93` y flecha
  ascendente.
- Tarjetas: blanco, borde `#bbbbbb`, radio 12px, sombra sutil. Metricas con
  numero 32px y barra de progreso `#004a93`.
- Graficos: solo la paleta, en SVG inline, con ejes y valores visibles siempre.
  Sin librerias externas.
- Formularios: label encima, borde `#bbbbbb`, focus `#004a93`, placeholder
  `#bbbbbb`. Campos bloqueados por rol con candado y texto explicando que rol
  los administra.

## ROLES

Cada rol tiene su propio menu lateral y sus propias pantallas. Nunca mezclar.

- Header comun: logo intacto, buscador, notificaciones, avatar, nombre y
  etiqueta del rol.
- Estudiante: Inicio, Estado de seguimiento, Mi emprendimiento, Diagnostico,
  Plan de trabajo, Seguimiento, Tareas, Asesorias, Eventos, Perfil.
- Docente: Inicio, Mis asesorias, Emprendimientos asignados, Seguimiento,
  Diagnostico, Tareas, Perfil.
- Administrador: Inicio, Gestion de perfiles, Emprendimientos, Seguimiento,
  Asignaciones, Diagnosticos, Eventos, Asesorias, Reportes, Perfil.
- Item activo: fondo `#004a93` texto blanco.

## LOGO

El logo institucional es un archivo real. No se redibuja, no se recolorea, no se
sustituye por iniciales ni por texto. Se usa la imagen original en 1:1, con
margen libre, sobre un cuadro blanco con padding de 12px porque el archivo tiene
fondo transparente. Aparece en login, sidebar y header.

## RESPONSIVE

Referencia 1440px. Sidebar fijo 264px en desktop. Bajo 1024 el sidebar pasa a
drawer. Bajo 768 las tablas hacen scroll horizontal con la primera columna fija.

## PROHIBICIONES

1. Cualquier color fuera de los seis hex.
2. Rojo, verde o naranja para semaforos o alertas: usar icono, texto y color de
   marca.
3. Texto `#ffd300` sobre blanco o `#bbbbbb` sobre blanco.
4. Redibujar, recortar o recolorear el logo.
5. Glassmorphism, degradados decorativos, sombras duras.
6. Inventar modulos, roles, campos o metricas que no existan.
7. Interacciones de un rol disponibles para otro.