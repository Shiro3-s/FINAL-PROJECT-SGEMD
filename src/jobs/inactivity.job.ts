import { query, withTransaction } from '../db/pool.js';
import { AUDIT_ACTIONS, audit } from '../services/audit.js';
import { notify } from '../services/notify.js';
import { settingInt } from '../services/programSettings.js';

/**
 * Inactividad automática (FR-007, BR-005, T14).
 *
 * Un estudiante `Activo` que lleva `inactividad_dias` (90 por defecto) sin actividad pasa a
 * `Inactivo`. La reactivación es manual y solo del administrador. El job es idempotente: la
 * segunda ejecución no encuentra filas y deja un registro de la corrida con 0 afectados.
 *
 * `ultima_actividad` nula no se marca: la tabla no guarda la fecha de creación, así que no
 * hay forma honesta de medir «90 días sin actividad» (P-46).
 */
export interface InactivityRun {
  umbralDias: number;
  afectados: number[];
  ejecutadoEn: string;
}

export async function runInactivityJob(): Promise<InactivityRun> {
  const umbralDias = await settingInt({ query }, 'inactividad_dias', 90);

  return withTransaction(async (db) => {
    const { rows } = await db.query<{
      id_usuarios: number;
      codigo: string;
      nombres: string;
      apellidos: string;
    }>(
      `UPDATE usuarios
          SET estado = 'Inactivo'
        WHERE estado = 'Activo'
          AND roles_id_roles = 2
          AND fecha_eliminacion IS NULL
          AND ultima_actividad IS NOT NULL
          AND ultima_actividad < now() - ($1 || ' days')::interval
        RETURNING id_usuarios, codigo, nombres, apellidos`,
      [umbralDias],
    );

    for (const user of rows) {
      await audit(db, {
        accion: AUDIT_ACTIONS.AUTOMATIC_INACTIVITY,
        entidad: 'usuarios',
        entidadId: user.id_usuarios,
        valorAnterior: { estado: 'Activo' },
        valorNuevo: { estado: 'Inactivo', motivo: `Sin actividad por ${umbralDias} días` },
        usuarioId: null,
        ip: null,
      });

      await notify(db, {
        usuarioId: user.id_usuarios,
        tipo: 'Sistema',
        mensaje:
          `Tu cuenta pasó a Inactivo tras ${umbralDias} días sin actividad. ` +
          'Escribe a la coordinación para reactivarla.',
        url: '/perfil',
      });
    }

    await audit(db, {
      accion: AUDIT_ACTIONS.RUN_INACTIVITY_JOB,
      entidad: 'jobs',
      entidadId: null,
      valorNuevo: { umbralDias, afectados: rows.length, ids: rows.map((row) => row.id_usuarios) },
      usuarioId: null,
      ip: null,
    });

    return {
      umbralDias,
      afectados: rows.map((row) => row.id_usuarios),
      ejecutadoEn: new Date().toISOString(),
    };
  });
}
