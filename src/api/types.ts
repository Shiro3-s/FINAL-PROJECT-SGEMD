import type {
  ActaEstado,
  AsesoriaEstado,
  CuentaEstado,
  DiagnosticoEstado,
  EmprendimientoEstado,
  EventoEstado,
  NivelAcademico,
  Prioridad,
  RevisionEstado,
  SeguimientoTipo,
  SolicitudEstado,
  SolicitudTipo,
  TareaEstado,
} from '@sgemd/shared';

/**
 * Tipos de la API que usa más de un módulo.
 *
 * El backend no publica sus `zod` en `shared/`, así que los DTO de lectura se
 * declaran aquí y se contrastan con `docs/api.md`. Las cadenas de estado NUNCA se
 * escriben a mano en un componente: vienen de `@sgemd/shared` o de estos tipos,
 * que a su vez las toman de allí.
 */

export type RoleKey = 'estudiante' | 'docente' | 'administrador';

export interface RoleRef {
  id: number;
  nombre: string;
}

/** Forma de `GET /api/users/me` y del `usuario` del login. */
export interface SessionUser {
  id: number;
  codigo: string;
  nombres: string;
  apellidos: string;
  correoInstitucional: string;
  numeroDocumento: string | null;
  tipoDocumentoId: number | null;
  nivelAcademico: NivelAcademico | null;
  programaAcademicoId: number | null;
  centroUniversitarioId: number | null;
  municipioId: number | null;
  tipoPoblacionId: number | null;
  tipoUsuarioId: number | null;
  verificado: boolean;
  estado: CuentaEstado;
  rol: RoleRef;
  ultimaActividad: string | null;
}

