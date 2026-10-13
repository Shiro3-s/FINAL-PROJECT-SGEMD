# Prototipo del Sistema SGEMD (Sistema de Información de Emprendimiento)

El sistema SGEMD presenta una interfaz web dividida por roles, con características y vistas específicas orientadas a la gestión y seguimiento de emprendimientos. A continuación, se detalla la estructuración de sus vistas y módulos.

---

## 1. Elementos de Interfaz Generales

*   **Navegación Principal (Sidebar):** Menú lateral izquierdo que agrupa categorías como *Perfil, Gestionar perfiles, Emprendimientos, Docentes* y *Eventos*, adaptándose según el rol del usuario.
*   **Barra Superior (Navbar):** Incluye el logotipo del sistema "SGEMD", un icono de notificaciones (campana) y el identificador visual/avatar del perfil del usuario activo.
*   **Gestión de Datos (Tablas):** Uso frecuente de tablas de datos para listar elementos. Estas incorporan columnas de ID, Nombres y botones de acción rápida como "Ver", "Editar" o "Eliminar" integrados en cada fila.
*   **Ventanas Emergentes (Modales):** Utilizadas como validación de seguridad para confirmar acciones críticas (ej. "¿Está seguro que lo quiere eliminar?") y para mostrar notificaciones o mensajes de éxito (ej. "Profesor eliminado correctamente").

---

## 2. Autenticación y Registro (Global)

Cuatro pantallas en `compartido/`: `login.html`, `registro.html`, `verificar-otp.html` y `recuperar-contrasena.html`. Comparten el mismo esqueleto (panel de marca a la izquierda, formulario a la derecha) y el mismo motor de validación en JavaScript embebido, sin dependencias externas.

*   **Inicio de Sesión:** Campos "Usuario" y "Contraseña", casilla "Recordar mi usuario", botón principal "Ingresar al sistema" y enlaces a registro y recuperación. Incluye un panel desplegable con las tres cuentas de demostración; al pulsar una fila se completa el usuario y queda resaltado el botón "Usar".
*   **Registro:** Nombres, apellidos, tipo y número de documento, correo personal, correo institucional, teléfono fijo, celular, contraseña y casilla obligatoria de aceptación del tratamiento de datos. Deriva a la verificación por código.
*   **Verificación por código:** Ocho campos de un dígito con avance automático, retroceso y pegado completo. "Reenviar código" confirma que el correo volvió a salir. Explica que el perfil queda en estado *Limitado* hasta la activación administrativa.
*   **Recuperación de Contraseña:** Correo registrado y número de documento; la respuesta es deliberadamente genérica para no revelar qué cuentas existen.

### 2.1. Alcance de la simulación

No hay backend: la autenticación es **simulada**. Los avisos de "revisa tu correo", "el enlace llega en minutos" y "código reenviado" no describen un envío real, y el texto lo declara en pantalla para que el prototipo no se lea como un sistema en producción. El estado de sesión vive en `localStorage`.

Cuentas de demostración (`usuario` / `contraseña`):

| Rol | Usuario | Contraseña | Destino |
| --- | --- | --- | --- |
| Estudiante | `estudiante` | `estudiante` | `estudiante/dashboard.html` |
| Docente | `profesor` | `profesor` | `docente/dashboard.html` |
| Administración | `admi` | `admi` | `admin/dashboard.html` |

Una sesión real exige backend, `bcrypt` para el hash y JWT para el token; ninguno de los tres existe en el prototipo.

---

## 3. Vistas por Rol

### 3.1. Perfil Administrativo
Cuenta con un menú lateral extenso que le otorga control total sobre los múltiples módulos del sistema.

*   **Módulo "Gestionar Perfiles"**
    *   **Listado de Docentes y Estudiantes:** Tabla con ID, Nombre y Correo de los usuarios. Incluye barra de búsqueda, opciones por fila (Editar/Eliminar) y un botón para "Crear".
    *   **Formularios (Crear/Editar):** Formularios simplificados para docentes (Nombre, Correo, ID) y estudiantes (añadiendo Tipo y Número de documento). Cuentan con botones de acción principal y de retroceso.
*   **Módulo "Emprendimientos"**
    *   **Lista General:** Tabla de proyectos con ID, Nombre, Tipo, Fecha de Creación y opciones (Ver/Editar/Eliminar).
    *   **Vista Detallada (Plan de Trabajo):** Matriz estructurada por fases (diferenciadas por colores) que detalla Actividad, Objetivo, Profesor encargado, Fechas (inicio/fin), Recursos y Resultados.
    *   **Lista de Seguimiento:** Tabla densa de actividades con fechas, frecuencia y progreso acumulado ("Accumulated progress") codificado por colores (rojo, amarillo, azul, verde).
    *   **Dashboard Visual de Seguimiento:** Pantalla analítica con porcentaje total completado. Muestra tareas completadas/no completadas en gráficos circulares y de barras categorizados por prioridad. Incluye tabla de próximas tareas.
*   **Módulo "Docentes"**
    *   **Asignar a Emprendimiento:** Interfaz que cruza emprendimientos (arriba) y docentes (abajo) con buscador y un botón central de "ASIGNAR".
    *   **Seguimiento (Comentarios):** Editor de texto con formato básico para registrar observaciones formales del acompañamiento de un docente a un emprendimiento.
    *   **Asesorías (Métricas):** Panel con velocímetros e indicadores de variables académicas (estudiantes, participación, evaluaciones).
