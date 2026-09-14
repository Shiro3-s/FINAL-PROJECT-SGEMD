# MOMENT 1

Estudiante (1): Buenos días, coordinadora. En el marco de nuestra investigación en el proyecto Quantum, hemos analizado su problemática en el Centro Progresa. Llevar la trazabilidad en Excel está causando cuellos de botella severos en la gestión. Proponemos migrar el proceso a una plataforma web autogestionable que elimine este trabajo manual.

Coordinadora (2): Buenos días. Agradezco el análisis, pero cambiar mi Excel por una web no es una solución mágica. Mi problema principal no es la herramienta en sí, sino que las personas no la alimentan. Si la plataforma requiere que yo o los asesores digitemos todo dos veces, va a fracasar antes del primer mes.

Estudiante (3): Justamente, la idea es trasladar esa responsabilidad operativa al emprendedor. Ellos deberán cargar sus avances obligatoriamente en la plataforma web para habilitar la solicitud de su asesoría. Usted ya no tendría que digitar datos, solo entraría a visualizar un panel de control con indicadores.

Coordinadora (4): Cuidado ahí. Si le ponemos demasiadas trabas a los estudiantes para pedir asesoría, la tasa de deserción se nos va a disparar. Ustedes asumen que el estudiante es sumamente proactivo, pero la realidad es que a muchos hay que impulsarlos. Si bloqueamos la agenda, perdemos a los emprendedores en etapas tempranas.

Estudiante (5): Entiendo ese riesgo. En lugar de un bloqueo estricto, la plataforma web podría usar un sistema de semaforización. Si un estudiante pide cita sin subir avances, el sistema le permite agendar, pero lo marca en rojo. Así el asesor sabe que debe dedicar esa sesión a nivelarlo, y usted obtiene la métrica exacta de quiénes están fallando en autonomía.

Coordinadora (6): Me parece mucho más realista el enfoque del semáforo. Pero eso nos lleva a la gestión del agendamiento. Hoy cruzar los horarios de múltiples asesores con decenas de estudiantes es un rompecabezas que armo manualmente. ¿Cómo automatiza esto la web sin que se generen huecos o citas cruzadas?

Estudiante (7): Los asesores tendrán un módulo donde sincronizan su disponibilidad. El estudiante entra a su perfil, visualiza los bloques verdes y agenda. La plataforma se encarga del emparejamiento y genera el enlace o confirma el espacio físico de forma automática.

Coordinadora (8): Hay un fallo en ese diseño. Mis asesores tienen horarios dinámicos que cambian cada semana. Si se les olvida actualizar su disponibilidad en la plataforma web, el estudiante agendará en un horario fantasma y se quedará esperando. Por eso en mi Excel yo confirmo personalmente cada cita.

Estudiante (9): Es un punto crítico. Lo solucionaremos conectando la plataforma web directamente con el calendario institucional (Google Calendar o Outlook) del asesor. Si el asesor recibe una invitación a una reunión o clase, ese bloque desaparece instantáneamente del portal web del emprendedor.

Coordinadora (10): Esa integración en tiempo real es absolutamente obligatoria; si no la tiene, el sistema es inviable. Otro tema espinoso: la trazabilidad a largo plazo. Actualmente, cuando un chico cambia de semestre o rota de asesor, la historia de su modelo de negocio se pierde y el nuevo asesor tiene que arrancar de cero.

Estudiante (11): La plataforma web resolverá eso creando un "Expediente Central del Proyecto". La información no estará anclada al perfil del asesor, sino a la idea de negocio. Cualquier asesor nuevo que asuma el caso podrá revisar la bitácora histórica, notas previas y los documentos para entender el contexto exacto.

Coordinadora (12): Suena excelente para el seguimiento, pero me genera pánico el tema de la confidencialidad. Aquí manejamos modelos financieros y validaciones de mercado. Mi Excel vive localmente en un entorno seguro. Si subimos todo a una plataforma web, nos exponemos a graves problemas si hay una filtración de información.

Estudiante (13): La seguridad es prioritaria. El despliegue de la base de datos contará con encriptación y estará alojado en servidores con normativas de protección de datos. Además, la arquitectura de permisos será estricta: un emprendedor solo ve lo suyo, el asesor solo ve sus proyectos asignados, y usted tiene la vista global.

Coordinadora (14): Tendrán que validar esa arquitectura con el departamento de TI. Pero tengo otra preocupación: ¿qué pasa cuando la web falla? Las plataformas se caen. Si el sistema colapsa en la semana de cierres de métricas, toda la operación del Centro Progresa se paraliza y yo me quedo a ciegas.

