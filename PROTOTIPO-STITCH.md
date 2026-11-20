# Rama `prototype/stitch`

Esta rama contiene la creación del **prototipo de SGEMD en Stitch**:

<https://stitch.withgoogle.com/projects/3060781598377201049>

> **Comentario sobre este enlace:** el proyecto anterior
> (`projects/8880818071963426152`) se borró a causa de un error, por lo que su URL
> quedó obsoleta. Se creó este proyecto nuevo en Stitch y se volvieron a subir las
> 51 pantallas, así que el enlace cambió.

Si llegaste aquí por el `README.md` de la raíz, ten en cuenta que ese
describe el proyecto completo. Lo que hay en esta rama es su versión
navegable.

## Qué hay aquí

- **50 pantallas HTML** del prototipo, navegables con doble clic.
- **`index.html`**: galería índice con enlace a las 50 pantallas.
  Es local y **no** forma parte de las 51 pantallas subidas a Stitch.
- El **README del prototipo**, con inventario de vistas, roles,
  reglas de negocio, colores, responsive y limitaciones.
- El **pipeline en Python** que genera, audita y publica todo.

## Roles cubiertos — 50 pantallas

| Rol | Pantallas |
|---|---|
| Acceso | 4 |
| Estudiante | 16 |
| Docente | 12 |
| Administrador | 18 |

## Cómo usarlo

| Acción | Comando |
|---|---|
| Regenerar las pantallas | `python generar.py` |
| Ver las 50 en el navegador | abrir `prototype/index.html` |
| Subir a Stitch | `$env:STITCH_API_KEY="..."` y luego `python subir.py --force` |

## Auditoría

Ocho validadores, todos en 0 problemas: estructura, auditoría general,
firmas, tipografía, porcentajes, responsive, interacción y accesibilidad.

## Advertencia

No hay backend. El login, el OTP, la recuperación y el guardado de
datos son **simulaciones de interfaz**.