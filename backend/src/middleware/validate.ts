import type { NextFunction, Request, RequestHandler, Response } from 'express';
import type { ZodType } from 'zod';
import { AppError } from '../utils/AppError.js';

/**
 * Valida el cuerpo contra un esquema `zod` y **reemplaza** `req.body` por el resultado.
 *
 * Los esquemas usan `.strict()`: un campo que el cliente no debería enviar (`role`,
 * `estado`, `avance`, `puntajeTotal`, …) se rechaza con 400 en vez de ignorarse
 * silenciosamente (§15, T33).
 */
export function validateBody<T>(schema: ZodType<T>): RequestHandler {
  return (req: Request, _res: Response, next: NextFunction) => {
    const result = schema.safeParse(req.body);

    if (!result.success) {
      const fields: Record<string, string> = {};
      for (const issue of result.error.issues) {
        const path = issue.path.join('.') || '_';
        if (!fields[path]) fields[path] = issue.message;
      }
      next(new AppError(400, 'VALIDATION_ERROR', 'Revisa los datos enviados.', fields));
      return;
    }

    req.body = result.data;
    next();
  };
}