/** Usuario resumido que aparece dentro de otras entidades. */
export interface UserSummary {
  id: number;
  codigo: string;
  nombres: string;
  apellidos: string;
  correoInstitucional?: string;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface CatalogItem {
  id: number;
  nombre: string;
}

export interface MunicipalityItem extends CatalogItem {
  departamento: string;
}

export interface DateTimeItem extends CatalogItem {
  fecha: string;
  horaInicio: string;
  horaFin: string;
}

export interface NotificationItem {
  id: number;
  tipo: string;
  mensaje: string;
  url: string | null;
  tipoObjeto: string | null;
  objetoId: number | null;
  leida: boolean;
  fecha: string;
}

/** Cuerpo del evento SSE `notification` (§T21: sin el texto del aviso). */
export interface NotificationEventPayload {
  notificationId: number;
  tipo: string;
  unreadCount: number;
}

export interface Attachment {
  id: number;
  nombreArchivo: string;
  tamanoBytes: number;
  tipoMime: string;
  fechaSubida: string;
  subidoPor: { id: number; nombres: string; apellidos: string } | null;
  entidad: 'task' | 'tracing' | 'advice' | 'acta';
  entidadId: number;
}

/** Resultado de una descarga (`Content-Disposition` resuelto por el cliente). */
export interface DownloadedFile {
  blob: Blob;
  filename: string;
}

const ROLE_KEY_BY_NAME: Record<string, RoleKey> = {
  Estudiante: 'estudiante',
  Docente: 'docente',
  Admin: 'administrador',
};

/**
 * Traduce el rol del servidor a la clave de navegación. Devuelve `null` para
 * Auditor (P2): la SPA no tiene pantallas para ese rol y no debe inventarlas.
 */
export function roleKeyOf(user: Pick<SessionUser, 'rol'> | null | undefined): RoleKey | null {
  if (!user) return null;
  return ROLE_KEY_BY_NAME[user.rol.nombre] ?? null;
}

/** `Ana María Prueba` → `AP`, como el avatar del prototipo. */
export function initialsOf(user: Pick<SessionUser, 'nombres' | 'apellidos'>): string {
  return `${user.nombres.charAt(0)}${user.apellidos.charAt(0)}`.toUpperCase();
}

export function fullNameOf(user: Pick<SessionUser, 'nombres' | 'apellidos'>): string {
  return `${user.nombres} ${user.apellidos}`.trim();
}


// --- Entidades de trabajo -----------------------------------------------------
// Formas tomadas de `docs/api.md`. No se inventan campos: si la API no lo
// devuelve, no existe en el DTO.

export interface EntityRef {
  id: number;
  codigo: string;
  nombre: string;
  estadoAprobacion?: EmprendimientoEstado;
}

export interface StudentRef {
  id: number;
  codigo?: string;
  nombres: string;
  apellidos: string;
  correoInstitucional?: string;
}

export interface TeacherRef {
  id: number;
  codigo?: string;
  nombres: string;
  apellidos: string;
  correoInstitucional?: string;
}

export interface Entrepreneurship {
  id: number;
  codigo: string;
  nombre: string;
  descripcion: string | null;
  redesSociales: string | null;
  estadoAprobacion: EmprendimientoEstado;
  motivoRechazo: string | null;
  esParalelo: boolean;
  avance: number;
  etapa: CatalogItem | null;
  sector: CatalogItem | null;
  centroUniversitario: CatalogItem | null;
  estudiante: StudentRef;
}

export interface Task {
  id: number;
  titulo: string;
  descripcion: string | null;
  fechaLimite: string | null;
  prioridad: Prioridad;
  puntos: number;
  estado: TareaEstado;
  vencida: boolean;
  puntajeObtenido: number | null;
  retroalimentacion: string | null;
  estadoRevision: RevisionEstado;
  evidenciaRequerida: boolean;
  motivoDevolucion: string | null;
  observacionesDevolucion: string | null;
  evidencias: number;
  fechaEnvio: string | null;
  emprendimiento: EntityRef;
  estudiante: StudentRef;
  creador: Pick<StudentRef, 'id' | 'nombres' | 'apellidos'>;
  fase: CatalogItem | null;
}

export interface Tracing {
  id: number;
  descripcion: string;
  tipo: SeguimientoTipo;
  puntaje: number | null;
  estadoRevision: RevisionEstado;
  fechaSeguimiento: string;
  retroalimentacion: string | null;
  evidencias: number;
  emprendimiento: EntityRef;
  autor: Pick<StudentRef, 'id' | 'nombres' | 'apellidos'> | null;
  fase: CatalogItem | null;
}

export interface Advice {
  id: number;
  codigo: string;
  tema: string;
  estado: AsesoriaEstado;
  fecha: string | null;
  horaInicio: string | null;
  horaFin: string | null;
  fechaAsesoria: string | null;
  lugarEnlace: string | null;
  modalidad: CatalogItem | null;
  emprendimiento: EntityRef;
  estudiante: StudentRef;
  /** La API la deja en `null` mientras la coordinación no fija docente. */
  docente: TeacherRef | null;
  evidencias: number;
}

export interface DiagnosisAnswer {
  id: number;
  seccion: number;
  orden: number;
  enunciado: string;
  tipo: string;
  opciones: string[];
  valor: string | null;
}

export interface DiagnosisQuestion {
  id: number;
  seccion: number;
  orden: number;
  enunciado: string;
  tipo: string;
  opciones: string[];
}

export interface DiagnosisForm {
  total: number;
  secciones: { numero: number; titulo: string }[];
  preguntas: DiagnosisQuestion[];
}

export interface DiagnosisScore {
  disponible: boolean;
  motivo: string;
  mensaje: string;
}

export interface Diagnosis {
  id: number;
  estado: DiagnosticoEstado;
  fechaDiagnostico: string;
  puntajeTotal: number | null;
  urlInforme: string | null;
  emprendimiento: EntityRef;
  estudiante: StudentRef;
  respuestas: DiagnosisAnswer[];
  totalPreguntas: number;
  respondidas: number;
  puntuacion: DiagnosisScore;
}

export interface CharacterizationSection {
  numero: number;
  titulo: string;
  respondidas: number;
  total: number;
  puntaje: number | null;
}

export interface Characterization {
  diagnosticoId: number;
  estado: DiagnosticoEstado;
  emprendimiento: EntityRef;
  respondidas: number;
  totalPreguntas: number;
  puntuacion: DiagnosisScore;
  secciones: CharacterizationSection[];
  valoracion: unknown[];
}

export interface EventItem {
  id: number;
  nombreEvento: string;
  descripcion: string | null;
  dirigidoA: string | null;
  capacidadMaxima: number | null;
  cupo: number | null;
  estado: EventoEstado;
  requiereRegistro: boolean;
  lugar: string | null;
  enlace: string | null;
  tipoEvento: CatalogItem | null;
  modalidad: CatalogItem | null;
  fecha: string | null;
  horaInicio: string | null;
  horaFin: string | null;
  organizador: Pick<StudentRef, 'id' | 'nombres' | 'apellidos'>;
  inscritos: number;
  inscrito: boolean;
}

export interface EventRecommendation {
  id: number;
  mensaje: string | null;
  estado: string;
  fecha: string;
  evento: { id: number; nombreEvento: string };
  emprendimiento: EntityRef;
  estudiante: StudentRef;
  docente: TeacherRef;
}

export interface Acta {
  id: number;
  estado: ActaEstado;
  observaciones: string | null;
  fechaCarga: string | null;
  fechaRevision: string | null;
  emprendimiento: EntityRef;
  estudiante: StudentRef;
  revisor: Pick<StudentRef, 'id' | 'nombres' | 'apellidos'> | null;
  adjunto: Attachment | null;
}

export interface RequestItem {
  id: number;
  tipo: SolicitudTipo;
  detalle: string | null;
  estado: SolicitudEstado;
  motivoRechazo: string | null;
  fechaSolicitud: string;
  fechaResolucion: string | null;
  solicitante: StudentRef;
  emprendimiento: EntityRef | null;
  resueltoPor: Pick<StudentRef, 'id' | 'nombres' | 'apellidos'> | null;
}

export interface Assignment {
  id: number;
  fechaAsignacion: string;
  estado: 'activa' | 'inactiva';
  horasSemanales: number;
  mentor: TeacherRef;
  estudiante: StudentRef;
  emprendimiento: EntityRef;
}

export interface PendingRequests {
  total: number;
  Desbloqueo: number;
  Paralelo: number;
  Cita: number;
}

export interface RequestPage extends Paginated<RequestItem> {
  pendientes: PendingRequests;
}

// --- Tableros ----------------------------------------------------------------
export interface AgendaItem {
  tipo: string;
  titulo: string;
  fecha: string;
  hora: string | null;
  detalle: string | null;
}

export interface ActivityItem {
  id: number;
  accion: string;
  entidad: string;
  entidadId: number | null;
  detalle: string | null;
  fecha: string;
  actor: string | null;
}

export interface StudentDashboard {
  emprendimiento: {
    id: number;
    codigo: string;
    nombre: string;
    estadoAprobacion: EmprendimientoEstado;
    avance: number;
    etapa: string | null;
  } | null;
  /**
   * El tablero solo informa si existe el diagnóstico y en qué estado está: no
   * trae puntaje ni número de respuestas porque la rúbrica sigue sin aprobar
   * (AQ-09). El detalle se lee en `/diagnosis/me`.
   */
  diagnostico: { id: number; estado: DiagnosticoEstado } | null;
  acta: { id: number; estado: ActaEstado } | null;
  tareas: {
    total: number;
    completadas: number;
    pendientes: number;
    vencidas: number;
    enRevision: number;
  };
  asesorias: { realizadas: number; proximas: number };
  fases: {
    faseId: number | null;
    fase: string | null;
    total: number;
    completadas: number;
    porcentaje: number;
  }[];
  /** Próximas sesiones ya agendadas, en el mismo formato de agenda del docente. */
  proximasAsesorias: AgendaItem[];
  tareasPorCompletar: {
    id: number;
    titulo: string;
    prioridad: Prioridad;
    fechaLimite: string | null;
    vencida: boolean;
  }[];
  eventos: {
    id: number;
    nombre: string;
    fecha: string | null;
    hora: string | null;
    lugar: string | null;
  }[];
  notificacionesSinLeer: number;
}

export interface TeacherDashboard {
  emprendimientos: number;
  avancePromedio: number;
  tareasPorRevisar: number;
  tareasAltaPrioridad: number;
  avancesRegistrados: number;
  avancesConEvidencia: number;
  asesorias: { agendadas: number; porAgendar: number; completadas: number; proxima: AgendaItem | null };
  avancePorEmprendimiento: {
    id: number;
    codigo: string;
    nombre: string;
    avance: number;
    estudiante: string;
  }[];
  agenda: AgendaItem[];
  actividadReciente: ActivityItem[];
}

export interface AdminDashboard {
  usuariosActivos: number;
  emprendimientos: number;
  tareas: number;
  avancePromedio: number;
  solicitudesPendientes: number;
  alertas: {
    sinDocente: number;
    diagnosticosSinRevisar: number;
    tareasVencidas: number;
    eventosPendientes: number;
    actasEnRevision: number;
  };
  avancePorMes: { mes: string; etiqueta: string; avances: number; promedio: number | null }[];
  porSede: { nombre: string; total: number }[];
  porSector: { nombre: string; total: number }[];
  agenda: AgendaItem[];
  actividadReciente: ActivityItem[];
}

// --- Administración ----------------------------------------------------------
export interface ReportCatalogItem {
  id: string;
  nombre: string;
  descripcion: string;
  formatos: string[];
  /** `true` si el reporte acepta el filtro `desde`/`hasta`. */
  periodo: boolean;
  filtroDocente: boolean;
  columnas: { key: string; header: string }[];
  ultimaGeneracion: string | null;
}

export interface SettingItem {
  clave: string;
  valor: string | null;
  tipoDato: 'int' | 'bool' | 'text' | 'date';
  descripcion: string | null;
  actualizadoPor: { id: number; nombres: string; apellidos: string } | null;
  fechaActualizacion: string | null;
}

export interface AuditEntry {
  id: number;
  accion: string;
  entidad: string;
  entidadId: number | null;
  /** JSON ya saneado por el servidor; se pinta como texto, nunca como objeto. */
  valorAnterior: unknown;
  valorNuevo: unknown;
  fecha: string;
  ip: string | null;
  actor: { id: number; nombres: string; apellidos: string } | null;
}

export interface Backup {
  id: number;
  codigo: string;
  tipo: 'Completo' | 'Parcial';
  fechaHora: string;
  tamanoLogicoMb: number | null;
  tamanoAnadidoMb: number | null;
  estado: 'Exitosa' | 'Fallida';
  destino: string | null;
  retencionDias: number | null;
  checksumManifiesto: string | null;
  ejecutadoPor: { id: number; nombres: string; apellidos: string } | null;
  artefactos: { dump: boolean; snapshot: boolean };
}

export interface BackupPanel {
  motor: 'rsync' | 'link';
  retencionDias: number;
  respaldosEnDisco: number;
}
