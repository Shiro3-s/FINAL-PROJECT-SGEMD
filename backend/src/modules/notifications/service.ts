import type { NotificacionTipo } from '@sgemd/shared';
import { query } from '../../db/pool.js';
import { countUnread } from '../../services/notify.js';
import { AppError } from '../../utils/AppError.js';
import type { SessionUser } from '../auth/types.js';
import type { ListNotificationsQuery } from './schemas.js';

/**
 * Bandeja de notificaciones (FR-019, T21).
 *
 * Solo se leen y se marcan las notificaciones **propias**: el filtro por
 * `usuarios_id_usuarios` va en todas las consultas, de modo que el id de otro usuario
 * responde `404` y no revela que existe (NFR-002).
 *
 * El contador `sinLeer` es exacto: se cuenta con la misma condición de tipo que el
 * listado, pero sin la condición de leída (si se filtró por «no leídas», el contador debe
 * seguir diciendo cuántas hay en total para ese tipo).
 */

export interface Notification {
  id: number;
  tipo: NotificacionTipo;
  mensaje: string;
  url: string | null;
  tipoObjeto: string | null;
  objetoId: number | null;
  leida: boolean;
  fecha: string;
}

export interface NotificationPage {
  items: Notification[];
  total: number;
  page: number;
  pageSize: number;
  sinLeer: number;
}

type NotificationRow = {
  id_notificaciones: number;
  tipo: string;
  mensaje: string;
  url: string | null;
  tipo_objeto: string | null;
  objeto_id: number | null;
  leida: boolean;
  fecha: Date;
};

const SELECT = `
  SELECT id_notificaciones, tipo, mensaje, url, tipo_objeto, objeto_id, leida, fecha
    FROM notificaciones
`;

function mapRow(row: NotificationRow): Notification {
  return {
    id: row.id_notificaciones,
    tipo: row.tipo as NotificacionTipo,
    mensaje: row.mensaje,
    url: row.url,
    tipoObjeto: row.tipo_objeto,
    objetoId: row.objeto_id,
    leida: row.leida,
    fecha: row.fecha.toISOString(),
  };
}

function notFound(): AppError {
  return new AppError(404, 'NOT_FOUND', 'La notificación no existe.');
}

export async function listNotifications(
  options: ListNotificationsQuery,
  actor: SessionUser,
): Promise<NotificationPage> {
  const params: unknown[] = [actor.id];
  const where = ['usuarios_id_usuarios = $1'];

  if (options.leida !== undefined) {
    params.push(options.leida);
    where.push(`leida = $${params.length}`);
  }
  if (options.tipo) {
    params.push(options.tipo);
    where.push(`tipo = $${params.length}`);
  }

  const whereSql = `WHERE ${where.join(' AND ')}`;
  const countParams = [...params];

  params.push(options.pageSize);
  const limit = `$${params.length}`;
  params.push((options.page - 1) * options.pageSize);
  const offset = `$${params.length}`;

  const [count, page, sinLeer] = await Promise.all([
    query<{ total: string }>(
      `SELECT COUNT(*)::text AS total FROM notificaciones ${whereSql}`,
      countParams,
    ),
    query<NotificationRow>(
      `${SELECT} ${whereSql}
        ORDER BY fecha DESC, id_notificaciones DESC
        LIMIT ${limit} OFFSET ${offset}`,
      params,
    ),
    countUnread({ query }, actor.id, options.tipo),
  ]);

  return {
    items: page.rows.map(mapRow),
    total: Number(count.rows[0]?.total ?? 0),
    page: options.page,
    pageSize: options.pageSize,
    sinLeer,
  };
}

/**
 * `PUT /notifications/:id/read` — marca una como leída.
 *
 * Es idempotente: volver a marcar una ya leída devuelve la fila y el contador actual. Una
 * notificación ajena responde `404` (el `WHERE` incluye al propietario).
 */
export async function markNotificationRead(
  id: number,
  actor: SessionUser,
): Promise<Notification & { sinLeer: number }> {
  const { rows } = await query<NotificationRow>(
    `UPDATE notificaciones SET leida = TRUE
      WHERE id_notificaciones = $1 AND usuarios_id_usuarios = $2
      RETURNING id_notificaciones, tipo, mensaje, url, tipo_objeto, objeto_id, leida, fecha`,
    [id, actor.id],
  );

  if (!rows[0]) throw notFound();

  return { ...mapRow(rows[0]), sinLeer: await countUnread({ query }, actor.id) };
}

/** `PUT /notifications/read-all` — marca todas las del usuario. */
export async function markAllNotificationsRead(
  actor: SessionUser,
): Promise<{ actualizadas: number; sinLeer: number }> {
  const { rowCount } = await query(
    `UPDATE notificaciones SET leida = TRUE
      WHERE usuarios_id_usuarios = $1 AND leida = FALSE`,
    [actor.id],
  );

  return { actualizadas: rowCount ?? 0, sinLeer: 0 };
}

/** Contador de no leídas que se envía al abrir el flujo SSE. */
export function unreadCount(actor: SessionUser): Promise<number> {
  return countUnread({ query }, actor.id);
}
