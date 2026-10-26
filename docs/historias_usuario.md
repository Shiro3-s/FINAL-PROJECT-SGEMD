# Documento de Requisitos e Historias de Usuario — SGEMD

> **Actualización:** 25 de octubre de 2026 · **trabajo local** (sin rama nueva, sin commit y sin push a GitHub).
> **Motivo:** alinear las historias con las correcciones C-1…C-7 y adiciones A-1…A-21, con el refactor de los roles y con las vistas realmente implementadas.
> **Convención de IDs:** las historias existentes conservan su redacción y no se renumeran. Las historias nuevas llevan `US-011` … `US-026`: las US-011 a US-024 se corresponden con `FR-011` … `FR-024` del SRS, **US-025** cubre el acta de compromiso (`FR-003`, `BR-009`) y **US-026** cubre el rol auditor (`NFR-002`, `NFR-007`, `FR-010`, `FR-017`).
> **Alcance:** el prototipo es estático; las operaciones de guardado y descarga están simuladas (`localStorage`). No hay backend, API ni PostgreSQL en este repositorio.

## 1. Resumen Ejecutivo
* **Dominio principal o propósito:** El documento detalla el diseño y los requisitos de **SGEMD (Sistema de Gestión de Emprendimiento Minuto de Dios)**, plataforma destinada a gestionar los procesos de emprendimiento en el Centro Progresa.
* **Roles principales identificados:** Administrador (Coordinadora), Estudiante (Emprendedor) y Docente (Asesor); **Auditor** como rol de consulta y exportación (AQ-08).
* **Procesos de negocio clave:** registro y activación de estudiantes, diagnóstico de caracterización, aprobación de emprendimientos, gestión y asignación manual de asesorías, seguimiento con evidencias, respaldos y reportes.
* **Propósito general de la funcionalidad:** Reemplazar la gestión manual basada en Excel para evitar cuellos de botella y pérdida de información. La herramienta centraliza los datos en un **Expediente Central del Proyecto**, automatiza el cálculo de métricas y opera con autenticación JWT y alta usabilidad. El prototipo actual permite validar la interfaz; la persistencia y la seguridad reales quedan para el backend.

## 2. Actores y Roles de Usuario
| Rol / Actor | Descripción | Responsabilidades |
| :--- | :--- | :--- |
| **Administrador (Coordinadora)** | Responsable del sistema en el Centro Progresa. | Visualizar toda la información global. Crear, editar, activar/desactivar y dar de baja lógica usuarios. Aprobar o rechazar emprendimientos (incluido el paralelo). Asignar y reasignar docentes. Crear y asignar asesorías directamente. Resolver la bandeja de solicitudes. Configurar el programa. Exportar reportes y respaldos y verificar su estado. |
| **Estudiante (Emprendedor)** | Emprendedor que busca apoyo y asesoría para su modelo de negocio. | Autoregistrarse. Completar el formulario de caracterización. Firmar el acta de confidencialidad. Registrar su emprendimiento (sujeto a aprobación). Solicitar asesorías. Subir avances y evidencias obligatorias. Consultar su perfil, su progreso por fases y su retroalimentación. |
| **Docente (Asesor)** | Encargado de brindar orientación a los estudiantes asignados. | Visualizar únicamente los proyectos y estudiantes asignados. Registrar avances con calificación y retroalimentación. Crear y calificar tareas. Aceptar o reprogramar asesorías. Revisar diagnósticos. Recomendar eventos. Mantener la bitácora del expediente. |
| **Auditor (rol 4)** | Rol de consulta institucional, sin intervención en la operación. | Consultar dashboards, expedientes y reportes; exportar reportes. **No** editar datos ni acceder a información sensible completa (`Fuera de alcance / Post-MVP`). |

## 3. Análisis de Procesos de Negocio
### Proceso: Flujo de Ingreso, Activación y Caracterización
* **Propósito:** Registrar al estudiante, activar su cuenta, evaluar su modelo de negocio y oficializar su ingreso al sistema.
* **Desencadenante:** El registro inicial del estudiante en el sistema.
* **Actores Involucrados:** Estudiante y Administrador.
* **Journey del Usuario:** El estudiante se registra y su cuenta queda en estado **Limitado**; el Administrador realiza la reunión de socialización y **desbloquea** el perfil (Limitado → Activo); se habilita el formulario de caracterización; el estudiante lo llena; el sistema calcula métricas; se firma el acta de confidencialidad; y se asigna un asesor.
* **Interacciones con el Sistema:** El sistema digitaliza el formulario y arroja un diagnóstico inmediato. El cambio de estado de la cuenta queda registrado y solo lo puede hacer el Administrador.

