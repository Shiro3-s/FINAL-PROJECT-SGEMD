import { Router } from 'express';
import { requireAuth, requireUser } from '../../middleware/auth.js';
import { toPublicUser } from '../auth/types.js';
import { sendData } from '../../utils/respond.js';

export const usersRouter = Router();

/**
 * `GET /api/users/me` — la SPA aprende quién es por aquí, nunca leyendo la cookie
 * (master §13.3). No devuelve la contraseña ni ningún hash.
 */
usersRouter.get('/users/me', requireAuth, (req, res) => {
  sendData(res, toPublicUser(requireUser(req)));
});
