# Especificación de Requisitos de Software (SRS) - Sistema de Gestión de Emprendimiento Minuto de Dios (SGEMD)

## 1. Resumen del Proyecto

El Sistema de Gestión de Emprendimiento Minuto de Dios (SGEMD) es una plataforma web orientada a la administración del emprendimiento estudiantil universitario[cite: 7]. El proyecto busca solucionar la ineficiencia, dispersión de datos y cuellos de botella generados por la gestión manual en hojas de cálculo (Excel) dentro del Centro Progresa[cite: 7, 9].

Los usuarios principales son Estudiantes (emprendedores), Docentes/Mentores (asesores) y Administradores (coordinadores)[cite: 7]. Los procesos clave incluyen el registro, la valoración automática del modelo de negocio, el agendamiento controlado de asesorías, el seguimiento del plan de trabajo y la visualización de métricas[cite: 7, 8, 9]. La solución se construirá desde cero utilizando Node.js y React, garantizando seguridad, roles aislados y una interfaz de alta usabilidad[cite: 7, 9].

## 2. Partes Interesadas y Roles de Usuario

| ID | Rol / Parte Interesada | Descripción | Responsabilidades | Necesidades y Objetivos | Referencia |
| -- | ------------------ | ----------- | ---------------- | --------------- | ---------------- |
| R-01 | Administrador (Coordinadora) | Gestiona el sistema, usuarios y asignaciones[cite: 7]. | Crear usuarios, asignar mentores, aprobar emprendimientos paralelos, controlar la agenda y descargar respaldos[cite: 7, 9]. | Automatizar tabulaciones, mantener el control del agendamiento, descargar reportes y respaldos en Excel/CSV[cite: 9]. |[cite: 7, 8, 9] |
| R-02 | Docente / Mentor (Asesor) | Acompaña a uno o varios estudiantes[cite: 7]. | Registrar seguimiento, crear tareas, confirmar asesorías y visualizar el diagnóstico inicial[cite: 7, 8]. | Conocer el contexto del emprendimiento (historial) y tener una interfaz simple[cite: 7, 8, 9]. |[cite: 7, 8, 9] |
| R-03 | Estudiante (Emprendedor) | Propietario del emprendimiento[cite: 7]. | Registrarse, diligenciar formularios de valoración, firmar acta de confidencialidad, cumplir tareas y solicitar asesorías[cite: 7, 8, 9]. | Recibir retroalimentación inmediata sobre su modelo de negocio y gestionar sus avances fácilmente[cite: 8, 9]. |[cite: 7, 8, 9] |

## 3. Análisis de Procesos de Negocio

### BP-001: Registro y Diagnóstico Inicial
* **Propósito:** Registrar al estudiante y evaluar el estado de su emprendimiento[cite: 7, 8].
* **Desencadenante:** El estudiante ingresa a la plataforma para crear una cuenta[cite: 7].
* **Actores:** Estudiante, Administrador[cite: 7, 8].
* **Flujo Actual:** El estudiante llena un formulario, el administrador cruza datos manualmente en Excel para generar un diagnóstico y le asigna un docente[cite: 8, 9].
* **Experiencia del Usuario:** El estudiante se registra y verifica su correo[cite: 7]. Tras una reunión de socialización, el administrador le habilita un formulario de caracterización (modelo de negocio, marketing, etc.)[cite: 8, 9]. Al completarlo, el sistema genera el diagnóstico automático y el estudiante firma el acta de confidencialidad[cite: 8, 9].
* **Puntos de Dolor:** Tabulación manual en Excel que consume tiempo y retrasa el feedback[cite: 9].
* **Resultado Deseado:** Diagnóstico automático inmediato y centralización de documentos[cite: 8, 9].
* **Reglas de Negocio:** El estudiante debe verificar su cuenta con un código OTP de 8 dígitos válido por 5 minutos[cite: 7]. La asignación del docente requiere el acta de confidencialidad firmada[cite: 8].
* **Requisitos Relacionados:** FR-001, FR-002, FR-003, BR-001.
* **Referencia:**[cite: 7, 8, 9].

