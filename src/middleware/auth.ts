import type { RequestHandler } from 'express';
import { SESSION_COOKIE, verifySession } from '../modules/auth/session.js';
import type { SessionUser } from '../modules/auth/types.js';
import { findUserById } from '../modules/users/repository.js';
import { AppError } from '../utils/AppError.js';
import { asyncHandler } from '../utils/asyncHandler.js';

/**
 * Autenticación por cookie `sgemd_session`.
 *
 * El JWT solo aporta el `id`; el rol y el estado se leen de la fila **en cada petición**
 * (master §15). Así, desactivar o dar de baja a un usuario surte efecto de inmediato
 * aunque su token siga vigente (T04). Un usuario con baja lógica recibe `401`.
 */
export const requireAuth: RequestHandler = asyncHandler(async (req, _res, next) => {
  const token = req.cookies?.[SESSION_COOKIE];
  if (typeof token !== 'string' || token.length === 0) {
    throw new AppError(401, 'AUTH_REQUIRED', 'Debes iniciar sesión.');
  }

  let claims;
  try {
    claims = await verifySession(token);
  } catch {
    throw new AppError(401, 'AUTH_INVALID', 'La sesión no es válida o expiró. Inicia sesión de nuevo.');
  }

  const user = await findUserById(claims.id);
  if (!user) {
    throw new AppError(401, 'AUTH_INVALID', 'La sesión no es válida o expiró. Inicia sesión de nuevo.');
  }

  req.user = user;
  next();
});

/** Devuelve el usuario ya autenticado o falla: evita `req.user!` repartido por el código. */
export function requireUser(req: { user?: SessionUser }): SessionUser {
  if (!req.user) {
    throw new AppError(401, 'AUTH_REQUIRED', 'Debes iniciar sesión.');
  }
  return req.user;
}
