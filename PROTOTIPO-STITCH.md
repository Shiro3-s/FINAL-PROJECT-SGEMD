# Rama `prototype/stitch`

Esta rama contiene la creación del **prototipo de SGEMD en Stitch**:

<https://stitch.withgoogle.com/projects/3060781598377201049>

> **Comentario sobre este enlace:** el proyecto anterior
> (`projects/8880818071963426152`) se borró a causa de un error, por lo que su URL
> quedó obsoleta. Se creó este proyecto nuevo en Stitch y se volvieron a subir las
> pantallas, así que el enlace cambió. El repositorio conserva **73 pantallas**
> en `prototype/`; la copia en Stitch puede ir por detrás.

Si llegaste aquí por el `README.md` de la raíz, ten en cuenta que ese
describe el proyecto completo. Lo que hay en esta rama es su versión
navegable.

## Qué hay aquí

- **73 pantallas HTML** del prototipo, navegables con doble clic.
- **`index.html`**: galería índice con enlace a las 73 pantallas.
  Es local y **no** forma parte de las pantallas subidas a Stitch.
- El **README del prototipo**, con inventario de vistas, roles,
  reglas de negocio, colores, responsive y limitaciones.
- El **pipeline en Python** que genera, audita y publica todo.

## Roles cubiertos — 73 pantallas

| Rol | Pantallas |
|---|---|
| Acceso (compartido) | 4 |
| Estudiante | 27 (18 vistas base + 9 variantes) |
| Docente | 23 |
| Administrador | 19 |

> **Fuente de verdad:** el prototipo de `prototype/` es la referencia vigente
> (2026-10-25). Stitch es una copia de presentación y puede no estar sincronizada.

## Cómo usarlo

| Acción | Comando |
|---|---|
| Regenerar las pantallas | `python generar.py` |
| Ver las 73 en el navegador | abrir `prototype/index.html` |
| Subir a Stitch | `$env:STITCH_API_KEY="..."` y luego `python subir.py --force` |

## Auditoría

Los validadores citados en `prototype/README.md` (estructura, auditoría general,
firmas, tipografía, porcentajes, responsive, interacción y accesibilidad) **no
están todos en el repositorio**: varios scripts `_auditar.py`, `_estructura.py`,
`_responsive.py`, `_interaccion.py`, `_accesos.py` y `_reconciliar.py` no existen.
No se puede reproducir la auditoría con lo versionado.

## Advertencia

No hay backend. El login, el OTP, la recuperación y el guardado de
datos son **simulaciones de interfaz**.