### Proceso: Registro y Aprobación de Emprendimientos
* **Propósito:** Autorizar la creación de un emprendimiento y controlar la existencia de proyectos paralelos.
* **Desencadenante:** El estudiante registra un emprendimiento.
* **Actores Involucrados:** Estudiante y Administrador.
* **Journey del Usuario:** El estudiante registra el emprendimiento; queda en **Pendiente de aprobación**. El Administrador lo revisa en la **bandeja de solicitudes** y lo aprueba o rechaza con motivo. Si el estudiante ya tiene un proyecto activo, la aprobación se registra como **paralelo autorizado**. El estudiante recibe la notificación.
* **Interacciones con el Sistema:** El estado del emprendimiento y la decisión quedan trazables; el rechazo notifica al estudiante.

### Proceso: Agendamiento y Seguimiento de Asesorías
* **Propósito:** Organizar las sesiones de orientación entre estudiantes y asesores, y documentar el avance del modelo de negocio.
* **Desencadenante:** La necesidad de una sesión de revisión o avance, o la programación administrativa.
* **Actores Involucrados:** Administrador, Docente, Estudiante.
* **Journey del Usuario:** El estudiante solicita una cita o el Administrador la crea y asigna directamente. El sistema verifica si el estudiante ha subido avances y aplica un semáforo (rojo si no lo ha hecho). El Docente **acepta, rechaza o propone otra fecha**. El sistema envía notificaciones In-App a ambas partes.
* **Interacciones con el Sistema:** El sistema evita la superposición de citas y ancla el historial, las notas y los adjuntos al **Expediente Central del Proyecto**. El estudiante no agenda por su cuenta.

### Proceso: Monitoreo, Reportes y Respaldos
* **Propósito:** Proporcionar métricas de impacto a la institución y mantener respaldos de seguridad.
* **Desencadenante:** La necesidad de presentar indicadores, cerrar un periodo o realizar copias de contingencia.
* **Actores Involucrados:** Administrador.
* **Journey del Usuario:** El Administrador accede al dashboard analítico, filtra y exporta informes en CSV, PDF o XLSX. En **Respaldos** consulta el último respaldo, el tamaño, el historial y la verificación de integridad, y exporta la base. En **Configuración** ajusta parámetros del programa y revisa la bitácora.
* **Interacciones con el Sistema:** El sistema genera reportes a partir de los datos y marca como **Inactivo** a quien supere **90 días** sin movimientos. La reactivación es manual.

## 4. Historias de Usuario (Formato Gherkin V2)

### Feature: Registro y Perfil Progresivo
**Como** Estudiante  
**Quiero** registrarme en la plataforma y tener un perfil que se desbloquee progresivamente  
**Para** cumplir con el proceso secuencial de ingreso al Centro Progresa  

* **Escenario:** Autoregistro con acceso limitado  
  * **Dado** un estudiante nuevo que desea ingresar al programa  
  * **Cuando** completa el formulario de registro independiente  
  * **Entonces** el sistema crea su cuenta, gestiona la sesión mediante un token JWT y le asigna un perfil con estado "Limitado"  

* **Escenario:** Desbloqueo manual por parte de la Coordinadora  
  * **Dado** que un estudiante con perfil "Limitado" ha participado en la reunión de socialización  
  * **Cuando** la Coordinadora actualiza su estado en el panel administrativo  
  * **Entonces** el sistema desbloquea las funciones de su perfil, permitiendo el acceso al formulario de caracterización  

### Feature: Control de Niveles de Permisos y Roles
**Como** Coordinadora  
**Quiero** que el sistema tenga tres niveles de permisos estrictos  
**Para** que la información confidencial de los proyectos solo sea visible por el personal autorizado  

* **Escenario:** Acceso global para la Coordinadora  
  * **Dado** que inicio sesión con el rol de "Coordinadora"  
  * **Cuando** accedo al panel principal  
  * **Entonces** puedo visualizar todos los estudiantes, asesores y proyectos globales  

* **Escenario:** Acceso restringido para el Asesor  
  * **Dado** que inicio sesión con el rol de "Asesor"  
  * **Cuando** accedo al panel principal  
  * **Entonces** solo puedo visualizar los proyectos y estudiantes que me han sido asignados explícitamente  

* **Escenario:** Acceso individual para el Estudiante  
  * **Dado** que inicio sesión con el rol de "Estudiante"  
  * **Cuando** accedo al panel principal  
  * **Entonces** solo puedo ver mi propio perfil, mis observaciones y mi proyecto  

### Feature: Diagnóstico Automático de Caracterización
**Como** Estudiante  
**Quiero** completar un formulario de valoración digitalizado  
**Para** que el sistema calcule mis métricas y me entregue un diagnóstico inmediato  

* **Escenario:** Cálculo automático de métricas al enviar  
  * **Dado** que he completado el formulario de caracterización (con preguntas estáticas configurables por backend)  
  * **Cuando** presiono el botón "Enviar"  
  * **Entonces** el sistema calcula las métricas automáticamente sin intervención manual  

