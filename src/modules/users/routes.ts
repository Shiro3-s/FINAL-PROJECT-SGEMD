import { Router } from 'express';
import { requireActiveAccount } from '../../middleware/accountState.js';
import { requireAuth, requireUser } from '../../middleware/auth.js';
import { requireRole } from '../../middleware/role.js';
import { queryOf, validateBody, validateQuery } from '../../middleware/validate.js';
import { ROLES } from '../../policy/roles.js';
import { asyncHandler } from '../../utils/asyncHandler.js';
import { parseId } from '../../utils/params.js';
import { sendData, sendMessage } from '../../utils/respond.js';
import { toPublicUser } from '../auth/types.js';
import {
  createUserSchema,
  listUsersQuerySchema,
  rejectSchema,
  stateSchema,
  updateMeSchema,
  updateUserSchema,
  type ListUsersQuery,
} from './schemas.js';
import {
  changeState,
  createUser,
  deleteUser,
  getUser,
  listUsers,
  reactivateUser,
  rejectActivation,
  updateMe,
  updateUser,
  validateUser,
} from './service.js';

export const usersRouter = Router();

/** Cadena de autorización de la gestión de cuentas: sesión, rol y cuenta operativa. */
const admin = [requireAuth, requireRole(ROLES.ADMIN), requireActiveAccount];

/* -------------------------------------------------------------------------------------
 * Perfil propio (siempre disponible, también para cuentas Limitado: AQ-07 opción A)
 * ----------------------------------------------------------------------------------- */

usersRouter.get('/users/me', requireAuth, (req, res) => {
  sendData(res, toPublicUser(requireUser(req)));
});

usersRouter.put(
  '/users/me',
  requireAuth,
  validateBody(updateMeSchema),
  asyncHandler(async (req, res) => {
    const user = await updateMe(requireUser(req), req.body, req.ip ?? null);
    sendData(res, user);
  }),
);

/* -------------------------------------------------------------------------------------
 * Listados y alta
 * ----------------------------------------------------------------------------------- */

usersRouter.get(
  '/users',
  ...admin,
  validateQuery(listUsersQuerySchema),
  asyncHandler(async (_req, res) => {
    sendData(res, await listUsers(queryOf<ListUsersQuery>(res)));
  }),
);

usersRouter.get(
  '/users/students',
  ...admin,
  validateQuery(listUsersQuerySchema),
  asyncHandler(async (_req, res) => {
    sendData(res, await listUsers(queryOf<ListUsersQuery>(res), ROLES.ESTUDIANTE));
  }),
);

usersRouter.get(
  '/users/teachers',
  ...admin,
  validateQuery(listUsersQuerySchema),
  asyncHandler(async (_req, res) => {
    sendData(res, await listUsers(queryOf<ListUsersQuery>(res), ROLES.DOCENTE));
  }),
);

usersRouter.post(
  '/users',
  ...admin,
  validateBody(createUserSchema),
  asyncHandler(async (req, res) => {
    const user = await createUser(req.body, requireUser(req), req.ip ?? null);
    sendData(res, user, 201);
  }),
);

/* -------------------------------------------------------------------------------------
 * Detalle y edición
 * ----------------------------------------------------------------------------------- */

usersRouter.get(
  '/users/:id',
  requireAuth,
  asyncHandler(async (req, res) => {
    sendData(res, await getUser(parseId(req, 'usuario'), requireUser(req)));
  }),
);

usersRouter.put(
  '/users/:id',
  ...admin,
  validateBody(updateUserSchema),
  asyncHandler(async (req, res) => {
    const user = await updateUser(parseId(req, 'usuario'), req.body, requireUser(req), req.ip ?? null);
    sendData(res, user);
  }),
);

usersRouter.delete(
  '/users/:id',
  ...admin,
  asyncHandler(async (req, res) => {
    await deleteUser(parseId(req, 'usuario'), requireUser(req), req.ip ?? null);
    sendMessage(res, 'Cuenta dada de baja.');
  }),
);

/* -------------------------------------------------------------------------------------
 * Ciclo de vida de la cuenta (BR-003, R34)
 * ----------------------------------------------------------------------------------- */

usersRouter.post(
  '/users/:id/validate',
  ...admin,
  asyncHandler(async (req, res) => {
    sendData(res, await validateUser(parseId(req, 'usuario'), requireUser(req), req.ip ?? null));
  }),
);

usersRouter.post(
  '/users/:id/reject',
  ...admin,
  validateBody(rejectSchema),
  asyncHandler(async (req, res) => {
    await rejectActivation(parseId(req, 'usuario'), req.body.motivo, requireUser(req), req.ip ?? null);
    sendMessage(res, 'Activación rechazada. Se notificó al titular.');
  }),
);

usersRouter.post(
  '/users/:id/reactivate',
  ...admin,
  asyncHandler(async (req, res) => {
    sendData(res, await reactivateUser(parseId(req, 'usuario'), requireUser(req), req.ip ?? null));
  }),
);

usersRouter.patch(
  '/users/:id/state',
  ...admin,
  validateBody(stateSchema),
  asyncHandler(async (req, res) => {
    sendData(res, await changeState(parseId(req, 'usuario'), req.body, requireUser(req), req.ip ?? null));
  }),
);
