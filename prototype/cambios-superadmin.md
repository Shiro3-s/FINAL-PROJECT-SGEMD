# Cambios — Módulo Super Admin (SGEMD)

> Documento de trabajo. Registra **todo** lo que se hizo para incorporar y evolucionar
> el rol **Super Admin** en el prototipo.
> Estado: **ejecutado**.
> Ámbito: `prototype/superadmin/**` (7 pantallas), `prototype/paginas_superadmin.py`,
> `prototype/index.html` y los cambios mínimos de `lib_ui.py`, `lib_js.py`,
> `paginas_auth.py`, `compartido/login.html` y `generar.py`.
> Regeneración: `python generar.py --rol superadmin` (desde `prototype/`).

---

## 1. Objetivo

Incorporar un rol **Super Admin** dedicado exclusivamente a la **gestión de perfiles
de usuario**: crear, consultar, editar, activar/desactivar y ajustar permisos de las
cuentas de **Estudiante, Docente y Administrador**.

El Super Admin **no** gestiona emprendimientos, asesorías, eventos, tareas,
diagnósticos ni información académica, y **no puede crear otros Super Admin ni
cambiar el rol de un perfil**. Esas restricciones están aplicadas en la interfaz y
en la lógica del módulo, no solo ocultando botones.

A partir de esta iteración:
- Cada persona tiene **dos identificadores distintos**: la **identificación personal**
  (documento) y el **ID institucional** (código que asigna la universidad).
- El correo institucional es siempre **`@uniminuto.edu.co`**.
- La creación incluye una **contraseña provisional** con generador; la persona debe
  cambiarla en el primer inicio de sesión.
- **No se elimina nada**: retirar el acceso es desactivar la cuenta.
- **Cambiar rol** se elimina por completo; el rol no es editable.
- **Desactivar** sale de la fila y pasa a un interruptor **Activo** dentro de Editar.
- **Eliminar** se retira por completo.
- `Editar perfil` y `Gestión de permisos` dejan de ser modales y pasan a vistas
  dedicadas (`editar-perfil.html`, `permisos.html`).
- `Ver detalle` sigue siendo modal.
- El Super Admin puede editar **su propio perfil** desde `Mi perfil`, accesible
  también desde el menú superior derecho (no solo "Cerrar sesión").
- Los perfiles **limitados** son los que no gozan de todos los permisos del rol.

---

## 2. Alcance y restricciones

- Solo perfiles de Estudiante, Docente y Administrador.
- Sin vistas de emprendimientos, asesorías, eventos, tareas, diagnósticos ni académicas.
- Sin creación de otros Super Admin ni cambio de rol.
- Sin eliminación permanente de perfiles.

---

## 3. Fuentes de datos reutilizadas

- `paginas_admin.DOCENTES` (5 docentes), `ESTUDIANTES` (12 estudiantes),
  `CORREOS_EST`, `SEDE_EST`.
- Cuenta institucional del administrador (Ana Restrepo).
- Cuenta propia del Super Admin (Laura Gómez), almacenada aparte.

No se inventan usuarios. La identificación personal solo se conoce para Mariana
López (`1020304050`) y Carlos Mendoza (`79 456 123`); el resto queda en blanco
(`—`) hasta que se complete en edición. Los ID institucionales son los códigos ya
existentes (`912646`, `DOC-014`, etc.).

---

## 4. Modelo de datos

Cada perfil tiene: `clave`, `identificacion` (personal), `id_institucional`
(universidad), `nombre`, `correo` (`@uniminuto.edu.co`), `rol`, `estado`,
`fecha`, `origen`, `detalle`, `permisos`, `password` (provisional), `debe_cambiar`.

Estados derivados:
- `Inactivo` si la cuenta está desactivada.
- `Limitado` si está activa pero le faltan permisos del rol.
- `Activo` si está activa y conserva todos los permisos del rol.

`perfiles-activos.html` muestra únicamente los derivados `Activo`.

---

## 5. Vistas (7)

| # | Archivo | Qué resuelve |
|---|---|---|
| 01 | `dashboard.html` | Métricas enlazadas (registrados, activos, inactivos, limitados) con hover preview y navegación; distribución por rol; accesos |
| 02 | `crear-perfil.html` | Asistente de 3 fases: datos (identificación personal, ID institucional, correo @uniminuto.edu.co, contraseña provisional con generador), rol, permisos |
| 03 | `perfiles.html` | Tabla con búsqueda, filtros por rol/estado, orden, paginación; acciones: ver, editar, permisos |
| 04 | `perfiles-activos.html` | Igual que perfiles pero solo activos |
| 05 | `editar-perfil.html` | Datos, estado (interruptor Activo), cambio de contraseña con generador, enlace a permisos |
| 06 | `permisos.html` | Ficha del perfil, permisos por módulo, restablecer y guardar; estado derivado |
| 07 | `mi-perfil.html` | Datos del propio Super Admin y seguridad; sincroniza encabezado |

---

## 6. Permisos

Se derivan del menú lateral real de cada rol (NAV). Cada módulo y vista existente
se convierte en un permiso. El permiso de Inicio es base y no se puede retirar.
Si faltan permisos del rol, el perfil queda como Limitado.

---

## 7. Persistencia

- Clave `sgemd:superadmin:v1` con `creados` y `cambios`. Las bajas lógicas
  (`bajas`) se ignoran y se eliminan al leer.
- Clave `sgemd:superadmin:cuenta` para la cuenta propia del Super Admin.
- Las vistas comparten el mismo almacén; `storage` event repinta.
- Las contraseñas son simuladas y no reemplazan las credenciales fijas del login demo.

---

## 8. Validación

- `python -m py_compile paginas_superadmin.py lib_ui.py lib_js.py`
- `python generar.py --rol superadmin` (7 páginas)
- `python verify.py` (OK)
- `node --check` sobre el `<script>` final de cada página (OK)
- Pruebas de navegador: creación, validación de duplicados y dominio, generador,
  filtros, detalle, edición, interruptor de estado, permisos/limitado, mi perfil
  y sincronización del encabezado.

---

## 9. Limitaciones conocidas

- Sin backend: todo vive en `localStorage` del navegador.
- Las contraseñas se guardan en texto plano en el prototipo.
- La cuenta de demostración del login (`superadmin` / `superadmin`) no se reemplaza
  por la contraseña guardada en `Mi perfil`.
