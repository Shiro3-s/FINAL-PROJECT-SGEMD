import type { NotificacionTipo } from '@sgemd/shared';
import { afterCommit } from '../db/pool.js';
import type { Queryable } from './audit.js';
import { notificationChannel } from './notificationChannel/index.js';

/**
 * Escritura de notificaciones (FR-005, FR-019, T21).
 *
 * Se llama **dentro** de la misma transacción que el cambio que la origina, igual que la
 * auditoría. El aviso por SSE se registra con `afterCommit`: si la transacción revierte,
 * el cliente nunca recibe un evento de una notificación que no existe.
 *
 * Preferencias: `configuracion_programa` tiene `notif_tareas`, `notif_asesorias` y
 * `notif_seguimiento`. Si la bandera está en `false`, la fila no se crea (no se avisa de
 * lo que el programa decidió no avisar). Un valor ausente o ilegible se interpreta como
 * `true`: es preferible avisar de más que perder un aviso por una configuración corrupta.
 */
export interface NotifyInput {
  usuarioId: number;
  tipo: NotificacionTipo;
  mensaje: string;
  url?: string | null;
  tipoObjeto?: string | null;
  objetoId?: number | null;
}

const PREFERENCE: Partial<Record<NotificacionTipo, string>> = {
  Tarea: 'notif_tareas',
  Asesoría: 'notif_asesorias',
  Seguimiento: 'notif_seguimiento',
};

async function isEnabled(db: Queryable, tipo: NotificacionTipo): Promise<boolean> {
  const clave = PREFERENCE[tipo];
  if (!clave) return true;

  const { rows } = await db.query<{ valor: string | null }>(
    'SELECT valor FROM configuracion_programa WHERE clave = $1',
    [clave],
  );

  const valor = rows[0]?.valor;
  if (valor === undefined || valor === null || valor.trim() === '') return true;
  return valor.trim().toLowerCase() !== 'false';
}

/** Cuenta de no leídas del usuario, opcionalmente restringida a un tipo. */
export async function countUnread(
  db: Queryable,
  usuarioId: number,
  tipo?: NotificacionTipo,
): Promise<number> {
  const params: unknown[] = [usuarioId];
  let filter = '';
  if (tipo) {
    params.push(tipo);
    filter = ` AND tipo = $${params.length}`;
  }

  const { rows } = await db.query<{ total: number }>(
    `SELECT COUNT(*)::int AS total
       FROM notificaciones
      WHERE usuarios_id_usuarios = $1 AND leida = FALSE${filter}`,
    params,
  );

  return rows[0]?.total ?? 0;
}

/**
 * Inserta la notificación y publica el evento mínimo tras confirmar la transacción.
 * Devuelve el id, o `null` si la preferencia del programa la suprimió.
 */
export async function notify(db: Queryable, input: NotifyInput): Promise<number | null> {
  if (!(await isEnabled(db, input.tipo))) return null;

  const { rows } = await db.query<{ id_notificaciones: number }>(
    `INSERT INTO notificaciones (tipo, mensaje, url, tipo_objeto, objeto_id, usuarios_id_usuarios)
     VALUES ($1, $2, $3, $4, $5, $6)
     RETURNING id_notificaciones`,
    [
      input.tipo,
      input.mensaje,
      input.url ?? null,
      input.tipoObjeto ?? null,
      input.objetoId ?? null,
      input.usuarioId,
    ],
  );

  const id = rows[0]!.id_notificaciones;
  const unreadCount = await countUnread(db, input.usuarioId);

  afterCommit(() => {
    notificationChannel.publish(input.usuarioId, {
      notificationId: id,
      tipo: input.tipo,
      unreadCount,
    });
  });

  return id;
}
