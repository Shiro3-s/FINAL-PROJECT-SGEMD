# Documento de Requisitos e Historias de Usuario - Proyecto Quantum

## 1. Resumen Ejecutivo
* **Dominio principal o propósito:** El documento detalla el diseño y los requisitos de una plataforma web (Proyecto Quantum) destinada a gestionar los procesos de emprendimiento en el Centro Progresa.
* **Roles principales identificados:** Coordinadora (Administradora), Estudiante (Emprendedor) y Asesor (Docente).
* **Procesos de negocio clave:** El sistema abarca el registro de estudiantes, el diagnóstico de caracterización, la gestión y asignación manual de agendas para asesorías, y la generación de reportes analíticos.
* **Propósito general de la funcionalidad:** Se busca reemplazar la gestión manual basada en Excel para evitar cuellos de botella y pérdidas de información. La nueva herramienta centralizará los datos en un "Expediente Central del Proyecto", soportado por una base de datos PostgreSQL. Además, automatizará el cálculo de métricas y proporcionará un entorno seguro con autenticación JWT y alta usabilidad.

## 2. Actores y Roles de Usuario
| Rol / Actor | Descripción | Responsabilidades |
| :--- | :--- | :--- |
| **Coordinadora** | Administradora principal del sistema en el Centro Progresa. | Visualizar toda la información global. Aprobar y asignar manualmente los espacios de asesoría asegurando aislamiento transaccional. Exportar datos y generar reportes. Desbloquear perfiles limitados. |
| **Estudiante** | Emprendedor que busca apoyo y asesoría para su modelo de negocio. | Autoregistrarse. Completar el formulario de caracterización. Firmar el acta de confidencialidad. Subir avances/archivos adjuntos obligatorios. Visualizar su propio perfil y retroalimentación. |
| **Asesor (Docente)** | Encargado de brindar orientación a los estudiantes asignados. | Visualizar únicamente los proyectos y estudiantes asignados a su perfil. Registrar el historial, documentos y notas en la bitácora del proyecto. |

## 3. Análisis de Procesos de Negocio
### Proceso: Flujo de Ingreso y Caracterización
* **Propósito:** Registrar al estudiante, evaluar su modelo de negocio y oficializar su ingreso al sistema.
* **Desencadenante:** El registro inicial del estudiante en el sistema.
* **Actores Involucrados:** Estudiante y Coordinadora.
* **Journey del Usuario:** El estudiante se registra (perfil limitado); la coordinadora realiza una reunión de socialización y desbloquea el perfil; se habilita el formulario de caracterización; el estudiante lo llena; el sistema calcula métricas; firman el acta de confidencialidad; y se asigna un asesor.
* **Interacciones con el Sistema:** El sistema digitaliza el formulario y arroja un diagnóstico inmediato en la pantalla del estudiante.

### Proceso: Agendamiento y Seguimiento de Asesorías
* **Propósito:** Organizar las sesiones de orientación entre estudiantes y asesores, y documentar el avance del modelo de negocio.
* **Desencadenante:** La necesidad de una sesión de revisión o avance por parte del estudiante.
* **Actores Involucrados:** Coordinadora, Asesor, Estudiante.
* **Journey del Usuario:** El estudiante solicita una cita. El sistema verifica si el estudiante ha subido avances y aplica un semáforo (rojo si no lo ha hecho). La coordinadora asigna y cruza los horarios manualmente. El sistema envía notificaciones In-App de confirmación.
* **Interacciones con el Sistema:** El sistema permite a la coordinadora cruzar las agendas bajo principios ACID para evitar duplicidad de envíos. El sistema ancla todo el historial y notas (incluyendo adjuntos PDF/Excel) al "Expediente Central del Proyecto".

### Proceso: Monitoreo y Reportes Directivos
* **Propósito:** Proporcionar métricas de impacto a la institución y mantener respaldos de seguridad.
* **Desencadenante:** La necesidad de presentar indicadores o realizar backups de contingencia.
* **Actores Involucrados:** Coordinadora.
* **Journey del Usuario:** La coordinadora accede al dashboard analítico. Descarga informes en PDF o gráficas. Alternativamente, exporta la base de datos a CSV/Excel con un clic.
* **Interacciones con el Sistema:** El sistema genera reportes en tiempo real y permite la exportación masiva de datos. También marca como inactivos a los usuarios que superen los 3 meses sin generar movimientos en plataforma.

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

## 5. Journey del Usuario y Flujo del Proceso
1. **Inicio (Registro):** El Estudiante inicia el proceso registrándose en el sistema web, obteniendo un perfil con estado "Limitado" (autenticación vía JWT).
2. **Validación Administrativa:** La Coordinadora recibe al estudiante, realiza la reunión de socialización presencial/virtual y, posteriormente, desbloquea el perfil.
3. **Auto-diagnóstico:** El Estudiante completa el formulario digital de valoración. El sistema calcula inmediatamente las métricas y le brinda el diagnóstico.
4. **Requisito Legal:** El Estudiante firma el acta de confidencialidad y la registra.
5. **Emparejamiento:** La Coordinadora asigna el proyecto al Asesor correspondiente.
6. **Seguimiento Continuo:** Cuando el estudiante necesita asesoría, utiliza la plataforma (generando trazabilidad/movimientos, adjuntando PDFs/Excel) y solicita la cita.
7. **Agendamiento:** La Coordinadora aprueba el horario con transacciones seguras (ACID). El sistema notifica a ambas partes vía notificaciones In-App.
8. **Finalización o Inactividad:** El Asesor atiende la cita y deja notas en el Expediente Central (PostgreSQL). Si el estudiante deja de usar el portal durante 3 meses, pasa a estado Inactivo automáticamente.

## 6. Casos Límite y Flujos Alternativos
* **Caso Límite 1: Solicitud de Cita sin Avances.** El estudiante pide mentoría sin completar trazabilidad reciente. El sistema permite la solicitud pero la resalta visualmente en color rojo para el asesor.
* **Caso Límite 2: Caída del Servidor.** El sistema web sufre una interrupción. La Coordinadora utiliza el archivo CSV/Excel de contingencia descargado previamente para continuar operaciones de forma manual temporalmente.
* **Caso Límite 3: Cambio de Asesor.** El proyecto evoluciona y cambia de tutor. El nuevo docente ingresa y ve el Expediente Central intacto, ya que los datos están vinculados al proyecto y no al usuario docente.

## 7. Decisiones Técnicas y Reglas de Negocio Aclaradas
* **Autenticación:** Implementación de registro independiente con JWT y perfiles de habilitación progresiva.
* **Diagnóstico:** Las preguntas y métricas son estáticas en código, pero se cambiarán mediante requerimientos a backend según solicitudes administrativas.
* **Expediente Central:** Soportado por base de datos relacional PostgreSQL, adaptada para almacenar y vincular archivos adjuntos (Excel, PDF, etc.) y exportar datos.
* **Notificaciones:** Exclusivamente In-App, reemplazando la necesidad de envíos vía correo electrónico.
* **Semaforización:** El parámetro para considerar un "avance" es generar trazabilidad y movimientos orgánicos dentro de la plataforma.
* **Inactividad:** El umbral se establece estrictamente en 3 meses exactos sin generar movimientos.
* **Agendamiento (Concurrencia):** Uso de principios de Aislamiento de Transacciones (ACID) y teorema CAP (priorizando CA - Consistencia y Disponibilidad adaptada) para evitar problemas de duplicidad de envío en la confirmación de citas.
