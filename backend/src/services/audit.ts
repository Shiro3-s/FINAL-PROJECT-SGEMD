/**
 * Escritura de auditoría (NFR-007). Se llama **dentro** de la misma transacción que el
 * cambio que describe, para que nunca exista un efecto sin su rastro ni al revés.
 */
export interface Queryable {
  query(text: string, params?: unknown[]): Promise<unknown>;
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
