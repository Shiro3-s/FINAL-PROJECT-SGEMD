import { Router } from 'express';
import { requireAuth, requireUser } from '../../middleware/auth.js';
import { requireRole } from '../../middleware/role.js';
import { queryOf, validateBody, validateQuery } from '../../middleware/validate.js';
import { ROLES } from '../../policy/roles.js';
import { asyncHandler } from '../../utils/asyncHandler.js';
import { parseId } from '../../utils/params.js';
import { sendData } from '../../utils/respond.js';
import {
  listActaQuerySchema,
  reviewActaSchema,
  type ListActaQuery,
  type ReviewActaInput,
} from './schemas.js';
import { actaTemplate, getActa, listActas, reviewActa, uploadActa } from './service.js';

/**
 * Acta de compromiso y confidencialidad (FR-003, BR-009, T26).
 *
 * El estudiante descarga la plantilla, la firma y la sube; el administrador la revisa. El
 * docente no participa en este circuito: recibe `403` en todas las rutas.
 *
 * Ninguna ruta exige cuenta `Activo`: AQ-07 opción A deja el acta disponible también para
 * una cuenta `Limitado`, que es justo la que espera su desbloqueo.
 */
export const actaRouter = Router();

const reader = [requireAuth, requireRole(ROLES.ADMIN, ROLES.ESTUDIANTE)];

actaRouter.get(
  '/acta/template',
  ...reader,
  asyncHandler(async (_req, _res) => {
    actaTemplate();
  }),
);

actaRouter.get(
  '/acta',
  ...reader,
  validateQuery(listActaQuerySchema),
  asyncHandler(async (req, res) => {
    sendData(res, await listActas(queryOf<ListActaQuery>(res), requireUser(req)));
  }),
);

actaRouter.post(
  '/acta',
  ...reader,
  asyncHandler(async (req, res) => {
    sendData(res, await uploadActa(requireUser(req), req, req.ip ?? null), 201);
  }),
);

actaRouter.get(
  '/acta/:id',
  ...reader,
  asyncHandler(async (req, res) => {
    sendData(res, await getActa(parseId(req, 'acta'), requireUser(req)));
  }),
);

actaRouter.put(
  '/acta/:id/review',
  requireAuth,
  requireRole(ROLES.ADMIN),
  validateBody(reviewActaSchema),
  asyncHandler(async (req, res) => {
    sendData(
      res,
      await reviewActa(
        parseId(req, 'acta'),
        requireUser(req),
        req.body as ReviewActaInput,
        req.ip ?? null,
      ),
    );
  }),
);
