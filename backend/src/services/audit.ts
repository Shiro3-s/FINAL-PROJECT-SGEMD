import type { QueryResult, QueryResultRow } from 'pg';

/**
 * Escritura de auditoría (NFR-007). Se llama **dentro** de la misma transacción que el
 * cambio que describe, para que nunca exista un efecto sin su rastro ni al revés.
 */
export interface Queryable {
  query<R extends QueryResultRow = QueryResultRow>(
    text: string,
    params?: unknown[],
  ): Promise<QueryResult<R>>;
}

export interface AuditEntry {
  accion: string;
  entidad: string;
  entidadId?: number | null;
  valorAnterior?: unknown;
  valorNuevo?: unknown;
  usuarioId?: number | null;
  ip?: string | null;
}

/**
 * Acciones auditadas. La lista crecerá con cada módulo (P-4).
 *
 * No hay `CHECK` en `auditoria_eventos.accion`: el vocabulario se controla aquí y no en
 * el esquema, para no migrar la tabla cada vez que un módulo añade una acción.
 */
export const AUDIT_ACTIONS = {
  REGISTER: 'Registro',
  VERIFY_EMAIL: 'Verificación de correo',
  LOGIN: 'Inicio de sesión',
  PASSWORD_RESET: 'Cambio de contraseña',
  CREATE_USER: 'Alta de usuario',
  UPDATE_USER: 'Edición de usuario',
  DELETE_USER: 'Baja lógica de usuario',
  STATE_CHANGE: 'Cambio de estado de cuenta',
  REJECT_ACTIVATION: 'Rechazo de activación',
  CREATE_ENTREPRENEURSHIP: 'Alta de emprendimiento',
  UPDATE_ENTREPRENEURSHIP: 'Edición de emprendimiento',
  DELETE_ENTREPRENEURSHIP: 'Baja lógica de emprendimiento',
  APPROVE_ENTREPRENEURSHIP: 'Aprobación de emprendimiento',
  REJECT_ENTREPRENEURSHIP: 'Rechazo de emprendimiento',
  CREATE_REQUEST: 'Solicitud creada',
  APPROVE_REQUEST: 'Solicitud aprobada',
  REJECT_REQUEST: 'Solicitud rechazada',
  CREATE_ASSIGNMENT: 'Alta de asignación',
  UPDATE_ASSIGNMENT: 'Edición de asignación',
  DEACTIVATE_ASSIGNMENT: 'Baja de asignación',
  CREATE_TASK: 'Alta de tarea',
  UPDATE_TASK: 'Edición de tarea',
  SUBMIT_TASK: 'Entrega de tarea',
  GRADE_TASK: 'Calificación de tarea',
  RETURN_TASK: 'Devolución de tarea',
  DELETE_TASK: 'Baja lógica de tarea',
  CREATE_TRACING: 'Alta de seguimiento',
  UPDATE_TRACING: 'Edición de seguimiento',
  DELETE_TRACING: 'Baja lógica de seguimiento',
  UPLOAD_ATTACHMENT: 'Carga de evidencia',
  DELETE_ATTACHMENT: 'Baja lógica de evidencia',
  CREATE_ADVICE: 'Alta de asesoría',
  UPDATE_ADVICE: 'Edición de asesoría',
  ACCEPT_ADVICE: 'Confirmación de asesoría',
  REPROPOSE_ADVICE: 'Reprogramación de asesoría',
  REJECT_ADVICE: 'Cancelación de asesoría',
  DELETE_ADVICE: 'Baja lógica de asesoría',
  SAVE_DIAGNOSIS: 'Guardado de diagnóstico',
  SUBMIT_DIAGNOSIS: 'Envío de diagnóstico',
  UPLOAD_ACTA: 'Carga de acta',
  REVIEW_ACTA: 'Revisión de acta',
  CREATE_EVENT: 'Alta de evento',
  UPDATE_EVENT: 'Edición de evento',
  DELETE_EVENT: 'Baja lógica de evento',
  REGISTER_EVENT: 'Inscripción a evento',
  UNREGISTER_EVENT: 'Cancelación de inscripción a evento',
  RECOMMEND_EVENT: 'Recomendación de evento',
  UPDATE_SETTING: 'Cambio de configuración',
  CREATE_BACKUP: 'Alta de respaldo',
  VERIFY_BACKUP: 'Verificación de respaldo',
  DOWNLOAD_BACKUP: 'Descarga de respaldo',
  EXPORT_DATABASE: 'Exportación de base de datos',
  EXPORT_REPORT: 'Exportación de reporte',
  AUDIT_READ: 'Consulta de auditoría',
  AUDIT_EXPORT: 'Exportación de auditoría',
  RUN_INACTIVITY_JOB: 'Ejecución del job de inactividad',
  RUN_OVERDUE_JOB: 'Ejecución del job de tareas vencidas',
  AUTOMATIC_INACTIVITY: 'Inactividad automática',
  OVERDUE_TASK_NOTICE: 'Aviso de tarea vencida',
} as const;

export async function audit(db: Queryable, entry: AuditEntry): Promise<void> {
  await db.query(
    `INSERT INTO auditoria_eventos
       (accion, entidad, entidad_id, valor_anterior, valor_nuevo, usuarios_id_usuarios, ip)
     VALUES ($1, $2, $3, $4, $5, $6, $7)`,
    [
      entry.accion,
      entry.entidad,
      entry.entidadId ?? null,
      entry.valorAnterior === undefined ? null : JSON.stringify(entry.valorAnterior),
      entry.valorNuevo === undefined ? null : JSON.stringify(entry.valorNuevo),
      entry.usuarioId ?? null,
      entry.ip ?? null,
    ],
  );
}
