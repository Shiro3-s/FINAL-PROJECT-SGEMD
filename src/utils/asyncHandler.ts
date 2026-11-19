import type { NextFunction, Request, RequestHandler, Response } from 'express';

/**
 * Envuelve un handler async para que cualquier rechazo llegue al manejador de errores.
 * Ningún `catch` vacío: los errores siempre se propagan.
 */
export function asyncHandler(
  handler: (req: Request, res: Response, next: NextFunction) => Promise<unknown>,
): RequestHandler {
  return (req, res, next) => {
    handler(req, res, next).catch(next);
  };
}