### BP-002: Gestión y Asignación de Asesorías
* **Propósito:** Conectar al estudiante con un mentor y programar sesiones de trabajo[cite: 7, 9].
* **Desencadenante:** El estudiante solicita una asesoría o el administrador empareja perfiles[cite: 7, 9].
* **Actores:** Administrador, Docente, Estudiante[cite: 7, 9].
* **Flujo Actual:** Coordinación manual propensa a errores y cruces de horarios[cite: 9].
* **Experiencia del Usuario:** El Administrador asigna manualmente el estudiante a un Docente[cite: 7, 9]. El sistema envía notificaciones en tiempo real al confirmar espacios[cite: 7].
* **Puntos de Dolor:** Agendamiento fantasma si los docentes no actualizan disponibilidad; pérdida de control si los estudiantes agendan libremente[cite: 9].
* **Resultado Deseado:** Un módulo centralizado y restrictivo donde el Administrador controla los cruces de agenda[cite: 9].
* **Reglas de Negocio:** No existirá flujo de agendamiento automático ni integración con calendarios externos; todo se controla manualmente en la plataforma por el Administrador[cite: 9].
* **Requisitos Relacionados:** FR-004, FR-005, BR-002.
* **Referencia:**[cite: 7, 9].

### BP-003: Seguimiento y Trazabilidad del Proyecto
* **Propósito:** Mantener el historial de tareas, notas y avances del emprendimiento[cite: 7, 9].
* **Desencadenante:** El docente evalúa avances o crea un plan de trabajo[cite: 7].
* **Actores:** Docente, Estudiante, Administrador[cite: 7].
* **Flujo Actual:** Pérdida de historial cuando un estudiante cambia de asesor[cite: 9].
* **Experiencia del Usuario:** El Docente registra notas y adjunta evidencias (archivos)[cite: 7]. El estudiante ingresa para ver sus tareas, completarlas y visualizar su porcentaje de progreso[cite: 7]. Si un estudiante se inactiva, el sistema alerta al Administrador[cite: 9].
* **Puntos de Dolor:** Pérdida de información histórica y dificultad para identificar estudiantes inactivos[cite: 9].
* **Resultado Deseado:** Un Expediente Central anclado a la idea de negocio, no al docente[cite: 9].
* **Reglas de Negocio:** El historial pertenece al emprendimiento[cite: 9]. Estudiantes inactivos deben ser marcados por el sistema tras un periodo de tiempo[cite: 9].
* **Requisitos Relacionados:** FR-006, FR-007, FR-008.
* **Referencia:**[cite: 7, 9].

## 4. Requisitos Funcionales

### FR-001: Registro y Verificación de Estudiantes
* **Declaración:** El sistema deberá permitir a los estudiantes registrarse utilizando un correo institucional y verificar su cuenta mediante un código OTP de 8 dígitos enviado por correo[cite: 7].
* **Descripción:** Garantiza que solo usuarios válidos accedan al sistema[cite: 7].
* **Rol Relacionado:** Estudiante[cite: 7].
* **Reglas de Negocio:** El código caduca en 5 minutos y se valida estrictamente en el backend[cite: 7].
* **Prioridad:** Alta[cite: 7].
* **Referencia:**[cite: 7].

### FR-002: Formulario de Valoración y Diagnóstico Automático
* **Declaración:** El sistema deberá proveer un formulario de caracterización (modelo de negocio, marketing, producto, financiero) y calcular automáticamente las métricas para generar un diagnóstico de fortalezas y debilidades[cite: 8, 9].
* **Descripción:** Elimina la tabulación manual y provee feedback inmediato al estudiante y al docente[cite: 8, 9].
* **Rol Relacionado:** Estudiante, Administrador, Docente[cite: 8, 9].
* **Prioridad:** Alta[cite: 8, 9].
* **Referencia:**[cite: 8, 9].

### FR-003: Gestión de Acta de Confidencialidad
* **Declaración:** El sistema deberá permitir a los estudiantes descargar, firmar y subir el acta de compromiso de confidencialidad[cite: 8].
* **Descripción:** Requisito legal previo a la asignación de un mentor[cite: 8].
* **Rol Relacionado:** Estudiante, Administrador[cite: 8].
* **Reglas de Negocio:** Requisito obligatorio para iniciar la asesoría[cite: 8].
* **Prioridad:** Alta[cite: 8].
* **Referencia:**[cite: 8].

