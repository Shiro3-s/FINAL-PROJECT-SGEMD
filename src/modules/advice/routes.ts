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
  acceptAdviceSchema,
  createAdviceSchema,
  listAdviceQuerySchema,
  rejectAdviceSchema,
  reproposeAdviceSchema,
  updateAdviceSchema,
  type ListAdviceQuery,
} from './schemas.js';
import {
  acceptAdvice,
  createAdvice,
  deleteAdvice,
  getAdvice,
  listAdvice,
  rejectAdvice,
  reproposeAdvice,
  updateAdvice,
} from './service.js';

/**
 * Asesorías (FR-004, FR-015, BR-002).
 *
 * Todos los roles leen (cada uno con su alcance); solo el administrador y el docente
 * escriben. El estudiante no tiene ninguna ruta de escritura: pide una cita por la
 * bandeja de solicitudes y la coordinación la convierte en asesoría (BR-002).
 */
export const adviceRouter = Router();

const reader = [
  requireAuth,
  requireActiveAccount,
  requireRole(ROLES.ADMIN, ROLES.DOCENTE, ROLES.ESTUDIANTE),
];
const writer = [requireAuth, requireActiveAccount, requireRole(ROLES.ADMIN, ROLES.DOCENTE)];

adviceRouter.get(
  '/advice',
  ...reader,
  validateQuery(listAdviceQuerySchema),
  asyncHandler(async (req, res) => {
    sendData(res, await listAdvice(queryOf<ListAdviceQuery>(res), requireUser(req)));
  }),
);

adviceRouter.get(
  '/advice/:id',
  ...reader,
  asyncHandler(async (req, res) => {
    sendData(res, await getAdvice(parseId(req, 'asesoría'), requireUser(req)));
  }),
);

adviceRouter.post(
  '/advice',
  ...writer,
  validateBody(createAdviceSchema),
  asyncHandler(async (req, res) => {
    sendData(res, await createAdvice(req.body, requireUser(req), req.ip ?? null), 201);
  }),
);

adviceRouter.put(
  '/advice/:id',
  ...writer,
  validateBody(updateAdviceSchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await updateAdvice(
        parseId(req, 'asesoría'),
        req.body,
        requireUser(req),
        req.ip ?? null,
      ),
    );
  }),
);

adviceRouter.post(
  '/advice/:id/accept',
  ...writer,
  validateBody(acceptAdviceSchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await acceptAdvice(
        parseId(req, 'asesoría'),
        req.body,
        requireUser(req),
        req.ip ?? null,
      ),
    );
  }),
);

adviceRouter.post(
  '/advice/:id/repropose',
  ...writer,
  validateBody(reproposeAdviceSchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await reproposeAdvice(
        parseId(req, 'asesoría'),
        req.body,
        requireUser(req),
        req.ip ?? null,
      ),
    );
  }),
);

adviceRouter.post(
  '/advice/:id/reject',
  ...writer,
  validateBody(rejectAdviceSchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await rejectAdvice(
        parseId(req, 'asesoría'),
        req.body.motivo,
        requireUser(req),
        req.ip ?? null,
      ),
    );
  }),
);

adviceRouter.delete(
  '/advice/:id',
  ...writer,
  asyncHandler(async (req, res) => {
    await deleteAdvice(parseId(req, 'asesoría'), requireUser(req), req.ip ?? null);
    sendMessage(res, 'Asesoría dada de baja.');
  }),
);
