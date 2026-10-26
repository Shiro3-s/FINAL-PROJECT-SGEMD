import { z } from 'zod';

/**
 * Exportación de reportes (FR-010, FR-017).
 *
 * `format` es obligatorio: el master documenta `?format=csv`, `xlsx` o `pdf` y un valor
 * por defecto silencioso haría que el archivo descargado no fuera el que el usuario pidió.
 */
export const exportQuerySchema = z
  .object({
    format: z.enum(['csv', 'xlsx', 'pdf']),
    desde: z
      .string()
      .regex(/^\d{4}-\d{2}-\d{2}$/, 'Usa el formato AAAA-MM-DD')
      .optional(),
    hasta: z
      .string()
      .regex(/^\d{4}-\d{2}-\d{2}$/, 'Usa el formato AAAA-MM-DD')
      .optional(),
    docenteId: z.coerce.number().int().positive().optional(),
  })
  .strict();

export type ExportQuery = z.infer<typeof exportQuerySchema>;
