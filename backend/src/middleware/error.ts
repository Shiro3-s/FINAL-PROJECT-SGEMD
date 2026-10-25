import type { NextFunction, Request, Response } from 'express';
import { logger } from '../config/logger.js';
import { AppError } from '../utils/AppError.js';

export function notFound(req: Request, _res: Response, next: NextFunction): void {
  next(new AppError(404, 'NOT_FOUND', `Ruta no encontrada: ${req.method} ${req.path}`));
}

/**
 * Envoltura única de error: `{ success: false, error: { code, message, fields? } }`.
 * Nunca se devuelve un stack ni una ruta interna.
 */
export function errorHandler(
  error: unknown,
  _req: Request,
  res: Response,
  next: NextFunction,
): void {
  if (res.headersSent) {
    next(error);
    return;
  }

  if (error instanceof AppError) {
    res.status(error.status).json({
      success: false,
      error: {
        code: error.code,
        message: error.message,
        ...(error.fields ? { fields: error.fields } : {}),
      },
    });
    return;
  }

  logger.error({ err: error }, 'Error no controlado');
  res.status(500).json({
    success: false,
    error: {
      code: 'INTERNAL_ERROR',
      message: 'Ocurrió un error inesperado. Intenta de nuevo.',
    },
  });
}