*   **Módulo "Eventos"**
    *   **Creación/Edición:** Formulario con calendarios/relojes para fechas, selectores de "Tipo" y "Temática", datos del organizador y un editor de texto enriquecido para los detalles del evento.
    *   **Listado y Calendario:** Tarjetas rectangulares de eventos activos y un calendario interactivo de vista mensual fijo a la derecha.

### 3.2. Perfil Emprendedor (Estudiante)
Enfocado en el desarrollo del proyecto, seguimiento de tareas y solicitud de asesorías.

*   **Pantalla Principal (Dashboard de Inicio)**
    *   Panel de control con un resumen general: incluye un gráfico de barras comparativo (ej. Dollars vs Profit), un calendario mensual y perfiles informativos circulares.
*   **Módulo "Emprendimientos"**
    *   **Listado y Detalles:** Tabla de proyectos propios. Al abrir uno, detalla información profunda como el "Sector Productivo".
    *   **Diagnóstico Emprendedor:** Cuestionario paginado para recolectar datos estructurales (tipo de usuario, centro universitario, modalidad, programa, actividad productiva).
    *   **Resultados del Diagnóstico:** Panel visual con diagramas de barras, gráfico circular de objetivos y un sistema NPS (Detractors, Passives, Promoters) usando emoticonos y gradientes (rojo a verde).
    *   **Plan de Trabajo:** Matriz por bloques (FASE 1, FASE 2) para el seguimiento de actividades, objetivos, profesores asignados, fechas y recursos.
    *   **Estado de Seguimiento (Dashboard):** Tarjetas de casos abiertos/cerrados, gráficos circulares ("Cases Per Person") y de barras ("Cases Per Filing Date"). Incluye lista de "Mis Tareas" marcadas por prioridad (rojo, amarillo, verde).
*   **Módulo "Docentes y Asesorías"**
    *   **Listado de Asesorías:** Tabla que relaciona a los docentes con el emprendimiento. Permite Asignar, Editar y Eliminar (con modal de seguridad).
    *   **Programar/Editar Asesorías:** Formularios para agendar reuniones, eligiendo fecha/hora, temática, selección de profesor y datos de contacto.
*   **Módulo "Eventos"**
    *   **Consultar Eventos:** Vista de catálogo mediante tarjetas con barra de búsqueda superior y calendario lateral.

### 3.3. Perfil Docente (Asesor)
El menú lateral se adapta para centrarse en las herramientas de tutoría, retroalimentación y seguimiento académico y usa la **misma estructura de grupos/acordeón que el rol Estudiante** (Inicio + grupo *Mis emprendimientos* + grupo *Acompañamiento y actividades*; Notificaciones y Perfil viven en la barra superior). El rol se compone de **9 pantallas** en `docente/` (Inicio, Asesorías, Registrar asesoría, Emprendimientos asignados, Expediente, Diagnóstico, Tareas asignadas, Perfil y Notificaciones) y fue objeto de un refactor UX/UI completo — ver [`docente-rol-ux.md`](docente-rol-ux.md).

*   **Inicio:** panorama de emprendimientos asignados, tarjeta de **acciones rápidas** (registrar avance, calificar, revisar diagnóstico, **generar asesoría**), próximas asesorías y compromisos del día. Los pendientes enlazan a la **lista ya filtrada** (`?f=`).
*   **Módulo "Asesorías"**
    *   **Mis Asesorías:** tabla con las asignaciones bajo su cargo, filtros funcionales por **estado**, **estudiante** y **emprendimiento** con contador de resultados, y acciones por fila: **Confirmar** (modal de confirmación/notificación), **Reprogramar** (modal con fecha/hora) y **Ver detalle**. La acción **Generar asesoría** abre un modal que permite agendarla para **un estudiante específico** o para **un proyecto completo** (se anexa a todos los estudiantes del grupo).
    *   **Crear/Editar Asesorías (Registrar asesoría):** interfaz de agendamiento que **permite elegir estudiante y emprendimiento**, con fecha, hora, modalidad y lugar; "Confirmar y notificar", "Proponer otra fecha" y "Rechazar solicitud" abren modal o confirmación.
*   **Módulo "Emprendimientos"**
    *   **Listado:** pestañas **Tarjetas / Tabla**; el modelo es **N:N** (un emprendimiento puede tener varios estudiantes y un estudiante varios emprendimientos), así que la tabla muestra el grupo (Emprendimiento, Estudiante, Sector, Etapa, Avance, **Estado de revisión**, **Evidencia**, Última actividad, Acciones) con filtros de etapa/sector/**evidencia** y contador. Cada fila abre el expediente.
    *   **Expediente del emprendimiento:** pestañas **Avances · Tareas · Asesorías · Diagnóstico · Comentarios**; incluye la tarjeta **Estudiantes del grupo**, **bitácora de comentarios** (autor · fecha · texto + editor), y permite **calificar** y **registrar avance** (modal) desde el tablero de avances.
*   **Módulo "Diagnóstico y Tareas"**
    *   **Revisión del Diagnóstico:** resultados del diagnóstico con recomendaciones; tabla de **pendientes de revisión** y confirmación al guardar las recomendaciones.
    *   **Tareas asignadas:** filtros por **estado** y **prioridad**; **modal de calificación** por tarea, **modal de asignación** de tarea y acción "Devolver al estudiante".
*   **Perfil y Notificaciones:** datos personales con **título / especialidad** y tarjeta de **ubicación** (región/rectoría, departamento, ciudad, sede); cambio de contraseña por modal y notificaciones con filtro por tipo (chips con `aria-pressed`) y "Marcar todo como leído" con confirmación.

> El módulo **Seguimiento** del docente se eliminó; el registro de avance vive en el **modal «Registrar avance»** y la **columna Evidencia** de *Emprendimientos asignados*.