Estudiante (15): Implementaremos backups (copias de seguridad) diarios automatizados. Adicionalmente, crearemos un módulo en su perfil de coordinadora para que pueda exportar toda la base de datos a un archivo formato CSV o Excel con un solo clic. Si la web llega a fallar, usted tendrá su respaldo local para no detener la operación.

Coordinadora (16): Que me permitan descargar mis datos de vuelta a Excel como plan de contingencia me da mucha tranquilidad. ¿Y respecto a los reportes directivos? Hoy paso días enteros filtrando celdas para entregarle indicadores de impacto a la institución.

Estudiante (17): Ese será el principal valor agregado de la web para su cargo. Tendrá un dashboard analítico en tiempo real. Podrá descargar informes en PDF o generar gráficas sobre retención, número de emprendimientos activos y efectividad de asesores directamente desde el sistema, ahorrándole esos días de trabajo.

Coordinadora (18): Todo esto resolvería gran parte del desgaste administrativo. Sin embargo, tengo una última condición, y no es negociable: la simplicidad. Si la interfaz tiene más de tres clics para agendar o subir un archivo, ni los estudiantes ni los asesores la usarán, y yo no tengo tiempo para ser la mesa de ayuda técnica de nadie.

Estudiante (19): Nos enfocaremos cien por ciento en la usabilidad. Utilizaremos un diseño centrado en el usuario con menús mínimos. Antes de programar la versión final, haremos pruebas piloto de los prototipos iniciales con sus asesores menos tecnológicos para ajustar cualquier fricción en la navegación.

Coordinadora (20): Ese es el trato. Hagan la prueba piloto del entorno web con ellos. Si ellos logran completar un ciclo completo de seguimiento sin llamarme a preguntar cómo funciona, tendrán luz verde para implementar toda la plataforma en el Centro Progresa.

# MOMENT 2

Estudiante (1): Hola, Coordinadora. Basado en el levantamiento de información previo, hemos ajustado la arquitectura de la plataforma web. Entendemos que su proceso actual es secuencial y estricto: el estudiante se registra, usted hace una reunión de socialización, luego se le habilita el formulario de caracterización, el sistema arroja el diagnóstico, firman el acta de confidencialidad y, finalmente, se le asigna el asesor.

Coordinadora (2): Exactamente, ese flujo no se puede alterar porque es el procedimiento oficial del Centro Progresa. Mi preocupación ahora es la implementación. ¿Cómo asegurar que los asesores y emprendedores adopten la nueva plataforma web y no la perciban como una carga administrativa adicional a lo que ya hacíamos en Excel y correos?

Estudiante (3): La transición será progresiva. No vamos a imponer el sistema de un día para otro. Esto vendrá acompañado de jornadas de capacitación en las que se les mostrará cómo usar la plataforma y, sobre todo, las utilidades que les ahorrarán tiempo en su día a día.

Coordinadora (4): Eso es fundamental. Porque actualmente, al depender de Excel para tabular el formulario de caracterización y las secciones del modelo de negocio, se pierde mucho tiempo. ¿Cómo nos va a ayudar exactamente la plataforma con las métricas que hoy en día terminan ralentizando los proyectos por falta de feedback rápido?

Estudiante (5): Al digitalizar el formulario de valoración (modelo de negocio, marketing, financiero, etc.), el sistema calculará automáticamente las métricas. Se elimina el error manual de tabulación y el estudiante recibe un diagnóstico casi inmediato en su pantalla sobre sus fortalezas y debilidades, sin que usted tenga que cruzar esos datos a mano.

Coordinadora (6): Eso me quitaría una carga inmensa. Ahora, hablemos del agendamiento de las asesorías. He visto sistemas donde el estudiante escoge la hora libremente. El horario y flujo automático no está permitido aquí; nos gusta un sistema más restrictivo en el que el agendamiento se gestione directamente por nosotros en el área administrativa.

Estudiante (7): Comprendido. No habrá flujo automático para las citas. La plataforma tendrá un módulo de gestión donde usted (como administradora) tendrá el control total para aprobar, cruzar y asignar manualmente los espacios entre los estudiantes y los docentes, manteniendo la restricción que requieren.

Coordinadora (8): Perfecto, yo debo tener el control. Y hablando de control, ¿cómo vamos a manejar lo que cada persona puede ver? Porque el estudiante no debe ver los diagnósticos de otros, y el asesor no necesita ver a todos los emprendedores de la universidad.