### Feature: Expediente Central del Proyecto
**Como** Asesor y Estudiante  
**Queremos** acceder a una bitácora histórica y adjuntar documentos  
**Para** centralizar toda la información y evidencias en una base de datos relacional PostgreSQL  

* **Escenario:** Revisión de historia por nuevo asesor asignado  
  * **Dado** que soy un nuevo asesor asignado a un proyecto existente  
  * **Cuando** abro el detalle del proyecto  
  * **Entonces** puedo ver toda la historia, diagnósticos y notas previas dejadas por otros asesores  

* **Escenario:** Subida de archivos adjuntos al expediente  
  * **Dado** que un usuario (Estudiante o Asesor) se encuentra en el perfil del proyecto  
  * **Cuando** sube un archivo de evidencia (ej. PDF, Excel)  
  * **Entonces** el sistema almacena el documento en la base de datos PostgreSQL y lo vincula de forma permanente al Expediente Central  

### Feature: Agendamiento Manual Restringido
**Como** Coordinadora  
**Quiero** un módulo de gestión de agendas confiable y seguro  
**Para** que los estudiantes no elijan horarios libremente y se eviten cruces de citas  

* **Escenario:** Solicitud de cita queda en estado pendiente  
  * **Dado** que un estudiante requiere asesoría  
  * **Cuando** envía su solicitud a través de la plataforma  
  * **Entonces** esta solicitud queda en estado "Pendiente de aprobación" en el panel de la Coordinadora  

* **Escenario:** Prevención de duplicidad mediante propiedades ACID  
  * **Dado** que la Coordinadora intenta cruzar y confirmar una cita en un espacio horario específico  
  * **Cuando** el sistema procesa la asignación  
  * **Entonces** se ejecuta la operación bajo principios de aislamiento de transacciones (ACID) para garantizar la fiabilidad y evitar la superposición de citas  

### Feature: Sistema de Notificaciones In-App
**Como** Usuario del Sistema  
**Quiero** recibir alertas dentro de la misma plataforma  
**Para** enterarme rápidamente de las asignaciones sin depender de correos externos  

* **Escenario:** Notificación de confirmación de cita  
  * **Dado** que la Coordinadora ha asignado y confirmado una cita de asesoría  
  * **Cuando** el sistema completa el registro exitosamente  
  * **Entonces** el Estudiante y el Asesor reciben de forma inmediata una notificación visual (In-App) en sus respectivos paneles  

### Feature: Sistema de Semaforización por Avances
**Como** Asesor  
**Quiero** ver una alerta de color (semáforo rojo) cuando un estudiante agenda sin avances  
**Para** que pueda dedicar la sesión a nivelarlo  

* **Escenario:** Etiquetado de solicitud sin avances  
  * **Dado** que un estudiante intenta pedir cita sin haber registrado movimientos o avances recientes  
  * **Cuando** genera la solicitud  
  * **Entonces** el sistema procesa la solicitud pero la etiqueta visualmente en color rojo  

### Feature: Dashboard y Reportes Analíticos
**Como** Coordinadora  
**Quiero** visualizar un dashboard en tiempo real y exportar gráficas  
**Para** entregar indicadores de impacto a la institución rápidamente  

* **Escenario:** Exportación de gráficas e informes  
  * **Dado** que me encuentro en la vista del dashboard analítico  
  * **Cuando** presiono el botón de "Exportar a PDF"  
  * **Entonces** el sistema genera y descarga un archivo PDF con las gráficas de retención y emprendimientos activos  

### Feature: Respaldo y Contingencia de Datos
**Como** Coordinadora  
**Quiero** poder exportar toda la base de datos a formato Excel o CSV  
**Para** tener un respaldo local en caso de caídas del servidor  

* **Escenario:** Exportación de la base de datos completa  
  * **Dado** que he iniciado sesión como Coordinadora  
  * **Cuando** hago clic en el botón "Exportar base de datos"  
  * **Entonces** recibo un archivo CSV/Excel con la información completa de manera inmediata  

### Feature: Alertas de Inactividad
**Como** Coordinadora  
**Quiero** que el sistema cambie automáticamente el estado de los estudiantes tras un periodo largo sin uso  
**Para** poder identificarlos y reengancharlos fácilmente  

* **Escenario:** Cambio automático a estado inactivo tras 3 meses  
  * **Dado** que un estudiante no genera trazabilidad ni movimientos en la plataforma web  
  * **Cuando** transcurren 3 meses continuos (90 días) desde su última interacción  
  * **Entonces** el sistema actualiza su estado a "Inactivo" automáticamente  

### US-011: Alta y gestión de usuarios por el Administrador
**Como** Administrador  
**Quiero** crear, editar, activar/desactivar y dar de baja lógica cuentas de estudiante y docente  
**Para** habilitar el acceso sin depender del autorregistro  

