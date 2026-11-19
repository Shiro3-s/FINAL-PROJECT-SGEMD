import type { NextFunction, Request, Response } from 'express';
import { env } from '../config/env.js';
import { AppError } from '../utils/AppError.js';

const SAFE_METHODS = new Set(['GET', 'HEAD', 'OPTIONS']);

/**
 * Defensa en profundidad sobre `SameSite=Strict` (master §12 regla 10): toda petición
 * que muta debe ser del mismo origen. Los clientes que no envían `Origin` (curl, pruebas
 * de integración) deben enviarlo explícitamente.
 */
export function originCheck(req: Request, _res: Response, next: NextFunction): void {
  if (SAFE_METHODS.has(req.method)) {
    next();
    return;
  }

  const origin = req.get('origin');
  const fetchSite = req.get('sec-fetch-site');

  if (origin === env.APP_ORIGIN) {
    next();
    return;
  }

  if (!origin && fetchSite === 'same-origin') {
    next();
    return;
  }

  next(new AppError(403, 'ORIGIN_NOT_ALLOWED', 'Origen de la petición no permitido'));
}