Estudiante (9): Manejaremos tres niveles de permisos muy claros. Usted, como Coordinadora, tendrá permisos para visualizar absolutamente toda la información: estudiantes, asesores, gestión de asesorías y el seguimiento global de los proyectos.

Coordinadora (10): ¿Y los asesores y estudiantes?

Estudiante (11): Los asesores podrán visualizar solo a los estudiantes y proyectos que usted les asigne, junto con las citas de asesoría correspondientes. Por su parte, el estudiante solo podrá visualizar su propio perfil, su proyecto, las observaciones recibidas y un bloque exclusivo con sus asesorías y anotaciones.

Coordinadora (12): Muy bien, roles aislados. Volviendo al tema de mi gestión manual de la agenda de los asesores, ¿de qué manera la plataforma web se integrará con los calendarios o sistemas de información que los docentes ya utilizan hoy para evitar cruces de agenda?

Estudiante (13): Analizamos esa posibilidad, pero no se realizará ninguna integración externa debido a que actualmente no existe dicho sistema de información unificado para los docentes. Todo el seguimiento y asignación de tiempos vivirá exclusivamente dentro de nuestra plataforma.

Coordinadora (14): Entiendo, lo manejaremos de forma interna. Ahora, un punto crítico: los datos. Como vio en la transcripción, nosotros manejamos el "acta de confidencialidad". ¿Cómo se garantizará la confidencialidad, seguridad y respaldo de los datos de los proyectos alojados en la nube?

Estudiante (15): Estableceremos un sistema de gobernanza de datos, explicando claramente las métricas y accesos para cada rol. A nivel técnico, añadiremos métodos como JWT para garantizar la seguridad de contraseñas y códigos de acceso. Además, el acceso directo a la base de datos estará restringido; usaremos una API en el backend para validar las reglas de autorización antes de cualquier consulta.

Coordinadora (16): Me da tranquilidad saber que la información de los emprendimientos estará blindada. Cambiando de tema, actualmente me cuesta identificar a simple vista en mis sábanas de Excel quién dejó de asistir. ¿Qué tipo de alertas o semaforización tendrá el sistema para identificar a emprendedores inactivos o rezagados?

Estudiante (17): Estableceremos un tiempo definido (por ejemplo, X días sin registrar actividad o asesorías). Una vez cumplido ese plazo, el sistema colocará automáticamente al estudiante en un estado específico. Así, usted solo tendrá que filtrar su lista por ese estado y podrá comunicarse con ellos rápidamente.

Coordinadora (18): Muy útil. Y cuando logre reengancharlos, a veces necesitan cambiar de profesor porque su proyecto evolucionó. ¿Cómo facilita la plataforma que el historial del diagnóstico inicial y las asesorías previas no se pierdan al cambiar de asesor a mitad de semestre?

Estudiante (19): El diseño de la base de datos ancla el historial al "Proyecto" y no al asesor. De hecho, el estudiante puede tener varios asesores (docentes) asignados que le ayudan a enriquecer su emprendimiento. La información centralizada siempre estará disponible para cualquier docente nuevo que ingrese al caso.

Coordinadora (20): Eso soluciona muchos vacíos de comunicación. Sin embargo, depender 100% de la web me asusta. ¿Cuál es el plan de contingencia técnico si la plataforma sufre una caída de servidores durante nuestras semanas críticas de revisión de proyectos?

Estudiante (21): El sistema podrá controlarse mediante sus debidas copias de seguridad periódicas. En caso de una caída del servidor, la información estará respaldada y los estudiantes tendrán instrucciones claras para comunicarse con usted a través de los canales institucionales de contingencia mientras se restablece el servicio.

Coordinadora (22): De acuerdo. Finalmente, para que yo no termine convirtiéndome en soporte técnico de los estudiantes cuando intenten ver su diagnóstico o subir su acta de confidencialidad, ¿cómo garantizamos que el sistema sea fácil de usar para ellos?

Estudiante (23): Ya tenemos un boceto (UX/UI) de cómo será el acceso de los estudiantes a los diversos servicios. La interfaz está diseñada de forma muy limpia e intuitiva para permitirles ver su seguimiento de forma autogestionada, e incluye secciones de ayuda integradas para que no requieran soporte técnico constante de su parte.

Coordinadora (24): Si el sistema respeta el flujo de validación que realizo tras la primera reunión y me otorga el control total del agendamiento con estas medidas de seguridad, creo que tenemos una solución viable. Pueden avanzar con la plataforma.