* **Escenario:** Alta de un estudiante desde el panel  
  * **Dado** que estoy en la vista Usuarios  
  * **Cuando** selecciono "Nuevo estudiante" y completo los campos obligatorios  
  * **Entonces** el sistema valida documento y correo únicos y crea la cuenta con estado inicial  
* **Escenario:** Baja lógica con confirmación  
  * **Dado** un usuario con asignaciones activas  
  * **Cuando** selecciono "Dar de baja" y confirmo  
  * **Entonces** la cuenta queda inactiva, conserva su historial y sus asignaciones se liberan  

*Cubre:* FR-011, FR-013, FR-016 · BR-003, BR-006

### US-012: Aprobación de emprendimientos y paralelos
**Como** Administrador  
**Quiero** aprobar o rechazar el emprendimiento registrado por el estudiante, incluido el paralelo  
**Para** mantener el control sobre los proyectos activos  

* **Escenario:** Aprobación de un emprendimiento pendiente  
  * **Dado** un emprendimiento en estado "Pendiente de aprobación"  
  * **Cuando** lo apruebo desde la bandeja de solicitudes  
  * **Entonces** cambia a "Aprobado" y el estudiante recibe la notificación  
* **Escenario:** Rechazo con motivo  
  * **Dado** un emprendimiento pendiente  
  * **Cuando** lo rechazo e indico el motivo  
  * **Entonces** cambia a "Rechazado" y el motivo queda visible para el estudiante  
* **Escenario:** Autorización de un segundo emprendimiento  
  * **Dado** un estudiante con un emprendimiento aprobado  
  * **Cuando** registra un segundo emprendimiento y lo apruebo como paralelo  
  * **Entonces** ambos proyectos coexisten sin sobrescribirse  

*Cubre:* FR-012, FR-014, FR-019 · BR-004

### US-013: Desbloqueo y reactivación de cuentas
**Como** Administrador  
**Quiero** desbloquear un perfil Limitado y reactivar uno Inactivo  
**Para** controlar el acceso completo a la plataforma  

* **Escenario:** Desbloqueo tras la reunión de socialización  
  * **Dado** un estudiante con estado "Limitado"  
  * **Cuando** cambio su estado a "Activo"  
  * **Entonces** se habilitan las funciones completas y la transición queda registrada  
* **Escenario:** Reactivación tras inactividad  
  * **Dado** un estudiante marcado "Inactivo" por 90 días sin actividad  
  * **Cuando** el Administrador lo reactiva  
  * **Entonces** vuelve a "Activo" y puede operar de nuevo  
* **Escenario:** Intento de autoactivación  
  * **Dado** un estudiante con estado "Limitado"  
  * **Cuando** intenta cambiar su propio estado  
  * **Entonces** el sistema lo rechaza  

*Cubre:* FR-013, FR-007 · BR-003, BR-005

### US-014: Bandeja única de solicitudes
**Como** Administrador  
**Quiero** ver y resolver en un solo lugar desbloqueos, aprobaciones y citas pendientes  
**Para** reducir el tiempo de respuesta y no perder solicitudes  

* **Escenario:** Contador de pendientes  
  * **Dado** solicitudes de distinto tipo sin resolver  
  * **Cuando** abro la bandeja  
  * **Entonces** veo el contador por pestaña: Desbloqueos, Paralelos y Citas  
* **Escenario:** Resolución con confirmación  
  * **Dado** una solicitud pendiente  
  * **Cuando** la apruebo o rechazo  
  * **Entonces** el sistema aplica el cambio, notifica al solicitante y muestra confirmación  

*Cubre:* FR-014, FR-019

### US-015: Asignación directa de asesoría y aceptación docente
**Como** Administrador  
**Quiero** crear y asignar una asesoría directamente  
**Para** programar el acompañamiento sin depender de un permiso de horario  

* **Escenario:** Asignación directa  
  * **Dado** un emprendimiento con docente asignado  
  * **Cuando** creo la asesoría con fecha, hora y modalidad  
  * **Entonces** la cita queda agendada y se notifica al estudiante y al docente  
* **Escenario:** Aceptación o reprogramación por el docente  
  * **Dado** una asesoría asignada al docente  
  * **Cuando** el docente la acepta o propone otra fecha  
  * **Entonces** el estado cambia y el estudiante recibe la notificación  
* **Escenario:** Intento de agendamiento libre por el estudiante  
  * **Dado** un estudiante autenticado  
  * **Cuando** intenta crear una cita por su cuenta  
  * **Entonces** el sistema solo le permite solicitar, no confirmar  

*Cubre:* FR-004, FR-015, FR-019 · BR-002

### US-016: Validación y unicidad de formularios
**Como** Administrador  
**Quiero** que las altas y ediciones validen campos obligatorios y unicidad  
**Para** evitar duplicados y datos incompletos  

