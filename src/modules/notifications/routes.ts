import { Router } from 'express';
import { requireAuth, requireUser } from '../../middleware/auth.js';
import { requireRole } from '../../middleware/role.js';
import { queryOf, validateQuery } from '../../middleware/validate.js';
import { ROLES } from '../../policy/roles.js';
import { notificationChannel } from '../../services/notificationChannel/index.js';
import { asyncHandler } from '../../utils/asyncHandler.js';
import { parseId } from '../../utils/params.js';
import { sendData } from '../../utils/respond.js';
import {
  listNotificationsQuerySchema,
  type ListNotificationsQuery,
} from './schemas.js';
import {
  listNotifications,
  markAllNotificationsRead,
  markNotificationRead,
  unreadCount,
} from './service.js';

/**
 * Bandeja y canal en tiempo real (FR-019, T21).
 *
 * Ninguna ruta exige cuenta `Activo`: AQ-07 opción A deja las notificaciones disponibles
 * también para una cuenta `Limitado`, que es justo la que necesita enterarse de que su
 * desbloqueo fue resuelto. La lectura siempre se limita a las notificaciones propias.
 */
export const notificationsRouter = Router();

const reader = [
  requireAuth,
  requireRole(ROLES.ADMIN, ROLES.DOCENTE, ROLES.ESTUDIANTE),
];

notificationsRouter.get(
  '/notifications',
  ...reader,
  validateQuery(listNotificationsQuerySchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await listNotifications(
        queryOf<ListNotificationsQuery>(res),
        requireUser(req),
      ),
    );
  }),
);

/**
 * `GET /notifications/stream` — SSE.
 *
 * La respuesta queda abierta: no se llama a `res.end()` ni se envía un cuerpo JSON. El
 * evento `ready` entrega el contador inicial; cada `notification` solo lleva el id, el
 * tipo y el contador (nunca el mensaje). El cierre lo gestiona el canal.
 */
notificationsRouter.get(
  '/notifications/stream',
  ...reader,
  asyncHandler(async (req, res) => {
    const actor = requireUser(req);
    const unread = await unreadCount(actor);
    notificationChannel.subscribe(actor.id, res, unread);
  }),
);

notificationsRouter.put(
  '/notifications/read-all',
  ...reader,
  asyncHandler(async (req, res) => {
    sendData(res, await markAllNotificationsRead(requireUser(req)));
  }),
);

notificationsRouter.put(
  '/notifications/:id/read',
  ...reader,
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await markNotificationRead(parseId(req, 'notificación'), requireUser(req)),
    );
  }),
);
