import type { Request } from 'express';
import { z } from 'zod';
import { AppError } from './AppError.js';

const idSchema = z.coerce.number().int().positive();

/**
 * `:id` de la ruta como entero positivo.
 *
 * Un id no numérico es un error de la petición (`400`), no un «no encontrado» ambiguo.
 * `label` solo cambia el texto del mensaje ("usuario", "emprendimiento", …).
 */
export function parseId(req: Request, label: string): number {
  const parsed = idSchema.safeParse(req.params.id);

  if (!parsed.success) {
    throw new AppError(
      400,
      'VALIDATION_ERROR',
      `El identificador de ${label} no es válido.`,
      { id: 'Debe ser un número entero positivo' },
    );
  }

  return parsed.data;
}
