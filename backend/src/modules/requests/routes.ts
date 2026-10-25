import { Router } from 'express';
import { requireActiveAccount } from '../../middleware/accountState.js';
import { requireAuth, requireUser } from '../../middleware/auth.js';
import { requireRole } from '../../middleware/role.js';
import { queryOf, validateBody, validateQuery } from '../../middleware/validate.js';
import { ROLES } from '../../policy/roles.js';
import { asyncHandler } from '../../utils/asyncHandler.js';
import { parseId } from '../../utils/params.js';
import { sendData } from '../../utils/respond.js';
import {
  createRequestSchema,
  listRequestsQuerySchema,
  rejectRequestSchema,
  type ListRequestsQuery,
} from './schemas.js';
import { approveRequest, createRequest, getRequest, listRequests, rejectRequest } from './service.js';

/**
 * Bandeja de solicitudes (FR-014, R38).
 *
 * `POST /requests` solo exige sesión: una cuenta `Limitado` o `Inactivo` debe poder pedir
 * su propio desbloqueo, que es justo lo que la política de cuenta le impide hacer por la
 * vía normal. El resto de la bandeja es exclusiva de la coordinación.
 */
export const requestsRouter = Router();

const admin = [requireAuth, requireRole(ROLES.ADMIN), requireActiveAccount];

requestsRouter.post(
  '/requests',
  requireAuth,
  validateBody(createRequestSchema),
  asyncHandler(async (req, res) => {
    const created = await createRequest(req.body, requireUser(req), req.ip ?? null);
    sendData(res, created, 201);
  }),
);

requestsRouter.get(
  '/requests',
  ...admin,
  validateQuery(listRequestsQuerySchema),
  asyncHandler(async (_req, res) => {
    sendData(res, await listRequests(queryOf<ListRequestsQuery>(res)));
  }),
);

requestsRouter.get(
  '/requests/:id',
  ...admin,
  asyncHandler(async (req, res) => {
    sendData(res, await getRequest(parseId(req, 'solicitud')));
  }),
);

requestsRouter.put(
  '/requests/:id/approve',
  ...admin,
  asyncHandler(async (req, res) => {
    sendData(res, await approveRequest(parseId(req, 'solicitud'), requireUser(req), req.ip ?? null));
  }),
);

requestsRouter.put(
  '/requests/:id/reject',
  ...admin,
  validateBody(rejectRequestSchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await rejectRequest(
        parseId(req, 'solicitud'),
        req.body.motivo,
        requireUser(req),
        req.ip ?? null,
      ),
    );
  }),
);
