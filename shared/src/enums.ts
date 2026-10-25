/**
 * Cadenas canónicas del sistema.
 *
 * Fuente: `MASTER_IMPLEMENTATION_PROMPT.md` §7.2 y la tabla de enumeraciones de
 * `docs/diagrama-clases.md` v2. Se declaran UNA sola vez aquí; el backend las usa en los
 * `CHECK` de `schema.sql` (verificado por script) y el frontend en `stateMap.ts`.
 *
 * Español con tildes, exactamente como las muestra la interfaz. No renombrar.
 */

export const CUENTA_ESTADOS = ['Limitado', 'Activo', 'Inactivo'] as const;
export type CuentaEstado = (typeof CUENTA_ESTADOS)[number];

export const NIVELES_ACADEMICOS = ['Pregrado', 'Posgrado', 'Egresado'] as const;
export type NivelAcademico = (typeof NIVELES_ACADEMICOS)[number];

export const EMPRENDIMIENTO_ESTADOS = ['Pendiente', 'Aprobado', 'Rechazado'] as const;
export type EmprendimientoEstado = (typeof EMPRENDIMIENTO_ESTADOS)[number];

export const ASIGNACION_ESTADOS = ['activa', 'inactiva'] as const;
export type AsignacionEstado = (typeof ASIGNACION_ESTADOS)[number];

export const SEGUIMIENTO_TIPOS = ['Avance de fase', 'Comentario'] as const;
export type SeguimientoTipo = (typeof SEGUIMIENTO_TIPOS)[number];

export const TAREA_ESTADOS = [
  'Pendiente',
  'En curso',
  'En revisión',
  'Completada',
  'Vencida',
  'Devuelta',
] as const;
export type TareaEstado = (typeof TAREA_ESTADOS)[number];

export const PRIORIDADES = ['Alta', 'Media', 'Baja'] as const;
export type Prioridad = (typeof PRIORIDADES)[number];

export const REVISION_ESTADOS = ['Pendiente', 'En revisión', 'Calificada', 'Devuelta'] as const;
export type RevisionEstado = (typeof REVISION_ESTADOS)[number];

export const ASESORIA_ESTADOS = [
  'Por agendar',
  'Programada',
  'Confirmada',
  'En curso',
  'Completada',
  'Cancelada',
] as const;
export type AsesoriaEstado = (typeof ASESORIA_ESTADOS)[number];

/**
 * Etiqueta de FILTRO del listado docente: agrupa Programada + Confirmada + En curso.
 * Nunca es un estado almacenado (master §7.2).
 */
export const ASESORIA_FILTRO_AGENDADA = ['Programada', 'Confirmada', 'En curso'] as const;

export const ACTA_ESTADOS = ['Pendiente', 'En revisión', 'Aprobada', 'Rechazada'] as const;
export type ActaEstado = (typeof ACTA_ESTADOS)[number];

export const DIAGNOSTICO_ESTADOS = ['En progreso', 'Enviado', 'Revisado'] as const;
export type DiagnosticoEstado = (typeof DIAGNOSTICO_ESTADOS)[number];

export const VALORACION_BANDAS = ['90-100', '70-89', '50-69', '<50'] as const;
export type ValoracionBanda = (typeof VALORACION_BANDAS)[number];

export const EVENTO_ESTADOS = ['Pendiente', 'Aprobado', 'Rechazado', 'Publicado'] as const;
export type EventoEstado = (typeof EVENTO_ESTADOS)[number];

export const SOLICITUD_TIPOS = ['Desbloqueo', 'Paralelo', 'Cita'] as const;
export type SolicitudTipo = (typeof SOLICITUD_TIPOS)[number];

export const SOLICITUD_ESTADOS = ['Pendiente', 'Aprobada', 'Rechazada'] as const;
export type SolicitudEstado = (typeof SOLICITUD_ESTADOS)[number];

export const RESPALDO_TIPOS = ['Completo', 'Parcial'] as const;
export type RespaldoTipo = (typeof RESPALDO_TIPOS)[number];

export const RESPALDO_ESTADOS = ['Exitosa', 'Fallida'] as const;
export type RespaldoEstado = (typeof RESPALDO_ESTADOS)[number];

/**
 * Valores del diagrama de clases v2. No figuran en el master §7.2: se registran como
 * inferidos en `docs/decisions.md` (P-5).
 */
export const NOTIFICACION_TIPOS = [
  'Tarea',
  'Asesoría',
  'Seguimiento',
  'Solicitud',
  'Diagnóstico',
  'Evento',
  'Sistema',
] as const;
export type NotificacionTipo = (typeof NOTIFICACION_TIPOS)[number];

/**
 * Necesario para el token de recuperación de contraseña (T39). Inferido: el master no
 * tiene otra tabla de tokens (P-6).
 */
export const CODIGO_PROPOSITOS = ['Verificación', 'Recuperación'] as const;
export type CodigoProposito = (typeof CODIGO_PROPOSITOS)[number];

/** Roles del catálogo `roles`. El 4 (Auditor) es P2. */
export const ROLES = {
  ADMIN: 1,
  ESTUDIANTE: 2,
  DOCENTE: 3,
  AUDITOR: 4,
} as const;
export type RolId = (typeof ROLES)[keyof typeof ROLES];

/**
 * Catálogos de solo lectura. Los valores son los canónicos del master §13.1 y del
 * diagrama de clases; el seed debe usar exactamente estas cadenas.
 */
export const CATALOGO_ROLES = ['Admin', 'Estudiante', 'Docente', 'Auditor'] as const;
export const CATALOGO_TIPO_DOCUMENTO = ['CC', 'TI', 'CE'] as const;
export const CATALOGO_CENTRO_UNIVERSITARIO = ['Sede Norte', 'Sede Centro', 'Sede Sur'] as const;
export const CATALOGO_TIPO_USUARIO = [
  'Estudiante',
  'Egresado',
  'Docente',
  'Administrativo',
] as const;
export const CATALOGO_ETAPA_EMPRENDIMIENTO = [
  'FASE 1 - Ideación',
  'FASE 2 - Prototipo',
  'FASE 3 - Validación',
  'FASE 4 - Formalización',
] as const;
export const CATALOGO_FASE_PLAN = [
  'FASE 1 Ideación y priorización de ideas',
  'FASE 2 Estructuración y ejecución',
  'FASE 3 Consolidación del proceso',
  'FASE 4 Escalamiento',
] as const;
export const CATALOGO_SECTOR_ECONOMICO = [
  'Alimentos',
  'Moda',
  'Ambiental',
  'Muebles',
  'Tecnología',
  'Comercio',
] as const;
export const CATALOGO_MODALIDAD = ['Presencial', 'Virtual', 'Mixta'] as const;
export const CATALOGO_TIPO_EVENTO = [
  'Startup',
  'Capacitación',
  'Asesoría grupal',
  'Showroom',
  'Taller',
] as const;
export const CATALOGO_MODULOS = [
  'Perfil',
  'Emprendimiento',
  'Diagnóstico',
  'Tareas',
  'Asesorías',
  'Seguimiento',
  'Eventos',
  'Reportes',
] as const;
