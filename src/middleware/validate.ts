import type { NextFunction, Request, RequestHandler, Response } from 'express';
import type { ZodType } from 'zod';
import { AppError } from '../utils/AppError.js';

function fieldErrors(issues: readonly { path: PropertyKey[]; message: string }[]) {
  const fields: Record<string, string> = {};
  for (const issue of issues) {
    const path = issue.path.map(String).join('.') || '_';
    if (!fields[path]) fields[path] = issue.message;
  }
  return fields;
}

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
      next(
        new AppError(
          400,
          'VALIDATION_ERROR',
          'Revisa los datos enviados.',
          fieldErrors(result.error.issues),
        ),
      );
      return;
    }

    req.body = result.data;
    next();
  };
}

/**
 * Valida y normaliza la cadena de consulta (`page`, `pageSize`, filtros, orden).
 *
 * Express entrega todo como texto; los esquemas usan `z.coerce`. `.strict()` rechaza
 * parámetros desconocidos, de modo que un nombre de columna arbitrario nunca llega al
 * `ORDER BY`.
 *
 * Express 5 declara `req.query` como de solo lectura, así que el resultado convertido se
 * guarda en `res.locals.query` y el handler lo lee con `queryOf(res)`.
 */
export function validateQuery<T>(schema: ZodType<T>): RequestHandler {
  return (req: Request, res: Response, next: NextFunction) => {
    const result = schema.safeParse(req.query);

    if (!result.success) {
      next(
        new AppError(
          400,
          'VALIDATION_ERROR',
          'Revisa los parámetros de la consulta.',
          fieldErrors(result.error.issues),
        ),
      );
      return;
    }

    res.locals.query = result.data;
    next();
  };
}

/** Consulta ya validada y convertida por `validateQuery`. */
export function queryOf<T>(res: Response): T {
  return res.locals.query as T;
}
