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
El menú lateral se adapta para centrarse en las herramientas de tutoría, retroalimentación y seguimiento académico y usa la **misma estructura de grupos/acordeón que el rol Estudiante** (Inicio + grupo *Mis emprendimientos* + grupo *Acompañamiento y actividades*; Notificaciones y Perfil viven en la barra superior). El rol se compone de **23 pantallas** en `docente/` y fue objeto de un refactor UX/UI completo — ver [`docente-rol-ux.md`](docente-rol-ux.md). Como principio, las acciones del docente son **vistas completas** y no ventanas emergentes: ver un avance, calificar o devolver una tarea, registrar o confirmar una asesoría, ver un evento y recomendar a los estudiantes y cambiar la contraseña llevan a su propia pantalla. El **grupo *Mis emprendimientos*** reúne *Emprendimientos asignados*, *Diagnóstico* y *Tareas*; **Acompañamiento y actividades** contiene *Asesorías*; **Eventos**, *Mi perfil*, *Configuración* y *Notificaciones* completan el rol.

*   **Inicio (`dashboard.html`):** panorama con métricas, el gráfico **Avance por emprendimiento** a **ancho completo** (barras responsivas), una tarjeta de **acciones rápidas** (registrar avance, calificar, revisar diagnóstico, **generar asesoría**), próximas asesorías y un **calendario de compromisos**: arranca en el **día de hoy** y, al hacer clic en un día, cambia la lista de asesorías, tareas y eventos de esa fecha (los días sin compromisos muestran un estado vacío). Cada acceso enlaza a una vista completa; los pendientes enlazan a la **lista ya filtrada** (`?f=`).
*   **Módulo "Mis emprendimientos"**
    *   **Emprendimientos asignados (`emprendimientos.html`):** solo los asignados, en pestañas **Tarjetas / Tabla** (modelo **N:N**: un emprendimiento con varios estudiantes y viceversa). La tabla muestra el grupo (Emprendimiento, Estudiante, Sector, Etapa, Avance, **Estado de revisión**, **Evidencia**, Última actividad, Acciones) con filtros de etapa/sector/**evidencia** y contador. Un **selector de estudiante** reemplaza la lista por **los emprendimientos de ese estudiante como pestañas** (la primera activa por defecto).
    *   **Expediente del emprendimiento (`emprendimiento-expediente.html`):** pestañas **Avances · Tareas · Asesorías · Diagnóstico · Comentarios**; incluye **Estudiantes del grupo**, **bitácora de comentarios** (autor · fecha · texto + editor) y enlaces a las vistas completas de avance y asesoría.
    *   **Detalle del avance (`avance-detalle.html`)** y **Registrar avance (`avance-form.html`):** visualización del avance (descripción, evidencia adjunta, historial) y formulario-página para registrar o editar (fase, fecha, descripción, puntaje 0–100, estado de revisión y evidencia).
    *   **Diagnóstico (`diagnostico.html`):** **selector de emprendimiento** y **filtros por estudiante/proyecto**; el diagnóstico se calcula por la **completación de las 4 fases** o por una **serie de tareas clave**. Muestra el **avance por fases** y el comportamiento entrepreneurial.
    *   **Revisión del diagnóstico (`diagnostico-revision.html`):** lectura del resultado con **recomendaciones** del docente, resumen y tabla de **pendientes de revisión**.
    *   **Tareas asignadas (`tareas.html`)** con sus vistas completas: **Detalle de tarea (`tarea-detalle.html`)** para ver y **calificar**; **Devolver tarea (`tarea-devolver.html`)** con **motivo** y **observaciones**; **Asignar tarea (`tarea-form.html`)**. Filtros por **estado** y **prioridad**.
*   **Módulo "Acompañamiento y actividades"**
    *   **Mis asesorías (`asesorias.html`):** **una sola tabla** con **filtro de estado agrupado** (*Por agendar · Agendada · Completada · Cancelada*, derivado del estado detallado) y filtros por **estudiante** y **emprendimiento**, con contador de resultados. La acción **Registrar asesoría** lleva a su vista.
    *   **Detalle de asesoría (`asesoria-detalle.html`):** vista completa de una solicitud (datos, agenda, estudiantes agendados) con **Confirmar y notificar**, **Proponer otra fecha** y **Rechazar solicitud**. La acción **Generar asesoría** permite agendarla para **un emprendimiento** (se anexa a **todo su grupo**) partiendo del flujo de referencia del estudiante (`solicitar-asesoria`, sin modificar).
    *   **Registrar asesoría (`asesoria-form.html`):** formulario-página con emprendimiento (por grupo), **tema por defecto** (*FASE 2 - Prototipo: empaque*, *Tarea: …*), **fecha/hora disponible**, **modalidad** y **descripción de necesidades**.
*   **Módulo "Eventos"**
    *   **Eventos (`eventos.html`):** catálogo de los eventos del programa (tabla con tipo, fecha, modalidad y organizador), **calendario** del mes y la tabla de **recomendaciones enviadas** (estudiante · evento · estado · fecha). Cada evento ofrece **Ver evento** y **Recomendar a estudiantes**, que llevan al mismo detalle.
    *   **Detalle del evento (`evento-detalle-startup.html`, `evento-detalle-capacitacion.html`, `evento-detalle-asesoria-grupal.html`, `evento-detalle-showroom.html`):** información completa del evento —espejo del rol Estudiante: en qué consiste, fecha y hora, modalidad, lugar, organizador y cupos, más el **acceso al evento virtual** en el taller— y la **recomendación embebida**: un selector **por emprendimiento** (marca a todo el grupo), un **checklist individual** de estudiantes, un **mensaje opcional** y el botón **Enviar recomendación**. El detalle de asesoría grupal añade los **pasos** y el de showroom, la nota de montaje. Sustituye a la antigua vista `evento-recomendar.html`.
*   **Perfil y Notificaciones:** **Mi perfil (`perfil.html`)** funciona como **dashboard de la cuenta** (datos, emprendimientos asignados y estado); la edición vive en **Configuración (`configuracion.html`)** (datos, preferencias de notificación y accesos de seguridad); **Cambiar contraseña (`contrasena.html`)** como vista propia; **Notificaciones (`notificaciones.html`)** con filtro por tipo (chips con `aria-pressed`) y *Marcar todo como leído* con confirmación (único diálogo del rol).

> El módulo **Seguimiento** del docente se eliminó; el registro de avance vive en la vista **«Registrar avance»** y la **columna Evidencia** de *Emprendimientos asignados*.