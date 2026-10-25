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
  createEntrepreneurshipSchema,
  listEntrepreneurshipQuerySchema,
  rejectEntrepreneurshipSchema,
  updateEntrepreneurshipSchema,
  type ListEntrepreneurshipQuery,
} from './schemas.js';
import {
  approveEntrepreneurship,
  createEntrepreneurship,
  deleteEntrepreneurship,
  getEntrepreneurship,
  listEntrepreneurship,
  rejectEntrepreneurship,
  updateEntrepreneurship,
} from './service.js';

/**
 * Emprendimientos. Todas las rutas exigen sesión y cuenta `Activo`: es un módulo de
 * trabajo (AQ-07 opción A). La lectura se filtra por rol en el servicio: el estudiante ve
 * los suyos, el docente los asignados y el administrador todos.
 */
export const entrepreneurshipRouter = Router();

const reader = [
  requireAuth,
  requireActiveAccount,
  requireRole(ROLES.ADMIN, ROLES.ESTUDIANTE, ROLES.DOCENTE),
];
const admin = [requireAuth, requireRole(ROLES.ADMIN), requireActiveAccount];

entrepreneurshipRouter.get(
  '/entrepreneurship',
  ...reader,
  validateQuery(listEntrepreneurshipQuerySchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await listEntrepreneurship(queryOf<ListEntrepreneurshipQuery>(res), requireUser(req)),
    );
  }),
);

entrepreneurshipRouter.get(
  '/entrepreneurship/:id',
  ...reader,
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await getEntrepreneurship(parseId(req, 'emprendimiento'), requireUser(req)),
    );
  }),
);

entrepreneurshipRouter.post(
  '/entrepreneurship',
  ...admin,
  validateBody(createEntrepreneurshipSchema),
  asyncHandler(async (req, res) => {
    const created = await createEntrepreneurship(
      req.body,
      requireUser(req),
      req.ip ?? null,
    );
    sendData(res, created, 201);
  }),
);

entrepreneurshipRouter.put(
  '/entrepreneurship/:id',
  requireAuth,
  requireRole(ROLES.ADMIN, ROLES.ESTUDIANTE),
  requireActiveAccount,
  validateBody(updateEntrepreneurshipSchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await updateEntrepreneurship(
        parseId(req, 'emprendimiento'),
        req.body,
        requireUser(req),
        req.ip ?? null,
      ),
    );
  }),
);

entrepreneurshipRouter.delete(
  '/entrepreneurship/:id',
  ...admin,
  asyncHandler(async (req, res) => {
    await deleteEntrepreneurship(parseId(req, 'emprendimiento'), requireUser(req), req.ip ?? null);
    sendMessage(res, 'Emprendimiento dado de baja.');
  }),
);

entrepreneurshipRouter.post(
  '/entrepreneurship/:id/approve',
  ...admin,
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await approveEntrepreneurship(parseId(req, 'emprendimiento'), requireUser(req), req.ip ?? null),
    );
  }),
);

entrepreneurshipRouter.post(
  '/entrepreneurship/:id/reject',
  ...admin,
  validateBody(rejectEntrepreneurshipSchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await rejectEntrepreneurship(
        parseId(req, 'emprendimiento'),
        req.body.motivo,
        requireUser(req),
        req.ip ?? null,
      ),
    );
  }),
);
