import { Router } from 'express';
import { requireActiveAccount } from '../../middleware/accountState.js';
import { requireAuth, requireUser } from '../../middleware/auth.js';
import { requireRole } from '../../middleware/role.js';
import { queryOf, validateBody, validateQuery } from '../../middleware/validate.js';
import { ROLES } from '../../policy/roles.js';
import { asyncHandler } from '../../utils/asyncHandler.js';
import { parseId } from '../../utils/params.js';
import { sendData, sendMessage } from '../../utils/respond.js';
import {
  createTracingSchema,
  listTracingQuerySchema,
  updateTracingSchema,
  type ListTracingQuery,
} from './schemas.js';
import {
  createTracing,
  deleteTracing,
  getTracing,
  listTracing,
  updateTracing,
} from './service.js';

/**
 * Seguimientos del emprendimiento.
 *
 * El estudiante solo lee; el docente asignado y el administrador escriben. El listado
 * cuelga del emprendimiento (`/tracing/entrepreneurship/:id`), como en el contrato.
 */
export const tracingRouter = Router();

const reader = [
  requireAuth,
  requireActiveAccount,
  requireRole(ROLES.ADMIN, ROLES.DOCENTE, ROLES.ESTUDIANTE),
];
const writer = [requireAuth, requireActiveAccount, requireRole(ROLES.ADMIN, ROLES.DOCENTE)];

tracingRouter.get(
  '/tracing/entrepreneurship/:id',
  ...reader,
  validateQuery(listTracingQuerySchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await listTracing(
        parseId(req, 'emprendimiento'),
        queryOf<ListTracingQuery>(res),
        requireUser(req),
      ),
    );
  }),
);

tracingRouter.get(
  '/tracing/:id',
  ...reader,
  asyncHandler(async (req, res) => {
    sendData(res, await getTracing(parseId(req, 'seguimiento'), requireUser(req)));
  }),
);

tracingRouter.post(
  '/tracing',
  ...writer,
  validateBody(createTracingSchema),
  asyncHandler(async (req, res) => {
    sendData(res, await createTracing(req.body, requireUser(req), req.ip ?? null), 201);
  }),
);

tracingRouter.put(
  '/tracing/:id',
  ...writer,
  validateBody(updateTracingSchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await updateTracing(parseId(req, 'seguimiento'), req.body, requireUser(req), req.ip ?? null),
    );
  }),
);

tracingRouter.delete(
  '/tracing/:id',
  ...writer,
  asyncHandler(async (req, res) => {
    await deleteTracing(parseId(req, 'seguimiento'), requireUser(req), req.ip ?? null);
    sendMessage(res, 'Seguimiento dado de baja.');
  }),
);