### FR-004: Asignación y Agendamiento Manual
* **Declaración:** El sistema deberá incluir un módulo donde el Administrador asigne manualmente docentes a estudiantes y apruebe/gestione los cruces de espacios para asesorías[cite: 7, 9].
* **Descripción:** Mantiene el control administrativo sobre los horarios[cite: 9].
* **Rol Relacionado:** Administrador[cite: 9].
* **Reglas de Negocio:** Prohibido el agendamiento libre o automático por parte del estudiante[cite: 9].
* **Prioridad:** Alta[cite: 9].
* **Referencia:**[cite: 7, 9].

### FR-005: Notificaciones en Tiempo Real
* **Declaración:** El sistema deberá enviar notificaciones en tiempo real a los usuarios cuando un docente asigne una nueva tarea o confirme una asesoría[cite: 7].
* **Descripción:** Mejora la comunicación y tiempos de respuesta[cite: 7].
* **Rol Relacionado:** Estudiante, Docente[cite: 7].
* **Prioridad:** Media[cite: 7].
* **Referencia:**[cite: 7].

### FR-006: Expediente Central del Emprendimiento (Trazabilidad)
* **Declaración:** El sistema deberá anclar todo el historial de diagnósticos, notas de seguimiento, tareas y asesorías directamente a la entidad "Emprendimiento"[cite: 7, 9].
* **Descripción:** Permite que nuevos docentes asignados vean todo el contexto histórico del proyecto sin importar rotaciones de personal[cite: 9].
* **Rol Relacionado:** Docente, Administrador[cite: 9].
* **Prioridad:** Alta[cite: 7, 9].
* **Referencia:**[cite: 7, 9].

### FR-007: Semaforización de Inactividad
* **Declaración:** El sistema deberá cambiar automáticamente el estado de un estudiante (semaforización/alerta) tras un periodo de tiempo definido sin registrar actividad o avances[cite: 9].
* **Descripción:** Facilita la identificación rápida de deserción para contactar al estudiante[cite: 9].
* **Rol Relacionado:** Administrador[cite: 9].
* **Prioridad:** Media[cite: 9].
* **Referencia:**[cite: 9].

### FR-008: Gestión de Archivos Adjuntos
* **Declaración:** El sistema deberá permitir la subida, almacenamiento y descarga de archivos (PDFs, imágenes) de hasta 500 MB en los módulos de tareas, seguimientos y asesorías[cite: 7].
* **Descripción:** Permite cargar evidencias del trabajo[cite: 7].
* **Rol Relacionado:** Todos[cite: 7].
* **Reglas de Negocio:** Los archivos se eliminan físicamente del servidor si se borra el registro asociado[cite: 7].
* **Prioridad:** Alta[cite: 7].
* **Referencia:**[cite: 7].

### FR-009: Exportación de Datos (Backup Local)
* **Declaración:** El sistema deberá incluir un módulo en el perfil del Administrador para exportar la base de datos a formato CSV o Excel con un solo clic[cite: 9].
* **Descripción:** Sirve como plan de contingencia ante caídas del servidor[cite: 9].
* **Rol Relacionado:** Administrador[cite: 9].
* **Prioridad:** Alta[cite: 9].
* **Referencia:**[cite: 9].

### FR-010: Dashboards de Métricas
* **Declaración:** El sistema deberá mostrar métricas derivadas de la base de datos en tiempo real, incluyendo conteos totales (usuarios, emprendimientos), porcentajes de avance de tareas y distribución por etapa[cite: 7, 9].
* **Descripción:** Elimina el procesamiento manual de informes[cite: 9].
* **Rol Relacionado:** Administrador, Docente, Estudiante[cite: 7].
* **Prioridad:** Alta[cite: 7, 9].
* **Referencia:**[cite: 7, 9].

## 5. Requisitos No Funcionales

### NFR-001: Usabilidad y Simplicidad
* **Categoría:** Usabilidad
* **Declaración:** El sistema deberá tener una interfaz de navegación donde el agendamiento y la subida de archivos requieran un máximo de tres clics desde el panel principal[cite: 9].
* **Descripción:** Asegura la adopción por parte de usuarios no tecnológicos[cite: 9].
* **Condición de Aceptación:** Prueba piloto superada sin necesidad de soporte técnico recurrente[cite: 9].
* **Prioridad:** Alta[cite: 9].
* **Referencia:**[cite: 9].