* **Escenario:** Documento o correo repetido  
  * **Dado** un formulario de alta de usuario  
  * **Cuando** ingreso un documento o correo ya registrado  
  * **Entonces** el sistema muestra el error en el campo y no guarda  
* **Escenario:** Tope de carga docente  
  * **Dado** un docente con la carga máxima configurada  
  * **Cuando** intento asignarle un nuevo emprendimiento  
  * **Entonces** el sistema advierte que se supera el tope de 12 horas  

*Cubre:* FR-016

### US-017: Expediente consolidado y trazable
**Como** Administrador y Docente  
**Quiero** ver el expediente completo de un emprendimiento en una sola vista  
**Para** reconstruir su historia sin importar quién lo atendió antes  

* **Escenario:** Consulta del expediente  
  * **Dado** un emprendimiento con asesorías, diagnósticos, seguimientos y evidencias  
  * **Cuando** abro su expediente  
  * **Entonces** veo cada bloque en pestañas y puedo exportar el expediente  
* **Escenario:** Cambio de docente  
  * **Dado** un emprendimiento reasignado a otro docente  
  * **Cuando** el nuevo docente abre el expediente  
  * **Entonces** conserva todo el historial previo  

*Cubre:* FR-017, FR-006 · NFR-007

### US-018: Respaldo y estado de la copia
**Como** Administrador  
**Quiero** exportar la base y ver el estado del respaldo  
**Para** tener contingencia y saber cuál es la copia vigente  

* **Escenario:** Consulta del estado  
  * **Dado** que ingreso a Respaldos  
  * **Cuando** reviso el panel  
  * **Entonces** veo el último respaldo, el tamaño, el historial y la verificación de integridad  
* **Escenario:** Exportación  
  * **Dado** que estoy en Respaldos  
  * **Cuando** selecciono exportar  
  * **Entonces** el sistema genera el archivo CSV/Excel (simulado en el prototipo)  

*Cubre:* FR-018, FR-009 · NFR-004

### US-019: Notificaciones accionables
**Como** Usuario del sistema  
**Quiero** que cada notificación abra el objeto referido y poder marcarla como leída  
**Para** actuar sobre el aviso sin buscarlo manualmente  

* **Escenario:** Abrir el objeto referido  
  * **Dado** una notificación de asesoría o solicitud  
  * **Cuando** hago clic en ella  
  * **Entonces** se abre la vista correspondiente  
* **Escenario:** Marcar como leídas  
  * **Dado** varias notificaciones sin leer  
  * **Cuando** selecciono "Marcar todo como leído"  
  * **Entonces** el contador de no leídas queda en cero  

*Cubre:* FR-005, FR-019

### US-020: Configuración del programa
**Como** Administrador  
**Quiero** ajustar los parámetros del programa en un solo lugar  
**Para** mantener consistentes las reglas de operación  

* **Escenario:** Cambio de parámetros  
  * **Dado** que ingreso a Configuración  
  * **Cuando** modifico carga docente, cupos o sedes y guardo  
  * **Entonces** el cambio aplica al programa y queda en la bitácora  
* **Escenario:** Consulta de la bitácora  
  * **Dado** cambios previos de configuración  
  * **Cuando** abro la bitácora  
  * **Entonces** veo autor, fecha y cambio realizado  

*Cubre:* FR-020 · NFR-007

### US-021: Eventos y recomendación docente
**Como** Docente  
**Quiero** consultar el detalle de un evento y recomendarlo a mis estudiantes  
**Para** vincular la agenda institucional con el acompañamiento  

* **Escenario:** Recomendación a un emprendimiento  
  * **Dado** un evento publicado y un emprendimiento asignado  
  * **Cuando** selecciono el emprendimiento y confirmo la recomendación  
  * **Entonces** todos sus estudiantes reciben la notificación  
* **Escenario:** Recomendación individual  
  * **Dado** un evento publicado y un estudiante asignado  
  * **Cuando** marco solo a ese estudiante  
  * **Entonces** la recomendación queda registrada para él  

*Cubre:* FR-021, FR-005

### US-022: Progreso por fases y descarga del plan
**Como** Estudiante  
**Quiero** ver mi avance por cada fase y descargar mi plan de trabajo  
**Para** saber qué me falta y trabajar fuera de la plataforma  

* **Escenario:** Avance por fase  
  * **Dado** un plan con tareas distribuidas en fases  
  * **Cuando** abro Estado de seguimiento  
  * **Entonces** veo una barra y un porcentaje por cada fase  
* **Escenario:** Descarga del plan  
  * **Dado** que estoy en el plan de trabajo  
  * **Cuando** selecciono "Descargar plan"  
  * **Entonces** obtengo el documento con el plan vigente (simulado en el prototipo)  

*Cubre:* FR-022

