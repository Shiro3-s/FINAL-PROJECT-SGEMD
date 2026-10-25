import type { RequestHandler } from 'express';
import { AppError } from '../utils/AppError.js';
import { requireUser } from './auth.js';

/**
 * Autorización por rol. El rol sale de la fila del usuario, no del token (§15).
 * Denegar por defecto: sin rol permitido explícito, 403.
 */
export function requireRole(...roles: number[]): RequestHandler {
  return (req, _res, next) => {
    const user = requireUser(req);
    if (!roles.includes(user.rolId)) {
      next(new AppError(403, 'ROLE_NOT_ALLOWED', 'No tienes permiso para realizar esta acción.'));
      return;
    }
    next();
  };
}
