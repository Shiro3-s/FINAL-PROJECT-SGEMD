import type { RequestHandler } from 'express';
import { blockedReason, canOperate } from '../policy/accountState.js';
import { AppError } from '../utils/AppError.js';
import { requireUser } from './auth.js';

/**
 * Exige una cuenta operativa (`Activo`) para entrar a un módulo de trabajo.
 *
 * Responde `403 ACCOUNT_NOT_ACTIVE` (código documentado en `docs/api.md`), que es el
 * que comprueba T03 para una cuenta `Limitado`.
 */
export const requireActiveAccount: RequestHandler = (req, _res, next) => {
  const user = requireUser(req);

  if (!canOperate(user.estado)) {
    next(new AppError(403, 'ACCOUNT_NOT_ACTIVE', blockedReason(user.estado)));
    return;
  }

  next();
};
