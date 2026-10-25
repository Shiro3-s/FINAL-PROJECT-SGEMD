import type { CuentaEstado } from '@sgemd/shared';
import type { PoolClient } from 'pg';
import { assertTransition } from '../policy/accountTransitions.js';
import { AppError } from '../utils/AppError.js';
import { AUDIT_ACTIONS, audit } from './audit.js';
import { notify } from './notify.js';

/**
 * Aplicación de una transición de estado de cuenta **dentro de una transacción**.
 *
 * Vive en `services/` y no en `modules/users` porque la resuelve también la bandeja de
 * solicitudes: aprobar un desbloqueo es exactamente la misma transición
 * (`Limitado`/`Inactivo → Activo`) y debe dejar el mismo rastro, en la misma transacción
 * que la resolución de la solicitud. Duplicarla habría permitido que los dos caminos se
 * separaran con el tiempo.
 *
 * El llamador decide quién puede ejecutarla (hoy, solo el administrador) y si además hay
 * que avisar al titular: en la bandeja, la notificación de la solicitud ya lo hace.
 */
export interface AccountTransitionInput {
  usuarioId: number;
  to: CuentaEstado;
  /** Autor del cambio; queda en la auditoría. */
  actorId: number;
  ip?: string | null;
  /**
   * `false` omite la notificación de la cuenta. Se usa cuando otra notificación de la
   * misma transacción ya explica el hecho (resolución de una solicitud).
   */
  notifyAccount?: boolean;
}

export interface AccountTransitionResult {
  from: CuentaEstado;
  to: CuentaEstado;
  correoInstitucional: string;
  nombres: string;
}

type AccountRow = {
  estado: string;
  correo_institucional: string;
  nombres: string;
};

/**
 * Lee la fila **con bloqueo**, valida la transición, la aplica y escribe auditoría (y
 * notificación). El `SELECT … FOR UPDATE` serializa dos peticiones simultáneas sobre la
 * misma cuenta; el `UPDATE` condicionado por el estado leído es la segunda red.
 */
export async function applyAccountTransition(
  db: PoolClient,
  input: AccountTransitionInput,
): Promise<AccountTransitionResult> {
  const { rows } = await db.query<AccountRow>(
    `SELECT estado, correo_institucional, nombres
       FROM usuarios
      WHERE id_usuarios = $1 AND fecha_eliminacion IS NULL
      FOR UPDATE`,
    [input.usuarioId],
  );

  const row = rows[0];
  if (!row) {
    throw new AppError(404, 'NOT_FOUND', 'El usuario no existe.');
  }

  const from = row.estado as CuentaEstado;
  assertTransition(from, input.to);

  const { rowCount } = await db.query(
    'UPDATE usuarios SET estado = $3 WHERE id_usuarios = $1 AND estado = $2',
    [input.usuarioId, from, input.to],
  );

  if (rowCount === 0) {
    throw new AppError(
      422,
      'INVALID_STATE_TRANSITION',
      'La cuenta cambió de estado mientras se procesaba la solicitud. Vuelve a intentarlo.',
    );
  }

  await audit(db, {
    accion: AUDIT_ACTIONS.STATE_CHANGE,
    entidad: 'usuarios',
    entidadId: input.usuarioId,
    valorAnterior: { estado: from },
    valorNuevo: { estado: input.to },
    usuarioId: input.actorId,
    ip: input.ip ?? null,
  });

  if (input.notifyAccount !== false) {
    await notify(db, {
      usuarioId: input.usuarioId,
      tipo: 'Sistema',
      mensaje:
        input.to === 'Activo'
          ? 'Tu cuenta fue activada. Ya puedes usar los módulos de trabajo.'
          : 'Tu cuenta fue desactivada. Contacta a la coordinación del programa.',
      tipoObjeto: 'usuarios',
      objetoId: input.usuarioId,
    });
  }

  return {
    from,
    to: input.to,
    correoInstitucional: row.correo_institucional,
    nombres: row.nombres,
  };
}