### US-023: Evidencia obligatoria para completar una tarea
**Como** Estudiante  
**Quiero** que el sistema me exija adjuntar evidencia antes de completar una tarea  
**Para** garantizar que mi avance esté respaldado  

* **Escenario:** Botón deshabilitado sin evidencia  
  * **Dado** una tarea sin archivos adjuntos  
  * **Cuando** abro su detalle  
  * **Entonces** "Marcar como completada" está deshabilitado  
* **Escenario:** Habilitación tras adjuntar  
  * **Dado** una tarea sin evidencia  
  * **Cuando** adjunto al menos un archivo  
  * **Entonces** el botón se habilita y la tarea puede pasar a "Completada"  

*Cubre:* FR-023, FR-008 · BR-007

### US-024: Datos académicos condicionales
**Como** Estudiante  
**Quiero** que mi formulario académico muestre solo los campos que aplican a mi nivel  
**Para** no diligenciar información irrelevante  

* **Escenario:** Nivel Pregrado  
  * **Dado** que selecciono "Pregrado"  
  * **Cuando** avanzo en el formulario  
  * **Entonces** se solicita el semestre y no el tipo de posgrado  
* **Escenario:** Nivel Egresado  
  * **Dado** que selecciono "Egresado"  
  * **Cuando** avanzo en el formulario  
  * **Entonces** desaparece el campo semestre  
* **Escenario:** Programa académico restringido  
  * **Dado** un estudiante en Configuración  
  * **Cuando** intenta cambiar su programa académico  
  * **Entonces** el sistema indica que solo el Administrador puede modificarlo  

*Cubre:* FR-024

### US-025: Gestión y rechazo del acta de compromiso
**Como** Administrador  
**Quiero** revisar el acta firmada y rechazarla con un motivo obligatorio  
**Para** garantizar el requisito legal antes de asignar un docente y dejar trazabilidad de la decisión

* **Escenario:** Carga del acta firmada
  * **Dado** un estudiante con la cuenta activa
  * **Cuando** descarga, firma y sube el acta de compromiso
  * **Entonces** el sistema registra el acta y habilita la revisión administrativa

* **Escenario:** Rechazo con motivo obligatorio
  * **Dado** un acta en revisión
  * **Cuando** el Administrador intenta rechazarla sin escribir un motivo
  * **Entonces** el sistema impide confirmar y exige el motivo
  * **Y** al confirmarlo, notifica al estudiante con la justificación

* **Escenario:** Asignación bloqueada sin acta aprobada
  * **Dado** un emprendimiento sin acta aprobada
  * **Cuando** el Administrador intenta asignar un docente definitivo
  * **Entonces** el sistema bloquea la asignación (BR-001)

*Cubre:* FR-003, BR-001, BR-009

> **Nota de alcance:** `Pendiente de backend`. El prototipo no tiene vista de acta y el modal de rechazo de la bandeja no valida el campo vacío.

### US-026: Consulta y exportación de reportes por el auditor
**Como** Auditor  
**Quiero** consultar dashboards y expedientes y exportar reportes sin modificar datos  
**Para** verificar el estado del programa y respaldar decisiones sin alterar la operación

* **Escenario:** Consulta de solo lectura
  * **Dado** un usuario con rol auditor
  * **Cuando** abre un dashboard o un expediente consolidado
  * **Entonces** ve la información en modo lectura y **no** aparecen acciones de edición

* **Escenario:** Datos sensibles protegidos
  * **Dado** un auditor que consulta un expediente
  * **Cuando** revisa los datos del estudiante o del emprendimiento
  * **Entonces** el sistema **no** muestra información sensible completa

* **Escenario:** Exportación con trazabilidad
  * **Dado** un auditor en un reporte disponible
  * **Cuando** solicita exportarlo
  * **Entonces** el sistema genera el archivo y registra usuario, fecha y objeto consultado (NFR-007)

* **Escenario:** Intento de escritura bloqueado
  * **Dado** un auditor autenticado
  * **Cuando** intenta crear, editar o eliminar cualquier registro
  * **Entonces** el sistema responde **403** y no modifica nada (NFR-002)

*Cubre:* NFR-002, NFR-007, FR-010, FR-017

> **Nota de alcance:** `Fuera de alcance / Post-MVP`. El rol auditor **no existe** en el prototipo; las coincidencias de “auditor” en las vistas corresponden a “Auditorio”. La decisión AQ-08 no crea un FR nuevo.