### NFR-002: Autorización Restringida por Rol y Alcance
* **Categoría:** Seguridad
* **Declaración:** El sistema deberá validar el rol y el alcance (propiedad) en el backend para cada endpoint, asegurando que un docente solo acceda a sus emprendimientos asignados y un estudiante únicamente al suyo[cite: 7, 9].
* **Descripción:** Previene la visualización no autorizada de datos cruzados[cite: 7, 9].
* **Condición de Aceptación:** Pruebas de API (HTTP 403) al intentar acceder a IDs no pertenecientes al usuario[cite: 7].
* **Prioridad:** Alta[cite: 7, 9].
* **Referencia:**[cite: 7, 9].

### NFR-003: Seguridad de Credenciales y Autenticación
* **Categoría:** Seguridad
* **Declaración:** El sistema deberá usar JWT (expiración de 8h) para el manejo de sesiones y `bcrypt` para encriptar contraseñas; las credenciales y códigos OTP nunca deben exponerse en respuestas JSON[cite: 7, 9].
* **Descripción:** Mitiga riesgos de interceptación de información y vulnerabilidades previas[cite: 7].
* **Condición de Aceptación:** Análisis de payload de respuestas HTTP[cite: 7].
* **Prioridad:** Alta[cite: 7, 9].
* **Referencia:**[cite: 7, 9].

### NFR-004: Copias de Seguridad Automatizadas
* **Categoría:** Fiabilidad
* **Declaración:** El sistema deberá ejecutar backups automatizados diarios de la base de datos[cite: 9].
* **Descripción:** Garantiza la continuidad del negocio en semanas críticas de evaluación[cite: 9].
* **Condición de Aceptación:** Verificación de archivos de volcado (dump) generados diariamente en el servidor[cite: 9].
* **Prioridad:** Alta[cite: 9].
* **Referencia:**[cite: 9].

## 6. Reglas de Negocio

### BR-001: Exigencia de Acta para Asignación
* **Regla:** El administrador no puede asignar un docente definitivo al emprendimiento hasta que el estudiante haya diligenciado y firmado el acta de confidencialidad[cite: 8].
* **Descripción:** Proceso de control jurídico del programa[cite: 8].
* **Procesos Afectados:** BP-001, BP-002.
* **Referencia:**[cite: 8].

### BR-002: Gestión Manual de Agenda (Gobernanza Administrativa)
* **Regla:** Se prohíbe la integración con calendarios externos (Google/Outlook) y el agendamiento libre por estudiantes; la plataforma alojará toda la lógica y los cruces serán confirmados manualmente por administración o el asesor[cite: 9].
* **Descripción:** Conserva el control restrictivo solicitado por la coordinación[cite: 9].
* **Procesos Afectados:** BP-002.
* **Referencia:**[cite: 9].

## 7. Experiencia de Usuario y Recorrido (User Journey)

**Flujo de Ingreso y Diagnóstico (Estudiante)**
1. **Inicio:** El estudiante se registra en la web e introduce el OTP recibido por correo[cite: 7].
2. **Acción Administrativa:** El Administrador, tras una charla, le habilita secciones de la plataforma[cite: 8].
3. **Caracterización:** El estudiante accede a su perfil y llena el formulario de valoración (preguntas de negocio)[cite: 8, 9].
4. **Respuesta del Sistema:** El sistema procesa los datos y presenta un diagnóstico gráfico (fortalezas y debilidades) sin tabulación manual[cite: 8, 9].
5. **Documentación:** El estudiante descarga, firma y sube el acta de confidencialidad[cite: 8].
6. **Resultado:** El Administrador ve los requisitos cumplidos y asocia el emprendimiento a un Docente en el módulo de Asignaciones[cite: 7, 8]. A partir de ahí, el estudiante visualiza a su mentor y las tareas del plan de trabajo[cite: 7].

## 8. Matriz de Trazabilidad