## 5. Journey del Usuario y Flujo del Proceso
1. **Inicio (Registro):** El Estudiante inicia el proceso registrándose en el sistema web, obteniendo un perfil con estado **Limitado** (autenticación vía JWT).
2. **Validación Administrativa:** El Administrador recibe al estudiante, realiza la reunión de socialización y **desbloquea** el perfil (Limitado → Activo). El cambio es exclusivo del Administrador.
3. **Auto-diagnóstico:** El Estudiante completa el formulario digital de valoración. El sistema calcula inmediatamente las métricas y le brinda el diagnóstico.
4. **Requisito Legal:** El Estudiante firma el acta de confidencialidad y la registra.
5. **Alta del Emprendimiento:** El Estudiante registra su emprendimiento. Queda en **Pendiente de aprobación** hasta que el Administrador lo apruebe; un segundo proyecto requiere autorización de **paralelo**.
6. **Emparejamiento:** El Administrador asigna el proyecto al Docente correspondiente desde Asignaciones.
7. **Seguimiento Continuo:** Cuando el estudiante necesita asesoría, **solicita** la cita o el Administrador la crea y asigna directamente. El Docente **acepta o propone otra fecha**. El sistema notifica a ambas partes vía notificaciones In-App.
8. **Evidencias:** El Estudiante adjunta archivos a sus tareas; el sistema exige al menos una evidencia para habilitar **Marcar como completada**.
9. **Finalización o Inactividad:** El Docente atiende la cita y deja notas y calificación en el Expediente Central. Si el estudiante deja de usar el portal durante **90 días**, pasa a **Inactivo**; el Administrador puede reactivarlo.

## 6. Casos Límite y Flujos Alternativos
* **Caso Límite 1: Solicitud de Cita sin Avances.** El estudiante pide mentoría sin completar trazabilidad reciente. El sistema permite la solicitud pero la resalta visualmente en color rojo para el docente.
* **Caso Límite 2: Caída del Servidor.** El sistema web sufre una interrupción. El Administrador utiliza el archivo CSV/Excel de contingencia descargado previamente para continuar operaciones de forma manual temporalmente.
* **Caso Límite 3: Cambio de Asesor.** El proyecto evoluciona y cambia de tutor. El nuevo docente ingresa y ve el Expediente Central intacto, ya que los datos están vinculados al proyecto y no al usuario docente.
* **Caso Límite 4: Estudiante con dos emprendimientos.** El segundo registro no sobrescribe al primero; queda en **Pendiente de aprobación** y solo coexiste si el Administrador autoriza el paralelo.
* **Caso Límite 5: Cuenta inactiva que desea volver.** El estudiante no puede reactivarse solo; debe solicitarlo y el Administrador ejecuta la transición Inactivo → Activo.
* **Caso Límite 6: Docente con carga completa.** Al superar el tope configurado (12 h), el sistema impide una nueva asignación y muestra el motivo.
* **Caso Límite 7: Tarea sin evidencia.** El estudiante intenta completarla sin adjuntos; el botón permanece deshabilitado hasta que suba al menos un archivo.
* **Caso Límite 8: Rechazo de emprendimiento.** El Administrador debe indicar el motivo; el estudiante lo ve en su notificación y puede corregir y reenviar.

## 7. Decisiones Técnicas y Reglas de Negocio Aclaradas
* **Autenticación:** Registro independiente con JWT y perfiles de habilitación progresiva.
* **Estados de cuenta:** **Limitado → Activo → Inactivo**. Solo el Administrador desbloquea y reactiva.
* **Diagnóstico:** Las preguntas y métricas son estáticas en código, pero se cambiarán mediante requerimientos a backend según solicitudes administrativas.
* **Expediente Central:** Soportado por una base de datos relacional PostgreSQL, adaptada para almacenar y vincular archivos adjuntos (Excel, PDF, etc.) y exportar datos. El registro de auditoría de cambios es **pendiente de backend**.
* **Notificaciones:** In-App y accionables; cada aviso abre el objeto referido y puede marcarse como leído.
* **Semaforización:** El parámetro para considerar un "avance" es generar trazabilidad y movimientos orgánicos dentro de la plataforma.
* **Inactividad:** El umbral se establece estrictamente en **3 meses (90 días)** sin generar movimientos.
* **Asesorías:** El Administrador asigna directamente; el Docente acepta o reprograma; el estudiante solo solicita. Sin integración con calendarios externos.
* **Agendamiento (Concurrencia):** Uso de principios de Aislamiento de Transacciones (ACID) para evitar la superposición de citas.
* **Alcance del prototipo:** el HTML es estático y generado desde Python. Guardar, descargar, exportar y notificar son simulaciones; no hay backend, API ni PostgreSQL en este repositorio.
* **Duplicidad intencional:** "Registrar avance" y "Revisar diagnóstico" existen para Administrador y Docente; es una decisión de diseño, no un defecto.
* **Acta de compromiso:** requisito legal previo a la asignación (BR-001). Su rechazo exige **motivo obligatorio** y notifica al estudiante (BR-009); la carga y la revisión están `Pendiente de backend`.
* **Respaldos:** el Administrador **exporta** la base/reportes y consulta estado e integridad; la **restauración** es una operación técnica, `Fuera de alcance / Post-MVP`.
* **Rol auditor (rol 4):** **solo lectura y exportación de reportes**; no edita datos ni accede a información sensible completa. Se cubre con NFR-002, NFR-007, FR-010, FR-017 y **US-026**, sin FR nuevo (AQ-08).