| Source ID | Necesidad del Usuario / Hallazgo | Proceso Relacionado | ID Requisito(s) | Tipo | Estado |
| --------- | ----------------------------- | ------------------------ | ----------------- | ---------------- | ------ |
|[cite: 7] | Verificación segura por correo OTP 8 dígitos | BP-001 | FR-001 | FR | Confirmado |
|[cite: 8, 9] | Eliminar tabulación manual de diagnóstico | BP-001 | FR-002 | FR | Confirmado |
|[cite: 8] | Subir acta de confidencialidad antes de asignar | BP-001 | FR-003, BR-001 | FR, BR | Confirmado |
|[cite: 9] | Control manual administrativo de agenda (sin calendarios externos) | BP-002 | FR-004, BR-002 | FR, BR | Confirmado |
|[cite: 7] | Notificaciones al recibir tareas o confirmar citas | BP-002, BP-003 | FR-005 | FR | Confirmado |
|[cite: 9] | Historial ligado a la idea de negocio (no al docente) | BP-003 | FR-006 | FR | Confirmado |
|[cite: 9] | Alertas por inactividad del estudiante | BP-003 | FR-007 | FR | Confirmado |
|[cite: 7] | Subida de evidencias de hasta 500MB | BP-003 | FR-008 | FR | Confirmado |
|[cite: 9] | Descarga de Excel/CSV como contingencia local | BP-003 | FR-009 | FR | Confirmado |
|[cite: 9] | Máximo 3 clics para acciones principales | N/A | NFR-001 | NFR | Confirmado |
|[cite: 7, 9] | Seguridad de roles y JWT estricta | N/A | NFR-002, NFR-003 | NFR | Confirmado |

## 9. Ambigüedades, Suposiciones y Preguntas Abiertas

| ID | Tipo | Descripción | Requisito Relacionado | Impacto | Recomendación |
| -- | ---- | ----------- | ---------------------- | ------ | ------------------------- |
| AQ-01 | Ambigüedad | **Tiempo exacto para semaforización:** Se menciona cambiar el estado "tras un periodo de tiempo", pero no se especifica la cantidad de días de inactividad requeridos[cite: 9]. | FR-007 | Medio | Validar con la Coordinadora el número exacto de días (ej. 15, 30 días) para activar la alerta. |
| AQ-02 | Ambigüedad | **Habilitación de plataforma:** Se menciona que el estudiante se registra pero espera una "reunión" para que se le habilite el resto de la plataforma[cite: 8]. | FR-001, FR-002 | Alto | Aclarar si esto será un control manual por parte del Admin (ej. botón "Habilitar Valoración" en la UI) tras confirmar que asistió a la reunión física. |

## 10. Revisión de Calidad de Requisitos

* **Correctitud y Consistencia:** Se alinearon los requerimientos conflictivos de los calendarios. Aunque en el "MOMENT 1" se sugirió integración con Google Calendar[cite: 9], el "MOMENT 2" dictaminó explícitamente que todo vivirá dentro de la plataforma sin integraciones externas[cite: 9]. La matriz refleja la decisión final.
* **Separación de Responsabilidades:** Se separaron estrictamente las reglas funcionales de negocio (como el diagnóstico) de los requisitos técnicos estructurales (JWT, Node.js, aislamientos por API)[cite: 7, 9].
* **Recomendación:** Definir en la etapa de planeación de Sprints los campos exactos del formulario de caracterización (Modelo de Negocio, Marketing, etc.) mencionados cualitativamente por Doris[cite: 8].

## 11. Resumen Ejecutivo de Requisitos

El proyecto SGEMD incluye **10 requisitos funcionales** principales y **4 requisitos no funcionales**[cite: 7, 8, 9]. Las áreas funcionales más críticas incluyen el diagnóstico automático de emprendimientos para ahorrar cargas administrativas (BP-001) y la consolidación de un expediente central e intransferible para los proyectos (BP-003)[cite: 8, 9]. 

Los requisitos de mayor prioridad se enfocan en la seguridad del control de datos (exportaciones a Excel, roles estrictos validados en el backend, firmas confidenciales)[cite: 7, 8, 9]. El principal riesgo a mitigar es la fricción en la usabilidad, por lo que el sistema exige un límite de tres clics para tareas básicas como adjuntar archivos y agendar, asegurando la adopción por todos los actores involucrados[cite: 9]. Como próximo paso, se requiere validar con el equipo de coordinación el tiempo exacto en días para activar el mecanismo de semaforización por inactividad[cite: 9].