## 8. Matriz de Cobertura — Historia → Requisito

| Historia | Requisitos | Reglas | Estado en prototipo |
|---|---|---|---|
| US-011 | FR-011, FR-013, FR-016 | BR-003, BR-006 | `Implementado en prototipo (UI)` |
| US-012 | FR-012, FR-014, FR-019 | BR-004 | `Implementado en prototipo (UI)` |
| US-013 | FR-013, FR-007 | BR-003, BR-005 | `Implementado en prototipo (UI)` |
| US-014 | FR-014, FR-019 | — | `Implementado en prototipo (UI)` |
| US-015 | FR-004, FR-015, FR-019 | BR-002 | `Implementado en prototipo (UI)` |
| US-016 | FR-016 | — | `Simulado en prototipo` (unicidad real: backend) |
| US-017 | FR-017, FR-006 | — | `Implementado en prototipo (UI)`; log de auditoría pendiente |
| US-018 | FR-018, FR-009 | — | `Implementado en prototipo (UI)`; archivo simulado |
| US-019 | FR-005, FR-019 | — | `Implementado en prototipo (UI)` |
| US-020 | FR-020 | — | `Implementado en prototipo (UI)` |
| US-021 | FR-021, FR-005 | — | `Implementado en prototipo (UI)` |
| US-022 | FR-022 | — | `Implementado en prototipo (UI)`; descarga simulada |
| US-023 | FR-023, FR-008 | BR-007 | `Implementado en prototipo (UI)` |
| US-024 | FR-024 | — | `Implementado en prototipo (UI)` |
| US-025 | FR-003 | BR-001, BR-009 | `Pendiente de backend` (sin vista de acta) |
| US-026 | FR-010, FR-017, NFR-002, NFR-007 | — | `Fuera de alcance / Post-MVP` (rol no implementado) |

**Cobertura de las historias existentes:** las historias de registro, permisos por rol, diagnóstico, expediente, agendamiento, notificaciones, semaforización, dashboard, respaldo e inactividad se mantienen vigentes y se alinean con `FR-001` a `FR-010`. La historia de inactividad queda cerrada en **90 días** (coincide con `FR-007` y `BR-005`).

## 9. Control de Cambios

| Fecha | Cambio | Historias / secciones | Evidencia |
|---|---|---|---|
| 2026-10-25 | Renombre de “Proyecto Quantum” a SGEMD | Título, §1 | `README.md` §1 |
| 2026-10-25 | Actualización de actores y responsabilidades | §2 | `prototype/admin/usuarios.html`, `admin/solicitudes.html` |
| 2026-10-25 | Nuevos procesos de negocio | §3 | `prototype/admin/**` |
| 2026-10-25 | Nuevas historias Gherkin | US-011 … US-025 | Vistas de los tres roles |
| 2026-10-25 | Rol auditor: solo lectura y exportación | US-026, §7, §8 | AQ-08; NFR-002, NFR-007, FR-010, FR-017 |
| 2026-10-25 | Asesoría: Admin asigna, docente acepta | §3, §5, §7, US-015 | C-1, C-2, C-5, C-6 |
| 2026-10-25 | Inactividad en 90 días | §3, §5, §6, §7 | C-3, AQ-01 |
| 2026-10-25 | Matriz de cobertura | §8 | `fr_nfr_sgemd.md` §8 |
| 2026-10-25 | Declaración de alcance estático | Encabezado, §1, §7 | A-20 |
| 2026-10-25 | Rechazo del acta con motivo obligatorio | US-025, §7 | AQ-05; BR-009 |
| 2026-10-25 | Restauración de respaldos fuera de la UI | §7 | AQ-04; FR-018 |
| 2026-10-25 | Cierre de AQ-03 por equivalencia de archivo | §9 | SHA-256 `EDCDE30F…836B5872` |

**Preguntas abiertas:** **AQ-01 … AQ-05 y AQ-08 quedaron cerradas** el 2026-10-25; **AQ-11** se cerró con el modelo textual. AQ-03 se cerró al verificar que el archivo de correcciones es idéntico por hash al usado; AQ-04 fijó la restauración como operación técnica; AQ-05 hizo obligatorio el motivo de rechazo del acta (BR-009); AQ-08 definió el rol auditor de solo lectura y exportación (US-026). Siguen abiertas **AQ-06, AQ-07, AQ-09, AQ-10 y AQ-12**, tratadas en `docs/dossier-decisiones-pendientes-2026-10.md`; no se deciden por defecto.
